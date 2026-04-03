"""Front-half-first empirical smoke runner for structured-spec benchmarks.

This module exists because the older empirical gate measured only a bounded
back-half slice over a frozen blueprint. The front-half-first lane keeps the
same benchmark discipline, but it requires AC14 to earn an approved front-half
artifact before any runtime-only success can reopen the full-trial budget.
"""

from __future__ import annotations

import ast
import asyncio
import copy
import importlib.util
import os
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Literal, Protocol, Sequence, cast

from pydantic import BaseModel, Field
from llm_client.io_log import activate_feature_profile, experiment_run  # type: ignore[import-not-found]

from ac14.acceptance import AcceptanceReviewResponse, acall_llm_structured, render_prompt
from ac14.atomic_io import atomic_write_json, atomic_write_text
from ac14.empirical_comparison import (
    DEFAULT_MAX_ATTEMPTS,
    EMPIRICAL_FEATURE_PROFILE,
    BenchmarkBundle,
    CostObservation,
    RuntimeCaseExecution,
    _attempt_indicates_infrastructure_provider_failure,
    _build_failure_summary,
    _dynamic_field_exists,
    _is_infrastructure_provider_error,
    _observe_llm_cost,
    _review_runtime_cases,
    _semantic_review_passed,
    _strip_dynamic_field_paths,
    load_benchmark_bundle,
)
from ac14.front_half_acceptance import (
    StructuredSpecFrontHalfAcceptanceArtifact,
    build_structured_spec_front_half_acceptance_report,
)
from ac14.generated_codegen import (
    DEFAULT_LLM_MAX_BUDGET,
    DEFAULT_LLM_MODEL,
    GeneratedPackage,
    emit_generated_package,
    load_generated_component_builders,
)
from ac14.generated_evidence import PacketTestReport, run_generated_packet_tests, run_generated_recomposition_proof
from ac14.loader import load_blueprint_dir
from ac14.models import FrozenBlueprint
from ac14.packets import compile_packets
from ac14.recomposition import RecompositionReport
from ac14.runtime import RuntimeComponent, run_blueprint_once
from ac14.structured_spec import (
    StructuredSpecDocument,
    StructuredSpecInterface,
    build_structured_spec_artifact,
)
from ac14.structured_spec_benchmark import (
    StructuredSpecBenchmarkBundle,
    load_structured_spec_benchmark_bundle,
)


FRONT_HALF_FIRST_MONOLITHIC_PROMPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "prompts"
    / "generate_monolithic_runtime_system_from_structured_spec.yaml"
)

FrontHalfFirstCondition = Literal["monolithic", "ac14"]
FrontHalfFirstFailureCategory = Literal[
    "success",
    "infrastructure_provider",
    "front_half",
    "generation",
    "runtime_outputs",
    "semantic_review",
]
FrontHalfFirstSmokeReadinessVerdict = Literal[
    "ready_for_full_trials",
    "blocked_on_front_half",
    "blocked_on_runtime_outputs",
    "blocked_on_harness",
    "blocked_on_infrastructure",
]


class RuntimeSystem(Protocol):
    """Protocol for a whole-system monolithic runtime implementation."""

    def run_case(self, record: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Execute one runtime case and return final outputs keyed by output port."""


class FrontHalfRuntimeContract(BaseModel):
    """Runtime contract inferred from a generated AC14 draft bundle."""

    source_component_id: str = Field(description="Generated source component used for runtime execution.")
    source_port_name: str = Field(description="Top-level input or source-output port used at runtime.")
    source_mode: Literal["input_port", "source_output"] = Field(
        default="input_port",
        description="Whether runtime records are injected into one input port or one zero-input source component output.",
    )
    final_component_id: str | None = Field(
        default=None,
        description="Single generated final component when all reviewable outputs come from one component.",
    )
    final_output_ports: list[str] = Field(description="Final output ports evaluated at runtime.")
    final_output_components: dict[str, str] = Field(
        description="Mapping from each reviewable final output port to the component that emits it.",
    )
    final_output_emitted_ports: dict[str, str] = Field(
        description=(
            "Mapping from each structured-spec final output name to the actual generated "
            "emitted port name used during runtime extraction."
        ),
    )


class MonolithicRuntimeSystemResponse(BaseModel):
    """Structured LLM response for one direct monolithic runtime system."""

    module_code: str = Field(
        description=(
            "Complete standalone Python module source that defines build_system(), "
            "and whose returned object implements run_case(record)."
        ),
    )
    implementation_notes: list[str] = Field(
        description="Short notes about key implementation choices or limitations.",
    )


class FrontHalfFirstFailureClassification(BaseModel):
    """Stable failure classification for one front-half-first attempt."""

    category: FrontHalfFirstFailureCategory = Field(description="Bounded failure category.")
    detail: str = Field(description="Short explanation of the failure.")


class FrontHalfFirstConditionAttemptReport(BaseModel):
    """One bounded attempt for one condition inside the front-half-first smoke lane."""

    attempt_id: int = Field(description="Sequential attempt number starting at 1.")
    artifact_dir: str = Field(description="Directory containing the attempt artifacts.")
    duration_s: float = Field(description="Wall-clock duration for the attempt.")
    llm_cost: CostObservation = Field(description="Observed or unavailable LLM cost for the attempt.")
    front_half_report_path: str | None = Field(
        default=None,
        description="Structured-spec front-half artifact path for the AC14 condition.",
    )
    front_half_passed: bool | None = Field(
        default=None,
        description="Whether the AC14 front-half artifact ended in approved freeze.",
    )
    runtime_contract: FrontHalfRuntimeContract | None = Field(
        default=None,
        description="Inferred runtime contract used for the AC14 generated blueprint.",
    )
    packet_tests_passed: bool | None = Field(
        default=None,
        description="Diagnostic packet-test result when the AC14 condition generated code.",
    )
    recomposition_passed: bool | None = Field(
        default=None,
        description="Diagnostic recomposition result when the AC14 condition generated code.",
    )
    packet_test_report_path: str | None = Field(
        default=None,
        description="Persisted packet-test report path for the AC14 condition.",
    )
    recomposition_report_path: str | None = Field(
        default=None,
        description="Persisted recomposition report path for the AC14 condition.",
    )
    runtime_outputs_passed: bool = Field(description="Whether runtime outputs matched expected outputs.")
    semantic_review: AcceptanceReviewResponse | None = Field(
        default=None,
        description="Requirements-aware review of the runtime outputs when available.",
    )
    semantic_review_passed: bool = Field(description="Whether semantic review passed the benchmark policy.")
    failure_classification: FrontHalfFirstFailureClassification = Field(
        description="Structured failure classification for this attempt.",
    )
    generation_error: str | None = Field(
        default=None,
        description="Generation or runtime-system construction error when one occurred.",
    )
    runtime_cases: list[RuntimeCaseExecution] = Field(description="Per-case runtime execution outcomes.")
    failure_summary: list[str] = Field(description="Compact repair guidance extracted from the attempt.")
    passed: bool = Field(description="Whether the full attempt passed the front-half-first harness.")


class FrontHalfFirstConditionTrialReport(BaseModel):
    """Outcome for one condition across all allowed attempts."""

    condition: FrontHalfFirstCondition = Field(description="Compared condition.")
    passed: bool = Field(description="Whether the condition passed within the allowed attempts.")
    attempts_used: int = Field(description="How many attempts were consumed.")
    repair_loops_used: int = Field(description="How many repair loops were consumed after the first attempt.")
    attempts: list[FrontHalfFirstConditionAttemptReport] = Field(description="Per-attempt reports.")


class FrontHalfFirstPairedTrialReport(BaseModel):
    """Persisted report for one front-half-first paired trial."""

    benchmark_id: str = Field(description="Structured-spec benchmark identifier under evaluation.")
    trial_id: int = Field(description="Sequential paired-trial identifier.")
    monolithic: FrontHalfFirstConditionTrialReport = Field(description="Monolithic condition report.")
    ac14: FrontHalfFirstConditionTrialReport = Field(description="AC14 condition report.")


class FrontHalfFirstSmokeReadinessArtifact(BaseModel):
    """Persisted stop/go verdict for the front-half-first smoke gate."""

    benchmark_id: str = Field(description="Structured-spec benchmark identifier under smoke evaluation.")
    trial_report_path: str = Field(description="Paired smoke trial report used for this verdict.")
    verdict: FrontHalfFirstSmokeReadinessVerdict = Field(description="Whether the next branch is full trials or blocker work.")
    rationale: str = Field(description="Short explanation of the smoke verdict.")
    ac14_front_half_success: bool = Field(
        description="Whether AC14 produced an approved front-half artifact in any bounded attempt.",
    )
    runtime_hard_harness_success: bool = Field(
        description="Whether either condition achieved an end-to-end runtime hard-harness pass.",
    )
    infrastructure_failure_detected: bool = Field(
        description="Whether provider or transport instability appeared in any attempt.",
    )
    monolithic_failure_categories: list[FrontHalfFirstFailureCategory] = Field(
        description="Observed failure categories across monolithic attempts.",
    )
    ac14_failure_categories: list[FrontHalfFirstFailureCategory] = Field(
        description="Observed failure categories across AC14 attempts.",
    )
    monolithic_failure_details: list[str] = Field(
        description="Observed attempt-level failure details across monolithic attempts.",
    )
    ac14_failure_details: list[str] = Field(
        description="Observed attempt-level failure details across AC14 attempts.",
    )
    ac14_pre_runtime_proof_failed: bool = Field(
        description=(
            "Whether any AC14 attempt also failed packet tests or recomposition proof "
            "before the runtime-output verdict was finalized."
        ),
    )


class _RuntimeInjectedSourceComponent:
    """Synthetic runtime source used when a generated draft emits a zero-input source node."""

    def __init__(self, *, output_port_name: str, payload: dict[str, Any]) -> None:
        self._output_port_name = output_port_name
        self._payload = copy.deepcopy(payload)

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        if inputs:
            raise ValueError("runtime-injected source component must not receive bound inputs")
        return {self._output_port_name: copy.deepcopy(self._payload)}


def run_front_half_first_smoke_gate(
    benchmark_dir: Path | str,
    output_dir: Path | str,
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    model: str = DEFAULT_LLM_MODEL,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
) -> FrontHalfFirstSmokeReadinessArtifact:
    """Run one bounded front-half-first smoke trial and persist the verdict."""

    structured_bundle = load_structured_spec_benchmark_bundle(benchmark_dir)
    reference_bundle = load_benchmark_bundle(structured_bundle.reference_benchmark_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    report = run_front_half_first_paired_trial(
        structured_bundle=structured_bundle,
        reference_bundle=reference_bundle,
        output_dir=destination / "trial_1",
        trial_id=1,
        model=model,
        max_budget=max_budget,
        max_attempts=max_attempts,
    )
    trial_report_path = destination / "trial_1" / "paired_trial_report.json"
    artifact = build_front_half_first_smoke_readiness_artifact(
        benchmark_id=report.benchmark_id,
        paired_trial_report=report,
        trial_report_path=str(trial_report_path),
    )
    atomic_write_json(destination / "smoke_readiness_report.json", artifact.model_dump(mode="json"))
    return artifact


def run_front_half_first_paired_trial(
    *,
    structured_bundle: StructuredSpecBenchmarkBundle,
    reference_bundle: BenchmarkBundle,
    output_dir: Path | str,
    trial_id: int,
    model: str = DEFAULT_LLM_MODEL,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> FrontHalfFirstPairedTrialReport:
    """Run one bounded paired trial for the front-half-first comparison lane."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    monolithic = _run_condition_trial(
        condition="monolithic",
        structured_bundle=structured_bundle,
        reference_bundle=reference_bundle,
        output_dir=destination / "monolithic",
        trial_id=trial_id,
        model=model,
        max_budget=max_budget,
        max_attempts=max_attempts,
    )
    ac14 = _run_condition_trial(
        condition="ac14",
        structured_bundle=structured_bundle,
        reference_bundle=reference_bundle,
        output_dir=destination / "ac14",
        trial_id=trial_id,
        model=model,
        max_budget=max_budget,
        max_attempts=max_attempts,
    )
    report = FrontHalfFirstPairedTrialReport(
        benchmark_id=structured_bundle.config.benchmark_id,
        trial_id=trial_id,
        monolithic=monolithic,
        ac14=ac14,
    )
    atomic_write_json(destination / "paired_trial_report.json", report.model_dump(mode="json"))
    return report


def build_front_half_first_smoke_readiness_artifact(
    *,
    benchmark_id: str,
    paired_trial_report: FrontHalfFirstPairedTrialReport,
    trial_report_path: str,
) -> FrontHalfFirstSmokeReadinessArtifact:
    """Turn one paired front-half-first smoke trial into a stop/go verdict."""

    monolithic_categories = [
        attempt.failure_classification.category
        for attempt in paired_trial_report.monolithic.attempts
    ]
    monolithic_details = [
        attempt.failure_classification.detail
        for attempt in paired_trial_report.monolithic.attempts
    ]
    ac14_categories = [
        attempt.failure_classification.category
        for attempt in paired_trial_report.ac14.attempts
    ]
    ac14_details = [
        attempt.failure_classification.detail
        for attempt in paired_trial_report.ac14.attempts
    ]
    infrastructure_failure_detected = any(
        _attempt_indicates_infrastructure_provider_failure(
            category=attempt.failure_classification.category,
            generation_error=attempt.generation_error,
        )
        for attempt in [*paired_trial_report.monolithic.attempts, *paired_trial_report.ac14.attempts]
    )
    ac14_front_half_success = any(
        attempt.front_half_passed is True for attempt in paired_trial_report.ac14.attempts
    )
    runtime_hard_harness_success = (
        paired_trial_report.monolithic.passed or paired_trial_report.ac14.passed
    )
    ac14_pre_runtime_proof_failed = any(
        attempt.packet_tests_passed is False or attempt.recomposition_passed is False
        for attempt in paired_trial_report.ac14.attempts
    )
    runtime_output_failure_detected = (
        ac14_front_half_success
        and not infrastructure_failure_detected
        and not runtime_hard_harness_success
        and bool(monolithic_categories)
        and bool(ac14_categories)
        and all(
            category == "runtime_outputs"
            for category in [*monolithic_categories, *ac14_categories]
        )
    )
    if infrastructure_failure_detected:
        verdict: FrontHalfFirstSmokeReadinessVerdict = "blocked_on_infrastructure"
        rationale = (
            "At least one bounded attempt failed because of provider or transport "
            "instability, so the next branch would still mix thesis evidence with "
            "infrastructure noise."
        )
    elif not ac14_front_half_success:
        verdict = "blocked_on_front_half"
        rationale = (
            "AC14 did not produce an approved structured-spec front-half artifact "
            "in the bounded smoke budget, so the front-half-first gate is not ready "
            "for full trials yet."
        )
    elif runtime_hard_harness_success:
        verdict = "ready_for_full_trials"
        rationale = (
            "AC14 earned an approved front-half artifact and at least one condition "
            "achieved an end-to-end runtime hard-harness success without "
            "infrastructure contamination."
        )
    elif runtime_output_failure_detected:
        verdict = "blocked_on_runtime_outputs"
        rationale = (
            "AC14 front-half approval now exists and both conditions reached runtime "
            "evaluation, but no bounded attempt matched the benchmark runtime outputs, "
            "so the next lane should diagnose runtime-output or benchmark fidelity rather "
            "than the old harness bug."
        )
    else:
        verdict = "blocked_on_harness"
        rationale = (
            "AC14 front-half approval now exists, but no condition achieved an "
            "end-to-end runtime hard-harness success inside the bounded smoke "
            "budget, so the next lane should diagnose harness or benchmark issues."
        )
    return FrontHalfFirstSmokeReadinessArtifact(
        benchmark_id=benchmark_id,
        trial_report_path=trial_report_path,
        verdict=verdict,
        rationale=rationale,
        ac14_front_half_success=ac14_front_half_success,
        runtime_hard_harness_success=runtime_hard_harness_success,
        infrastructure_failure_detected=infrastructure_failure_detected,
        monolithic_failure_categories=monolithic_categories,
        ac14_failure_categories=ac14_categories,
        monolithic_failure_details=monolithic_details,
        ac14_failure_details=ac14_details,
        ac14_pre_runtime_proof_failed=ac14_pre_runtime_proof_failed,
    )


def _run_condition_trial(
    *,
    condition: FrontHalfFirstCondition,
    structured_bundle: StructuredSpecBenchmarkBundle,
    reference_bundle: BenchmarkBundle,
    output_dir: Path,
    trial_id: int,
    model: str,
    max_budget: float,
    max_attempts: int,
) -> FrontHalfFirstConditionTrialReport:
    """Run one condition across the allowed bounded attempts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    attempts: list[FrontHalfFirstConditionAttemptReport] = []
    repair_guidance: list[str] = []
    for attempt_id in range(1, max_attempts + 1):
        attempt_dir = output_dir / f"attempt_{attempt_id}"
        if condition == "monolithic":
            attempt = _run_monolithic_attempt(
                structured_bundle=structured_bundle,
                reference_bundle=reference_bundle,
                output_dir=attempt_dir,
                trial_id=trial_id,
                attempt_id=attempt_id,
                model=model,
                max_budget=max_budget,
                repair_guidance=repair_guidance,
            )
        else:
            attempt = _run_ac14_attempt(
                structured_bundle=structured_bundle,
                reference_bundle=reference_bundle,
                output_dir=attempt_dir,
                trial_id=trial_id,
                attempt_id=attempt_id,
                model=model,
                max_budget=max_budget,
            )
        attempts.append(attempt)
        repair_guidance = list(attempt.failure_summary)
        if attempt.passed:
            break

    return FrontHalfFirstConditionTrialReport(
        condition=condition,
        passed=attempts[-1].passed,
        attempts_used=len(attempts),
        repair_loops_used=max(0, len(attempts) - 1),
        attempts=attempts,
    )


def _run_ac14_attempt(
    *,
    structured_bundle: StructuredSpecBenchmarkBundle,
    reference_bundle: BenchmarkBundle,
    output_dir: Path,
    trial_id: int,
    attempt_id: int,
    model: str,
    max_budget: float,
) -> FrontHalfFirstConditionAttemptReport:
    """Run one AC14 front-half-first attempt from structured spec through runtime."""

    output_dir.mkdir(parents=True, exist_ok=True)
    trace_prefix = (
        f"ac14/front_half_first_empirical/{structured_bundle.config.benchmark_id}/ac14/"
        f"trial_{trial_id}/attempt_{attempt_id}"
    )
    start = time.perf_counter()

    front_half_artifact: StructuredSpecFrontHalfAcceptanceArtifact | None = None
    runtime_contract: FrontHalfRuntimeContract | None = None
    packet_report: PacketTestReport | None = None
    recomposition_report: RecompositionReport | None = None
    semantic_review: AcceptanceReviewResponse | None = None
    runtime_cases: list[RuntimeCaseExecution] = []
    generation_error: str | None = None
    runtime_outputs_passed = False
    semantic_review_passed = False

    try:
        structured_spec_source = Path(structured_bundle.benchmark_dir) / structured_bundle.config.structured_spec_path
        build_structured_spec_artifact(
            structured_spec_source,
            output_dir / "structured_spec",
        )
        front_half_artifact = build_structured_spec_front_half_acceptance_report(
            output_dir / "structured_spec" / "structured_spec_artifact.json",
            output_dir / "front_half",
            model=model,
            max_budget=max_budget,
            retry_blocked_freeze=True,
            retry_model=model,
            retry_max_budget=max_budget,
        )

        if front_half_artifact.final_freeze_approved:
            draft_bundle_dir = Path(front_half_artifact.artifact_paths.draft_bundle_dir)
            blueprint = load_blueprint_dir(draft_bundle_dir)
            runtime_contract = infer_runtime_contract_from_structured_spec(
                blueprint=blueprint,
                structured_spec=structured_bundle.structured_spec,
            )
            packet_bundle = compile_packets(blueprint)
            with activate_feature_profile(EMPIRICAL_FEATURE_PROFILE), experiment_run(
                dataset=structured_bundle.config.benchmark_id,
                model=model,
                run_id=trace_prefix.replace("/", "__"),
                condition_id="ac14",
                seed=trial_id,
                replicate=attempt_id,
                scenario_id=f"trial_{trial_id}",
                phase="front_half_first_ac14_attempt",
                feature_profile=EMPIRICAL_FEATURE_PROFILE,
                project="ac14",
                provenance={
                    "benchmark_dir": structured_bundle.benchmark_dir,
                    "reference_benchmark_dir": reference_bundle.benchmark_dir,
                    "trial_id": trial_id,
                    "attempt_id": attempt_id,
                    "condition": "ac14",
                },
            ):
                generated_package = emit_generated_package(
                    packet_bundle,
                    output_dir / "generated",
                    generator_kind="llm",
                    llm_model=model,
                    llm_max_budget=max_budget,
                    trace_id_prefix=trace_prefix,
                )
                packet_report = run_generated_packet_tests(
                    packet_bundle,
                    generated_package,
                    llm_model=model,
                    trace_id=f"{trace_prefix}/packet_eval",
                    llm_max_budget=max_budget,
                )
                recomposition_report = run_generated_recomposition_proof(
                    draft_bundle_dir,
                    generated_package,
                    llm_model=model,
                    trace_id=f"{trace_prefix}/recomp_eval",
                    llm_max_budget=max_budget,
                )
                runtime_cases = _execute_generated_blueprint_runtime_cases(
                    blueprint=blueprint,
                    runtime_contract=runtime_contract,
                    reference_bundle=reference_bundle,
                    generated_package=generated_package,
                )
                runtime_outputs_passed = all(case.matched_expected for case in runtime_cases)
                if runtime_cases:
                    semantic_review = _review_runtime_cases(
                        bundle=reference_bundle,
                        runtime_cases=runtime_cases,
                        model=model,
                        max_budget=max_budget,
                        trace_id=f"{trace_prefix}/semantic_review",
                    )
                    semantic_review_passed = _semantic_review_passed(
                        semantic_review=semantic_review,
                        runtime_outputs_passed=runtime_outputs_passed,
                        policy=reference_bundle.config.semantic_review_policy,
                    )
        else:
            semantic_review_passed = False
    except Exception as exc:  # pragma: no cover - explicit failure capture
        generation_error = str(exc)

    duration_s = time.perf_counter() - start
    llm_cost = _observe_llm_cost(trace_prefix)
    packet_report_path = output_dir / "packet_test_report.json"
    recomposition_report_path = output_dir / "recomposition_report.json"
    if packet_report is not None:
        atomic_write_json(packet_report_path, packet_report.model_dump(mode="json"))
    if recomposition_report is not None:
        atomic_write_json(recomposition_report_path, recomposition_report.model_dump(mode="json"))

    front_half_passed = (
        front_half_artifact.final_freeze_approved
        if front_half_artifact is not None
        else None
    )
    failure_classification = _normalize_front_half_first_failure_classification(
        classification=_classify_front_half_first_failure(
            front_half_passed=front_half_passed,
            generation_error=generation_error,
            runtime_cases=runtime_cases,
            semantic_review=semantic_review,
            semantic_review_passed=semantic_review_passed,
        ),
        generation_error=generation_error,
    )
    failure_summary = _build_ac14_failure_summary(
        front_half_artifact=front_half_artifact,
        generation_error=generation_error,
        runtime_cases=runtime_cases,
        semantic_review=semantic_review,
        packet_report=packet_report,
        recomposition_report=recomposition_report,
        dynamic_output_fields=reference_bundle.config.dynamic_output_fields,
    )
    report = FrontHalfFirstConditionAttemptReport(
        attempt_id=attempt_id,
        artifact_dir=str(output_dir),
        duration_s=duration_s,
        llm_cost=llm_cost,
        front_half_report_path=(
            str(output_dir / "front_half" / "structured_spec_front_half_acceptance_report.json")
            if front_half_artifact is not None
            else None
        ),
        front_half_passed=front_half_passed,
        runtime_contract=runtime_contract,
        packet_tests_passed=packet_report.passed if packet_report is not None else None,
        recomposition_passed=recomposition_report.passed if recomposition_report is not None else None,
        packet_test_report_path=str(packet_report_path) if packet_report is not None else None,
        recomposition_report_path=(
            str(recomposition_report_path) if recomposition_report is not None else None
        ),
        runtime_outputs_passed=runtime_outputs_passed,
        semantic_review=semantic_review,
        semantic_review_passed=semantic_review_passed,
        failure_classification=failure_classification,
        generation_error=generation_error,
        runtime_cases=runtime_cases,
        failure_summary=failure_summary,
        passed=(
            front_half_passed is True
            and generation_error is None
            and runtime_outputs_passed
            and semantic_review_passed
        ),
    )
    atomic_write_json(
        output_dir / "failure_classification.json",
        failure_classification.model_dump(mode="json"),
    )
    atomic_write_json(output_dir / "attempt_report.json", report.model_dump(mode="json"))
    return report


def _run_monolithic_attempt(
    *,
    structured_bundle: StructuredSpecBenchmarkBundle,
    reference_bundle: BenchmarkBundle,
    output_dir: Path,
    trial_id: int,
    attempt_id: int,
    model: str,
    max_budget: float,
    repair_guidance: list[str],
) -> FrontHalfFirstConditionAttemptReport:
    """Run one monolithic front-half-first attempt from structured spec to runtime."""

    output_dir.mkdir(parents=True, exist_ok=True)
    trace_prefix = (
        f"ac14/front_half_first_empirical/{structured_bundle.config.benchmark_id}/monolithic/"
        f"trial_{trial_id}/attempt_{attempt_id}"
    )
    start = time.perf_counter()
    semantic_review: AcceptanceReviewResponse | None = None
    runtime_cases: list[RuntimeCaseExecution] = []
    generation_error: str | None = None
    runtime_outputs_passed = False
    semantic_review_passed = False

    try:
        with activate_feature_profile(EMPIRICAL_FEATURE_PROFILE), experiment_run(
            dataset=structured_bundle.config.benchmark_id,
            model=model,
            run_id=trace_prefix.replace("/", "__"),
            condition_id="monolithic",
            seed=trial_id,
            replicate=attempt_id,
            scenario_id=f"trial_{trial_id}",
            phase="front_half_first_monolithic_attempt",
            feature_profile=EMPIRICAL_FEATURE_PROFILE,
            project="ac14",
            provenance={
                "benchmark_dir": structured_bundle.benchmark_dir,
                "reference_benchmark_dir": reference_bundle.benchmark_dir,
                "trial_id": trial_id,
                "attempt_id": attempt_id,
                "condition": "monolithic",
            },
        ):
            response = generate_monolithic_runtime_system_with_llm(
                structured_bundle=structured_bundle,
                reference_bundle=reference_bundle,
                output_dir=output_dir / "generated",
                model=model,
                trace_id=trace_prefix,
                max_budget=max_budget,
                repair_guidance=repair_guidance,
            )
            system = load_monolithic_runtime_system(output_dir / "generated" / "monolithic_runtime.py")
            runtime_cases = _execute_monolithic_runtime_cases(
                reference_bundle=reference_bundle,
                runtime_system=system,
            )
            runtime_outputs_passed = all(case.matched_expected for case in runtime_cases)
            if runtime_cases:
                semantic_review = _review_runtime_cases(
                    bundle=reference_bundle,
                    runtime_cases=runtime_cases,
                    model=model,
                    max_budget=max_budget,
                    trace_id=f"{trace_prefix}/semantic_review",
                )
                semantic_review_passed = _semantic_review_passed(
                    semantic_review=semantic_review,
                    runtime_outputs_passed=runtime_outputs_passed,
                    policy=reference_bundle.config.semantic_review_policy,
                )
            atomic_write_json(
                output_dir / "monolithic_response.json",
                response.model_dump(mode="json"),
            )
    except Exception as exc:  # pragma: no cover - explicit failure capture
        generation_error = str(exc)

    duration_s = time.perf_counter() - start
    llm_cost = _observe_llm_cost(trace_prefix)
    failure_classification = _normalize_front_half_first_failure_classification(
        classification=_classify_front_half_first_failure(
            front_half_passed=True,
            generation_error=generation_error,
            runtime_cases=runtime_cases,
            semantic_review=semantic_review,
            semantic_review_passed=semantic_review_passed,
        ),
        generation_error=generation_error,
    )
    failure_summary = _build_monolithic_failure_summary(
        generation_error=generation_error,
        runtime_cases=runtime_cases,
        semantic_review=semantic_review,
        dynamic_output_fields=reference_bundle.config.dynamic_output_fields,
    )
    report = FrontHalfFirstConditionAttemptReport(
        attempt_id=attempt_id,
        artifact_dir=str(output_dir),
        duration_s=duration_s,
        llm_cost=llm_cost,
        front_half_report_path=None,
        front_half_passed=None,
        runtime_contract=None,
        packet_tests_passed=None,
        recomposition_passed=None,
        packet_test_report_path=None,
        recomposition_report_path=None,
        runtime_outputs_passed=runtime_outputs_passed,
        semantic_review=semantic_review,
        semantic_review_passed=semantic_review_passed,
        failure_classification=failure_classification,
        generation_error=generation_error,
        runtime_cases=runtime_cases,
        failure_summary=failure_summary,
        passed=generation_error is None and runtime_outputs_passed and semantic_review_passed,
    )
    atomic_write_json(
        output_dir / "failure_classification.json",
        failure_classification.model_dump(mode="json"),
    )
    atomic_write_json(output_dir / "attempt_report.json", report.model_dump(mode="json"))
    return report


def infer_runtime_contract_from_structured_spec(
    *,
    blueprint: FrozenBlueprint,
    structured_spec: StructuredSpecDocument,
) -> FrontHalfRuntimeContract:
    """Infer the runtime execution contract from a generated blueprint and structured spec."""

    structured_inputs = structured_spec.inputs
    input_names = [item.name for item in structured_inputs]
    if len(input_names) != 1:
        raise ValueError("front-half-first runtime contract currently requires exactly one top-level input")
    structured_input = structured_inputs[0]
    bound_input_ports = {
        (binding.to_component, binding.to_port)
        for binding in blueprint.bindings
    }
    unbound_input_candidates = sorted(
        (
            component_id,
            port.name,
            port.schema_id,
            port.required,
        )
        for component_id, component in blueprint.components.items()
        for port in component.input_ports
        if (component_id, port.name) not in bound_input_ports
    )
    exact_name_candidates = [
        candidate
        for candidate in unbound_input_candidates
        if candidate[1] == structured_input.name
    ]
    schema_match_candidates = [
            candidate
            for candidate in unbound_input_candidates
            if _schema_matches_structured_spec_input(
                blueprint=blueprint,
                schema_id=candidate[2],
                structured_input=structured_input,
            )
        ]
    if exact_name_candidates or schema_match_candidates or len(unbound_input_candidates) == 1:
        selected_source = _select_structured_spec_source_candidate(
            structured_input_name=structured_input.name,
            candidate_kind="input port",
            candidates=unbound_input_candidates,
            exact_name_candidates=exact_name_candidates,
            schema_match_candidates=schema_match_candidates,
        )
        source_mode: Literal["input_port", "source_output"] = "input_port"
    else:
        source_output_candidates = sorted(
            (
                component_id,
                port.name,
                port.schema_id,
                False,
            )
            for component_id, component in blueprint.components.items()
            if component.kind == "source" and not component.input_ports
            for port in component.output_ports
        )
        source_output_exact_name_candidates = [
            candidate
            for candidate in source_output_candidates
            if candidate[1] == structured_input.name
        ]
        source_output_schema_match_candidates = [
            candidate
            for candidate in source_output_candidates
            if _schema_matches_structured_spec_input(
                blueprint=blueprint,
                schema_id=candidate[2],
                structured_input=structured_input,
            )
        ]
        selected_source = _select_structured_spec_source_candidate(
            structured_input_name=structured_input.name,
            candidate_kind="source output",
            candidates=source_output_candidates,
            exact_name_candidates=source_output_exact_name_candidates,
            schema_match_candidates=source_output_schema_match_candidates,
        )
        source_mode = "source_output"

    final_output_ports = [item.name for item in structured_spec.outputs]
    final_output_bindings = _infer_final_output_bindings(
        blueprint=blueprint,
        structured_outputs=structured_spec.outputs,
    )
    final_output_components = {
        structured_output_name: binding[0]
        for structured_output_name, binding in final_output_bindings.items()
    }
    final_output_emitted_ports = {
        structured_output_name: binding[1]
        for structured_output_name, binding in final_output_bindings.items()
    }
    unique_final_components = sorted(set(final_output_components.values()))
    final_component_id = unique_final_components[0] if len(unique_final_components) == 1 else None
    _assert_no_extra_required_unbound_inputs(
        unbound_input_candidates=unbound_input_candidates,
        selected_source=selected_source,
        source_mode=source_mode,
    )

    return FrontHalfRuntimeContract(
        source_component_id=selected_source[0],
        source_port_name=selected_source[1],
        source_mode=source_mode,
        final_component_id=final_component_id,
        final_output_ports=final_output_ports,
        final_output_components=final_output_components,
        final_output_emitted_ports=final_output_emitted_ports,
    )


def _select_structured_spec_source_candidate(
    *,
    structured_input_name: str,
    candidate_kind: str,
    candidates: list[tuple[str, str, str, bool]],
    exact_name_candidates: list[tuple[str, str, str, bool]],
    schema_match_candidates: list[tuple[str, str, str, bool]],
) -> tuple[str, str, str, bool]:
    """Select one source input port for the runtime contract or fail loud."""

    if len(exact_name_candidates) == 1:
        return exact_name_candidates[0]
    if len(exact_name_candidates) > 1:
        raise ValueError(
            "unable to infer one unique source component from structured spec input "
            f"{structured_input_name!r}: multiple exact-name {candidate_kind} candidates "
            f"{_format_runtime_source_candidates(exact_name_candidates)}",
        )
    if len(schema_match_candidates) == 1:
        return schema_match_candidates[0]
    if len(schema_match_candidates) > 1:
        raise ValueError(
            "unable to infer one unique source component from structured spec input "
            f"{structured_input_name!r}: multiple schema-matched {candidate_kind} candidates "
            f"{_format_runtime_source_candidates(schema_match_candidates)}",
        )
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError(
        "unable to infer one unique source component from structured spec input "
        f"{structured_input_name!r}: exact-name candidates "
        f"{_format_runtime_source_candidates(exact_name_candidates)}, schema-matched "
        f"candidates {_format_runtime_source_candidates(schema_match_candidates)}, "
        f"all {candidate_kind} candidates {_format_runtime_source_candidates(candidates)}",
    )


def _format_runtime_source_candidates(
    candidates: Sequence[tuple[str, str, str] | tuple[str, str, str, bool]],
) -> list[str]:
    """Render bounded runtime-source candidates for failure messages."""

    return [
        f"{component_id}.{port_name}:{schema_id}"
        for component_id, port_name, schema_id, *_rest in candidates
    ]


def _assert_no_extra_required_unbound_inputs(
    *,
    unbound_input_candidates: list[tuple[str, str, str, bool]],
    selected_source: tuple[str, str, str, bool],
    source_mode: Literal["input_port", "source_output"],
) -> None:
    """Fail loud when the blueprint still has extra required unbound inputs."""

    if source_mode != "input_port":
        extra_required = [
            candidate
            for candidate in unbound_input_candidates
            if candidate[3]
        ]
    else:
        extra_required = [
            candidate
            for candidate in unbound_input_candidates
            if candidate[3] and candidate[:3] != selected_source[:3]
        ]
    if extra_required:
        raise ValueError(
            "runtime contract inference found extra required unbound inputs beyond the top-level "
            f"structured-spec source: {_format_runtime_source_candidates(extra_required)}",
        )


def _schema_matches_structured_spec_interface(
    *,
    blueprint: FrozenBlueprint,
    schema_id: str,
    structured_interface: StructuredSpecInterface,
) -> bool:
    """Return whether one blueprint schema matches one structured-spec interface shape."""

    schema = blueprint.schemas.get(schema_id)
    if schema is None:
        return False
    if structured_interface.kind != "record" or schema.kind != "object":
        return False
    blueprint_fields = {
        field.name: _normalize_runtime_contract_type(field.type, blueprint=blueprint)
        for field in schema.fields
    }
    structured_fields = {
        field.field_name: _normalize_runtime_contract_type(field.field_type, blueprint=blueprint)
        for field in structured_interface.fields
    }
    return blueprint_fields == structured_fields


def _schema_matches_structured_spec_input(
    *,
    blueprint: FrozenBlueprint,
    schema_id: str,
    structured_input: StructuredSpecInterface,
) -> bool:
    """Return whether one blueprint schema matches the top-level structured input shape."""

    return _schema_matches_structured_spec_interface(
        blueprint=blueprint,
        schema_id=schema_id,
        structured_interface=structured_input,
    )


def _normalize_runtime_contract_type(
    type_label: str,
    *,
    blueprint: FrozenBlueprint | None = None,
) -> str:
    """Normalize compact and canonical field types into one comparison label."""

    normalized = type_label.strip()
    lower = normalized.lower()
    if lower.startswith("list[") and lower.endswith("]"):
        inner = normalized[5:-1].strip()
        return f"list[{_normalize_runtime_contract_type(inner, blueprint=blueprint)}]"
    aliases = {
        "str": "string",
        "string": "string",
        "int": "integer",
        "integer": "integer",
        "float": "number",
        "number": "number",
        "bool": "boolean",
        "boolean": "boolean",
        "record": "object",
        "dict": "object",
        "object": "object",
    }
    if blueprint is not None:
        referenced_schema = blueprint.schemas.get(normalized)
        if referenced_schema is not None and referenced_schema.kind == "object":
            return "object"
    return aliases.get(lower, normalized)


def _infer_final_output_bindings(
    *,
    blueprint: FrozenBlueprint,
    structured_outputs: list[StructuredSpecInterface],
) -> dict[str, tuple[str, str]]:
    """Infer which generated output satisfies each structured-spec final output."""

    inferred: dict[str, tuple[str, str]] = {}
    bound_to_sink_candidates = _collect_bound_sink_output_candidates(blueprint)
    non_source_candidates = _collect_non_source_output_candidates(blueprint)
    for structured_output in structured_outputs:
        candidates = sorted(
            (
                component_id,
                port.name,
                port.schema_id,
            )
            for component_id, component in blueprint.components.items()
            for port in component.output_ports
        )
        sink_exact_name_candidates = [
            candidate
            for candidate in bound_to_sink_candidates
            if candidate[1] == structured_output.name
        ]
        sink_schema_name_candidates = [
            candidate
            for candidate in bound_to_sink_candidates
            if _normalize_runtime_contract_identifier(candidate[2])
            == _normalize_runtime_contract_identifier(structured_output.name)
        ]
        sink_schema_match_candidates = [
            candidate
            for candidate in bound_to_sink_candidates
            if _schema_matches_structured_spec_interface(
                blueprint=blueprint,
                schema_id=candidate[2],
                structured_interface=structured_output,
            )
        ]
        exact_name_candidates = [
            candidate
            for candidate in candidates
            if candidate[1] == structured_output.name
        ]
        non_source_exact_name_candidates = [
            candidate
            for candidate in non_source_candidates
            if candidate[1] == structured_output.name
        ]
        schema_name_candidates = [
            candidate
            for candidate in candidates
            if _normalize_runtime_contract_identifier(candidate[2])
            == _normalize_runtime_contract_identifier(structured_output.name)
        ]
        non_source_schema_name_candidates = [
            candidate
            for candidate in non_source_candidates
            if _normalize_runtime_contract_identifier(candidate[2])
            == _normalize_runtime_contract_identifier(structured_output.name)
        ]
        schema_match_candidates = [
            candidate
            for candidate in candidates
            if _schema_matches_structured_spec_interface(
                blueprint=blueprint,
                schema_id=candidate[2],
                structured_interface=structured_output,
            )
        ]
        non_source_schema_match_candidates = [
            candidate
            for candidate in non_source_candidates
            if _schema_matches_structured_spec_interface(
                blueprint=blueprint,
                schema_id=candidate[2],
                structured_interface=structured_output,
            )
        ]
        component_id, emitted_port_name, _schema_id = _select_structured_spec_output_candidate(
            structured_output_name=structured_output.name,
            candidates=candidates,
            sink_exact_name_candidates=sink_exact_name_candidates,
            sink_schema_name_candidates=sink_schema_name_candidates,
            sink_schema_match_candidates=sink_schema_match_candidates,
            exact_name_candidates=exact_name_candidates,
            non_source_exact_name_candidates=non_source_exact_name_candidates,
            schema_name_candidates=schema_name_candidates,
            non_source_schema_name_candidates=non_source_schema_name_candidates,
            schema_match_candidates=schema_match_candidates,
            non_source_schema_match_candidates=non_source_schema_match_candidates,
        )
        inferred[structured_output.name] = (component_id, emitted_port_name)
    return inferred


def _collect_non_source_output_candidates(
    blueprint: FrozenBlueprint,
) -> list[tuple[str, str, str]]:
    """Return output candidates that do not come from zero-input source components."""

    return sorted(
        (
            component_id,
            port.name,
            port.schema_id,
        )
        for component_id, component in blueprint.components.items()
        if component.kind != "source"
        for port in component.output_ports
    )


def _collect_bound_sink_output_candidates(
    blueprint: FrozenBlueprint,
) -> list[tuple[str, str, str]]:
    """Return output candidates that feed a sink component input."""

    sink_component_ids = {
        component_id
        for component_id, component in blueprint.components.items()
        if component.kind == "sink"
    }
    return sorted(
        (
            binding.from_component,
            binding.from_port,
            next(
                port.schema_id
                for port in blueprint.components[binding.from_component].output_ports
                if port.name == binding.from_port
            ),
        )
        for binding in blueprint.bindings
        if binding.to_component in sink_component_ids
    )


def _select_structured_spec_output_candidate(
    *,
    structured_output_name: str,
    candidates: list[tuple[str, str, str]],
    sink_exact_name_candidates: list[tuple[str, str, str]],
    sink_schema_name_candidates: list[tuple[str, str, str]],
    sink_schema_match_candidates: list[tuple[str, str, str]],
    exact_name_candidates: list[tuple[str, str, str]],
    non_source_exact_name_candidates: list[tuple[str, str, str]],
    schema_name_candidates: list[tuple[str, str, str]],
    non_source_schema_name_candidates: list[tuple[str, str, str]],
    schema_match_candidates: list[tuple[str, str, str]],
    non_source_schema_match_candidates: list[tuple[str, str, str]],
) -> tuple[str, str, str]:
    """Select one generated output candidate for one structured-spec final output or fail loud."""

    if len(sink_exact_name_candidates) == 1:
        return sink_exact_name_candidates[0]
    if len(sink_exact_name_candidates) > 1:
        raise ValueError(
            "unable to infer one unique final component from structured spec output "
            f"{structured_output_name!r}: multiple sink-forward exact-name candidates "
            f"{_format_output_candidates(sink_exact_name_candidates)}",
        )
    if len(non_source_exact_name_candidates) == 1:
        return non_source_exact_name_candidates[0]
    if len(non_source_exact_name_candidates) > 1:
        raise ValueError(
            "unable to infer one unique final component from structured spec output "
            f"{structured_output_name!r}: multiple non-source exact-name candidates "
            f"{_format_output_candidates(non_source_exact_name_candidates)}",
        )
    if len(exact_name_candidates) == 1:
        return exact_name_candidates[0]
    if len(exact_name_candidates) > 1:
        raise ValueError(
            "unable to infer one unique final component from structured spec output "
            f"{structured_output_name!r}: multiple exact-name candidates "
            f"{_format_runtime_source_candidates(exact_name_candidates)}",
        )
    if len(sink_schema_name_candidates) == 1:
        return sink_schema_name_candidates[0]
    if len(sink_schema_name_candidates) > 1:
        raise ValueError(
            "unable to infer one unique final component from structured spec output "
            f"{structured_output_name!r}: multiple sink-forward schema-name candidates "
            f"{_format_output_candidates(sink_schema_name_candidates)}",
        )
    if len(non_source_schema_name_candidates) == 1:
        return non_source_schema_name_candidates[0]
    if len(non_source_schema_name_candidates) > 1:
        raise ValueError(
            "unable to infer one unique final component from structured spec output "
            f"{structured_output_name!r}: multiple non-source schema-name candidates "
            f"{_format_output_candidates(non_source_schema_name_candidates)}",
        )
    if len(schema_name_candidates) == 1:
        return schema_name_candidates[0]
    if len(schema_name_candidates) > 1:
        raise ValueError(
            "unable to infer one unique final component from structured spec output "
            f"{structured_output_name!r}: multiple schema-name candidates "
            f"{_format_runtime_source_candidates(schema_name_candidates)}",
        )
    if len(sink_schema_match_candidates) == 1:
        return sink_schema_match_candidates[0]
    if len(sink_schema_match_candidates) > 1:
        raise ValueError(
            "unable to infer one unique final component from structured spec output "
            f"{structured_output_name!r}: multiple sink-forward schema-matched candidates "
            f"{_format_output_candidates(sink_schema_match_candidates)}",
        )
    if len(non_source_schema_match_candidates) == 1:
        return non_source_schema_match_candidates[0]
    if len(non_source_schema_match_candidates) > 1:
        raise ValueError(
            "unable to infer one unique final component from structured spec output "
            f"{structured_output_name!r}: multiple non-source schema-matched candidates "
            f"{_format_output_candidates(non_source_schema_match_candidates)}",
        )
    if len(schema_match_candidates) == 1:
        return schema_match_candidates[0]
    if len(schema_match_candidates) > 1:
        raise ValueError(
            "unable to infer one unique final component from structured spec output "
            f"{structured_output_name!r}: multiple schema-matched candidates "
            f"{_format_runtime_source_candidates(schema_match_candidates)}",
        )
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError(
        "unable to infer one unique final component from structured spec output "
        f"{structured_output_name!r}: exact-name candidates "
        f"{_format_runtime_source_candidates(exact_name_candidates)}, schema-name candidates "
        f"{_format_runtime_source_candidates(schema_name_candidates)}, schema-matched candidates "
        f"{_format_runtime_source_candidates(schema_match_candidates)}, all output candidates "
        f"{_format_runtime_source_candidates(candidates)}",
    )


def _format_output_candidates(
    candidates: list[tuple[str, str, str]],
) -> list[str]:
    """Render output candidates for failure messages."""

    return [f"{component_id}.{port_name}:{schema_id}" for component_id, port_name, schema_id in candidates]


def _normalize_runtime_contract_identifier(identifier: str) -> str:
    """Normalize one identifier for case-insensitive schema/name comparisons."""

    return "".join(character for character in identifier.lower() if character.isalnum())


def generate_monolithic_runtime_system_with_llm(
    *,
    structured_bundle: StructuredSpecBenchmarkBundle,
    reference_bundle: BenchmarkBundle,
    output_dir: Path | str,
    model: str,
    trace_id: str,
    max_budget: float,
    repair_guidance: list[str],
) -> MonolithicRuntimeSystemResponse:
    """Generate one whole-task monolithic runtime system and persist its module."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    response = asyncio.run(
        agenerate_monolithic_runtime_system_with_llm(
            structured_bundle=structured_bundle,
            reference_bundle=reference_bundle,
            model=model,
            trace_id=trace_id,
            max_budget=max_budget,
            repair_guidance=repair_guidance,
        ),
    )
    atomic_write_json(destination / "monolithic_response.json", response.model_dump(mode="json"))
    source_port_name = _structured_spec_source_port_name(structured_bundle)
    try:
        _validate_monolithic_runtime_module(
            response.module_code,
            source_port_name=source_port_name,
        )
    except Exception as exc:
        failed_path = _persist_failed_monolithic_runtime_artifacts(
            destination=destination,
            module_code=response.module_code,
            error=exc,
        )
        raise ValueError(
            f"{exc}; failed module source persisted at {failed_path}",
        ) from exc
    module_path = destination / "monolithic_runtime.py"
    atomic_write_text(module_path, response.module_code)
    return response


async def agenerate_monolithic_runtime_system_with_llm(
    *,
    structured_bundle: StructuredSpecBenchmarkBundle,
    reference_bundle: BenchmarkBundle,
    model: str,
    trace_id: str,
    max_budget: float,
    repair_guidance: list[str],
) -> MonolithicRuntimeSystemResponse:
    """Generate a direct whole-task runtime system from raw structured-spec inputs."""

    fixture_path = os.environ.get("AC14_FRONT_HALF_FIRST_MONOLITHIC_FIXTURE")
    if fixture_path:
        return MonolithicRuntimeSystemResponse.model_validate_json(Path(fixture_path).read_text())

    messages = cast(
        list[Any],
        render_prompt(
            FRONT_HALF_FIRST_MONOLITHIC_PROMPT_PATH,
            benchmark=structured_bundle.config.model_dump(mode="json"),
            requirements_text=structured_bundle.requirements_text,
            structured_spec=structured_bundle.structured_spec.model_dump(mode="json"),
            source_port_name=_structured_spec_source_port_name(structured_bundle),
            sample_runtime_record=(
                reference_bundle.runtime_cases[0] if reference_bundle.runtime_cases else None
            ),
            allowed_dependencies=reference_bundle.config.allowed_dependencies,
            final_output_ports=reference_bundle.config.final_output_ports,
            repair_guidance=repair_guidance,
        ),
    )
    response, _meta = cast(
        tuple[MonolithicRuntimeSystemResponse, object],
        await acall_llm_structured(
            model,
            messages,
            response_model=MonolithicRuntimeSystemResponse,
            task="ac14_generate_monolithic_runtime_system_from_structured_spec",
            trace_id=trace_id,
            max_budget=max_budget,
        ),
    )
    return response


def load_monolithic_runtime_system(module_path: Path | str) -> RuntimeSystem:
    """Import and instantiate one persisted monolithic runtime system module."""

    path = Path(module_path)
    module = _load_module("front_half_first_monolithic", path)
    build_system = getattr(module, "build_system", None)
    if not callable(build_system):
        raise ValueError("monolithic runtime module must define callable build_system()")
    system = build_system()
    if not hasattr(system, "run_case") or not callable(system.run_case):
        raise ValueError("build_system() must return an object with callable run_case(record)")
    return cast(RuntimeSystem, system)


def _load_module(name: str, module_path: Path) -> ModuleType:
    """Import one runtime module from disk."""

    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load runtime module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_monolithic_runtime_module(
    module_code: str,
    *,
    source_port_name: str | None = None,
) -> None:
    """Fail loud when a monolithic runtime module misses the required contract."""

    tree = ast.parse(module_code)
    build_system_defined = any(
        isinstance(node, ast.FunctionDef) and node.name == "build_system"
        for node in tree.body
    )
    if not build_system_defined:
        raise ValueError("monolithic runtime module must define build_system()")
    if source_port_name is not None and _uses_nested_source_port_access(
        tree,
        source_port_name=source_port_name,
    ):
        raise ValueError(
            "monolithic runtime module must treat run_case(record) as the raw benchmark "
            f"record directly; do not read record[{source_port_name!r}] or "
            f"record.get({source_port_name!r})",
        )


def _structured_spec_source_port_name(structured_bundle: StructuredSpecBenchmarkBundle) -> str:
    """Return the one top-level structured-spec input name for front-half-first trials."""

    input_names = [item.name for item in structured_bundle.structured_spec.inputs]
    if len(input_names) != 1:
        raise ValueError("front-half-first monolithic runtime contract requires exactly one top-level input")
    return input_names[0]


def _uses_nested_source_port_access(tree: ast.AST, *, source_port_name: str) -> bool:
    """Return whether the generated runtime expects the raw record to be nested."""

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "record"
            and _extract_string_literal(node.slice) == source_port_name
        ):
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "record"
            and node.args
            and _extract_string_literal(node.args[0]) == source_port_name
        ):
            return True
        if (
            isinstance(node, ast.Compare)
            and len(node.ops) == 1
            and isinstance(node.ops[0], (ast.In, ast.NotIn))
            and len(node.comparators) == 1
            and isinstance(node.comparators[0], ast.Name)
            and node.comparators[0].id == "record"
            and _extract_string_literal(node.left) == source_port_name
        ):
            return True
    return False


def _extract_string_literal(node: ast.AST) -> str | None:
    """Return one literal string value when an AST node is statically known."""

    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _persist_failed_monolithic_runtime_artifacts(
    *,
    destination: Path,
    module_code: str,
    error: Exception,
) -> Path:
    """Persist invalid monolithic runtime module source and validation metadata."""

    failed_path = destination / "monolithic_runtime.failed.py"
    atomic_write_text(failed_path, module_code)
    atomic_write_json(
        destination / "monolithic_runtime.validation_error.json",
        {
            "error": str(error),
            "failed_module_path": str(failed_path),
            "persisted_failed_module_source": True,
        },
    )
    return failed_path


def _execute_generated_blueprint_runtime_cases(
    *,
    blueprint: FrozenBlueprint,
    runtime_contract: FrontHalfRuntimeContract,
    reference_bundle: BenchmarkBundle,
    generated_package: GeneratedPackage,
) -> list[RuntimeCaseExecution]:
    """Execute reference runtime cases against one generated AC14 blueprint."""

    builders = load_generated_component_builders(generated_package)
    base_implementations = {
        component_id: builders[component_id]()
        for component_id in blueprint.components
    }
    expected_by_case = {
        case.case_id: case.expected_outputs
        for case in reference_bundle.expected_runtime_cases
    }
    results: list[RuntimeCaseExecution] = []
    for record in reference_bundle.runtime_cases:
        case_id = cast(str, record["case_id"])
        expected_outputs = expected_by_case[case_id]
        try:
            implementations, initial_inputs = _prepare_generated_runtime_execution(
                base_implementations=base_implementations,
                runtime_contract=runtime_contract,
                record=record,
            )
            outputs_by_component = run_blueprint_once(
                blueprint,
                implementations,
                initial_inputs,
            )
            selected_outputs = {
                port_name: outputs_by_component[runtime_contract.final_output_components[port_name]][
                    runtime_contract.final_output_emitted_ports[port_name]
                ]
                for port_name in runtime_contract.final_output_ports
            }
            results.append(
                _build_runtime_case_result(
                    case_id=case_id,
                    actual_outputs=selected_outputs,
                    expected_outputs=expected_outputs,
                    dynamic_output_fields=reference_bundle.config.dynamic_output_fields,
                ),
            )
        except Exception as exc:  # pragma: no cover - explicit failure capture
            results.append(
                RuntimeCaseExecution(
                    case_id=case_id,
                    matched_expected=False,
                    expected_outputs=expected_outputs,
                    error=str(exc),
                ),
            )
    return results


def _prepare_generated_runtime_execution(
    *,
    base_implementations: dict[str, RuntimeComponent],
    runtime_contract: FrontHalfRuntimeContract,
    record: dict[str, Any],
) -> tuple[dict[str, RuntimeComponent], dict[str, dict[str, dict[str, Any]]]]:
    """Prepare one bounded runtime execution from the inferred source contract."""

    implementations = dict(base_implementations)
    payload = copy.deepcopy(record)
    if runtime_contract.source_mode == "source_output":
        implementations[runtime_contract.source_component_id] = _RuntimeInjectedSourceComponent(
            output_port_name=runtime_contract.source_port_name,
            payload=payload,
        )
        return implementations, {}
    return implementations, {
        runtime_contract.source_component_id: {
            runtime_contract.source_port_name: payload,
        },
    }


def _execute_monolithic_runtime_cases(
    *,
    reference_bundle: BenchmarkBundle,
    runtime_system: RuntimeSystem,
) -> list[RuntimeCaseExecution]:
    """Execute reference runtime cases against one whole-task monolithic system."""

    expected_by_case = {
        case.case_id: case.expected_outputs
        for case in reference_bundle.expected_runtime_cases
    }
    results: list[RuntimeCaseExecution] = []
    for record in reference_bundle.runtime_cases:
        case_id = cast(str, record["case_id"])
        expected_outputs = expected_by_case[case_id]
        try:
            actual_outputs = runtime_system.run_case(record)
            results.append(
                _build_runtime_case_result(
                    case_id=case_id,
                    actual_outputs=actual_outputs,
                    expected_outputs=expected_outputs,
                    dynamic_output_fields=reference_bundle.config.dynamic_output_fields,
                ),
            )
        except KeyError as exc:
            # Detect the nested source-port contract mistake: run_case(record) tried to
            # access record[port_name] instead of using the raw record dict directly.
            missing_key = str(exc)
            error = (
                f"Monolithic runtime contract error: run_case(record) accessed "
                f"record[{missing_key}] but that key is not in the benchmark record. "
                "Ensure run_case(record) consumes the raw case dict directly — "
                "do not wrap record in a source-port key before accessing it."
            )
            results.append(
                RuntimeCaseExecution(
                    case_id=case_id,
                    matched_expected=False,
                    expected_outputs=expected_outputs,
                    error=error,
                ),
            )
        except Exception as exc:  # pragma: no cover - explicit failure capture
            results.append(
                RuntimeCaseExecution(
                    case_id=case_id,
                    matched_expected=False,
                    expected_outputs=expected_outputs,
                    error=str(exc),
                ),
            )
    return results


def _build_runtime_case_result(
    *,
    case_id: str,
    actual_outputs: dict[str, dict[str, Any]],
    expected_outputs: dict[str, dict[str, Any]],
    dynamic_output_fields: list[str],
) -> RuntimeCaseExecution:
    """Build one runtime-case result with dynamic-field-aware comparison."""

    frozen_outputs = copy.deepcopy(actual_outputs)
    compare_actual = _strip_dynamic_field_paths(frozen_outputs, dynamic_output_fields)
    compare_expected = _strip_dynamic_field_paths(expected_outputs, dynamic_output_fields)
    missing_dynamic = [
        field_name
        for field_name in dynamic_output_fields
        if not _dynamic_field_exists(frozen_outputs, field_name)
    ]
    matched = compare_actual == compare_expected and not missing_dynamic
    return RuntimeCaseExecution(
        case_id=case_id,
        matched_expected=matched,
        actual_outputs=frozen_outputs,
        expected_outputs=expected_outputs,
    )


def _classify_front_half_first_failure(
    *,
    front_half_passed: bool | None,
    generation_error: str | None,
    runtime_cases: list[RuntimeCaseExecution],
    semantic_review: AcceptanceReviewResponse | None,
    semantic_review_passed: bool,
) -> FrontHalfFirstFailureClassification:
    """Classify one bounded front-half-first attempt into a stable failure domain."""

    if generation_error is not None:
        if _is_infrastructure_provider_error(generation_error):
            return FrontHalfFirstFailureClassification(
                category="infrastructure_provider",
                detail=generation_error,
            )
        return FrontHalfFirstFailureClassification(category="generation", detail=generation_error)
    if front_half_passed is False:
        return FrontHalfFirstFailureClassification(
            category="front_half",
            detail="AC14 did not produce an approved front-half artifact",
        )
    failing_runtime_cases = [case for case in runtime_cases if not case.matched_expected]
    if failing_runtime_cases:
        details = [
            case.error or f"{case.case_id} outputs mismatched expected outputs"
            for case in failing_runtime_cases
        ]
        return FrontHalfFirstFailureClassification(
            category="runtime_outputs",
            detail="; ".join(details),
        )
    if semantic_review is not None and not semantic_review_passed:
        concerns = "; ".join(semantic_review.concerns) or semantic_review.overall_verdict
        return FrontHalfFirstFailureClassification(category="semantic_review", detail=concerns)
    return FrontHalfFirstFailureClassification(
        category="success",
        detail="attempt passed the front-half-first harness",
    )


def _normalize_front_half_first_failure_classification(
    *,
    classification: FrontHalfFirstFailureClassification,
    generation_error: str | None,
) -> FrontHalfFirstFailureClassification:
    """Guarantee that detectable provider noise persists as infrastructure failure."""

    if _attempt_indicates_infrastructure_provider_failure(
        category=classification.category,
        generation_error=generation_error,
    ):
        return FrontHalfFirstFailureClassification(
            category="infrastructure_provider",
            detail=generation_error or classification.detail,
        )
    return classification


def _build_ac14_failure_summary(
    *,
    front_half_artifact: StructuredSpecFrontHalfAcceptanceArtifact | None,
    generation_error: str | None,
    runtime_cases: list[RuntimeCaseExecution],
    semantic_review: AcceptanceReviewResponse | None,
    packet_report: PacketTestReport | None,
    recomposition_report: RecompositionReport | None,
    dynamic_output_fields: list[str],
) -> list[str]:
    """Summarize one AC14 front-half-first attempt into bounded repair guidance."""

    if front_half_artifact is not None and not front_half_artifact.final_freeze_approved:
        summary = [
            "structured-spec front-half did not end in approved freeze",
            *[f"front-half review concern: {concern}" for concern in front_half_artifact.review.concerns],
            *[
                f"freeze blocker code: {code}"
                for code in front_half_artifact.blocking_finding_codes
            ],
        ]
        return summary or ["structured-spec front-half remained blocked"]
    return _build_failure_summary(
        generation_error=generation_error,
        packet_tests_passed=packet_report.passed if packet_report is not None else True,
        recomposition_passed=recomposition_report.passed if recomposition_report is not None else True,
        runtime_cases=runtime_cases,
        semantic_review=semantic_review,
        packet_report=packet_report,
        recomposition_report=recomposition_report,
        dynamic_output_fields=dynamic_output_fields,
    )


def _build_monolithic_failure_summary(
    *,
    generation_error: str | None,
    runtime_cases: list[RuntimeCaseExecution],
    semantic_review: AcceptanceReviewResponse | None,
    dynamic_output_fields: list[str],
) -> list[str]:
    """Summarize one monolithic front-half-first attempt into bounded repair guidance."""

    return _build_failure_summary(
        generation_error=generation_error,
        packet_tests_passed=True,
        recomposition_passed=True,
        runtime_cases=runtime_cases,
        semantic_review=semantic_review,
        dynamic_output_fields=dynamic_output_fields,
    )

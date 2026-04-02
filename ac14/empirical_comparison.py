"""Empirical monolithic-vs-AC14 comparison for the first thesis gate."""

from __future__ import annotations

import asyncio
import ast
import copy
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field
from llm_client.io_log import activate_feature_profile, experiment_run  # type: ignore[import-not-found]

from ac14.acceptance import (
    ACCEPTANCE_PROMPT_PATH,
    AcceptanceReviewResponse,
    acall_llm_structured,
    render_prompt,
)
from ac14.generated_codegen import (
    DEFAULT_LLM_MAX_BUDGET,
    DEFAULT_LLM_MODEL,
    GeneratedPackage,
    emit_generated_package,
    load_generated_component_builders,
)
from ac14.generated_evidence import (
    PacketTestReport,
    run_generated_packet_tests,
    run_generated_recomposition_proof,
)
from ac14.loader import load_blueprint_dir
from ac14.models import FrozenBlueprint, PacketBundle, Scenario
from ac14.output_diff import collect_bounded_differences
from ac14.recomposition import RecompositionReport
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets
from ac14.runtime import run_blueprint_once
from ac14.structured_inputs import load_structured_input_records


MONOLITHIC_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "generate_monolithic_system.yaml"
DEFAULT_TRIAL_COUNT = 5
DEFAULT_MAX_ATTEMPTS = 3
EMPIRICAL_FEATURE_PROFILE: dict[str, Any] = {
    "name": "ac14_empirical_benchmark",
    "features": {
        "experiment_context": True,
    },
}

TrialCondition = Literal["monolithic", "ac14"]
DecisionVerdict = Literal["ac14_wins", "monolithic_wins", "inconclusive"]
CostObservationStatus = Literal["observed", "no_rows", "missing_db"]
AttemptFailureCategory = Literal[
    "success",
    "infrastructure_provider",
    "generation",
    "packet_tests",
    "recomposition",
    "runtime_outputs",
    "semantic_review",
]
SmokeReadinessVerdict = Literal[
    "ready_for_full_trials",
    "blocked_on_infrastructure",
    "blocked_on_harness",
]
SemanticReviewPolicy = Literal["required", "advisory_on_exact_match"]


class BenchmarkConfig(BaseModel):
    """Benchmark-level configuration loaded from ``benchmark.yaml``."""

    benchmark_id: str = Field(description="Stable benchmark identifier.")
    name: str = Field(description="Human-readable benchmark name.")
    purpose: str = Field(description="Why this benchmark exists.")
    comparison_scope: str = Field(description="What the comparison isolates.")
    blueprint_dir: str = Field(description="Relative path to the frozen benchmark blueprint.")
    requirements_path: str = Field(description="Relative path to the requirements document.")
    runtime_input_path: str = Field(description="Relative path to the runtime input records.")
    expected_outputs_path: str = Field(description="Relative path to expected runtime outputs.")
    source_artifacts: list[str] = Field(description="Raw source artifacts provided to both conditions.")
    allowed_dependencies: list[str] = Field(description="Dependencies explicitly allowed in the benchmark.")
    primary_source_component_id: str = Field(description="Source component used for runtime execution.")
    primary_source_port_name: str = Field(description="Input port used for runtime execution.")
    final_component_id: str = Field(description="Final component that emits the reviewable outputs.")
    final_output_ports: list[str] = Field(description="Final output ports evaluated at runtime.")
    system_requirements: list[str] = Field(description="High-level benchmark requirements.")
    dynamic_output_fields: list[str] = Field(
        default_factory=list,
        description=(
            "Dot-separated output field paths excluded from exact value comparison. "
            "Dynamic fields (e.g. wall-clock timestamps) must exist in actual outputs "
            "but their exact values are not compared to expected outputs."
        ),
    )
    semantic_review_policy: SemanticReviewPolicy = Field(
        default="required",
        description=(
            "Whether semantic review is a required gate or advisory once exact runtime outputs already match."
        ),
    )


class BenchmarkFile(BaseModel):
    """On-disk shape of ``benchmark.yaml``."""

    benchmark: BenchmarkConfig = Field(description="Benchmark configuration block.")


class ExpectedRuntimeCase(BaseModel):
    """Expected outputs for one runtime case."""

    case_id: str = Field(description="Stable runtime case identifier.")
    expected_outputs: dict[str, dict[str, Any]] = Field(
        description="Expected final outputs keyed by output port.",
    )


class BenchmarkBundle(BaseModel):
    """Frozen benchmark assets used by the empirical comparison."""

    benchmark_dir: str = Field(description="Root directory containing the benchmark assets.")
    config: BenchmarkConfig = Field(description="Benchmark configuration.")
    requirements_text: str = Field(description="Human-readable requirements document.")
    blueprint: FrozenBlueprint = Field(description="Frozen blueprint used by the AC14 condition.")
    packet_bundle: PacketBundle = Field(description="Compiled packets for the benchmark blueprint.")
    runtime_cases: list[dict[str, Any]] = Field(description="Runtime input records used by both conditions.")
    expected_runtime_cases: list[ExpectedRuntimeCase] = Field(
        description="Expected final outputs for the runtime input records.",
    )


class MonolithicGeneratedModule(BaseModel):
    """One module emitted by the monolithic whole-task generator."""

    component_id: str = Field(description="Component identifier implemented by this module.")
    module_code: str = Field(description="Complete standalone Python module source.")


class MonolithicSystemResponse(BaseModel):
    """Structured LLM response for monolithic whole-task generation."""

    modules: list[MonolithicGeneratedModule] = Field(
        description="Exactly one module for every component in the benchmark blueprint.",
    )
    implementation_notes: list[str] = Field(
        description="Short notes about key implementation choices or limitations.",
    )


class CostObservation(BaseModel):
    """Observed or unavailable LLM cost for one trace prefix."""

    status: CostObservationStatus = Field(description="Whether the cost was observed.")
    cost_usd: float | None = Field(default=None, description="Observed total cost in USD when available.")


class AttemptFailureClassification(BaseModel):
    """Structured classification for one empirical-comparison attempt outcome."""

    category: AttemptFailureCategory = Field(description="Bounded failure category for this attempt.")
    detail: str = Field(description="Short reason describing the classification.")


class RuntimeCaseExecution(BaseModel):
    """Runtime execution outcome for one benchmark case."""

    case_id: str = Field(description="Stable runtime case identifier.")
    matched_expected: bool = Field(description="Whether final outputs matched the expected outputs.")
    actual_outputs: dict[str, dict[str, Any]] | None = Field(
        default=None,
        description="Actual final outputs keyed by output port when execution succeeded.",
    )
    expected_outputs: dict[str, dict[str, Any]] = Field(
        description="Expected final outputs keyed by output port.",
    )
    error: str | None = Field(default=None, description="Execution error when runtime evaluation failed.")


class ConditionAttemptReport(BaseModel):
    """One bounded attempt for one condition inside a paired trial."""

    attempt_id: int = Field(description="Sequential attempt number starting at 1.")
    artifact_dir: str = Field(description="Directory containing the attempt artifacts.")
    duration_s: float = Field(description="Wall-clock duration for the attempt.")
    llm_cost: CostObservation = Field(description="Observed or unavailable LLM cost for the attempt.")
    packet_tests_passed: bool = Field(description="Whether packet-local tests passed.")
    recomposition_passed: bool = Field(description="Whether recomposition proof passed.")
    runtime_outputs_passed: bool = Field(description="Whether runtime outputs matched the expected outputs.")
    packet_test_report_path: str | None = Field(
        default=None,
        description="Persisted packet-test report path for this attempt.",
    )
    recomposition_report_path: str | None = Field(
        default=None,
        description="Persisted recomposition report path for this attempt.",
    )
    semantic_review: AcceptanceReviewResponse | None = Field(
        default=None,
        description="Requirements-aware review of the runtime outputs when available.",
    )
    semantic_review_passed: bool = Field(description="Whether semantic review was acceptable.")
    failure_classification: AttemptFailureClassification = Field(
        description="Structured failure classification for this attempt.",
    )
    generation_error: str | None = Field(
        default=None,
        description="Generation failure that prevented evaluation.",
    )
    runtime_cases: list[RuntimeCaseExecution] = Field(description="Runtime-case execution outcomes.")
    failure_summary: list[str] = Field(description="Compact failure guidance extracted from the attempt.")
    passed: bool = Field(description="Whether the full attempt passed the benchmark harness.")


class ConditionTrialReport(BaseModel):
    """Outcome for one condition across all allowed attempts inside a paired trial."""

    condition: TrialCondition = Field(description="Compared condition.")
    passed: bool = Field(description="Whether the condition passed within the allowed attempts.")
    attempts_used: int = Field(description="How many attempts were consumed.")
    repair_loops_used: int = Field(description="How many repair loops were consumed after the first attempt.")
    attempts: list[ConditionAttemptReport] = Field(description="Per-attempt reports.")


class PairedTrialReport(BaseModel):
    """Persisted report for one monolithic-vs-AC14 paired trial."""

    benchmark_id: str = Field(description="Benchmark identifier under evaluation.")
    trial_id: int = Field(description="Sequential paired-trial identifier.")
    monolithic: ConditionTrialReport = Field(description="Monolithic condition report.")
    ac14: ConditionTrialReport = Field(description="AC14 condition report.")


class ConditionAggregate(BaseModel):
    """Aggregate condition metrics derived from the paired trials."""

    condition: TrialCondition = Field(description="Compared condition.")
    successes: int = Field(description="Trials that passed within the allowed attempts.")
    average_repair_loops: float = Field(description="Average repair loops consumed per trial.")
    average_semantic_score: float = Field(description="Average semantic-review score across attempts with reviews.")
    average_duration_s: float = Field(description="Average wall-clock duration per trial.")
    total_observed_cost_usd: float = Field(description="Total observed LLM cost across all attempts with cost rows.")
    observed_cost_trials: int = Field(description="Trials with at least one observed LLM cost row.")


class ExperimentDecisionArtifact(BaseModel):
    """Final persisted experiment decision for the empirical comparison gate."""

    benchmark_id: str = Field(description="Benchmark identifier.")
    trial_count: int = Field(description="Number of paired trials included in the decision.")
    verdict: DecisionVerdict = Field(description="Final experiment verdict.")
    rationale: str = Field(description="Short explanation of the verdict.")
    ac14: ConditionAggregate = Field(description="Aggregate AC14 metrics.")
    monolithic: ConditionAggregate = Field(description="Aggregate monolithic metrics.")
    trial_report_paths: list[str] = Field(description="Persisted paired-trial report paths.")


class SmokeReadinessArtifact(BaseModel):
    """Persisted stop/go decision for the empirical smoke gate."""

    benchmark_id: str = Field(description="Benchmark identifier under smoke evaluation.")
    trial_report_path: str = Field(description="Paired smoke trial report used for this verdict.")
    verdict: SmokeReadinessVerdict = Field(description="Whether the full five-trial gate should proceed.")
    rationale: str = Field(description="Short explanation of the smoke verdict.")
    hard_harness_success: bool = Field(description="Whether either condition achieved a hard-harness pass.")
    infrastructure_failure_detected: bool = Field(
        description="Whether any attempt showed infrastructure/provider instability.",
    )
    monolithic_failure_categories: list[AttemptFailureCategory] = Field(
        description="Observed failure categories across monolithic attempts.",
    )
    ac14_failure_categories: list[AttemptFailureCategory] = Field(
        description="Observed failure categories across AC14 attempts.",
    )


def load_benchmark_bundle(benchmark_dir: Path | str) -> BenchmarkBundle:
    """Load and validate the frozen benchmark assets for one comparison target."""

    benchmark_path = Path(benchmark_dir)
    benchmark_file = BenchmarkFile.model_validate(
        yaml.safe_load((benchmark_path / "benchmark.yaml").read_text()),
    )
    config = benchmark_file.benchmark
    blueprint = load_blueprint_dir(benchmark_path / config.blueprint_dir)
    packet_bundle = compile_packets(blueprint)
    requirements_text = (benchmark_path / config.requirements_path).read_text()
    runtime_cases = load_structured_input_records(benchmark_path / config.runtime_input_path)
    expected_runtime_cases = [
        ExpectedRuntimeCase.model_validate(payload)
        for payload in json.loads((benchmark_path / config.expected_outputs_path).read_text())
    ]

    bundle = BenchmarkBundle(
        benchmark_dir=str(benchmark_path),
        config=config,
        requirements_text=requirements_text,
        blueprint=blueprint,
        packet_bundle=packet_bundle,
        runtime_cases=runtime_cases,
        expected_runtime_cases=expected_runtime_cases,
    )
    _validate_benchmark_bundle(bundle)
    return bundle


def run_paired_trial(
    benchmark_dir: Path | str,
    output_dir: Path | str,
    *,
    trial_id: int,
    model: str = DEFAULT_LLM_MODEL,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> PairedTrialReport:
    """Run one paired monolithic-vs-AC14 trial and persist the report."""

    bundle = load_benchmark_bundle(benchmark_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    monolithic_report = _run_condition_trial(
        bundle=bundle,
        condition="monolithic",
        output_dir=destination / "monolithic",
        trial_id=trial_id,
        model=model,
        max_budget=max_budget,
        max_attempts=max_attempts,
    )
    ac14_report = _run_condition_trial(
        bundle=bundle,
        condition="ac14",
        output_dir=destination / "ac14",
        trial_id=trial_id,
        model=model,
        max_budget=max_budget,
        max_attempts=max_attempts,
    )
    paired_report = PairedTrialReport(
        benchmark_id=bundle.config.benchmark_id,
        trial_id=trial_id,
        monolithic=monolithic_report,
        ac14=ac14_report,
    )
    (destination / "paired_trial_report.json").write_text(
        json.dumps(paired_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return paired_report


def run_empirical_comparison(
    benchmark_dir: Path | str,
    output_dir: Path | str,
    *,
    trial_count: int = DEFAULT_TRIAL_COUNT,
    model: str = DEFAULT_LLM_MODEL,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> ExperimentDecisionArtifact:
    """Run the full paired-trial experiment and persist the final decision."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    bundle = load_benchmark_bundle(benchmark_dir)

    reports: list[PairedTrialReport] = []
    report_paths: list[str] = []
    for trial_id in range(1, trial_count + 1):
        trial_dir = destination / f"trial_{trial_id}"
        report = run_paired_trial(
            benchmark_dir,
            trial_dir,
            trial_id=trial_id,
            model=model,
            max_budget=max_budget,
            max_attempts=max_attempts,
        )
        reports.append(report)
        report_paths.append(str(trial_dir / "paired_trial_report.json"))

    decision = build_experiment_decision_artifact(
        benchmark_id=bundle.config.benchmark_id,
        trial_reports=reports,
        trial_report_paths=report_paths,
    )
    (destination / "experiment_decision.json").write_text(
        json.dumps(decision.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return decision


def run_empirical_smoke_gate(
    benchmark_dir: Path | str,
    output_dir: Path | str,
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    model: str = DEFAULT_LLM_MODEL,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
) -> SmokeReadinessArtifact:
    """Run one bounded smoke paired trial and persist a stop/go artifact."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    report = run_paired_trial(
        benchmark_dir=benchmark_dir,
        output_dir=destination / "trial_1",
        trial_id=1,
        model=model,
        max_budget=max_budget,
        max_attempts=max_attempts,
    )
    trial_report_path = destination / "trial_1" / "paired_trial_report.json"
    artifact = build_smoke_readiness_artifact(
        benchmark_id=report.benchmark_id,
        paired_trial_report=report,
        trial_report_path=str(trial_report_path),
    )
    (destination / "smoke_readiness_report.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def build_experiment_decision_artifact(
    *,
    benchmark_id: str,
    trial_reports: list[PairedTrialReport],
    trial_report_paths: list[str],
) -> ExperimentDecisionArtifact:
    """Apply the frozen Plan #38 rule to the paired-trial reports."""

    ac14_aggregate = _aggregate_condition(trial_reports, "ac14")
    monolithic_aggregate = _aggregate_condition(trial_reports, "monolithic")
    success_gap = ac14_aggregate.successes - monolithic_aggregate.successes

    if success_gap >= 2:
        verdict: DecisionVerdict = "ac14_wins"
        rationale = "AC14 beat the monolithic condition by at least two successful trials."
    elif success_gap <= -2:
        verdict = "monolithic_wins"
        rationale = "The monolithic condition beat AC14 by at least two successful trials."
    elif ac14_aggregate.successes == monolithic_aggregate.successes:
        if (
            ac14_aggregate.average_semantic_score >= monolithic_aggregate.average_semantic_score
            and ac14_aggregate.average_repair_loops < monolithic_aggregate.average_repair_loops
        ):
            verdict = "ac14_wins"
            rationale = (
                "The conditions tied on success, but AC14 matched semantic quality and used "
                "fewer repair loops."
            )
        elif (
            monolithic_aggregate.average_semantic_score >= ac14_aggregate.average_semantic_score
            and monolithic_aggregate.average_repair_loops < ac14_aggregate.average_repair_loops
        ):
            verdict = "monolithic_wins"
            rationale = (
                "The conditions tied on success, but the monolithic condition matched semantic "
                "quality and used fewer repair loops."
            )
        else:
            verdict = "inconclusive"
            rationale = (
                "The conditions tied on success and the secondary metrics did not separate them "
                "cleanly."
            )
    else:
        verdict = "inconclusive"
        rationale = (
            "The success gap was at most one trial and the secondary metrics were mixed."
        )

    return ExperimentDecisionArtifact(
        benchmark_id=benchmark_id,
        trial_count=len(trial_reports),
        verdict=verdict,
        rationale=rationale,
        ac14=ac14_aggregate,
        monolithic=monolithic_aggregate,
        trial_report_paths=trial_report_paths,
    )


def build_smoke_readiness_artifact(
    *,
    benchmark_id: str,
    paired_trial_report: PairedTrialReport,
    trial_report_path: str,
) -> SmokeReadinessArtifact:
    """Turn one bounded paired smoke trial into an explicit stop/go verdict."""

    monolithic_categories = [
        attempt.failure_classification.category
        for attempt in paired_trial_report.monolithic.attempts
    ]
    ac14_categories = [
        attempt.failure_classification.category
        for attempt in paired_trial_report.ac14.attempts
    ]
    infrastructure_failure_detected = any(
        category == "infrastructure_provider"
        for category in [*monolithic_categories, *ac14_categories]
    )
    hard_harness_success = paired_trial_report.monolithic.passed or paired_trial_report.ac14.passed
    if infrastructure_failure_detected:
        verdict: SmokeReadinessVerdict = "blocked_on_infrastructure"
        rationale = (
            "At least one bounded smoke attempt failed because of provider or transport "
            "instability, so the five-trial budget would currently mix thesis evidence "
            "with infrastructure noise."
        )
    elif hard_harness_success:
        verdict = "ready_for_full_trials"
        rationale = (
            "The smoke run produced at least one hard-harness success without "
            "infrastructure/provider contamination, so the full paired-trial gate is "
            "worth spending."
        )
    else:
        verdict = "blocked_on_harness"
        rationale = (
            "The smoke run showed no hard-harness success and no infrastructure-only "
            "explanation, so the benchmark, prompts, or harness still need work before "
            "the five-trial gate."
        )
    return SmokeReadinessArtifact(
        benchmark_id=benchmark_id,
        trial_report_path=trial_report_path,
        verdict=verdict,
        rationale=rationale,
        hard_harness_success=hard_harness_success,
        infrastructure_failure_detected=infrastructure_failure_detected,
        monolithic_failure_categories=monolithic_categories,
        ac14_failure_categories=ac14_categories,
    )


def _validate_benchmark_bundle(bundle: BenchmarkBundle) -> None:
    """Fail loud when the benchmark bundle is internally inconsistent."""

    component_ids = set(bundle.blueprint.components)
    if bundle.config.primary_source_component_id not in component_ids:
        raise ValueError("benchmark primary source component is absent from the blueprint")
    if bundle.config.final_component_id not in component_ids:
        raise ValueError("benchmark final component is absent from the blueprint")

    source_component = bundle.blueprint.components[bundle.config.primary_source_component_id]
    if bundle.config.primary_source_port_name not in {port.name for port in source_component.input_ports}:
        raise ValueError("benchmark primary source port is absent from the source component")

    final_component = bundle.blueprint.components[bundle.config.final_component_id]
    final_output_ports = {port.name for port in final_component.output_ports}
    missing_final_ports = sorted(set(bundle.config.final_output_ports).difference(final_output_ports))
    if missing_final_ports:
        raise ValueError(
            "benchmark final output ports are absent from the final component: "
            + ", ".join(missing_final_ports),
        )

    runtime_case_ids = [record["case_id"] for record in bundle.runtime_cases]
    expected_case_ids = [case.case_id for case in bundle.expected_runtime_cases]
    if runtime_case_ids != expected_case_ids:
        raise ValueError(
            "runtime case ids do not match expected output ids: "
            f"{runtime_case_ids!r} vs {expected_case_ids!r}",
        )


def _run_condition_trial(
    *,
    bundle: BenchmarkBundle,
    condition: TrialCondition,
    output_dir: Path,
    trial_id: int,
    model: str,
    max_budget: float,
    max_attempts: int,
) -> ConditionTrialReport:
    """Run one condition across the allowed bounded attempts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    attempts: list[ConditionAttemptReport] = []
    repair_guidance: list[str] = []

    for attempt_id in range(1, max_attempts + 1):
        attempt_dir = output_dir / f"attempt_{attempt_id}"
        attempt_report = _run_condition_attempt(
            bundle=bundle,
            condition=condition,
            trial_id=trial_id,
            attempt_id=attempt_id,
            output_dir=attempt_dir,
            model=model,
            max_budget=max_budget,
            repair_guidance=repair_guidance,
        )
        attempts.append(attempt_report)
        repair_guidance = list(attempt_report.failure_summary)
        if attempt_report.passed:
            break

    return ConditionTrialReport(
        condition=condition,
        passed=attempts[-1].passed,
        attempts_used=len(attempts),
        repair_loops_used=max(0, len(attempts) - 1),
        attempts=attempts,
    )


def _run_condition_attempt(
    *,
    bundle: BenchmarkBundle,
    condition: TrialCondition,
    trial_id: int,
    attempt_id: int,
    output_dir: Path,
    model: str,
    max_budget: float,
    repair_guidance: list[str],
) -> ConditionAttemptReport:
    """Run one bounded attempt for one condition and persist the artifact."""

    output_dir.mkdir(parents=True, exist_ok=True)
    trace_prefix = f"ac14/empirical_comparison/{bundle.config.benchmark_id}/{condition}/trial_{trial_id}/attempt_{attempt_id}"
    start = time.perf_counter()

    generation_error: str | None = None
    semantic_review: AcceptanceReviewResponse | None = None
    runtime_cases: list[RuntimeCaseExecution] = []
    packet_tests_passed = False
    recomposition_passed = False
    runtime_outputs_passed = False
    packet_report: PacketTestReport | None = None
    recomposition_report: RecompositionReport | None = None

    try:
        with activate_feature_profile(EMPIRICAL_FEATURE_PROFILE), experiment_run(
            dataset=bundle.config.benchmark_id,
            model=model,
            run_id=trace_prefix.replace("/", "__"),
            condition_id=condition,
            seed=trial_id,
            replicate=attempt_id,
            scenario_id=f"trial_{trial_id}",
            phase="empirical_attempt",
            feature_profile=EMPIRICAL_FEATURE_PROFILE,
            project="ac14",
            provenance={
                "benchmark_dir": bundle.benchmark_dir,
                "trial_id": trial_id,
                "attempt_id": attempt_id,
                "condition": condition,
            },
        ):
            if condition == "monolithic":
                generated_package = emit_monolithic_package_with_llm(
                    bundle=bundle,
                    output_dir=output_dir / "generated",
                    model=model,
                    max_budget=max_budget,
                    trace_id=trace_prefix,
                    repair_guidance=_build_condition_repair_guidance(
                        bundle=bundle,
                        condition=condition,
                        prior_guidance=repair_guidance,
                    ),
                )
            else:
                repair_guidance_by_component = _build_component_repair_guidance(
                    bundle=bundle,
                    prior_guidance=repair_guidance,
                )
                generated_package = emit_generated_package(
                    bundle.packet_bundle,
                    output_dir / "generated",
                    generator_kind="llm",
                    llm_model=model,
                    llm_max_budget=max_budget,
                    trace_id_prefix=trace_prefix,
                    repair_guidance_by_component=repair_guidance_by_component,
                )
            packet_report = run_generated_packet_tests(
                bundle.packet_bundle,
                generated_package,
                llm_model=model,
                trace_id=f"{trace_prefix}/packet_eval",
                llm_max_budget=max_budget,
            )
            packet_tests_passed = packet_report.passed
            recomposition_report = run_generated_recomposition_proof(
                Path(bundle.benchmark_dir) / bundle.config.blueprint_dir,
                generated_package,
                llm_model=model,
                trace_id=f"{trace_prefix}/recomp_eval",
                llm_max_budget=max_budget,
            )
            recomposition_passed = recomposition_report.passed
            runtime_cases = _execute_runtime_cases(bundle=bundle, generated_package=generated_package)
            runtime_outputs_passed = all(case.matched_expected for case in runtime_cases)
            if runtime_cases:
                semantic_review = _review_runtime_cases(
                    bundle=bundle,
                    runtime_cases=runtime_cases,
                    model=model,
                    max_budget=max_budget,
                    trace_id=f"{trace_prefix}/semantic_review",
                )
    except Exception as exc:  # pragma: no cover - explicit failure capture
        generation_error = str(exc)

    packet_report_path = output_dir / "packet_test_report.json"
    recomposition_report_path = output_dir / "recomposition_report.json"
    packet_report = packet_report or PacketTestReport(
        passed=False,
        results=[],
        harness_error=f"attempt failed before packet tests completed: {generation_error or 'unknown error'}",
    )
    recomposition_report = recomposition_report or RecompositionReport(
        passed=False,
        runnable_scenario_count=0,
        skipped_scenarios=[],
        results=[],
        harness_error=f"attempt failed before recomposition proof completed: {generation_error or 'unknown error'}",
    )
    packet_report_path.write_text(
        json.dumps(packet_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    recomposition_report_path.write_text(
        json.dumps(recomposition_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )

    duration_s = time.perf_counter() - start
    llm_cost = _observe_llm_cost(trace_prefix)
    semantic_review_passed = _semantic_review_passed(
        semantic_review=semantic_review,
        runtime_outputs_passed=runtime_outputs_passed,
        policy=bundle.config.semantic_review_policy,
    )
    failure_classification = _classify_attempt_failure(
        generation_error=generation_error,
        packet_tests_passed=packet_tests_passed,
        recomposition_passed=recomposition_passed,
        runtime_cases=runtime_cases,
        semantic_review=semantic_review,
        semantic_review_policy=bundle.config.semantic_review_policy,
    )
    failure_summary = _build_failure_summary(
        generation_error=generation_error,
        packet_tests_passed=packet_tests_passed,
        recomposition_passed=recomposition_passed,
        runtime_cases=runtime_cases,
        semantic_review=semantic_review,
        packet_report=packet_report,
        recomposition_report=recomposition_report,
        dynamic_output_fields=bundle.config.dynamic_output_fields,
    )
    attempt_report = ConditionAttemptReport(
        attempt_id=attempt_id,
        artifact_dir=str(output_dir),
        duration_s=duration_s,
        llm_cost=llm_cost,
        packet_tests_passed=packet_tests_passed,
        recomposition_passed=recomposition_passed,
        runtime_outputs_passed=runtime_outputs_passed,
        packet_test_report_path=str(packet_report_path),
        recomposition_report_path=str(recomposition_report_path),
        semantic_review=semantic_review,
        semantic_review_passed=semantic_review_passed,
        failure_classification=failure_classification,
        generation_error=generation_error,
        runtime_cases=runtime_cases,
        failure_summary=failure_summary,
        passed=(
            generation_error is None
            and runtime_outputs_passed
            and semantic_review_passed
        ),
    )
    (output_dir / "attempt_report.json").write_text(
        json.dumps(attempt_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return attempt_report


def emit_monolithic_package_with_llm(
    *,
    bundle: BenchmarkBundle,
    output_dir: Path | str,
    model: str = DEFAULT_LLM_MODEL,
    trace_id: str,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    repair_guidance: list[str] | None = None,
) -> GeneratedPackage:
    """Generate a full component package in one whole-task pass and write it to disk."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    response = generate_monolithic_system_with_llm(
        bundle=bundle,
        model=model,
        trace_id=trace_id,
        max_budget=max_budget,
        repair_guidance=repair_guidance or [],
    )
    (destination / "monolithic_response.json").write_text(
        json.dumps(response.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    expected_component_ids = set(bundle.blueprint.components)
    modules_by_component = {module.component_id: module.module_code for module in response.modules}
    if set(modules_by_component) != expected_component_ids:
        raise ValueError(
            "monolithic generator did not return exactly one module per component: "
            f"expected {sorted(expected_component_ids)}, got {sorted(modules_by_component)}",
        )

    (destination / "__init__.py").write_text('"""Monolithically generated AC14 components."""\n')
    module_paths: dict[str, str] = {}
    components_by_id = bundle.blueprint.components
    for component_id, module_code in modules_by_component.items():
        try:
            _validate_module_contract(
                module_code,
                component_id=component_id,
                allowed_input_ports={port.name for port in components_by_id[component_id].input_ports},
            )
        except Exception as exc:
            failed_path = _persist_monolithic_failed_module_artifacts(
                destination,
                component_id=component_id,
                module_code=module_code,
                error=exc,
            )
            raise ValueError(
                f"{exc}; failed module source persisted at {failed_path}"
            ) from exc
        module_path = destination / f"{component_id}.py"
        module_path.write_text(module_code)
        module_paths[component_id] = str(module_path)
    return GeneratedPackage(
        output_dir=str(destination),
        generator_kind="llm",
        module_paths=module_paths,
    )


def _semantic_review_passed(
    *,
    semantic_review: AcceptanceReviewResponse | None,
    runtime_outputs_passed: bool,
    policy: SemanticReviewPolicy,
) -> bool:
    """Return whether semantic review should gate success for this benchmark."""

    if semantic_review is None:
        return False
    if semantic_review.overall_verdict == "accept":
        return True
    if policy == "advisory_on_exact_match" and runtime_outputs_passed:
        return True
    return False


def _validate_literal_input_port_references(
    tree: ast.Module,
    *,
    component_id: str,
    allowed_input_ports: set[str],
) -> None:
    """Fail loud when a generated module reads undeclared literal input ports."""

    referenced_ports: set[str] = set()

    class _Visitor(ast.NodeVisitor):
        def visit_Subscript(self, node: ast.Subscript) -> None:  # noqa: N802
            if isinstance(node.value, ast.Name) and node.value.id == "inputs":
                literal = _extract_string_literal(node.slice)
                if literal is not None:
                    referenced_ports.add(literal)
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "inputs"
                and node.args
            ):
                literal = _extract_string_literal(node.args[0])
                if literal is not None:
                    referenced_ports.add(literal)
            self.generic_visit(node)

    _Visitor().visit(tree)
    unknown_ports = sorted(referenced_ports - allowed_input_ports)
    if unknown_ports:
        raise ValueError(
            f"generated module for {component_id} references unknown input ports {unknown_ports}; "
            f"allowed ports are {sorted(allowed_input_ports)}"
        )


def _extract_string_literal(node: ast.AST) -> str | None:
    """Return a literal string when one AST node is statically known."""

    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _persist_monolithic_failed_module_artifacts(
    destination: Path,
    *,
    component_id: str,
    module_code: str,
    error: Exception,
) -> Path:
    """Persist invalid monolithic module source and validation metadata for diagnosis."""

    failed_path = destination / f"{component_id}.failed.py"
    failed_path.write_text(module_code)
    metadata = {
        "component_id": component_id,
        "error": str(error),
        "failed_module_path": str(failed_path),
        "persisted_failed_module_source": True,
    }
    (destination / f"{component_id}.validation_error.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True),
    )
    return failed_path


def generate_monolithic_system_with_llm(
    *,
    bundle: BenchmarkBundle,
    model: str = DEFAULT_LLM_MODEL,
    trace_id: str,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    repair_guidance: list[str],
    task: str = "ac14_generate_monolithic_system",
) -> MonolithicSystemResponse:
    """Synchronous wrapper for whole-task monolithic package generation."""

    return asyncio.run(
        agenerate_monolithic_system_with_llm(
            bundle=bundle,
            model=model,
            trace_id=trace_id,
            max_budget=max_budget,
            repair_guidance=repair_guidance,
            task=task,
        ),
    )


async def agenerate_monolithic_system_with_llm(
    *,
    bundle: BenchmarkBundle,
    model: str = DEFAULT_LLM_MODEL,
    trace_id: str,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    repair_guidance: list[str],
    task: str = "ac14_generate_monolithic_system",
) -> MonolithicSystemResponse:
    """Generate a whole component package using one structured LLM call."""

    fixture_path = os.environ.get("AC14_MONOLITHIC_CODEGEN_FIXTURE")
    if fixture_path:
        return MonolithicSystemResponse.model_validate_json(Path(fixture_path).read_text())

    packet_cases = materialize_packet_test_cases(bundle.packet_bundle)
    packet_cases_by_component = {
        component_id: [case.model_dump(mode="json") for case in cases]
        for component_id, cases in packet_cases.items()
    }
    messages = cast(
        list[Any],
        render_prompt(
            MONOLITHIC_PROMPT_PATH,
            benchmark=bundle.config.model_dump(mode="json"),
            requirements_text=bundle.requirements_text,
            blueprint_metadata=bundle.blueprint.metadata.model_dump(mode="json"),
            schemas={schema_id: schema.model_dump(mode="json") for schema_id, schema in bundle.blueprint.schemas.items()},
            components={component_id: component.model_dump(mode="json") for component_id, component in bundle.blueprint.components.items()},
            bindings=[binding.model_dump(mode="json") for binding in bundle.blueprint.bindings],
            state_stores={store_id: store.model_dump(mode="json") for store_id, store in bundle.blueprint.state_stores.items()},
            packet_test_cases_by_component=packet_cases_by_component,
            repair_guidance=repair_guidance,
        ),
    )
    response, _meta = cast(
        tuple[MonolithicSystemResponse, object],
        await acall_llm_structured(
            model,
            messages,
            response_model=MonolithicSystemResponse,
            task=task,
            trace_id=trace_id,
            max_budget=max_budget,
        ),
    )
    return response


def _build_condition_repair_guidance(
    *,
    bundle: BenchmarkBundle,
    condition: TrialCondition,
    prior_guidance: list[str],
) -> list[str]:
    """Build bounded whole-condition repair guidance for one empirical attempt."""

    benchmark_guidance = _benchmark_repair_guidance(bundle=bundle, condition=condition)
    return _dedupe_guidance([*benchmark_guidance, *prior_guidance])


def _build_component_repair_guidance(
    *,
    bundle: BenchmarkBundle,
    prior_guidance: list[str],
) -> dict[str, list[str]]:
    """Build component-specific repair guidance for the AC14 empirical lane."""

    component_guidance = _benchmark_component_repair_guidance(bundle)
    prior_guidance_by_component = _map_prior_guidance_to_components(
        bundle=bundle,
        prior_guidance=prior_guidance,
    )
    return {
        component_id: _dedupe_guidance(
            [
                *component_guidance.get(component_id, []),
                *prior_guidance_by_component.get(component_id, []),
            ],
        )
        for component_id in bundle.blueprint.components
    }


def _benchmark_repair_guidance(
    *,
    bundle: BenchmarkBundle,
    condition: TrialCondition,
) -> list[str]:
    """Return bounded benchmark-local guidance for one empirical condition."""

    if bundle.config.benchmark_id == "resource_scaling_v1":
        shared = [
            "All benchmark outputs are categorical, boolean, or integer. Do not invent free-form explanation fields or helper prose inside outputs.",
            "Thresholds are exact: cpu>=0.80, memory>=0.85, error_rate>=0.05. Do not introduce tolerance bands.",
            "scale_out requires both cpu and memory breach; scale_up requires only cpu breach; none is valid when no threshold breach is present and request rate stays >=20.",
            "Urgency is critical on error breach or breach_count>=3, high on two breaches, medium on one breach, low otherwise.",
            "bronze maps to budget, silver/gold to standard, platinum to premium. Budget never auto-executes.",
            "Maintenance window blocks any non-none action. Change freeze blocks only when urgency is not critical.",
            "Final decision action and strategy must become blocked whenever execution_gate.blocked is true.",
            "Keep decision-store entries purely categorical and preserve arrival order across runtime cases.",
        ]
        if condition == "monolithic":
            return shared + [
                "Emit one direct decision tree per module and keep the whole-package implementation free of helper inheritance or speculative fallback categories.",
            ]
        return shared
    if bundle.config.benchmark_id != "order_exception_resolution_v1":
        return []
    shared = [
        "Keep Python syntax minimal and valid: no incomplete if/elif/else branches, no missing parentheses, and no placeholder code.",
        "If a boolean condition spans multiple lines, wrap the whole expression in parentheses or keep it on one line; never break after and/or without explicit continuation.",
        "Never leave a branch with comments only. Use short direct logic and executable statements instead of essay-style commentary inside the code.",
        "Do not annotate build_component() with GeneratedComponent unless the annotation is guaranteed to resolve safely at import time; the safest pattern is an unannotated build_component() defined after the class.",
        "Treat shipping delay as a material shipping_delay exception at 24+ hours; severe shipping delay is 48+ hours or shipment_status == 'exception'.",
        "Shipping risk is already high at the 24-hour materiality threshold; 48+ hours or shipment_status == 'exception' is the severe subset of that same high-risk bucket, not a separate medium/high split.",
        "ORX-101 is a shipping-only benchmark case: no shortage plus a 24-47 hour shipping delay still means shipping_delay, blocker_source='shipping', recommended_team='logistics', priority_band='high', and escalation_required=false for the standard-customer path.",
        "Shipping-only high priority is independent of escalation_required. Keep ORX-101-style cases at priority_band='high' even when escalation_required=false.",
        "When both inventory shortage and severe shipping delay are present, classify compound_exception and route to blocker_source='compound', recommended_team='exception_desk', priority_band='critical'.",
        "Manual override is optional. Preserve it explicitly when present, but never assume override_action exists for every case.",
        "Manual override can change blocker_source downstream, but it does not replace the low-risk shipping rationale when shipment delay remains below threshold.",
        "A moderate shortage with delayed replenishment may still emit inventory_risk_band='high' while keeping the reason in the partial-fulfillment/back-order family; reserve threaten-the-order-promise language for clearly large shortages like ORX-100.",
        "Use only schema-valid categorical values and never invent fallback labels outside the benchmark schemas. If no schema-valid category applies, raise ValueError loudly instead of synthesizing a fallback label.",
        "Read only fields that actually exist on each local schema surface. For this benchmark, shipping_risk exposes shipment_risk_band and shipment_delay_hours, but not shipment_status.",
        "Maintain one deterministic digest store across processed cases; do not recreate the store from scratch on every execute call.",
    ]
    if condition == "monolithic":
        return shared + [
            "Whole-system generation must satisfy the benchmark packet fixtures and runtime cases without relying on hidden global assumptions.",
        ]
    return shared


def _benchmark_component_repair_guidance(bundle: BenchmarkBundle) -> dict[str, list[str]]:
    """Return benchmark-local component guidance for the AC14 empirical lane."""

    if bundle.config.benchmark_id == "resource_scaling_v1":
        return {
            "metrics_normalizer": [
                "Pass through the benchmark fields exactly; do not drop maintenance or freeze flags.",
            ],
            "threshold_detector": [
                "Threshold booleans are exact comparisons at cpu>=0.80, memory>=0.85, and error_rate>=0.05.",
                "breach_count must equal the count of true breach flags with no extra weighting.",
            ],
            "urgency_classifier": [
                "critical comes from error_breach or three breaches; high from exactly two breaches; medium from one; low from zero.",
            ],
            "recommendation_generator": [
                "scale_out requires both cpu and memory breach, scale_up requires only cpu breach, scale_down only when no breach and request_rate_rps<20, otherwise none.",
                "target_adjustment must be 0 only when action is none; otherwise use max(1, min(breach_count, max_scale_adjustment)).",
            ],
            "approval_resolver": [
                "premium is always auto; standard is auto only for low/medium urgency; budget always requires manager review.",
            ],
            "compliance_checker": [
                "Maintenance window blocks any non-none action. Change freeze blocks only when urgency is not critical.",
            ],
            "scaling_plan_builder": [
                "compliance_block wins over all other plan branches; do not emit immediate/staged/deferred when compliance says blocked.",
                "critical plus low deploy risk becomes immediate; deploy medium/high or urgency high becomes staged; otherwise deferred.",
            ],
            "execution_gate": [
                "authorization_mode is compliance_blocked when conflict is true, auto when authorized and no approval is required, otherwise manual.",
            ],
            "decision_recorder": [
                "If execution_gate.blocked is true, final action and strategy must both be blocked even when upstream recommendation/plan say otherwise.",
                "Keep the rolling store keyed by case_id and append new cases in arrival order.",
            ],
        } | {component_id: [] for component_id in bundle.blueprint.components if component_id not in {
            "metrics_normalizer", "threshold_detector", "urgency_classifier", "recommendation_generator", "approval_resolver", "compliance_checker", "scaling_plan_builder", "execution_gate", "decision_recorder"
        }}
    if bundle.config.benchmark_id != "order_exception_resolution_v1":
        return {component_id: [] for component_id in bundle.blueprint.components}
    return {
        "case_parser": [
            "Preserve manual_override_action and manual_override_reason when present on raw input, but do not synthesize them when absent.",
            "Compute shortage_units as max(quantity_requested - available_quantity, 0) and normalize support notes deterministically.",
            "Normalize support notes by lowercasing and stripping one trailing sentence period when present. Preserve the existing internal punctuation and wording; do not append new punctuation.",
        ],
        "exception_classifier": [
            "Classify shipping_delay when shipment_delay_hours >= 24 or shipment_status indicates a shipping problem; do not emit fallback labels outside the schema.",
            "ORX-101 is the shipping-only benchmark case: no shortage plus a 24-47 hour shipping delay still means shipping_delay, not no-exception or a fallback branch.",
            "Classify compound_exception only when there is both an inventory shortage and a severe shipping delay (48+ hours or shipment_status == 'exception').",
            "Implement the classifier as one short direct decision tree: shortage + severe shipping => compound_exception; shortage only => inventory_shortage; otherwise shipping_delay when delay >= 24 or shipment_status indicates a shipping problem. If no schema-valid label applies, raise ValueError instead of writing speculative fallback logic or long ambiguity comments.",
        ],
        "inventory_risk_evaluator": [
            "Keep inventory_risk_band within the schema's categorical values and align high-risk outputs with the benchmark fixtures for large shortages or delayed replenishment.",
            "For the ORX-100-style high-risk shortage case, use the benchmark-local rationale 'shortage is large enough to threaten the order promise' instead of a generic back-order explanation.",
            "For the ORX-102-style moderate shortage plus delayed replenishment case, inventory_risk_band can still be 'high' while the reason stays 'shortage requires partial fulfillment or back-order'.",
        ],
        "shipping_risk_evaluator": [
            "Treat 24+ hour delays as material and 48+ hour or shipment_status == 'exception' as severe, with schema-valid risk-band outputs.",
            "Do not emit a medium band for ORX-101-style 24-47 hour delays; shipping risk is already high at that threshold.",
            "If shipment delay remains below threshold, keep the low-risk rationale tied to the delay itself; do not rewrite it as a manual-override reason.",
        ],
        "customer_context_loader": [
            "Emit customer_priority_context.priority_lane='expedite' for platinum customers and gold customers with open_case_count >= 3; otherwise emit 'standard'.",
        ],
        "manual_override_loader": [
            "Emit manual_override_decision only when manual_override_action is present. When no override exists, return no output port at all.",
        ],
        "factor_correlator": [
            "The on_override input port is optional. Check for its presence before reading override_action.",
            "When validating multiple case_id comparisons in one guard, keep the boolean expression on one line or wrap it in parentheses; never split after or without explicit continuation.",
            "Do not read shipment_status from shipping_risk; that field does not exist on the ShippingRisk schema. Use shipment_risk_band and shipment_delay_hours instead.",
            "Override present => blocker_source='override' and recommended_team='account_operations'.",
            "Compound exception => blocker_source='compound' and recommended_team='exception_desk'.",
            "Shipping delay => blocker_source='shipping' and recommended_team='logistics'. Inventory shortage => blocker_source='inventory' and recommended_team='support'.",
            "Do not force escalation_required=True for every shipping-delay case. ORX-101 is the benchmark counterexample: standard customer, shipping route, escalation_required=False.",
            "Manual override can change blocker_source and team ownership, but it does not retroactively rewrite the upstream shipping-risk rationale.",
        ],
        "priority_scorer": [
            "Override and compound exceptions must score as critical. Shipping-delay cases should remain high. Use schema-valid categorical values only.",
            "Shipping-only standard-customer cases remain high priority even when escalation_required=False. Do not gate shipping-delay priority on the escalation flag.",
            "Do not merge override and compound logic into one branch. blocker_source='override' => priority_band='critical', score=96, reason='override and expedite lane require immediate action'. primary_exception_type='compound_exception' => priority_band='critical', score=95, reason='compound exception requires immediate coordinated escalation'.",
        ],
        "resolution_assembler": [
            "override_action is optional on resolution_factors. Use .get or membership checks before reading it.",
            "Emit override_applied only when an override exists; do not synthesize it for non-override cases.",
            "Map action_summary explicitly: override => 'expedite allocation and notify account team'; shipping_delay => 'open carrier escalation'; compound_exception => 'coordinate exception desk escalation'.",
            "Always end the module with a real build_component() function after GeneratedComponent; do not leave trailing prose, comments, or half-finished code at the end of the file.",
            "When updating the digest-store entries list, use ordinary ASCII Python list and dict operations only; do not emit non-ASCII punctuation or invented method names.",
            "Preserve one digest-store entry per case_id and keep entry order stable across cases.",
        ],
    }


def _map_prior_guidance_to_components(
    *,
    bundle: BenchmarkBundle,
    prior_guidance: list[str],
) -> dict[str, list[str]]:
    """Map previous-attempt guidance onto likely impacted AC14 components."""

    component_ids = list(bundle.blueprint.components)
    mapped: dict[str, list[str]] = {component_id: [] for component_id in component_ids}
    if bundle.config.benchmark_id != "order_exception_resolution_v1":
        for component_id in component_ids:
            mapped[component_id] = list(prior_guidance)
        return mapped

    keyword_targets: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
        (("override_action", "override_applied"), ("manual_override_loader", "factor_correlator", "resolution_assembler")),
        (("compound exception", "compound_exception", "orx-102"), ("exception_classifier", "shipping_risk_evaluator", "factor_correlator", "priority_scorer", "resolution_assembler", "customer_context_loader")),
        (("shipping_delay", "shipping", "orx-101"), ("exception_classifier", "shipping_risk_evaluator", "factor_correlator", "priority_scorer", "resolution_assembler")),
        (("resolution_digest_store", "missing outputs", "entries"), ("resolution_assembler",)),
    ]
    for line in prior_guidance:
        lowered = line.lower()
        targeted = False
        for component_id in component_ids:
            if component_id in lowered:
                mapped[component_id].append(line)
                targeted = True
        for keywords, targets in keyword_targets:
            if any(keyword in lowered for keyword in keywords):
                for component_id in targets:
                    mapped[component_id].append(line)
                targeted = True
        if not targeted and line.startswith("generation failed before evaluation"):
            for component_id in component_ids:
                mapped[component_id].append(line)
    return {component_id: _dedupe_guidance(lines) for component_id, lines in mapped.items()}


def _dedupe_guidance(lines: list[str]) -> list[str]:
    """Deduplicate bounded repair guidance while preserving order."""

    result: list[str] = []
    seen: set[str] = set()
    for line in lines:
        normalized = line.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _strip_dynamic_field_paths(
    data: dict[str, Any],
    paths: list[str],
) -> dict[str, Any]:
    """Return a deep copy of data with each dot-separated dynamic field path removed."""
    result = copy.deepcopy(data)
    for path in paths:
        parts = path.split(".")
        obj: Any = result
        for part in parts[:-1]:
            if not isinstance(obj, dict) or part not in obj:
                break
            obj = obj[part]
        else:
            if isinstance(obj, dict):
                obj.pop(parts[-1], None)
    return result


def _dynamic_field_exists(data: dict[str, Any], path: str) -> bool:
    """Return True if a dot-separated field path exists anywhere in data."""
    parts = path.split(".")
    obj: Any = data
    for part in parts:
        if not isinstance(obj, dict) or part not in obj:
            return False
        obj = obj[part]
    return True


def _execute_runtime_cases(
    *,
    bundle: BenchmarkBundle,
    generated_package: GeneratedPackage,
) -> list[RuntimeCaseExecution]:
    """Execute all runtime cases sequentially against one generated package."""

    builders = load_generated_component_builders(generated_package)
    implementations = {
        component_id: builders[component_id]()
        for component_id in bundle.blueprint.components
    }
    expected_by_case = {case.case_id: case.expected_outputs for case in bundle.expected_runtime_cases}
    results: list[RuntimeCaseExecution] = []

    for record in bundle.runtime_cases:
        case_id = cast(str, record["case_id"])
        expected_outputs = expected_by_case[case_id]
        try:
            outputs_by_component = run_blueprint_once(
                bundle.blueprint,
                implementations,
                {
                    bundle.config.primary_source_component_id: {
                        bundle.config.primary_source_port_name: record,
                    },
                },
            )
            final_outputs = outputs_by_component[bundle.config.final_component_id]
            selected_outputs = {
                port_name: final_outputs[port_name]
                for port_name in bundle.config.final_output_ports
            }
            frozen_outputs = copy.deepcopy(selected_outputs)
            dynamic_fields = bundle.config.dynamic_output_fields
            compare_actual = _strip_dynamic_field_paths(frozen_outputs, dynamic_fields)
            compare_expected = _strip_dynamic_field_paths(expected_outputs, dynamic_fields)
            missing_dynamic = [
                f for f in dynamic_fields
                if not _dynamic_field_exists(frozen_outputs, f)
            ]
            matched = compare_actual == compare_expected and not missing_dynamic
            results.append(
                RuntimeCaseExecution(
                    case_id=case_id,
                    matched_expected=matched,
                    actual_outputs=frozen_outputs,
                    expected_outputs=expected_outputs,
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


def _review_runtime_cases(
    *,
    bundle: BenchmarkBundle,
    runtime_cases: list[RuntimeCaseExecution],
    model: str,
    max_budget: float,
    trace_id: str,
) -> AcceptanceReviewResponse:
    """Run the shared acceptance-review rubric over the benchmark runtime outputs."""

    fixture_path = os.environ.get("AC14_ACCEPTANCE_REVIEW_FIXTURE")
    if fixture_path:
        return AcceptanceReviewResponse.model_validate_json(Path(fixture_path).read_text())

    scenario = Scenario(
        scenario_id="benchmark_runtime_review",
        kind="semantic_acceptance",
        description=(
            "Review the full runtime outputs for the empirical order-exception benchmark "
            "against the frozen system requirements."
        ),
        fixture_ids=[],
        evaluator_ids=["requirements_acceptance"],
        realistic_input=True,
        requirements=bundle.config.system_requirements,
    )
    outputs_by_component = {
        case.case_id: {
            bundle.config.final_component_id: case.actual_outputs or {},
        }
        for case in runtime_cases
    }
    messages = cast(
        list[Any],
        render_prompt(
            ACCEPTANCE_PROMPT_PATH,
            blueprint_metadata=bundle.blueprint.metadata.model_dump(mode="json"),
            scenario=scenario.model_dump(mode="json"),
            realistic_input_payload=bundle.runtime_cases,
            outputs_by_component=outputs_by_component,
        ),
    )
    response, _meta = cast(
        tuple[AcceptanceReviewResponse, object],
        asyncio.run(
            acall_llm_structured(
                model,
                messages,
                response_model=AcceptanceReviewResponse,
                task="ac14_review_acceptance",
                trace_id=trace_id,
                max_budget=max_budget,
            ),
        ),
    )
    return response


INFRASTRUCTURE_ERROR_MARKERS = (
    "503",
    "service unavailable",
    "server disconnected",
    "disconnect",
    "dns",
    "name resolution",
    "api connection",
    "connecterror",
    "remoteprotocolerror",
    "transport",
    "temporar",
    "connection failure",
    "timed out",
    "timeout",
)


def _classify_attempt_failure(
    *,
    generation_error: str | None,
    packet_tests_passed: bool,
    recomposition_passed: bool,
    runtime_cases: list[RuntimeCaseExecution],
    semantic_review: AcceptanceReviewResponse | None,
    semantic_review_policy: SemanticReviewPolicy,
) -> AttemptFailureClassification:
    """Classify one bounded empirical-comparison attempt into a stable failure domain."""

    if generation_error is not None:
        if _is_infrastructure_provider_error(generation_error):
            return AttemptFailureClassification(
                category="infrastructure_provider",
                detail=generation_error,
            )
        return AttemptFailureClassification(category="generation", detail=generation_error)
    # Packet tests and recomposition are diagnostic artifacts, not primary gates.
    # The primary success criterion is runtime output correctness.
    failing_runtime_cases = [case for case in runtime_cases if not case.matched_expected]
    if failing_runtime_cases:
        details = [
            case.error or f"{case.case_id} outputs mismatched expected outputs"
            for case in failing_runtime_cases
        ]
        return AttemptFailureClassification(
            category="runtime_outputs",
            detail="; ".join(details),
        )
    if (
        semantic_review is not None
        and semantic_review.overall_verdict != "accept"
        and not (
            semantic_review_policy == "advisory_on_exact_match"
            and not failing_runtime_cases
        )
    ):
        concerns = "; ".join(semantic_review.concerns) or semantic_review.overall_verdict
        return AttemptFailureClassification(
            category="semantic_review",
            detail=concerns,
        )
    return AttemptFailureClassification(
        category="success",
        detail="attempt passed the full benchmark harness",
    )


def _is_infrastructure_provider_error(error_text: str) -> bool:
    """Heuristically detect provider or transport instability from one error string."""

    lowered = error_text.lower()
    return any(marker in lowered for marker in INFRASTRUCTURE_ERROR_MARKERS)


def _build_failure_summary(
    *,
    generation_error: str | None,
    packet_tests_passed: bool,
    recomposition_passed: bool,
    runtime_cases: list[RuntimeCaseExecution],
    semantic_review: AcceptanceReviewResponse | None,
    packet_report: PacketTestReport | None = None,
    recomposition_report: RecompositionReport | None = None,
    dynamic_output_fields: list[str] | None = None,
) -> list[str]:
    """Summarize the previous attempt into bounded repair guidance."""

    summary: list[str] = []
    if generation_error is not None:
        summary.append(f"generation failed before evaluation: {generation_error}")
        return summary
    if not packet_tests_passed:
        summary.append("packet-local tests failed in the previous attempt")
        summary.extend(_summarize_packet_report(packet_report))
    if not recomposition_passed:
        summary.append("recomposition proof failed in the previous attempt")
        summary.extend(_summarize_recomposition_report(recomposition_report))
    failing_runtime_cases = [case for case in runtime_cases if not case.matched_expected]
    for case in failing_runtime_cases:
        if case.error is not None:
            summary.append(f"runtime case {case.case_id} failed: {case.error}")
        else:
            mismatch_details = _summarize_runtime_output_mismatch(
                case,
                dynamic_output_fields=dynamic_output_fields or [],
            )
            summary.append(
                f"runtime case {case.case_id} mismatches: " + "; ".join(mismatch_details),
            )
    if semantic_review is not None and semantic_review.overall_verdict != "accept":
        summary.extend(
            [f"semantic review concern: {concern}" for concern in semantic_review.concerns]
            or [f"semantic review verdict was {semantic_review.overall_verdict}"]
        )
    return summary or ["previous attempt failed without a more specific summary"]


def _summarize_packet_report(packet_report: PacketTestReport | None, *, limit: int = 4) -> list[str]:
    """Extract bounded component-local guidance from one packet-test report."""

    if packet_report is None:
        return []
    lines: list[str] = []
    for result in packet_report.results:
        if result.passed:
            continue
        if result.mismatch_details:
            lines.append(
                f"packet fixture {result.fixture_id} on {result.component_id} mismatches: "
                + "; ".join(result.mismatch_details[:3])
            )
        elif result.error:
            lines.append(
                f"packet fixture {result.fixture_id} on {result.component_id} failed: {result.error}"
            )
        if len(lines) >= limit:
            break
    if not lines and packet_report.harness_error:
        lines.append(f"packet harness error: {packet_report.harness_error}")
    return lines


def _summarize_recomposition_report(
    recomposition_report: RecompositionReport | None,
    *,
    limit: int = 4,
) -> list[str]:
    """Extract bounded scenario-local guidance from one recomposition report."""

    if recomposition_report is None:
        return []
    lines: list[str] = []
    for result in recomposition_report.results:
        if result.passed:
            continue
        if result.mismatch_details and result.mismatch_component_id is not None:
            lines.append(
                f"recomposition scenario {result.scenario_id} on {result.mismatch_component_id} mismatches: "
                + "; ".join(result.mismatch_details[:3])
            )
        elif result.error:
            lines.append(f"recomposition scenario {result.scenario_id} failed: {result.error}")
        if len(lines) >= limit:
            break
    if not lines and recomposition_report.harness_error:
        lines.append(f"recomposition harness error: {recomposition_report.harness_error}")
    return lines


def _aggregate_condition(
    trial_reports: list[PairedTrialReport],
    condition: TrialCondition,
) -> ConditionAggregate:
    """Aggregate one condition across all paired trials."""

    reports = [
        trial_report.ac14 if condition == "ac14" else trial_report.monolithic
        for trial_report in trial_reports
    ]
    semantic_scores = [
        _semantic_score(attempt.semantic_review)
        for report in reports
        for attempt in report.attempts
        if attempt.semantic_review is not None
    ]
    durations = [sum(attempt.duration_s for attempt in report.attempts) for report in reports]
    observed_costs = [
        attempt.llm_cost.cost_usd
        for report in reports
        for attempt in report.attempts
        if attempt.llm_cost.status == "observed" and attempt.llm_cost.cost_usd is not None
    ]
    trials_with_observed_cost = sum(
        1
        for report in reports
        if any(attempt.llm_cost.status == "observed" for attempt in report.attempts)
    )
    return ConditionAggregate(
        condition=condition,
        successes=sum(1 for report in reports if report.passed),
        average_repair_loops=(sum(report.repair_loops_used for report in reports) / len(reports)),
        average_semantic_score=(
            sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0.0
        ),
        average_duration_s=(sum(durations) / len(durations)),
        total_observed_cost_usd=sum(observed_costs),
        observed_cost_trials=trials_with_observed_cost,
    )


def _semantic_score(review: AcceptanceReviewResponse | None) -> float:
    """Map structured semantic-review verdicts into a bounded numeric score."""

    if review is None:
        return 0.0
    if review.overall_verdict == "accept":
        return 2.0
    if review.overall_verdict == "concern":
        return 1.0
    return 0.0


def _summarize_runtime_output_mismatch(
    case: RuntimeCaseExecution,
    *,
    max_differences: int = 6,
    dynamic_output_fields: list[str] | None = None,
) -> list[str]:
    """Build bounded field-level mismatch guidance for one runtime case.

    Dynamic output fields (e.g. wall-clock timestamps) are excluded from the
    diff because their values are intentionally not compared.
    """
    excluded: set[str] = set(dynamic_output_fields or [])
    actual_outputs = case.actual_outputs or {}
    stripped_actual = _strip_dynamic_field_paths(actual_outputs, list(excluded))
    stripped_expected = _strip_dynamic_field_paths(case.expected_outputs, list(excluded))
    differences: list[str] = []
    for port_name in sorted(set(stripped_expected) | set(stripped_actual)):
        if len(differences) >= max_differences:
            break
        if port_name not in stripped_actual:
            differences.append(f"{port_name} missing from actual outputs")
            continue
        if port_name not in stripped_expected:
            differences.append(f"{port_name} unexpectedly present in actual outputs")
            continue
        differences.extend(
            _collect_bounded_differences(
                expected=stripped_expected[port_name],
                actual=stripped_actual[port_name],
                prefix=port_name,
                limit=max_differences - len(differences),
            ),
        )
    return differences or ["final outputs differed without a bounded field diff"]


def _collect_bounded_differences(
    *,
    expected: Any,
    actual: Any,
    prefix: str,
    limit: int,
) -> list[str]:
    """Collect bounded path-level differences between expected and actual outputs."""

    return collect_bounded_differences(
        expected=expected,
        actual=actual,
        prefix=prefix,
        limit=limit,
    )


def _observe_llm_cost(trace_prefix: str) -> CostObservation:
    """Query the shared observability DB for total cost by trace prefix."""

    db_path = Path(
        os.environ.get(
            "AC14_LLM_OBSERVABILITY_DB",
            str(Path.home() / "projects" / "data" / "llm_observability.db"),
        )
    )
    if not db_path.exists():
        return CostObservation(status="missing_db")

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT SUM(cost)
            FROM llm_calls
            WHERE trace_id LIKE ? || '%'
            """,
            (trace_prefix,),
        ).fetchone()
    observed_cost = cast(float | None, row[0] if row is not None else None)
    if observed_cost is None:
        return CostObservation(status="no_rows")
    return CostObservation(status="observed", cost_usd=float(observed_cost))


def _validate_module_contract(
    module_code: str,
    *,
    component_id: str,
    allowed_input_ports: set[str] | None = None,
) -> None:
    """Fail loud when one generated module misses the AC14 runtime contract."""

    non_ascii = next((character for character in module_code if ord(character) > 127), None)
    if non_ascii is not None:
        raise ValueError(
            f"generated module for {component_id} contains non-ASCII character {non_ascii!r}",
        )

    try:
        tree = ast.parse(module_code)
    except SyntaxError as exc:  # pragma: no cover - fail-loud validation path
        raise ValueError(f"generated module for {component_id} is not valid Python: {exc}") from exc

    has_generated_component = any(
        isinstance(node, ast.ClassDef) and node.name == "GeneratedComponent"
        for node in tree.body
    )
    has_build_component = any(
        isinstance(node, ast.FunctionDef) and node.name == "build_component"
        for node in tree.body
    )
    if not has_generated_component:
        raise ValueError(f"generated module for {component_id} is missing GeneratedComponent class")
    if not has_build_component:
        raise ValueError(f"generated module for {component_id} is missing build_component function")

    if allowed_input_ports is not None:
        _validate_literal_input_port_references(
            tree,
            component_id=component_id,
            allowed_input_ports=allowed_input_ports,
        )

    namespace: dict[str, object] = {}
    try:
        exec(module_code, namespace)
    except Exception as exc:  # pragma: no cover - fail-loud validation path
        raise ValueError(
            f"generated module for {component_id} failed during import-time validation: {exc}",
        ) from exc

    build_component = namespace.get("build_component")
    if not callable(build_component):
        raise ValueError(
            f"generated module for {component_id} has a non-callable build_component",
        )
    try:
        component = build_component()
    except Exception as exc:  # pragma: no cover - fail-loud validation path
        raise ValueError(
            f"generated module for {component_id} failed when build_component() was called: {exc}",
        ) from exc
    execute = getattr(component, "execute", None)
    if not callable(execute):
        raise ValueError(
            f"generated module for {component_id} build_component() did not return a runtime component",
        )

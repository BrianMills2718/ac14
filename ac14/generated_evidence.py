"""Execution helpers for generated components and repeated fresh-run evidence."""

from __future__ import annotations

import asyncio
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, Field

from ac14.generated_codegen import (
    GeneratedPackage,
    GeneratorKind,
    emit_generated_package,
    load_generated_component_builders,
)
from ac14.loader import load_blueprint_dir
from ac14.models import PacketBundle
from ac14.output_diff import summarize_mapping_mismatch
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets
from ac14.recomposition import RecompositionReport, run_recomposition_proof

PACKET_EVALUATE_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "evaluate_packet_case.yaml"


_FIXTURE_FREE_FORM_FIELDS: frozenset[str] = frozenset({
    "reason",
    "score",
    "action_summary",
    "generated_at",
})
"""Fields excluded from packet-test and recomposition exact comparison.

LLM-generated components cannot deterministically reproduce free-form text
(reason strings, action summaries) or wall-clock timestamps. Stripping these
fields from both sides of the comparison keeps packet tests focused on
categorical correctness — the fields that matter for routing decisions.
"""

# Alias so callers and prompt logic share one name.
_PACKET_TEST_NON_CATEGORICAL_FIELDS: frozenset[str] = _FIXTURE_FREE_FORM_FIELDS

# Subset of non-categorical fields that carry semantic meaning the LLM should evaluate.
# ``score`` and ``generated_at`` are excluded: score is numeric (exact or not meaningful),
# generated_at is a timestamp (not semantic).
_PACKET_TEST_LLM_EVAL_FIELDS: frozenset[str] = frozenset({"reason", "action_summary"})


def _json_safe_semantic_eval_value(value: Any) -> Any:
    """Convert semantic-evaluation prompt inputs into JSON-safe values.

    Blueprint fixtures may legitimately parse ISO timestamps into ``datetime``
    objects. Semantic-evaluation prompts render those inputs with Jinja
    ``tojson``, so values must be normalized before templating.
    """

    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {
            str(key): _json_safe_semantic_eval_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_json_safe_semantic_eval_value(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe_semantic_eval_value(item) for item in value]
    return value


def _strip_fixture_free_form_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Remove free-form text and timestamp fields at any nesting depth.

    Only fields in ``_FIXTURE_FREE_FORM_FIELDS`` are removed. All other
    fields — including nested dicts and list items — are preserved intact so
    that categorical field comparison is still enforced.
    """
    result: dict[str, Any] = {}
    for k, v in data.items():
        if k in _FIXTURE_FREE_FORM_FIELDS:
            continue
        if isinstance(v, dict):
            result[k] = _strip_fixture_free_form_fields(v)
        elif isinstance(v, list):
            result[k] = [
                _strip_fixture_free_form_fields(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            result[k] = v
    return result


def _has_llm_eval_fields(data: dict[str, Any]) -> bool:
    """Return True if data (at any nesting depth) contains a free-form LLM-eval field."""
    for k, v in data.items():
        if k in _PACKET_TEST_LLM_EVAL_FIELDS:
            return True
        if isinstance(v, dict) and _has_llm_eval_fields(v):
            return True
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict) and _has_llm_eval_fields(item):
                    return True
    return False


class PacketCaseSemanticEval(BaseModel):
    """LLM evaluation of free-form fields in one packet case output."""

    semantic_fields_acceptable: bool = Field(
        description=(
            "True if all free-form text fields (reason, action_summary) are semantically correct"
            " given the inputs and component purpose"
        )
    )
    concerns: list[str] = Field(
        description="Specific concerns about semantic correctness; empty list if all fields are acceptable"
    )


async def _aevaluate_packet_case_semantically(
    component_id: str,
    fixture_description: str,
    inputs: dict[str, Any],
    expected_outputs: dict[str, Any],
    actual_outputs: dict[str, Any],
    model: str,
    trace_id: str,
    max_budget: float = 0.10,
) -> PacketCaseSemanticEval:
    """LLM evaluation of free-form output fields for one packet case."""

    from ac14.acceptance import acall_llm_structured, render_prompt  # lazy — avoids import-time llm_client dep

    messages = render_prompt(
        PACKET_EVALUATE_PROMPT_PATH,
        component_id=component_id,
        fixture_description=fixture_description,
        inputs=_json_safe_semantic_eval_value(inputs),
        expected_outputs=_json_safe_semantic_eval_value(expected_outputs),
        actual_outputs=_json_safe_semantic_eval_value(actual_outputs),
    )
    result, _ = await acall_llm_structured(
        model,
        messages,
        response_model=PacketCaseSemanticEval,
        task="ac14_evaluate_packet_case_semantics",
        trace_id=trace_id,
        max_budget=max_budget,
    )
    return cast(PacketCaseSemanticEval, result)


class PacketCaseResult(BaseModel):
    """Result of one packet-local generated component test case."""

    component_id: str = Field(description="Component under test.")
    fixture_id: str = Field(description="Fixture identifier.")
    passed: bool = Field(description="Whether the case passed.")
    error: str | None = Field(default=None, description="Failure message when the case fails.")
    mismatch_details: list[str] = Field(
        default_factory=list,
        description="Bounded field-level categorical mismatch details when available.",
    )
    semantic_eval: PacketCaseSemanticEval | None = Field(
        default=None,
        description="LLM semantic evaluation of free-form output fields when LLM evaluation was requested.",
    )


class PacketTestReport(BaseModel):
    """Aggregated results for all packet-local generated component tests."""

    passed: bool = Field(description="Whether all packet-local cases passed.")
    results: list[PacketCaseResult] = Field(description="Per-case results.")
    harness_error: str | None = Field(
        default=None,
        description="Attempt-level harness error when packet tests could not run normally.",
    )


class FreshRunTrial(BaseModel):
    """Outcome for one fresh generation and verification run."""

    trial_id: int = Field(description="Sequential trial identifier.")
    package_dir: str = Field(description="Directory containing emitted modules for the trial.")
    packet_tests_passed: bool = Field(description="Whether packet-local tests passed.")
    recomposition_passed: bool = Field(description="Whether recomposition scenarios passed.")


class FreshRunSummary(BaseModel):
    """Summary artifact for repeated fresh generation trials."""

    trial_count: int = Field(description="Number of executed trials.")
    passed_trials: int = Field(description="Number of trials with all checks passing.")
    failed_trials: int = Field(description="Number of failed trials.")
    trials: list[FreshRunTrial] = Field(description="Per-trial outcomes.")


def run_generated_packet_tests(
    packet_bundle: PacketBundle,
    generated_package: GeneratedPackage,
    *,
    llm_model: str | None = None,
    trace_id: str | None = None,
    llm_max_budget: float = 0.10,
) -> PacketTestReport:
    """Run packet-local fixtures against generated components.

    When ``llm_model`` is provided, free-form text fields (reason, action_summary)
    that pass categorical checks are additionally evaluated for semantic correctness
    by an LLM judge. The categorical phase must pass first; the LLM phase only runs
    when the categorical phase passes and the expected outputs contain at least one
    LLM-eval field.
    """

    packet_cases = materialize_packet_test_cases(packet_bundle)
    builders = load_generated_component_builders(generated_package)
    results: list[PacketCaseResult] = []

    for component_id, cases in packet_cases.items():
        for case in cases:
            component = builders[component_id]()
            error: str | None
            mismatch_details: list[str] = []
            semantic_eval: PacketCaseSemanticEval | None = None
            try:
                outputs = component.execute(case.inputs)
                if _expects_failure(case.scenario_kind):
                    passed = False
                    error = "negative case unexpectedly succeeded"
                else:
                    # Phase 1: categorical exact check (free-form fields stripped)
                    stripped_actual = _strip_fixture_free_form_fields(outputs)
                    stripped_expected = _strip_fixture_free_form_fields(case.expected_outputs)
                    categorical_passed = stripped_actual == stripped_expected

                    if not categorical_passed:
                        passed = False
                        mismatch_details = summarize_mapping_mismatch(
                            expected=stripped_expected,
                            actual=stripped_actual,
                        )
                        error = (
                            "categorical fields did not match expected outputs: "
                            + "; ".join(mismatch_details)
                        )
                    elif llm_model is not None and _has_llm_eval_fields(case.expected_outputs):
                        # Phase 2: LLM semantic eval for free-form fields
                        semantic_eval = asyncio.run(
                            _aevaluate_packet_case_semantically(
                                component_id=component_id,
                                fixture_description=case.description,
                                inputs=case.inputs,
                                expected_outputs=case.expected_outputs,
                                actual_outputs=outputs,
                                model=llm_model,
                                trace_id=f"{trace_id or 'packet_test'}/{component_id}/{case.fixture_id}/semantic",
                                max_budget=llm_max_budget,
                            )
                        )
                        passed = semantic_eval.semantic_fields_acceptable
                        error = "; ".join(semantic_eval.concerns) if not passed else None
                    else:
                        passed = True
                        error = None
            except Exception as exc:  # pragma: no cover - explicit failure capture
                if _expects_failure(case.scenario_kind):
                    passed = True
                    error = None
                else:
                    passed = False
                    error = str(exc)
            results.append(
                PacketCaseResult(
                    component_id=component_id,
                    fixture_id=case.fixture_id,
                    passed=passed,
                    error=error,
                    mismatch_details=mismatch_details,
                    semantic_eval=semantic_eval,
                ),
            )

    return PacketTestReport(
        passed=all(result.passed for result in results),
        results=results,
    )


def run_generated_recomposition_proof(
    blueprint_dir: Path | str,
    generated_package: GeneratedPackage,
    *,
    llm_model: str | None = None,
    trace_id: str | None = None,
    llm_max_budget: float = 0.10,
) -> RecompositionReport:
    """Run blueprint-driven recomposition scenarios against generated components.

    When ``llm_model`` is provided, free-form text fields in recomposition
    outputs are also evaluated for semantic correctness by an LLM judge after
    categorical checks pass.
    """

    blueprint = load_blueprint_dir(blueprint_dir)
    builders = load_generated_component_builders(generated_package)
    return run_recomposition_proof(
        blueprint,
        builders,
        llm_model=llm_model,
        trace_id=trace_id,
        llm_max_budget=llm_max_budget,
    )


def run_fresh_generation_trials(
    blueprint_dir: Path | str,
    trial_count: int,
    output_dir: Path | str,
    *,
    generator_kind: GeneratorKind = "deterministic",
    llm_model: str = "gemini/gemini-2.5-flash-lite",
    llm_max_budget: float = 0.50,
) -> FreshRunSummary:
    """Run repeated fresh generation trials and write a summary artifact."""

    blueprint = load_blueprint_dir(blueprint_dir)
    packet_bundle = compile_packets(blueprint)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    trials: list[FreshRunTrial] = []
    for trial_id in range(1, trial_count + 1):
        package_dir = destination / f"trial_{trial_id}"
        generated_package = emit_generated_package(
            packet_bundle,
            package_dir,
            generator_kind=generator_kind,
            llm_model=llm_model,
            llm_max_budget=llm_max_budget,
            trace_id_prefix=f"ac14/fresh_run_trial_{trial_id}",
        )
        packet_report = run_generated_packet_tests(packet_bundle, generated_package)
        recomposition_report = run_generated_recomposition_proof(blueprint_dir, generated_package)
        trials.append(
            FreshRunTrial(
                trial_id=trial_id,
                package_dir=str(package_dir),
                packet_tests_passed=packet_report.passed,
                recomposition_passed=recomposition_report.passed,
            ),
        )

    summary = FreshRunSummary(
        trial_count=trial_count,
        passed_trials=sum(
            1 for trial in trials if trial.packet_tests_passed and trial.recomposition_passed
        ),
        failed_trials=sum(
            1 for trial in trials if not (trial.packet_tests_passed and trial.recomposition_passed)
        ),
        trials=trials,
    )
    (destination / "fresh_run_summary.json").write_text(
        json.dumps(summary.model_dump(mode="json"), indent=2),
    )
    return summary


def _expects_failure(scenario_kind: str) -> bool:
    """Return true for negative packet-test scenarios that should fail loudly."""

    return scenario_kind == "negative"

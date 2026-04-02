"""Tests for the empirical monolithic-vs-AC14 comparison gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from llm_client import render_prompt  # type: ignore[import-not-found]

from ac14.acceptance import AcceptanceReviewResponse
from ac14.packet_tests import materialize_packet_test_cases
from ac14.empirical_comparison import (
    MONOLITHIC_PROMPT_PATH,
    AttemptFailureClassification,
    ConditionAttemptReport,
    ConditionTrialReport,
    CostObservation,
    ExperimentDecisionArtifact,
    PairedTrialReport,
    RuntimeCaseExecution,
    _benchmark_repair_guidance,
    _build_component_repair_guidance,
    _build_failure_summary,
    _dynamic_field_exists,
    _run_condition_attempt,
    _strip_dynamic_field_paths,
    build_experiment_decision_artifact,
    build_smoke_readiness_artifact,
    load_benchmark_bundle,
    run_paired_trial,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_DIR = REPO_ROOT / "benchmarks" / "order_exception_resolution"


def test_build_benchmark_bundle_order_exception_resolution() -> None:
    """The frozen benchmark bundle should load into a coherent comparison target."""

    bundle = load_benchmark_bundle(BENCHMARK_DIR)

    assert bundle.config.benchmark_id == "order_exception_resolution_v1"
    assert bundle.blueprint.metadata.blueprint_id == "order_exception_resolution_v1"
    assert len(bundle.packet_bundle.packets) == 9
    assert [record["case_id"] for record in bundle.runtime_cases] == ["ORX-100", "ORX-101", "ORX-102"]
    assert [case.case_id for case in bundle.expected_runtime_cases] == ["ORX-100", "ORX-101", "ORX-102"]


def test_run_paired_trial_persists_monolithic_and_ac14_artifacts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The paired-trial runner should persist both condition reports explicitly."""

    # mock-ok: this test verifies paired-trial persistence and report wiring, not live generation behavior.
    def _fake_run_condition_trial(**kwargs: object) -> ConditionTrialReport:
        condition = kwargs["condition"]
        return ConditionTrialReport(
            condition=condition,  # type: ignore[arg-type]
            passed=condition == "ac14",
            attempts_used=1,
            repair_loops_used=0,
            attempts=[
                ConditionAttemptReport(
                    attempt_id=1,
                    artifact_dir=str(tmp_path / str(condition) / "attempt_1"),
                    duration_s=0.25,
                    llm_cost=CostObservation(status="no_rows"),
                    packet_tests_passed=True,
                    recomposition_passed=True,
                    runtime_outputs_passed=condition == "ac14",
                    semantic_review=None,
                    semantic_review_passed=condition == "ac14",
                    failure_classification=AttemptFailureClassification(
                        category="success" if condition == "ac14" else "runtime_outputs",
                        detail="passed" if condition == "ac14" else "runtime mismatch",
                    ),
                    generation_error=None,
                    runtime_cases=[
                        RuntimeCaseExecution(
                            case_id="ORX-100",
                            matched_expected=condition == "ac14",
                            actual_outputs={},
                            expected_outputs={},
                        )
                    ],
                    failure_summary=[] if condition == "ac14" else ["runtime mismatch"],
                    passed=condition == "ac14",
                )
            ],
        )

    monkeypatch.setattr(
        "ac14.empirical_comparison._run_condition_trial",
        _fake_run_condition_trial,
    )

    report = run_paired_trial(
        BENCHMARK_DIR,
        tmp_path / "trial_1",
        trial_id=1,
    )

    persisted = json.loads((tmp_path / "trial_1" / "paired_trial_report.json").read_text())
    assert report.benchmark_id == "order_exception_resolution_v1"
    assert report.monolithic.condition == "monolithic"
    assert report.ac14.condition == "ac14"
    assert persisted["monolithic"]["condition"] == "monolithic"
    assert persisted["ac14"]["condition"] == "ac14"


def test_build_experiment_decision_artifact_applies_plan_38_rule() -> None:
    """The final decision artifact should follow the frozen comparison rule."""

    trial_reports = [
        PairedTrialReport(
            benchmark_id="order_exception_resolution_v1",
            trial_id=trial_id,
            monolithic=_condition_report("monolithic", passed=trial_id == 1, semantic_score=1.0, repair_loops=2),
            ac14=_condition_report("ac14", passed=True, semantic_score=2.0, repair_loops=0),
        )
        for trial_id in range(1, 6)
    ]

    decision = build_experiment_decision_artifact(
        benchmark_id="order_exception_resolution_v1",
        trial_reports=trial_reports,
        trial_report_paths=[f"/tmp/trial_{trial_id}.json" for trial_id in range(1, 6)],
    )

    assert isinstance(decision, ExperimentDecisionArtifact)
    assert decision.verdict == "ac14_wins"
    assert decision.ac14.successes == 5
    assert decision.monolithic.successes == 1


def _condition_report(
    condition: str,
    *,
    passed: bool,
    semantic_score: float,
    repair_loops: int,
) -> ConditionTrialReport:
    """Build one minimal condition report for decision-rule tests."""

    semantic_review: AcceptanceReviewResponse | None = None
    semantic_review_passed = False
    if semantic_score >= 2.0:
        semantic_review = AcceptanceReviewResponse(
            overall_verdict="accept",
            summary="accepted",
            concerns=[],
            requirement_assessments=[],
        )
        semantic_review_passed = True
    elif semantic_score >= 1.0:
        semantic_review = AcceptanceReviewResponse(
            overall_verdict="concern",
            summary="concern",
            concerns=["review concern"],
            requirement_assessments=[],
        )

    return ConditionTrialReport(
        condition=condition,  # type: ignore[arg-type]
        passed=passed,
        attempts_used=repair_loops + 1,
        repair_loops_used=repair_loops,
        attempts=[
            ConditionAttemptReport(
                attempt_id=repair_loops + 1,
                artifact_dir=f"/tmp/{condition}",
                duration_s=0.5,
                llm_cost=CostObservation(status="observed", cost_usd=0.12),
                packet_tests_passed=passed,
                recomposition_passed=passed,
                runtime_outputs_passed=passed,
                semantic_review=semantic_review,
                semantic_review_passed=semantic_review_passed,
                failure_classification=AttemptFailureClassification(
                    category="success" if passed else "semantic_review",
                    detail="accepted" if passed else "review concern",
                ),
                generation_error=None,
                runtime_cases=[],
                failure_summary=[] if passed else ["failed"],
                passed=passed,
            )
        ],
    )


def test_classify_infrastructure_failure_from_provider_error() -> None:
    """Provider/transport failures should be classified explicitly for smoke gating."""

    report = _condition_report(
        "monolithic",
        passed=False,
        semantic_score=0.0,
        repair_loops=0,
    )
    report.attempts[0].generation_error = "503 Service Unavailable: server disconnected during API request"
    report.attempts[0].failure_classification = AttemptFailureClassification(
        category="infrastructure_provider",
        detail=report.attempts[0].generation_error,
    )

    artifact = build_smoke_readiness_artifact(
        benchmark_id="order_exception_resolution_v1",
        paired_trial_report=PairedTrialReport(
            benchmark_id="order_exception_resolution_v1",
            trial_id=1,
            monolithic=report,
            ac14=_condition_report("ac14", passed=False, semantic_score=0.0, repair_loops=0),
        ),
        trial_report_path="/tmp/trial_1/paired_trial_report.json",
    )

    assert artifact.verdict == "blocked_on_infrastructure"
    assert artifact.infrastructure_failure_detected is True


def test_build_smoke_readiness_artifact_detects_harness_blocker() -> None:
    """A clean but unsuccessful smoke run should block on the harness rather than infra."""

    artifact = build_smoke_readiness_artifact(
        benchmark_id="order_exception_resolution_v1",
        paired_trial_report=PairedTrialReport(
            benchmark_id="order_exception_resolution_v1",
            trial_id=1,
            monolithic=_condition_report("monolithic", passed=False, semantic_score=0.0, repair_loops=1),
            ac14=_condition_report("ac14", passed=False, semantic_score=0.0, repair_loops=1),
        ),
        trial_report_path="/tmp/trial_1/paired_trial_report.json",
    )

    assert artifact.verdict == "blocked_on_harness"
    assert artifact.hard_harness_success is False


def test_empirical_attempt_persists_packet_and_recomposition_reports(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Empirical attempts should persist detailed harness reports even on generation failure."""

    bundle = load_benchmark_bundle(BENCHMARK_DIR)

    def _raise_generation_failure(*args: object, **kwargs: object) -> object:
        raise RuntimeError("synthetic generation failure")

    monkeypatch.setattr("ac14.empirical_comparison.emit_generated_package", _raise_generation_failure)
    monkeypatch.setattr(
        "ac14.empirical_comparison._observe_llm_cost",
        lambda trace_prefix: CostObservation(status="no_rows"),
    )

    report = _run_condition_attempt(
        bundle=bundle,
        condition="ac14",
        trial_id=1,
        attempt_id=1,
        output_dir=tmp_path / "attempt_1",
        model="test-model",
        max_budget=0.01,
        repair_guidance=[],
    )

    assert report.failure_classification.category == "generation"
    assert report.packet_test_report_path is not None
    assert report.recomposition_report_path is not None

    packet_report = json.loads(Path(report.packet_test_report_path).read_text())
    recomposition_report = json.loads(Path(report.recomposition_report_path).read_text())
    assert packet_report["passed"] is False
    assert recomposition_report["passed"] is False
    assert "synthetic generation failure" in packet_report["harness_error"]
    assert "synthetic generation failure" in recomposition_report["harness_error"]


def test_failure_summary_includes_runtime_port_diffs() -> None:
    """Runtime mismatch guidance should include bounded field-level diffs."""

    summary = _build_failure_summary(
        generation_error=None,
        packet_tests_passed=True,
        recomposition_passed=True,
        runtime_cases=[
            RuntimeCaseExecution(
                case_id="ORX-100",
                matched_expected=False,
                actual_outputs={"resolution_digest_entry": {"priority_band": "high"}},
                expected_outputs={"resolution_digest_entry": {"priority_band": "critical"}},
                error=None,
            )
        ],
        semantic_review=None,
    )

    assert "resolution_digest_entry.priority_band" in summary[0]
    assert "expected='critical' actual='high'" in summary[0]


def test_benchmark_bundle_loads_dynamic_output_fields() -> None:
    """The benchmark bundle should expose dynamic_output_fields from benchmark.yaml."""

    bundle = load_benchmark_bundle(BENCHMARK_DIR)
    assert "resolution_digest_store.generated_at" in bundle.config.dynamic_output_fields


def test_strip_dynamic_field_paths_removes_nested_field() -> None:
    """_strip_dynamic_field_paths should remove a dot-separated path from nested dicts."""

    data = {
        "resolution_digest_store": {
            "generated_at": "2026-04-01T09:00:00Z",
            "entries": [],
        }
    }
    result = _strip_dynamic_field_paths(data, ["resolution_digest_store.generated_at"])
    assert "generated_at" not in result["resolution_digest_store"]
    assert "entries" in result["resolution_digest_store"]
    # Original is not mutated
    assert "generated_at" in data["resolution_digest_store"]


def test_strip_dynamic_field_paths_ignores_missing_path() -> None:
    """_strip_dynamic_field_paths should not raise when the path is absent."""

    data: dict[str, object] = {"resolution_digest_entry": {"priority_band": "critical"}}
    result = _strip_dynamic_field_paths(data, ["resolution_digest_store.generated_at"])
    assert result == data


def test_dynamic_field_exists_returns_true_for_present_path() -> None:
    """_dynamic_field_exists should return True when a dot-separated path exists."""

    data = {"resolution_digest_store": {"generated_at": "2026-04-01T09:00:00Z"}}
    assert _dynamic_field_exists(data, "resolution_digest_store.generated_at") is True


def test_dynamic_field_exists_returns_false_for_absent_path() -> None:
    """_dynamic_field_exists should return False when the path is absent."""

    data: dict[str, object] = {"resolution_digest_store": {"entries": []}}
    assert _dynamic_field_exists(data, "resolution_digest_store.generated_at") is False


def test_benchmark_repair_guidance_targets_override_and_shipping_rules() -> None:
    """Benchmark-local repair guidance should name the real order-exception rules."""

    bundle = load_benchmark_bundle(BENCHMARK_DIR)
    guidance = _benchmark_repair_guidance(bundle=bundle, condition="monolithic")

    assert any("24+ hours" in line for line in guidance)
    assert any("compound_exception" in line for line in guidance)
    assert any("override_action" in line for line in guidance)


def test_benchmark_repair_guidance_marks_missing_schema_fields_and_no_fallback_labels() -> None:
    """Benchmark-local guidance should name the concrete monolithic schema-surface blocker."""

    bundle = load_benchmark_bundle(BENCHMARK_DIR)
    guidance = _benchmark_repair_guidance(bundle=bundle, condition="monolithic")

    assert any("shipping_risk exposes shipment_risk_band and shipment_delay_hours" in line for line in guidance)
    assert any("raise ValueError loudly instead of synthesizing a fallback label" in line for line in guidance)


def test_component_repair_guidance_targets_classifier_syntax_stability() -> None:
    """AC14 component guidance should name the direct classifier repair strategy."""

    bundle = load_benchmark_bundle(BENCHMARK_DIR)
    guidance = _build_component_repair_guidance(
        bundle=bundle,
        prior_guidance=["generation failed before evaluation: generated module for exception_classifier is not valid Python"],
    )

    assert any("short direct decision tree" in line for line in guidance["exception_classifier"])
    assert any("raise ValueError instead of writing speculative fallback logic" in line for line in guidance["exception_classifier"])


def test_component_specific_repair_guidance_targets_resolution_assembler() -> None:
    """AC14 repair guidance should target optional override handling to relevant components only."""

    bundle = load_benchmark_bundle(BENCHMARK_DIR)
    guidance = _build_component_repair_guidance(
        bundle=bundle,
        prior_guidance=["runtime case ORX-101 failed: 'override_action'"],
    )

    assert any("override_action is optional" in line for line in guidance["resolution_assembler"])
    assert any("override_action" in line for line in guidance["factor_correlator"])
    assert not any("runtime case ORX-101 failed: 'override_action'" in line for line in guidance["case_parser"])


def test_benchmark_repair_guidance_targets_shipping_only_orx101_and_case_parser_normalization() -> None:
    """Benchmark-local guidance should name the remaining ORX-101 and parser-fidelity rules."""

    bundle = load_benchmark_bundle(BENCHMARK_DIR)
    guidance = _benchmark_repair_guidance(bundle=bundle, condition="monolithic")
    component_guidance = _build_component_repair_guidance(bundle=bundle, prior_guidance=[])

    assert any("ORX-101 is a shipping-only benchmark case" in line for line in guidance)
    assert any("normalize support notes by lowercasing only" in line.lower() for line in component_guidance["case_parser"])


def test_monolithic_prompt_forbids_preclass_generatedcomponent_annotations_and_unparenthesized_multiline_conditions() -> None:
    """The monolithic prompt should harden the same import-time and multiline-condition failures."""

    bundle = load_benchmark_bundle(BENCHMARK_DIR)
    packet_test_cases_by_component = {
        component_id: [case.model_dump(mode="json") for case in cases]
        for component_id, cases in materialize_packet_test_cases(bundle.packet_bundle).items()
    }
    messages = render_prompt(
        MONOLITHIC_PROMPT_PATH,
        benchmark=bundle.config.model_dump(mode="json"),
        requirements_text=bundle.requirements_text,
        blueprint_metadata=bundle.blueprint.metadata.model_dump(mode="json"),
        schemas={schema_id: schema.model_dump(mode="json") for schema_id, schema in bundle.blueprint.schemas.items()},
        components={component_id: component.model_dump(mode="json") for component_id, component in bundle.blueprint.components.items()},
        bindings=[binding.model_dump(mode="json") for binding in bundle.blueprint.bindings],
        state_stores={store_id: store.model_dump(mode="json") for store_id, store in bundle.blueprint.state_stores.items()},
        packet_test_cases_by_component=packet_test_cases_by_component,
        repair_guidance=[],
    )

    system_message = next(message["content"] for message in messages if message["role"] == "system")
    assert "wrap the whole expression in parentheses" in system_message
    assert "never break after `and` / `or` without explicit continuation" in system_message
    assert "do not annotate `build_component()` with `GeneratedComponent`" in system_message


def test_benchmark_repair_guidance_excludes_dynamic_generated_at_from_diff() -> None:
    """Mismatch guidance should not flag generated_at as a value mismatch."""

    summary = _build_failure_summary(
        generation_error=None,
        packet_tests_passed=True,
        recomposition_passed=True,
        runtime_cases=[
            RuntimeCaseExecution(
                case_id="ORX-100",
                matched_expected=False,
                actual_outputs={
                    "resolution_digest_store": {
                        "generated_at": "2026-04-02T03:00:00Z",
                        "entries": [],
                    }
                },
                expected_outputs={
                    "resolution_digest_store": {
                        "generated_at": "2026-04-01T09:00:00Z",
                        "entries": [],
                    }
                },
                error=None,
            )
        ],
        semantic_review=None,
        dynamic_output_fields=["resolution_digest_store.generated_at"],
    )

    # generated_at must not appear as a mismatch in repair guidance
    assert not any("generated_at" in line for line in summary)

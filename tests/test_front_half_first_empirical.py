"""Tests for the front-half-first empirical smoke runner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ac14.front_half_first_empirical import (
    FrontHalfFirstConditionAttemptReport,
    FrontHalfFirstConditionTrialReport,
    FrontHalfFirstFailureClassification,
    FrontHalfFirstPairedTrialReport,
    build_front_half_first_smoke_readiness_artifact,
    infer_runtime_contract_from_structured_spec,
    load_monolithic_runtime_system,
    run_front_half_first_smoke_gate,
)
from ac14.empirical_comparison import CostObservation
from ac14.loader import load_blueprint_dir
from ac14.structured_spec import build_structured_spec_artifact, load_structured_spec_document
from tests.front_half_first_fixtures import (
    write_acceptance_review_fixture,
    write_freeze_semantic_review_fixture,
    write_front_half_first_benchmark_bundle,
    write_front_half_first_llm_codegen_fixture,
    write_front_half_first_monolithic_fixture,
    write_front_half_first_plan_fixture,
    write_front_half_first_structured_spec_front_half_fixture,
    write_front_half_review_fixture,
)


def test_build_front_half_first_smoke_readiness_artifact_blocks_on_front_half() -> None:
    """Smoke readiness should stay closed when AC14 never earns front-half approval."""

    report = FrontHalfFirstPairedTrialReport(
        benchmark_id="mini_scaling_structured_spec_v1",
        trial_id=1,
        monolithic=_condition_report("monolithic", passed=True, front_half_passed=None, category="success"),
        ac14=_condition_report("ac14", passed=False, front_half_passed=False, category="front_half"),
    )

    artifact = build_front_half_first_smoke_readiness_artifact(
        benchmark_id="mini_scaling_structured_spec_v1",
        paired_trial_report=report,
        trial_report_path="/tmp/front_half_trial.json",
    )

    assert artifact.verdict == "blocked_on_front_half"
    assert artifact.ac14_front_half_success is False
    assert artifact.runtime_hard_harness_success is True


def test_build_front_half_first_smoke_readiness_artifact_ready_for_full_trials() -> None:
    """Smoke readiness should open once AC14 front-half succeeds and one runtime pass exists."""

    report = FrontHalfFirstPairedTrialReport(
        benchmark_id="mini_scaling_structured_spec_v1",
        trial_id=1,
        monolithic=_condition_report("monolithic", passed=True, front_half_passed=None, category="success"),
        ac14=_condition_report("ac14", passed=False, front_half_passed=True, category="runtime_outputs"),
    )

    artifact = build_front_half_first_smoke_readiness_artifact(
        benchmark_id="mini_scaling_structured_spec_v1",
        paired_trial_report=report,
        trial_report_path="/tmp/front_half_trial.json",
    )

    assert artifact.verdict == "ready_for_full_trials"
    assert artifact.ac14_front_half_success is True
    assert artifact.runtime_hard_harness_success is True


def test_load_monolithic_runtime_system_requires_build_system(tmp_path: Path) -> None:
    """Monolithic runtime modules should fail loud when build_system is absent."""

    module_path = tmp_path / "broken_runtime.py"
    module_path.write_text("def not_build_system():\n    return object()\n")

    with pytest.raises(ValueError, match="build_system"):
        load_monolithic_runtime_system(module_path)


def test_infer_runtime_contract_from_generated_bundle(tmp_path: Path) -> None:
    """Runtime contract inference should find the source and final component from the authored bundle."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    source_path = benchmark_dir / "structured_spec_input.yaml"
    from ac14.front_half_acceptance import build_structured_spec_front_half_acceptance_report

    build_structured_spec_artifact(source_path, tmp_path / "structured_spec")
    monkey_env = {
        "AC14_BLUEPRINT_PLAN_FIXTURE": str(write_front_half_first_plan_fixture(tmp_path / "plan_fixture.json")),
        "AC14_FRONT_HALF_ACCEPTANCE_FIXTURE": str(write_front_half_review_fixture(tmp_path / "review_fixture.json")),
        "AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE": str(
            write_freeze_semantic_review_fixture(tmp_path / "freeze_review_fixture.json"),
        ),
    }
    with pytest.MonkeyPatch.context() as monkeypatch:
        for key, value in monkey_env.items():
            monkeypatch.setenv(key, value)
        artifact = build_structured_spec_front_half_acceptance_report(
            tmp_path / "structured_spec" / "structured_spec_artifact.json",
            tmp_path / "front_half",
        )
    blueprint = load_blueprint_dir(Path(artifact.artifact_paths.draft_bundle_dir))
    contract = infer_runtime_contract_from_structured_spec(
        blueprint=blueprint,
        structured_spec=load_structured_spec_document(source_path),
    )
    assert contract.source_component_id == "decision_engine"
    assert contract.final_component_id == "decision_engine"
    assert contract.final_output_ports == ["scaling_decision_entry", "scaling_decision_store"]


def test_run_front_half_first_smoke_gate_persists_ready_artifact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The runner should persist a ready artifact on the minimal structured-spec benchmark."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    monkeypatch.setenv(
        "AC14_STRUCTURED_SPEC_FRONT_HALF_ACCEPTANCE_FIXTURE",
        str(
            write_front_half_first_structured_spec_front_half_fixture(
                tmp_path / "structured_spec_front_half_fixture.json",
                benchmark_dir=benchmark_dir,
                plan_fixture_path=write_front_half_first_plan_fixture(tmp_path / "plan_fixture.json"),
            ),
        ),
    )
    monkeypatch.setenv(
        "AC14_LLM_CODEGEN_FIXTURE",
        str(write_front_half_first_llm_codegen_fixture(tmp_path / "llm_codegen_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FRONT_HALF_FIRST_MONOLITHIC_FIXTURE",
        str(write_front_half_first_monolithic_fixture(tmp_path / "monolithic_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_ACCEPTANCE_REVIEW_FIXTURE",
        str(write_acceptance_review_fixture(tmp_path / "acceptance_review_fixture.json")),
    )
    monkeypatch.setenv("AC14_LLM_OBSERVABILITY_DB", str(tmp_path / "missing_observability.db"))

    artifact = run_front_half_first_smoke_gate(
        benchmark_dir,
        tmp_path / "front_half_first_smoke",
        max_attempts=1,
    )

    assert artifact.verdict == "ready_for_full_trials"
    persisted = json.loads((tmp_path / "front_half_first_smoke" / "smoke_readiness_report.json").read_text())
    assert persisted["verdict"] == "ready_for_full_trials"
    assert persisted["ac14_front_half_success"] is True
    assert (tmp_path / "front_half_first_smoke" / "trial_1" / "paired_trial_report.json").exists()


def _condition_report(
    condition: str,
    *,
    passed: bool,
    front_half_passed: bool | None,
    category: str,
) -> FrontHalfFirstConditionTrialReport:
    """Build one minimal condition report for smoke-readiness tests."""

    attempt = FrontHalfFirstConditionAttemptReport(
        attempt_id=1,
        artifact_dir=f"/tmp/{condition}",
        duration_s=0.1,
        llm_cost=CostObservation(status="no_rows"),
        front_half_report_path=None,
        front_half_passed=front_half_passed,
        runtime_contract=None,
        packet_tests_passed=None,
        recomposition_passed=None,
        packet_test_report_path=None,
        recomposition_report_path=None,
        runtime_outputs_passed=passed,
        semantic_review=None,
        semantic_review_passed=passed,
        failure_classification=FrontHalfFirstFailureClassification(category=category, detail=category),  # type: ignore[arg-type]
        generation_error=None,
        runtime_cases=[],
        failure_summary=[],
        passed=passed,
    )
    return FrontHalfFirstConditionTrialReport(
        condition=condition,  # type: ignore[arg-type]
        passed=passed,
        attempts_used=1,
        repair_loops_used=0,
        attempts=[attempt],
    )

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
    FrontHalfRuntimeContract,
    _prepare_generated_runtime_execution,
    build_front_half_first_smoke_readiness_artifact,
    generate_monolithic_runtime_system_with_llm,
    infer_runtime_contract_from_structured_spec,
    load_monolithic_runtime_system,
    run_front_half_first_smoke_gate,
)
from ac14.empirical_comparison import CostObservation
from ac14.draft_authoring import materialize_draft_blueprint_bundle
from ac14.loader import load_blueprint_dir
from ac14.runtime import RuntimeComponent
from ac14.structured_spec import build_structured_spec_artifact, load_structured_spec_document
from ac14.structured_spec_benchmark import load_structured_spec_benchmark_bundle
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


def test_build_front_half_first_smoke_readiness_artifact_blocks_on_runtime_outputs() -> None:
    """Smoke readiness should surface runtime-output failures separately once both sides reach runtime."""

    monolithic = _condition_report(
        "monolithic",
        passed=False,
        front_half_passed=None,
        category="runtime_outputs",
    )
    ac14 = _condition_report(
        "ac14",
        passed=False,
        front_half_passed=True,
        category="runtime_outputs",
    )
    ac14.attempts[0].packet_tests_passed = False
    ac14.attempts[0].recomposition_passed = False
    ac14.attempts[0].failure_classification.detail = "RSC-100 outputs mismatched expected outputs"
    monolithic.attempts[0].failure_classification.detail = (
        "RSC-100 outputs mismatched expected outputs"
    )

    artifact = build_front_half_first_smoke_readiness_artifact(
        benchmark_id="mini_scaling_structured_spec_v1",
        paired_trial_report=FrontHalfFirstPairedTrialReport(
            benchmark_id="mini_scaling_structured_spec_v1",
            trial_id=1,
            monolithic=monolithic,
            ac14=ac14,
        ),
        trial_report_path="/tmp/front_half_trial.json",
    )

    assert artifact.verdict == "blocked_on_runtime_outputs"
    assert artifact.ac14_front_half_success is True
    assert artifact.runtime_hard_harness_success is False
    assert artifact.ac14_pre_runtime_proof_failed is True
    assert artifact.ac14_failure_details == ["RSC-100 outputs mismatched expected outputs"]
    assert artifact.monolithic_failure_details == ["RSC-100 outputs mismatched expected outputs"]


def test_build_front_half_first_smoke_readiness_artifact_detects_provider_noise_from_generation_error() -> None:
    """Front-half smoke readiness should block on infra when raw provider noise survives category drift."""

    monolithic = _condition_report(
        "monolithic",
        passed=False,
        front_half_passed=None,
        category="generation",
    )
    monolithic.attempts[0].generation_error = (
        'litellm.RateLimitError: GeminiException - {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED"}}'
    )
    monolithic.attempts[0].failure_summary = [monolithic.attempts[0].generation_error]

    artifact = build_front_half_first_smoke_readiness_artifact(
        benchmark_id="mini_scaling_structured_spec_v1",
        paired_trial_report=FrontHalfFirstPairedTrialReport(
            benchmark_id="mini_scaling_structured_spec_v1",
            trial_id=1,
            monolithic=monolithic,
            ac14=_condition_report(
                "ac14",
                passed=False,
                front_half_passed=False,
                category="generation",
            ),
        ),
        trial_report_path="/tmp/front_half_trial.json",
    )

    assert artifact.verdict == "blocked_on_infrastructure"
    assert artifact.infrastructure_failure_detected is True


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
    assert contract.source_mode == "input_port"
    assert contract.final_output_components == {
        "scaling_decision_entry": "decision_engine",
        "scaling_decision_store": "decision_engine",
    }
    assert contract.final_output_emitted_ports == {
        "scaling_decision_entry": "scaling_decision_entry",
        "scaling_decision_store": "scaling_decision_store",
    }


def test_infer_runtime_contract_accepts_unique_renamed_root_input_port(tmp_path: Path) -> None:
    """Runtime contract inference should tolerate one unique unbound root port with a renamed port name."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    source_path = benchmark_dir / "structured_spec_input.yaml"
    plan_path = write_front_half_first_plan_fixture(tmp_path / "plan_fixture.json")
    payload = json.loads(plan_path.read_text())
    payload["proposed_components"][0]["input_ports"][0]["port_name"] = "metrics_snapshot_in"
    plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_path,
        tmp_path / "draft_bundle",
    )
    blueprint = load_blueprint_dir(Path(manifest.draft_bundle_dir))
    contract = infer_runtime_contract_from_structured_spec(
        blueprint=blueprint,
        structured_spec=load_structured_spec_document(source_path),
    )

    assert contract.source_component_id == "decision_engine"
    assert contract.source_port_name == "metrics_snapshot_in"
    assert contract.source_mode == "input_port"
    assert contract.final_component_id == "decision_engine"
    assert contract.final_output_components == {
        "scaling_decision_entry": "decision_engine",
        "scaling_decision_store": "decision_engine",
    }
    assert contract.final_output_emitted_ports == {
        "scaling_decision_entry": "scaling_decision_entry",
        "scaling_decision_store": "scaling_decision_store",
    }


def test_infer_runtime_contract_supports_split_final_outputs(tmp_path: Path) -> None:
    """Runtime contract inference should support final outputs emitted by multiple components."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    source_path = benchmark_dir / "structured_spec_input.yaml"
    plan_path = write_front_half_first_plan_fixture(tmp_path / "plan_fixture.json")
    payload = json.loads(plan_path.read_text())
    payload["proposed_components"][0]["output_ports"] = [
        {
            "description": "Final single-case scaling decision.",
            "port_name": "scaling_decision_entry",
            "schema_name": "ScalingDecisionEntry",
        }
    ]
    payload["proposed_components"].append(
        {
            "component_id": "decision_store",
            "semantic_responsibility": "record_scaling_decision",
            "purpose": "Append the single-case decision into the rolling store.",
            "input_ports": [
                {
                    "port_name": "scaling_decision_entry",
                    "schema_name": "ScalingDecisionEntry",
                    "description": "Final single-case decision entry.",
                }
            ],
            "output_ports": [
                {
                    "port_name": "scaling_decision_store",
                    "schema_name": "ScalingDecisionStore",
                    "description": "Rolling scaling decision store.",
                }
            ],
            "packet_focus": ["preserve ordered decision history"],
            "dependency_notes": [],
        }
    )
    payload["proposed_bindings"] = [
        {
            "from_component": "decision_engine",
            "from_port": "scaling_decision_entry",
            "rationale": "The recorder consumes the emitted single-case decision entry.",
            "to_component": "decision_store",
            "to_port": "scaling_decision_entry",
        }
    ]
    plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_path,
        tmp_path / "draft_bundle",
    )
    blueprint = load_blueprint_dir(Path(manifest.draft_bundle_dir))
    contract = infer_runtime_contract_from_structured_spec(
        blueprint=blueprint,
        structured_spec=load_structured_spec_document(source_path),
    )

    assert contract.source_component_id == "decision_engine"
    assert contract.source_mode == "input_port"
    assert contract.final_component_id is None
    assert contract.final_output_components == {
        "scaling_decision_entry": "decision_engine",
        "scaling_decision_store": "decision_store",
    }
    assert contract.final_output_emitted_ports == {
        "scaling_decision_entry": "scaling_decision_entry",
        "scaling_decision_store": "scaling_decision_store",
    }


def test_infer_runtime_contract_supports_renamed_final_output_ports(tmp_path: Path) -> None:
    """Runtime contract inference should bind final outputs by schema-id fidelity when ports are renamed."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    source_path = benchmark_dir / "structured_spec_input.yaml"
    plan_path = write_front_half_first_plan_fixture(tmp_path / "plan_fixture.json")
    payload = json.loads(plan_path.read_text())
    payload["proposed_components"][0]["output_ports"] = [
        {
            "port_name": "final_decision_out",
            "schema_name": "ScalingDecisionEntry",
            "description": "Final single-case decision emitted under a renamed port.",
        },
        {
            "port_name": "store_snapshot_out",
            "schema_name": "ScalingDecisionStore",
            "description": "Rolling decision store emitted under a renamed port.",
        },
    ]
    plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_path,
        tmp_path / "draft_bundle",
    )
    blueprint = load_blueprint_dir(Path(manifest.draft_bundle_dir))
    contract = infer_runtime_contract_from_structured_spec(
        blueprint=blueprint,
        structured_spec=load_structured_spec_document(source_path),
    )

    assert contract.final_component_id == "decision_engine"
    assert contract.final_output_components == {
        "scaling_decision_entry": "decision_engine",
        "scaling_decision_store": "decision_engine",
    }
    assert contract.final_output_emitted_ports == {
        "scaling_decision_entry": "final_decision_out",
        "scaling_decision_store": "store_snapshot_out",
    }


def test_infer_runtime_contract_prefers_non_source_candidate_for_final_store(
    tmp_path: Path,
) -> None:
    """Runtime contract inference should prefer non-source final outputs over source snapshots."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    source_path = benchmark_dir / "structured_spec_input.yaml"
    plan_path = write_front_half_first_plan_fixture(tmp_path / "plan_fixture.json")
    payload = json.loads(plan_path.read_text())
    payload["proposed_components"][0]["output_ports"] = [
        {
            "port_name": "scaling_decision_entry",
            "schema_name": "ScalingDecisionEntry",
            "description": "Final single-case scaling decision.",
        }
    ]
    payload["proposed_components"].append(
        {
            "component_id": "prior_store_provider",
            "semantic_responsibility": "provide_prior_store",
            "purpose": "Provide the rolling store snapshot explicitly.",
            "kind": "source",
            "input_ports": [],
            "output_ports": [
                {
                    "port_name": "prior_store",
                    "schema_name": "ScalingDecisionStore",
                    "description": "Prior rolling store snapshot.",
                }
            ],
            "packet_focus": ["preserve prior rolling store exactly"],
            "dependency_notes": [],
        }
    )
    payload["proposed_components"].append(
        {
            "component_id": "decision_store",
            "semantic_responsibility": "record_scaling_decision",
            "purpose": "Append the current decision to the rolling store.",
            "input_ports": [
                {
                    "port_name": "decision_in",
                    "schema_name": "ScalingDecisionEntry",
                    "description": "Final single-case decision entry.",
                },
                {
                    "port_name": "prior_store",
                    "schema_name": "ScalingDecisionStore",
                    "description": "Prior rolling store snapshot.",
                },
            ],
            "output_ports": [
                {
                    "port_name": "updated_store",
                    "schema_name": "ScalingDecisionStore",
                    "description": "Updated rolling scaling store snapshot.",
                }
            ],
            "packet_focus": ["preserve ordered decision history"],
            "dependency_notes": [],
        }
    )
    payload["proposed_bindings"] = [
        {
            "from_component": "decision_engine",
            "from_port": "scaling_decision_entry",
            "rationale": "The recorder consumes the emitted single-case decision entry.",
            "to_component": "decision_store",
            "to_port": "decision_in",
        },
        {
            "from_component": "prior_store_provider",
            "from_port": "prior_store",
            "rationale": "The recorder consumes the prior rolling store explicitly.",
            "to_component": "decision_store",
            "to_port": "prior_store",
        },
    ]
    plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_path,
        tmp_path / "draft_bundle",
    )
    blueprint = load_blueprint_dir(Path(manifest.draft_bundle_dir))
    contract = infer_runtime_contract_from_structured_spec(
        blueprint=blueprint,
        structured_spec=load_structured_spec_document(source_path),
    )

    assert contract.final_output_components == {
        "scaling_decision_entry": "decision_engine",
        "scaling_decision_store": "decision_store",
    }
    assert contract.final_output_emitted_ports == {
        "scaling_decision_entry": "scaling_decision_entry",
        "scaling_decision_store": "updated_store",
    }


def test_infer_runtime_contract_prefers_leaf_candidate_for_duplicate_final_entry(
    tmp_path: Path,
) -> None:
    """Runtime contract inference should prefer the unique leaf final-entry output."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    source_path = benchmark_dir / "structured_spec_input.yaml"
    plan_path = write_front_half_first_plan_fixture(tmp_path / "plan_fixture.json")
    payload = json.loads(plan_path.read_text())
    payload["proposed_components"] = [
        {
            "component_id": "decision_engine",
            "semantic_responsibility": "emit_preliminary_scaling_decision",
            "purpose": "Emit the intermediate final decision before recording it.",
            "input_ports": [
                {
                    "port_name": "metrics_snapshot",
                    "schema_name": "MetricsSnapshot",
                    "description": "Incoming metrics snapshot.",
                }
            ],
            "output_ports": [
                {
                    "port_name": "final_decision",
                    "schema_name": "ScalingDecisionEntry",
                    "description": "Intermediate scaling decision entry.",
                }
            ],
            "packet_focus": ["keep threshold logic explicit"],
            "dependency_notes": [],
        },
        {
            "component_id": "decision_recorder",
            "semantic_responsibility": "record_scaling_decision",
            "purpose": "Emit the leaf final decision output and rolling store snapshot.",
            "input_ports": [
                {
                    "port_name": "decision_in",
                    "schema_name": "ScalingDecisionEntry",
                    "description": "Intermediate decision entry to record.",
                }
            ],
            "output_ports": [
                {
                    "port_name": "scaling_decision_entry_out",
                    "schema_name": "ScalingDecisionEntry",
                    "description": "Leaf final decision entry for system outputs.",
                },
                {
                    "port_name": "scaling_decision_store",
                    "schema_name": "ScalingDecisionStore",
                    "description": "Leaf rolling scaling decision store output.",
                },
            ],
            "packet_focus": ["preserve final decision and rolling store outputs"],
            "dependency_notes": [],
        },
    ]
    payload["proposed_bindings"] = [
        {
            "from_component": "decision_engine",
            "from_port": "final_decision",
            "rationale": "Recorder consumes the intermediate decision and emits the leaf final outputs.",
            "to_component": "decision_recorder",
            "to_port": "decision_in",
        }
    ]
    plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_path,
        tmp_path / "draft_bundle",
    )
    blueprint = load_blueprint_dir(Path(manifest.draft_bundle_dir))
    contract = infer_runtime_contract_from_structured_spec(
        blueprint=blueprint,
        structured_spec=load_structured_spec_document(source_path),
    )

    assert contract.final_component_id == "decision_recorder"
    assert contract.final_output_components == {
        "scaling_decision_entry": "decision_recorder",
        "scaling_decision_store": "decision_recorder",
    }
    assert contract.final_output_emitted_ports == {
        "scaling_decision_entry": "scaling_decision_entry_out",
        "scaling_decision_store": "scaling_decision_store",
    }


def test_infer_runtime_contract_rejects_extra_required_unbound_inputs(tmp_path: Path) -> None:
    """Runtime contract inference should fail loud on extra required unbound inputs."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    source_path = benchmark_dir / "structured_spec_input.yaml"
    plan_path = write_front_half_first_plan_fixture(tmp_path / "plan_fixture.json")
    payload = json.loads(plan_path.read_text())
    payload["proposed_components"][0]["input_ports"].append(
        {
            "port_name": "previous_store",
            "schema_name": "ScalingDecisionStore",
            "description": "Unexpected extra required store input.",
        }
    )
    plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_path,
        tmp_path / "draft_bundle",
    )
    blueprint = load_blueprint_dir(Path(manifest.draft_bundle_dir))

    with pytest.raises(ValueError, match="extra required unbound inputs"):
        infer_runtime_contract_from_structured_spec(
            blueprint=blueprint,
            structured_spec=load_structured_spec_document(source_path),
        )


def test_infer_runtime_contract_supports_zero_input_source_component(tmp_path: Path) -> None:
    """Runtime contract inference should support one unique zero-input source component."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    source_path = benchmark_dir / "structured_spec_input.yaml"
    plan_path = write_front_half_first_plan_fixture(tmp_path / "plan_fixture.json")
    payload = json.loads(plan_path.read_text())
    payload["proposed_components"] = [
        {
            "component_id": "metrics_source",
            "semantic_responsibility": "ingest_metrics_snapshot",
            "purpose": "Represent the top-level structured-spec input as one source node.",
            "kind": "source",
            "input_ports": [],
            "output_ports": [
                {
                    "port_name": "metrics_out",
                    "schema_name": "MetricsSnapshot",
                    "description": "Raw metrics snapshot emitted from the top-level source.",
                }
            ],
            "packet_focus": ["preserve the top-level input contract exactly"],
            "dependency_notes": [],
        },
        {
            "component_id": "decision_engine",
            "semantic_responsibility": "compute_scaling_decision",
            "purpose": "Turn one metrics snapshot into final benchmark outputs.",
            "input_ports": [
                {
                    "port_name": "metrics_snapshot",
                    "schema_name": "MetricsSnapshot",
                    "description": "Incoming metrics snapshot.",
                }
            ],
            "output_ports": [
                {
                    "port_name": "scaling_decision_entry",
                    "schema_name": "ScalingDecisionEntry",
                    "description": "Final single-case decision.",
                },
                {
                    "port_name": "scaling_decision_store",
                    "schema_name": "ScalingDecisionStore",
                    "description": "Rolling decision store.",
                },
            ],
            "packet_focus": ["preserve the benchmark output contract"],
            "dependency_notes": [],
        },
    ]
    payload["proposed_bindings"] = [
        {
            "from_component": "metrics_source",
            "from_port": "metrics_out",
            "rationale": "The decision engine consumes the emitted raw metrics snapshot.",
            "to_component": "decision_engine",
            "to_port": "metrics_snapshot",
        }
    ]
    plan_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_path,
        tmp_path / "draft_bundle",
    )
    blueprint = load_blueprint_dir(Path(manifest.draft_bundle_dir))
    contract = infer_runtime_contract_from_structured_spec(
        blueprint=blueprint,
        structured_spec=load_structured_spec_document(source_path),
    )

    assert contract.source_component_id == "metrics_source"
    assert contract.source_port_name == "metrics_out"
    assert contract.source_mode == "source_output"
    assert contract.final_component_id == "decision_engine"
    assert contract.final_output_components == {
        "scaling_decision_entry": "decision_engine",
        "scaling_decision_store": "decision_engine",
    }
    assert contract.final_output_emitted_ports == {
        "scaling_decision_entry": "scaling_decision_entry",
        "scaling_decision_store": "scaling_decision_store",
    }


class _DummyRuntimeComponent:
    """Minimal runtime component for source-injection tests."""

    def execute(self, inputs: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
        return {}


def test_prepare_generated_runtime_execution_supports_source_output_mode() -> None:
    """Runtime execution prep should wrap one zero-input source component with injected payload."""

    source_impl: RuntimeComponent = _DummyRuntimeComponent()
    decision_impl: RuntimeComponent = _DummyRuntimeComponent()
    base_implementations = {
        "metrics_source": source_impl,
        "decision_engine": decision_impl,
    }
    contract = FrontHalfRuntimeContract(
        source_component_id="metrics_source",
        source_port_name="metrics_out",
        source_mode="source_output",
        final_component_id="decision_engine",
        final_output_ports=["scaling_decision_entry"],
        final_output_components={"scaling_decision_entry": "decision_engine"},
        final_output_emitted_ports={"scaling_decision_entry": "decision_out"},
    )

    implementations, initial_inputs = _prepare_generated_runtime_execution(
        base_implementations=base_implementations,
        runtime_contract=contract,
        record={"case_id": "RSC-100", "service_id": "svc-premium-api"},
    )

    assert initial_inputs == {}
    assert implementations["decision_engine"] is decision_impl
    assert implementations["metrics_source"] is not source_impl
    assert implementations["metrics_source"].execute({}) == {
        "metrics_out": {"case_id": "RSC-100", "service_id": "svc-premium-api"}
    }


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
    assert (tmp_path / "front_half_first_smoke" / "trial_1" / "ac14" / "attempt_1" / "failure_classification.json").exists()
    assert (tmp_path / "front_half_first_smoke" / "trial_1" / "monolithic" / "attempt_1" / "failure_classification.json").exists()


def test_generate_monolithic_runtime_system_persists_failed_source_for_nested_input_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Monolithic front-half-first generation should fail loud and persist source for nested-record contracts."""

    benchmark_dir = write_front_half_first_benchmark_bundle(tmp_path)
    structured_bundle = load_structured_spec_benchmark_bundle(benchmark_dir)
    from ac14.empirical_comparison import load_benchmark_bundle

    reference_bundle = load_benchmark_bundle(structured_bundle.reference_benchmark_dir)
    fixture_path = tmp_path / "invalid_monolithic_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "module_code": "\n".join(
                    [
                        '"""Invalid monolithic runtime for contract testing."""',
                        "",
                        "class RuntimeSystem:",
                        "    def run_case(self, record):",
                        "        if 'metrics_snapshot' not in record:",
                        "            raise ValueError(\"nested input required\")",
                        "        payload = record['metrics_snapshot']",
                        "        return {'scaling_decision_entry': payload}",
                        "",
                        "def build_system():",
                        "    return RuntimeSystem()",
                        "",
                    ]
                ),
                "implementation_notes": ["intentionally invalid raw-record contract"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    monkeypatch.setenv("AC14_FRONT_HALF_FIRST_MONOLITHIC_FIXTURE", str(fixture_path))

    with pytest.raises(ValueError, match="raw benchmark record directly"):
        generate_monolithic_runtime_system_with_llm(
            structured_bundle=structured_bundle,
            reference_bundle=reference_bundle,
            output_dir=tmp_path / "generated",
            model="gpt-5-mini",
            trace_id="test/front_half_first/monolithic_contract",
            max_budget=0.1,
            repair_guidance=[],
        )

    failed_path = tmp_path / "generated" / "monolithic_runtime.failed.py"
    metadata_path = tmp_path / "generated" / "monolithic_runtime.validation_error.json"
    response_path = tmp_path / "generated" / "monolithic_response.json"
    assert failed_path.exists()
    assert metadata_path.exists()
    assert response_path.exists()
    assert "record['metrics_snapshot']" in failed_path.read_text()
    metadata = json.loads(metadata_path.read_text())
    assert metadata["persisted_failed_module_source"] is True
    assert "raw benchmark record directly" in metadata["error"]


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

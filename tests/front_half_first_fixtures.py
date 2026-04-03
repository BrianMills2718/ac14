"""Shared fixture helpers for the front-half-first empirical smoke tests."""

from __future__ import annotations

import json
from pathlib import Path

from ac14.draft_authoring import materialize_draft_blueprint_bundle
from ac14.front_half_acceptance import FrontHalfReviewResponse, StructuredSpecFrontHalfAcceptanceArtifact, StructuredSpecFrontHalfArtifactPaths
from ac14.structured_spec import build_structured_spec_artifact


def write_front_half_first_benchmark_bundle(root: Path) -> Path:
    """Persist a minimal structured-spec benchmark plus reference runtime assets."""

    structured_dir = root / "structured_benchmark"
    reference_dir = root / "reference_benchmark"
    blueprint_dir = reference_dir / "blueprint"
    structured_dir.mkdir(parents=True, exist_ok=True)
    blueprint_dir.mkdir(parents=True, exist_ok=True)

    _write_yaml(
        blueprint_dir / "metadata.yaml",
        "\n".join(
            [
                "metadata:",
                "  blueprint_id: mini_scaling_benchmark_v1",
                "  name: Mini Scaling Benchmark",
                "  version: 1.0.0",
                "  purpose: Emit one scaling decision from one metrics snapshot.",
                "  source_kind: benchmark_fixture",
                "  created_from: tests/front_half_first_fixtures.py",
                "compiler_profile:",
                "  target_backend: python",
                "  execution_model: latest_value_dag",
                "  component_model: typed_component_graph",
                "  validation_profile: code_component_v1",
                "generation_policy:",
                "  packet_test_mode: fixture_first",
                "  codegen_target: python",
            ],
        ),
    )
    _write_yaml(
        blueprint_dir / "schemas.yaml",
        "\n".join(
            [
                "schemas:",
                "  - schema_id: MetricsSnapshot",
                "    kind: object",
                "    description: One metrics snapshot.",
                "    fields:",
                "      - name: case_id",
                "        type: str",
                "        required: true",
                "        description: Stable case identifier.",
                "      - name: cpu_utilization",
                "        type: float",
                "        required: true",
                "        description: CPU utilization ratio.",
                "  - schema_id: ScalingDecisionEntry",
                "    kind: object",
                "    description: Final scaling decision.",
                "    fields:",
                "      - name: action",
                "        type: str",
                "        required: true",
                "        description: Final action.",
                "      - name: urgency",
                "        type: str",
                "        required: true",
                "        description: Final urgency.",
                "      - name: recommended_team",
                "        type: str",
                "        required: true",
                "        description: Final team routing.",
                "      - name: correlator",
                "        type: str",
                "        required: true",
                "        description: Dominant explanation category.",
                "      - name: case_id",
                "        type: str",
                "        required: true",
                "        description: Stable case identifier.",
                "  - schema_id: ScalingDecisionStore",
                "    kind: object",
                "    description: Rolling decision store.",
                "    fields:",
                "      - name: generated_at",
                "        type: str",
                "        required: true",
                "        description: Deterministic generated timestamp placeholder.",
                "      - name: decisions",
                "        type: list[ScalingDecisionEntry]",
                "        required: true",
                "        description: Ordered decision entries.",
            ],
        ),
    )
    _write_yaml(
        blueprint_dir / "components.yaml",
        "\n".join(
            [
                "components:",
                "  - component_id: decision_engine",
                "    kind: transform",
                "    purpose: Produce a scaling decision directly from the metrics snapshot.",
                "    semantic_responsibility: emit_scaling_decision",
                "    input_ports:",
                "      - name: metrics_snapshot",
                "        schema_id: MetricsSnapshot",
                "        description: Raw metrics snapshot.",
                "        required: true",
                "        arrival_policy: required_latest",
                "    output_ports:",
                "      - name: scaling_decision_entry",
                "        schema_id: ScalingDecisionEntry",
                "        description: Final single-case decision.",
                "      - name: scaling_decision_store",
                "        schema_id: ScalingDecisionStore",
                "        description: Rolling decision store.",
                "    local_invariants:",
                "      - Emit categorical outputs only.",
                "    failure_semantics:",
                "      - Fail loud on unsupported actions.",
                "    implementation_constraints:",
                "      - Keep state deterministic across cases.",
            ],
        ),
    )
    _write_yaml(blueprint_dir / "architecture.yaml", "bindings: []\nstate_stores: []\n")
    _write_yaml(
        blueprint_dir / "validation.yaml",
        "\n".join(
            [
                "evaluators:",
                "  - evaluator_id: requirements_acceptance",
                "    kind: llm_requirements_acceptance",
                "    description: Review final outputs against requirements.",
                "global_invariants: []",
                "scenarios:",
                "  - scenario_id: runtime_acceptance",
                "    kind: semantic_acceptance",
                "    description: Review final scaling outputs.",
                "    fixture_ids: []",
                "    evaluator_ids: [requirements_acceptance]",
                "    realistic_input: true",
                "    requirements:",
                "      - emit one scaling decision per case",
            ],
        ),
    )
    _write_yaml(blueprint_dir / "fixtures.yaml", "fixtures: []\n")

    (reference_dir / "requirements.md").write_text(
        "\n".join(
            [
                "# Mini Scaling Requirements",
                "",
                "1. Emit one scaling decision per metrics snapshot.",
                "2. Keep the final outputs categorical and deterministic.",
            ],
        ),
    )
    (reference_dir / "runtime_cases.json").write_text(
        json.dumps(
            [
                {"case_id": "MSC-100", "cpu_utilization": 0.91},
                {"case_id": "MSC-101", "cpu_utilization": 0.22},
            ],
            indent=2,
            sort_keys=True,
        ),
    )
    (reference_dir / "expected_outputs.json").write_text(
        json.dumps(
            [
                {
                    "case_id": "MSC-100",
                    "expected_outputs": {
                        "scaling_decision_entry": {
                            "action": "scale_up",
                            "urgency": "high",
                            "recommended_team": "platform",
                            "correlator": "cpu_threshold",
                            "case_id": "MSC-100",
                        },
                        "scaling_decision_store": {
                            "generated_at": "runtime",
                            "decisions": [
                                {
                                    "action": "scale_up",
                                    "urgency": "high",
                                    "recommended_team": "platform",
                                    "correlator": "cpu_threshold",
                                    "case_id": "MSC-100",
                                }
                            ],
                        },
                    },
                },
                {
                    "case_id": "MSC-101",
                    "expected_outputs": {
                        "scaling_decision_entry": {
                            "action": "none",
                            "urgency": "low",
                            "recommended_team": "platform",
                            "correlator": "steady_state",
                            "case_id": "MSC-101",
                        },
                        "scaling_decision_store": {
                            "generated_at": "runtime",
                            "decisions": [
                                {
                                    "action": "scale_up",
                                    "urgency": "high",
                                    "recommended_team": "platform",
                                    "correlator": "cpu_threshold",
                                    "case_id": "MSC-100",
                                },
                                {
                                    "action": "none",
                                    "urgency": "low",
                                    "recommended_team": "platform",
                                    "correlator": "steady_state",
                                    "case_id": "MSC-101",
                                },
                            ],
                        },
                    },
                },
            ],
            indent=2,
            sort_keys=True,
        ),
    )
    _write_yaml(
        reference_dir / "benchmark.yaml",
        "\n".join(
            [
                "benchmark:",
                "  benchmark_id: mini_scaling_reference_v1",
                "  name: Mini Scaling Reference Benchmark",
                "  purpose: Reference runtime benchmark for front-half-first tests.",
                "  comparison_scope: front_half_first_test_reference",
                "  blueprint_dir: blueprint",
                "  requirements_path: requirements.md",
                "  runtime_input_path: runtime_cases.json",
                "  expected_outputs_path: expected_outputs.json",
                "  source_artifacts: [runtime_cases.json, requirements.md]",
                "  allowed_dependencies: []",
                "  primary_source_component_id: decision_engine",
                "  primary_source_port_name: metrics_snapshot",
                "  final_component_id: decision_engine",
                "  final_output_ports: [scaling_decision_entry, scaling_decision_store]",
                "  system_requirements:",
                "    - emit one scaling decision per case",
                "    - keep outputs categorical and deterministic",
                "  dynamic_output_fields: [scaling_decision_store.generated_at]",
                "  semantic_review_policy: advisory_on_exact_match",
            ],
        ),
    )

    (structured_dir / "requirements.md").write_text(
        "\n".join(
            [
                "# Mini Structured-Spec Requirements",
                "",
                "1. Emit one scaling decision per metrics snapshot.",
                "2. Preserve a rolling decision store.",
            ],
        ),
    )
    _write_yaml(
        structured_dir / "structured_spec_input.yaml",
        "\n".join(
            [
                "system_name: Mini Scaling Contract",
                "purpose: Decide whether one service should scale for each metrics snapshot.",
                "requirements:",
                "  - emit one scaling decision per metrics snapshot",
                "  - preserve a deterministic rolling decision store",
                "success_criteria:",
                "  - final outputs remain categorical and deterministic",
                "inputs:",
                "  - name: metrics_snapshot",
                "    kind: record",
                "    description: One metrics snapshot.",
                "    fields:",
                "      - field_name: case_id",
                "        field_type: str",
                "        description: Stable case identifier.",
                "        required: true",
                "      - field_name: cpu_utilization",
                "        field_type: float",
                "        description: CPU utilization ratio.",
                "        required: true",
                "outputs:",
                "  - name: scaling_decision_entry",
                "    kind: record",
                "    description: Final single-case scaling decision.",
                "    fields:",
                "      - field_name: action",
                "        field_type: str",
                "        description: Final action.",
                "        required: true",
                "  - name: scaling_decision_store",
                "    kind: record",
                "    description: Rolling decision store.",
                "    fields:",
                "      - field_name: decisions",
                "        field_type: list[record]",
                "        description: Ordered decisions.",
                "        required: true",
                "workflow_hints:",
                "  - hint_id: direct_decision",
                "    summary: Emit one direct scaling decision.",
                "    input_names: [metrics_snapshot]",
                "    output_names: [scaling_decision_entry, scaling_decision_store]",
                "    business_rules:",
                "      - cpu >= 0.80 means scale_up and high urgency",
                "      - otherwise action is none and urgency is low",
                "human_context_notes:",
                "  - Keep the graph reviewable and bounded.",
            ],
        ),
    )
    _write_yaml(
        structured_dir / "benchmark.yaml",
        "\n".join(
            [
                "benchmark:",
                "  benchmark_id: mini_scaling_structured_spec_v1",
                "  name: Mini Scaling Structured-Spec Bundle",
                "  purpose: Front-half-first smoke bundle for subprocess tests.",
                "  comparison_scope: front_half_first_structured_spec",
                "  structured_spec_path: structured_spec_input.yaml",
                "  requirements_path: requirements.md",
                "  reference_benchmark_dir: ../reference_benchmark",
                "  source_artifacts: [structured_spec_input.yaml, requirements.md]",
            ],
        ),
    )
    return structured_dir


def write_front_half_first_plan_fixture(path: Path) -> Path:
    """Persist a draft-plan fixture compatible with the mini structured-spec benchmark."""

    structured_spec_artifact_path = path.parent / "structured_spec" / "structured_spec_artifact.json"
    path.write_text(
        json.dumps(
            {
                "planning_input_kind": "structured_spec",
                "planning_input_name": "Mini Scaling Contract",
                "planning_input_artifact_path": str(structured_spec_artifact_path),
                "structured_spec_artifact_path": str(structured_spec_artifact_path),
                "requirements": [
                    "emit one scaling decision per metrics snapshot",
                    "preserve a deterministic rolling decision store",
                ],
                "planning_input_open_concerns": [],
                "discovery_open_concerns": [],
                "planning_summary": "Use one direct decision engine for the mini scaling contract.",
                "proposed_schemas": [
                    {
                        "schema_name": "MetricsSnapshot",
                        "kind": "record",
                        "description": "One metrics snapshot.",
                        "fields": [
                            {
                                "field_name": "case_id",
                                "field_type": "str",
                                "description": "Stable case identifier.",
                            },
                            {
                                "field_name": "cpu_utilization",
                                "field_type": "float",
                                "description": "CPU utilization ratio.",
                            },
                        ],
                    },
                    {
                        "schema_name": "ScalingDecisionEntry",
                        "kind": "record",
                        "description": "Final single-case decision.",
                        "fields": [
                            {
                                "field_name": "action",
                                "field_type": "str",
                                "description": "Final action.",
                            }
                        ],
                    },
                    {
                        "schema_name": "ScalingDecisionStore",
                        "kind": "record",
                        "description": "Rolling decision store.",
                        "fields": [
                            {
                                "field_name": "decisions",
                                "field_type": "list[record]",
                                "description": "Ordered decisions.",
                            }
                        ],
                    },
                ],
                "proposed_components": [
                    {
                        "component_id": "decision_engine",
                        "semantic_responsibility": "emit_scaling_decision",
                        "purpose": "Emit one direct scaling decision from the metrics snapshot.",
                        "input_ports": [
                            {
                                "port_name": "metrics_snapshot",
                                "schema_name": "MetricsSnapshot",
                                "description": "Raw metrics snapshot.",
                            }
                        ],
                        "output_ports": [
                            {
                                "port_name": "scaling_decision_entry",
                                "schema_name": "ScalingDecisionEntry",
                                "description": "Final single-case scaling decision.",
                            },
                            {
                                "port_name": "scaling_decision_store",
                                "schema_name": "ScalingDecisionStore",
                                "description": "Rolling scaling decision store.",
                            },
                        ],
                        "packet_focus": [
                            "keep threshold logic explicit",
                            "preserve rolling decision state",
                        ],
                        "dependency_notes": [],
                    }
                ],
                "proposed_bindings": [],
                "proposed_scenarios": [
                    {
                        "scenario_id": "runtime_acceptance",
                        "kind": "semantic_acceptance",
                        "description": "Review runtime outputs for the mini scaling cases.",
                        "requirement_focus": [
                            "emit one scaling decision per case",
                            "preserve a deterministic rolling decision store",
                        ],
                    }
                ],
                "packetization_notes": ["Keep the graph as one direct bounded decision engine for the smoke test."],
                "dependency_decisions": [],
                "open_questions": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return path


def write_front_half_first_llm_codegen_fixture(path: Path) -> Path:
    """Persist a flat AC14 LLM codegen fixture for the mini smoke benchmark."""

    path.write_text(
        json.dumps(
            {
                "decision_engine": {
                    "module_code": _decision_engine_module_code(),
                    "implementation_notes": ["fixture-backed front-half-first AC14 codegen"],
                }
            },
            indent=2,
            sort_keys=True,
        )
    )
    return path


def write_front_half_first_monolithic_fixture(path: Path) -> Path:
    """Persist a monolithic runtime fixture for the mini smoke benchmark."""

    path.write_text(
        json.dumps(
            {
                "module_code": _monolithic_runtime_module_code(),
                "implementation_notes": ["fixture-backed front-half-first monolithic runtime"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return path


def write_front_half_first_structured_spec_front_half_fixture(
    path: Path,
    *,
    benchmark_dir: Path,
    plan_fixture_path: Path,
) -> Path:
    """Persist an approved structured-spec front-half fixture backed by a real draft bundle."""

    structured_spec_source = benchmark_dir / "structured_spec_input.yaml"
    structured_spec_dir = path.parent / "structured_spec"
    build_structured_spec_artifact(structured_spec_source, structured_spec_dir)
    manifest = materialize_draft_blueprint_bundle(
        plan_fixture_path,
        path.parent / "draft_bundle",
    )
    artifact = StructuredSpecFrontHalfAcceptanceArtifact(
        structured_spec_artifact_path=str(structured_spec_dir / "structured_spec_artifact.json"),
        planning_input_name="Mini Scaling Contract",
        requirements=[
            "emit one scaling decision per metrics snapshot",
            "preserve a deterministic rolling decision store",
        ],
        artifact_paths=StructuredSpecFrontHalfArtifactPaths(
            structured_spec_artifact_path=str(structured_spec_dir / "structured_spec_artifact.json"),
            draft_blueprint_plan_path=str(plan_fixture_path),
            draft_bundle_dir=manifest.draft_bundle_dir,
            freeze_readiness_report_path=manifest.freeze_readiness_report_path,
            freeze_decision_path=str(path.parent / "freeze_decision.json"),
            freeze_semantic_review_path=None,
            retry_freeze_artifact_path=None,
        ),
        freeze_approved=True,
        final_freeze_approved=True,
        retry_freeze_attempted=False,
        retry_freeze_approved=None,
        blocking_finding_codes=[],
        review=FrontHalfReviewResponse(
            overall_verdict="accept",
            freeze_verdict="ready",
            summary="Fixture-backed front-half acceptance approved the structured spec path.",
            strengths=["bounded graph", "reviewable thresholds"],
            concerns=[],
            requirement_assessments=[],
            recommended_next_steps=[],
        ),
    )
    path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))
    return path


def write_acceptance_review_fixture(path: Path) -> Path:
    """Persist a deterministic acceptance review fixture."""

    path.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Fixture-backed review approved the outputs.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return path


def write_front_half_review_fixture(path: Path) -> Path:
    """Persist a deterministic front-half review fixture."""

    path.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "freeze_verdict": "ready",
                "summary": "Fixture-backed review approved the front half.",
                "strengths": ["bounded graph", "clear threshold logic"],
                "concerns": [],
                "requirement_assessments": [],
                "recommended_next_steps": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return path


def write_freeze_semantic_review_fixture(path: Path) -> Path:
    """Persist a deterministic freeze-semantic review fixture."""

    path.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "freeze_verdict": "ready",
                "summary": "Freeze semantic review approved the draft bundle.",
                "strengths": ["requirements preserved"],
                "concerns": [],
                "requirement_assessments": [],
                "recommended_next_steps": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return path


def _decision_engine_module_code() -> str:
    """Return deterministic AC14 component code for the mini smoke benchmark."""

    return "\n".join(
        [
            '"""Fixture-backed decision engine for front-half-first smoke tests."""',
            "",
            "class DecisionEngine:",
            "    def __init__(self):",
            "        self._decisions = []",
            "",
            "    def execute(self, inputs):",
            "        record = inputs['metrics_snapshot']",
            "        if record['cpu_utilization'] >= 0.80:",
            "            action = 'scale_up'",
            "            urgency = 'high'",
            "            correlator = 'cpu_threshold'",
            "        else:",
            "            action = 'none'",
            "            urgency = 'low'",
            "            correlator = 'steady_state'",
            "        entry = {",
            "            'action': action,",
            "            'urgency': urgency,",
            "            'recommended_team': 'platform',",
            "            'correlator': correlator,",
            "            'case_id': record['case_id'],",
            "        }",
            "        self._decisions.append(entry)",
            "        return {",
            "            'scaling_decision_entry': entry,",
            "            'scaling_decision_store': {",
            "                'generated_at': 'runtime',",
            "                'decisions': list(self._decisions),",
            "            },",
            "        }",
            "",
            "def build_component():",
            "    return DecisionEngine()",
            "",
        ],
    )


def _monolithic_runtime_module_code() -> str:
    """Return deterministic monolithic runtime code for the mini smoke benchmark."""

    return "\n".join(
        [
            '"""Fixture-backed monolithic runtime for front-half-first smoke tests."""',
            "",
            "class RuntimeSystem:",
            "    def __init__(self):",
            "        self._decisions = []",
            "",
            "    def run_case(self, record):",
            "        if record['cpu_utilization'] >= 0.80:",
            "            action = 'scale_up'",
            "            urgency = 'high'",
            "            correlator = 'cpu_threshold'",
            "        else:",
            "            action = 'none'",
            "            urgency = 'low'",
            "            correlator = 'steady_state'",
            "        entry = {",
            "            'action': action,",
            "            'urgency': urgency,",
            "            'recommended_team': 'platform',",
            "            'correlator': correlator,",
            "            'case_id': record['case_id'],",
            "        }",
            "        self._decisions.append(entry)",
            "        return {",
            "            'scaling_decision_entry': entry,",
            "            'scaling_decision_store': {",
            "                'generated_at': 'runtime',",
            "                'decisions': list(self._decisions),",
            "            },",
            "        }",
            "",
            "def build_system():",
            "    return RuntimeSystem()",
            "",
        ],
    )


def _write_yaml(path: Path, content: str) -> None:
    """Persist one YAML-like text file with a trailing newline."""

    path.write_text(content.rstrip() + "\n")

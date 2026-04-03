"""Tests for draft blueprint planning artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from ac14.blueprint_planning import (
    DraftBlueprintPlanArtifact,
    DraftBlueprintPlanResponse,
    PlannedBinding,
    PlannedComponent,
    PlannedPort,
    PlannedScenario,
    PlannedSchema,
    PlannedSchemaField,
    PlanningQuestion,
    build_draft_blueprint_plan,
    build_draft_blueprint_plan_from_structured_spec,
    build_refined_draft_blueprint_plan,
    RefinedDraftBlueprintPlanResponse,
)
from ac14.dependency_execution import (
    DependencyExecutionArtifact,
    DependencyExecutionResult,
    DependencyRemediationArtifact,
    DependencySnapshot,
)
from ac14.dependency_planning import (
    DependencyPlanningArtifact,
    DependencyQuestion,
    DependencyRecommendation,
    DependencyEvidence,
)
from ac14.discovery import build_discovery_artifact
from ac14.structured_spec import build_structured_spec_artifact


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_build_draft_blueprint_plan_persists_artifact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Draft blueprint planning should persist a validated planning artifact."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"ticket_id": "T-1", "body": "Login is broken"}]')
    build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
        requested_packages=["pydantic"],
    )
    discovery_artifact_path = tmp_path / "discovery" / "discovery_artifact.json"
    dependency_plan = DependencyPlanningArtifact(
        discovery_artifact_path=str(discovery_artifact_path),
        requirements=["reuse installed schema tooling"],
        carried_forward_concerns=[],
        planning_summary="Reuse pydantic for typed schema contracts.",
        recommendations=[
            DependencyRecommendation(
                package_name="pydantic",
                action="reuse",
                capability_need="typed schema contracts",
                justification="already installed and directly aligned with schema validation",
                already_installed=True,
                install_command=None,
                evidence=[
                    DependencyEvidence(
                        source="environment",
                        locator="pydantic",
                        detail="Installed in the environment inventory.",
                    ),
                ],
            ),
        ],
        standard_library_notes=[],
        open_questions=[
            DependencyQuestion(
                question="Is any additional serialization library needed beyond Pydantic plus stdlib?",
                why_it_matters="It changes dependency scope before freeze.",
            ),
        ],
    )
    dependency_plan_path = tmp_path / "dependency_plan.json"
    dependency_plan_path.write_text(
        dependency_plan.model_dump_json(indent=2),
    )

    fake_response = DraftBlueprintPlanResponse(
        planning_summary="Use a source parser and one sink to keep packets bounded.",
        proposed_schemas=[
            PlannedSchema(
                schema_name="RawTicket",
                kind="record",
                description="Normalized raw ticket shape.",
                fields=[
                    PlannedSchemaField(
                        field_name="ticket_id",
                        field_type="str",
                        description="Stable ticket identifier.",
                    ),
                ],
            ),
        ],
        proposed_components=[
            PlannedComponent(
                component_id="ticket_ingest",
                semantic_responsibility="ingest_ticket",
                purpose="Normalize the discovered ticket input into a source schema.",
                input_ports=[],
                output_ports=[
                    PlannedPort(
                        port_name="raw_ticket",
                        schema_name="RawTicket",
                        description="Normalized ticket payload.",
                    ),
                ],
                packet_focus=["normalize incoming fields", "preserve ticket identity"],
                dependency_notes=["no external libraries required"],
            ),
        ],
        proposed_bindings=[],
        proposed_scenarios=[
            PlannedScenario(
                scenario_id="happy_path",
                kind="semantic_acceptance",
                description="Review one realistic ticket end to end.",
                requirement_focus=["normalize ticket input", "preserve meaning"],
            ),
        ],
        packetization_notes=["Keep the source component packet focused on normalization only."],
        dependency_decisions=["Stay within the current environment for the first slice."],
        open_questions=[
            PlanningQuestion(
                question="Should ticket tags become an explicit field in RawTicket?",
                why_it_matters="It changes source schema shape before freeze.",
            ),
        ],
    )
    fake_call = AsyncMock(return_value=(fake_response, object()))
    monkeypatch.setattr("ac14.blueprint_planning.acall_llm_structured", fake_call)

    plan = build_draft_blueprint_plan(
        discovery_artifact_path=discovery_artifact_path,
        output_dir=tmp_path / "plan",
        requirements=["normalize discovered ticket input", "keep packets bounded"],
        dependency_plan_path=dependency_plan_path,
        max_budget=0.1,
    )

    assert plan.requirements == [
        "normalize discovered ticket input",
        "keep packets bounded",
    ]
    assert plan.dependency_plan_path == str(dependency_plan_path)
    assert plan.dependency_plan_summary == "Reuse pydantic for typed schema contracts."
    assert plan.dependency_recommendations == ["reuse pydantic: typed schema contracts"]
    assert plan.dependency_open_questions[0].question.startswith("Is any additional serialization")
    assert plan.proposed_components[0].component_id == "ticket_ingest"
    assert (tmp_path / "plan" / "draft_blueprint_plan.json").exists()
    assert fake_call.await_count == 1
    assert fake_call.await_args is not None
    kwargs = fake_call.await_args.kwargs
    assert kwargs["task"] == "ac14_draft_blueprint_plan"
    assert kwargs["max_budget"] == 0.1


def test_build_draft_blueprint_plan_carries_dependency_execution_artifact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Draft planning should carry confirmed and blocked dependency probe evidence forward."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"ticket_id": "T-1", "body": "Login is broken"}]')
    build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
        requested_packages=["pydantic"],
    )
    discovery_artifact_path = tmp_path / "discovery" / "discovery_artifact.json"
    dependency_plan = DependencyPlanningArtifact(
        discovery_artifact_path=str(discovery_artifact_path),
        requirements=["reuse installed schema tooling", "investigate rich rendering"],
        carried_forward_concerns=[],
        planning_summary="Reuse pydantic and investigate rich for later UI work.",
        recommendations=[
            DependencyRecommendation(
                package_name="pydantic",
                action="reuse",
                capability_need="typed schema contracts",
                justification="already installed and directly aligned with schema validation",
                already_installed=True,
                install_command=None,
                evidence=[
                    DependencyEvidence(
                        source="environment",
                        locator="pydantic",
                        detail="Installed in the environment inventory.",
                    ),
                ],
            ),
            DependencyRecommendation(
                package_name="rich",
                action="install",
                capability_need="terminal review surfaces",
                justification="would improve operator readability later",
                already_installed=False,
                install_command="python -m pip install rich",
                evidence=[],
            ),
        ],
        standard_library_notes=[],
        open_questions=[],
    )
    dependency_plan_path = tmp_path / "dependency_plan.json"
    dependency_plan_path.write_text(dependency_plan.model_dump_json(indent=2))
    dependency_execution = DependencyExecutionArtifact(
        dependency_plan_path=str(dependency_plan_path),
        execution_mode="check_only",
        planning_summary=dependency_plan.planning_summary,
        carried_forward_questions=[],
        results=[
            DependencyExecutionResult(
                package_name="pydantic",
                action="reuse",
                result="confirmed",
                summary="reuse probe confirmed the package is already available",
                mutation_permitted=False,
                mutation_attempted=False,
                attempted_command=None,
                command_exit_code=None,
                before=DependencySnapshot(
                    package_name="pydantic",
                    installed=True,
                    version="2.11.0",
                    top_level_modules=["pydantic"],
                    discoverable_modules=["pydantic"],
                ),
                after=DependencySnapshot(
                    package_name="pydantic",
                    installed=True,
                    version="2.11.0",
                    top_level_modules=["pydantic"],
                    discoverable_modules=["pydantic"],
                ),
                observations=["checked installed distribution state for pydantic"],
            ),
            DependencyExecutionResult(
                package_name="rich",
                action="install",
                result="blocked",
                summary="install probe blocked because environment mutation is disabled",
                mutation_permitted=False,
                mutation_attempted=False,
                attempted_command="python -m pip install rich",
                command_exit_code=None,
                before=DependencySnapshot(
                    package_name="rich",
                    installed=False,
                    version=None,
                    top_level_modules=[],
                    discoverable_modules=[],
                ),
                after=DependencySnapshot(
                    package_name="rich",
                    installed=False,
                    version=None,
                    top_level_modules=[],
                    discoverable_modules=[],
                ),
                observations=["install command was not executed because mutation is disabled"],
            ),
        ],
        environment_observations=["install mutation was disabled for this run"],
    )
    dependency_execution_path = tmp_path / "dependency_execution_artifact.json"
    dependency_execution_path.write_text(dependency_execution.model_dump_json(indent=2))

    fake_response = DraftBlueprintPlanResponse(
        planning_summary="Use a source parser and one sink to keep packets bounded.",
        proposed_schemas=[
            PlannedSchema(
                schema_name="RawTicket",
                kind="record",
                description="Normalized raw ticket shape.",
                fields=[
                    PlannedSchemaField(
                        field_name="ticket_id",
                        field_type="str",
                        description="Stable ticket identifier.",
                    ),
                ],
            ),
        ],
        proposed_components=[
            PlannedComponent(
                component_id="ticket_ingest",
                semantic_responsibility="ingest_ticket",
                purpose="Normalize the discovered ticket input into a source schema.",
                input_ports=[],
                output_ports=[
                    PlannedPort(
                        port_name="raw_ticket",
                        schema_name="RawTicket",
                        description="Normalized ticket payload.",
                    ),
                ],
                packet_focus=["normalize incoming fields", "preserve ticket identity"],
                dependency_notes=["reuse pydantic only in the first slice"],
            ),
        ],
        proposed_bindings=[],
        proposed_scenarios=[
            PlannedScenario(
                scenario_id="happy_path",
                kind="semantic_acceptance",
                description="Review one realistic ticket end to end.",
                requirement_focus=["normalize ticket input", "preserve meaning"],
            ),
        ],
        packetization_notes=["Keep the source component packet focused on normalization only."],
        dependency_decisions=["Reuse pydantic now; leave rich blocked until explicitly revisited."],
        open_questions=[],
    )
    fake_call = AsyncMock(return_value=(fake_response, object()))
    monkeypatch.setattr("ac14.blueprint_planning.acall_llm_structured", fake_call)

    plan = build_draft_blueprint_plan(
        discovery_artifact_path=discovery_artifact_path,
        output_dir=tmp_path / "plan",
        requirements=["normalize discovered ticket input", "keep packets bounded"],
        dependency_plan_path=dependency_plan_path,
        dependency_execution_artifact_path=dependency_execution_path,
        max_budget=0.1,
    )

    assert plan.dependency_execution_artifact_path == str(dependency_execution_path)
    assert plan.dependency_execution_summary == "check_only dependency probes: 1 confirmed, 1 blocked, 0 skipped"
    assert plan.confirmed_dependency_probes == [
        "reuse pydantic: reuse probe confirmed the package is already available",
    ]
    assert plan.blocked_dependency_probes == [
        "install rich: install probe blocked because environment mutation is disabled",
    ]


def test_build_draft_blueprint_plan_from_structured_spec_persists_artifact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Structured-spec draft planning should persist a validated planning artifact."""

    spec_path = tmp_path / "resource_scaling_spec.yaml"
    spec_path.write_text(
        "\n".join(
            [
                "system_name: Resource Scaling Contract",
                "purpose: Decide when infrastructure should scale.",
                "requirements:",
                "  - produce a scaling decision for each metrics snapshot",
                "inputs:",
                "  - name: metrics_snapshot",
                "    kind: record",
                "    description: Current utilization metrics.",
                "    fields:",
                "      - field_name: cpu_utilization",
                "        field_type: float",
                "        description: CPU utilization ratio.",
                "        required: true",
                "outputs:",
                "  - name: scaling_decision",
                "    kind: record",
                "    description: Final scaling decision.",
                "    fields:",
                "      - field_name: action",
                "        field_type: str",
                "        description: One scaling action label.",
                "        required: true",
                "workflow_hints:",
                "  - hint_id: evaluate_thresholds",
                "    summary: Evaluate metrics against rules.",
                "    input_names: [metrics_snapshot]",
                "    output_names: [scaling_decision]",
            ],
        ),
    )
    build_structured_spec_artifact(
        input_path=spec_path,
        output_dir=tmp_path / "structured_spec",
    )
    structured_spec_artifact_path = tmp_path / "structured_spec" / "structured_spec_artifact.json"

    fake_response = DraftBlueprintPlanResponse(
        planning_summary="Use one evaluator component and one sink.",
        proposed_schemas=[
            PlannedSchema(
                schema_name="ScalingDecision",
                kind="record",
                description="Final scale or no-scale decision.",
                fields=[
                    PlannedSchemaField(
                        field_name="action",
                        field_type="str",
                        description="One scaling action label.",
                    ),
                ],
            ),
        ],
        proposed_components=[
            PlannedComponent(
                component_id="recommendation_generator",
                semantic_responsibility="generate_scaling_recommendation",
                purpose="Turn metrics into one bounded scaling recommendation.",
                input_ports=[],
                output_ports=[
                    PlannedPort(
                        port_name="scaling_decision",
                        schema_name="ScalingDecision",
                        description="Final scaling recommendation.",
                    ),
                ],
                packet_focus=["keep threshold logic explicit", "carry rule salience forward"],
                dependency_notes=[],
            ),
        ],
        proposed_bindings=[],
        proposed_scenarios=[
            PlannedScenario(
                scenario_id="critical_breach",
                kind="semantic_acceptance",
                description="Review one critical CPU breach case end to end.",
                requirement_focus=["produce a scaling decision"],
            ),
        ],
        packetization_notes=["Keep the first draft graph minimal."],
        dependency_decisions=[],
        open_questions=[],
    )
    fake_call = AsyncMock(return_value=(fake_response, object()))
    monkeypatch.setattr("ac14.blueprint_planning.acall_llm_structured", fake_call)

    plan = build_draft_blueprint_plan_from_structured_spec(
        structured_spec_artifact_path=structured_spec_artifact_path,
        output_dir=tmp_path / "plan",
        max_budget=0.1,
    )

    assert plan.planning_input_kind == "structured_spec"
    assert plan.planning_input_name == "Resource Scaling Contract"
    assert plan.structured_spec_artifact_path == str(structured_spec_artifact_path)
    assert plan.planning_input_artifact_path == str(structured_spec_artifact_path)
    assert plan.requirements == ["produce a scaling decision for each metrics snapshot"]
    assert plan.proposed_components[0].component_id == "recommendation_generator"
    assert (tmp_path / "plan" / "draft_blueprint_plan.json").exists()
    assert fake_call.await_count == 1
    assert fake_call.await_args is not None
    kwargs = fake_call.await_args.kwargs
    assert kwargs["task"] == "ac14_draft_blueprint_plan_from_structured_spec"
    assert kwargs["max_budget"] == 0.1


def test_build_draft_blueprint_plan_from_structured_spec_retries_retryable_binding_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Structured-spec planning should retry once when the first plan only fails binding validation."""

    spec_path = tmp_path / "resource_scaling_spec.yaml"
    spec_path.write_text(
        "\n".join(
            [
                "system_name: Resource Scaling Contract",
                "purpose: Decide when infrastructure should scale.",
                "requirements:",
                "  - produce a scaling decision for each metrics snapshot",
                "inputs:",
                "  - name: metrics_snapshot",
                "    kind: record",
                "    description: Current utilization metrics.",
                "    fields:",
                "      - field_name: cpu_utilization",
                "        field_type: float",
                "        description: CPU utilization ratio.",
                "        required: true",
                "outputs:",
                "  - name: scaling_decision",
                "    kind: record",
                "    description: Final scaling decision.",
                "    fields:",
                "      - field_name: action",
                "        field_type: str",
                "        description: One scaling action label.",
                "        required: true",
                "workflow_hints:",
                "  - hint_id: evaluate_thresholds",
                "    summary: Evaluate metrics against rules.",
                "    input_names: [metrics_snapshot]",
                "    output_names: [scaling_decision]",
            ],
        ),
    )
    build_structured_spec_artifact(
        input_path=spec_path,
        output_dir=tmp_path / "structured_spec",
    )
    structured_spec_artifact_path = tmp_path / "structured_spec" / "structured_spec_artifact.json"

    invalid_response = DraftBlueprintPlanResponse(
        planning_summary="Use one evaluator component and one external audit sink.",
        proposed_schemas=[
            PlannedSchema(
                schema_name="ScalingDecision",
                kind="record",
                description="Final scale or no-scale decision.",
                fields=[
                    PlannedSchemaField(
                        field_name="action",
                        field_type="str",
                        description="One scaling action label.",
                    ),
                ],
            ),
        ],
        proposed_components=[
            PlannedComponent(
                component_id="recommendation_generator",
                semantic_responsibility="generate_scaling_recommendation",
                purpose="Turn metrics into one bounded scaling recommendation.",
                input_ports=[],
                output_ports=[
                    PlannedPort(
                        port_name="scaling_decision",
                        schema_name="ScalingDecision",
                        description="Final scaling recommendation.",
                    ),
                ],
                packet_focus=["keep threshold logic explicit", "carry rule salience forward"],
                dependency_notes=[],
            ),
        ],
        proposed_bindings=[
            PlannedBinding(
                from_component="recommendation_generator",
                from_port="scaling_decision",
                to_component="external_audit_or_test",
                to_port="audit_input",
                rationale="send the decision to an undeclared audit helper",
            )
        ],
        proposed_scenarios=[],
        packetization_notes=["Keep the graph small."],
        dependency_decisions=[],
        open_questions=[],
    )
    valid_response = DraftBlueprintPlanResponse(
        planning_summary="Use one evaluator component only.",
        proposed_schemas=invalid_response.proposed_schemas,
        proposed_components=invalid_response.proposed_components,
        proposed_bindings=[],
        proposed_scenarios=[
            PlannedScenario(
                scenario_id="critical_breach",
                kind="semantic_acceptance",
                description="Review one critical CPU breach case end to end.",
                requirement_focus=["produce a scaling decision"],
            ),
        ],
        packetization_notes=["Keep the first draft graph minimal."],
        dependency_decisions=[],
        open_questions=[],
    )
    fake_call = AsyncMock(side_effect=[(invalid_response, object()), (valid_response, object())])
    monkeypatch.setattr("ac14.blueprint_planning.acall_llm_structured", fake_call)

    plan = build_draft_blueprint_plan_from_structured_spec(
        structured_spec_artifact_path=structured_spec_artifact_path,
        output_dir=tmp_path / "plan",
        max_budget=0.1,
    )

    assert plan.proposed_bindings == []
    assert fake_call.await_count == 2
    diagnostics_path = tmp_path / "plan" / "draft_blueprint_plan_validation_error_attempt_1.json"
    invalid_plan_path = tmp_path / "plan" / "draft_blueprint_plan_invalid_attempt_1.json"
    assert diagnostics_path.exists()
    assert invalid_plan_path.exists()
    diagnostics = json.loads(diagnostics_path.read_text())
    assert diagnostics["retryable"] is True
    assert diagnostics["retry_scheduled"] is True
    assert "unknown to_component 'external_audit_or_test'" in diagnostics["validation_error"]
    repair_messages = fake_call.await_args_list[1].args[1]
    combined_content = "\n".join(message["content"] for message in repair_messages)
    assert "Previous invalid draft-plan validation error" in combined_content
    assert "external_audit_or_test" in combined_content


def test_build_draft_blueprint_plan_from_structured_spec_persists_final_invalid_plan_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Structured-spec planning should fail loud with persisted diagnostics after the bounded retry."""

    spec_path = tmp_path / "resource_scaling_spec.yaml"
    spec_path.write_text(
        "\n".join(
            [
                "system_name: Resource Scaling Contract",
                "purpose: Decide when infrastructure should scale.",
                "requirements:",
                "  - produce a scaling decision for each metrics snapshot",
                "inputs:",
                "  - name: metrics_snapshot",
                "    kind: record",
                "    description: Current utilization metrics.",
                "    fields:",
                "      - field_name: cpu_utilization",
                "        field_type: float",
                "        description: CPU utilization ratio.",
                "        required: true",
                "outputs:",
                "  - name: scaling_decision",
                "    kind: record",
                "    description: Final scaling decision.",
                "    fields:",
                "      - field_name: action",
                "        field_type: str",
                "        description: One scaling action label.",
                "        required: true",
            ],
        ),
    )
    build_structured_spec_artifact(
        input_path=spec_path,
        output_dir=tmp_path / "structured_spec",
    )
    structured_spec_artifact_path = tmp_path / "structured_spec" / "structured_spec_artifact.json"

    invalid_response_one = DraftBlueprintPlanResponse(
        planning_summary="Use one evaluator component and one undeclared sink.",
        proposed_schemas=[
            PlannedSchema(
                schema_name="ScalingDecision",
                kind="record",
                description="Final scale or no-scale decision.",
                fields=[
                    PlannedSchemaField(
                        field_name="action",
                        field_type="str",
                        description="One scaling action label.",
                    ),
                ],
            ),
        ],
        proposed_components=[
            PlannedComponent(
                component_id="recommendation_generator",
                semantic_responsibility="generate_scaling_recommendation",
                purpose="Turn metrics into one bounded scaling recommendation.",
                input_ports=[],
                output_ports=[
                    PlannedPort(
                        port_name="scaling_decision",
                        schema_name="ScalingDecision",
                        description="Final scaling recommendation.",
                    ),
                ],
                packet_focus=["keep threshold logic explicit"],
                dependency_notes=[],
            ),
        ],
        proposed_bindings=[
            PlannedBinding(
                from_component="recommendation_generator",
                from_port="scaling_decision",
                to_component="external_audit_or_test",
                to_port="audit_input",
                rationale="send the decision to an undeclared audit helper",
            )
        ],
        proposed_scenarios=[],
        packetization_notes=[],
        dependency_decisions=[],
        open_questions=[],
    )
    invalid_response_two = DraftBlueprintPlanResponse(
        planning_summary="Retry still invents an implicit store read.",
        proposed_schemas=invalid_response_one.proposed_schemas,
        proposed_components=[
            PlannedComponent(
                component_id="recommendation_generator",
                semantic_responsibility="generate_scaling_recommendation",
                purpose="Turn metrics into one bounded scaling recommendation.",
                input_ports=[
                    PlannedPort(
                        port_name="metrics_snapshot",
                        schema_name="ScalingDecision",
                        description="Incorrect but irrelevant input for this retry test.",
                    ),
                ],
                output_ports=invalid_response_one.proposed_components[0].output_ports,
                packet_focus=["keep threshold logic explicit"],
                dependency_notes=[],
            ),
        ],
        proposed_bindings=[
            PlannedBinding(
                from_component="recommendation_generator",
                from_port="scaling_decision",
                to_component="recommendation_generator",
                to_port="store_snapshot",
                rationale="implicit store read that still is not a declared input port",
            )
        ],
        proposed_scenarios=[],
        packetization_notes=[],
        dependency_decisions=[],
        open_questions=[],
    )
    fake_call = AsyncMock(
        side_effect=[(invalid_response_one, object()), (invalid_response_two, object())],
    )
    monkeypatch.setattr("ac14.blueprint_planning.acall_llm_structured", fake_call)

    with pytest.raises(ValueError, match="invalid structured-spec draft plan persisted at"):
        build_draft_blueprint_plan_from_structured_spec(
            structured_spec_artifact_path=structured_spec_artifact_path,
            output_dir=tmp_path / "plan",
            max_budget=0.1,
        )

    assert fake_call.await_count == 2
    diagnostics_path = tmp_path / "plan" / "draft_blueprint_plan_validation_error_attempt_2.json"
    invalid_plan_path = tmp_path / "plan" / "draft_blueprint_plan_invalid_attempt_2.json"
    assert diagnostics_path.exists()
    assert invalid_plan_path.exists()
    diagnostics = json.loads(diagnostics_path.read_text())
    assert diagnostics["retryable"] is False
    assert diagnostics["retry_scheduled"] is False
    assert "unknown to_port 'store_snapshot'" in diagnostics["validation_error"]


def test_build_draft_blueprint_plan_requires_requirements(tmp_path: Path) -> None:
    """Planning should fail loud when no explicit requirements are provided."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"ticket_id": "T-1"}]')
    build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
    )

    with pytest.raises(ValueError, match="requires at least one requirement"):
        build_draft_blueprint_plan(
            discovery_artifact_path=tmp_path / "discovery" / "discovery_artifact.json",
            output_dir=tmp_path / "plan",
            requirements=[],
        )


def test_build_draft_blueprint_plan_rejects_mismatched_dependency_execution(
    tmp_path: Path,
) -> None:
    """Planning should fail loud when execution evidence points at the wrong dependency plan."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"ticket_id": "T-1"}]')
    build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
    )
    dependency_plan_path = tmp_path / "dependency_plan.json"
    dependency_plan_path.write_text(
        DependencyPlanningArtifact(
            discovery_artifact_path=str(tmp_path / "discovery" / "discovery_artifact.json"),
            requirements=["reuse schema tooling"],
            carried_forward_concerns=[],
            planning_summary="Reuse pydantic.",
            recommendations=[],
            standard_library_notes=[],
            open_questions=[],
        ).model_dump_json(indent=2),
    )
    mismatched_execution_path = tmp_path / "dependency_execution_artifact.json"
    mismatched_execution_path.write_text(
        DependencyExecutionArtifact(
            dependency_plan_path=str(tmp_path / "other_dependency_plan.json"),
            execution_mode="check_only",
            planning_summary="Reuse pydantic.",
            carried_forward_questions=[],
            results=[],
            environment_observations=[],
        ).model_dump_json(indent=2),
    )

    with pytest.raises(ValueError, match="different dependency plan"):
        build_draft_blueprint_plan(
            discovery_artifact_path=tmp_path / "discovery" / "discovery_artifact.json",
            output_dir=tmp_path / "plan",
            requirements=["normalize discovered ticket input"],
            dependency_plan_path=dependency_plan_path,
            dependency_execution_artifact_path=mismatched_execution_path,
        )


def test_build_draft_blueprint_plan_accepts_dependency_remediation_artifact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Planning should accept remediation artifacts and preserve execution provenance."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"ticket_id": "T-1", "body": "Login is broken"}]')
    build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
        requested_packages=["pydantic"],
    )
    discovery_artifact_path = tmp_path / "discovery" / "discovery_artifact.json"
    dependency_plan_path = tmp_path / "dependency_plan.json"
    dependency_plan_path.write_text(
        DependencyPlanningArtifact(
            discovery_artifact_path=str(discovery_artifact_path),
            requirements=["reuse installed schema tooling"],
            carried_forward_concerns=[],
            planning_summary="Reuse pydantic for typed schema contracts.",
            recommendations=[],
            standard_library_notes=[],
            open_questions=[],
        ).model_dump_json(indent=2),
    )
    dependency_execution_path = tmp_path / "dependency_execution_artifact.json"
    dependency_execution_path.write_text(
        DependencyExecutionArtifact(
            dependency_plan_path=str(dependency_plan_path),
            execution_mode="allow_install",
            planning_summary="Reuse pydantic for typed schema contracts.",
            carried_forward_questions=[],
            results=[],
            environment_observations=["all dependency probes are confirmed after remediation"],
        ).model_dump_json(indent=2),
    )
    remediation_path = tmp_path / "dependency_remediation_artifact.json"
    remediation_path.write_text(
        DependencyRemediationArtifact(
            prior_dependency_execution_artifact_path=str(tmp_path / "prior_dependency_execution_artifact.json"),
            remediated_dependency_execution_artifact_path=str(dependency_execution_path),
            attempted_packages=[],
            newly_confirmed_packages=[],
            still_blocked_packages=[],
            summary="no blocked install probes required remediation",
        ).model_dump_json(indent=2),
    )

    fake_response = DraftBlueprintPlanResponse(
        planning_summary="Use a source parser and one sink to keep packets bounded.",
        proposed_schemas=[
            PlannedSchema(
                schema_name="RawTicket",
                kind="record",
                description="Normalized raw ticket shape.",
                fields=[
                    PlannedSchemaField(
                        field_name="ticket_id",
                        field_type="str",
                        description="Stable ticket identifier.",
                    ),
                ],
            ),
        ],
        proposed_components=[
            PlannedComponent(
                component_id="ticket_ingest",
                semantic_responsibility="ingest_ticket",
                purpose="Normalize the discovered ticket input into a source schema.",
                input_ports=[],
                output_ports=[
                    PlannedPort(
                        port_name="raw_ticket",
                        schema_name="RawTicket",
                        description="Normalized ticket payload.",
                    ),
                ],
                packet_focus=["normalize incoming fields", "preserve ticket identity"],
                dependency_notes=["no external libraries required"],
            ),
        ],
        proposed_bindings=[],
        proposed_scenarios=[
            PlannedScenario(
                scenario_id="happy_path",
                kind="semantic_acceptance",
                description="Review one realistic ticket end to end.",
                requirement_focus=["normalize ticket input", "preserve meaning"],
            ),
        ],
        packetization_notes=["Keep the source component packet focused on normalization only."],
        dependency_decisions=["Stay within the current environment for the first slice."],
        open_questions=[],
    )
    fake_call = AsyncMock(return_value=(fake_response, object()))
    monkeypatch.setattr("ac14.blueprint_planning.acall_llm_structured", fake_call)

    plan = build_draft_blueprint_plan(
        discovery_artifact_path=discovery_artifact_path,
        output_dir=tmp_path / "plan",
        requirements=["normalize discovered ticket input", "keep packets bounded"],
        dependency_plan_path=dependency_plan_path,
        dependency_remediation_artifact_path=remediation_path,
        max_budget=0.1,
    )

    assert plan.dependency_remediation_artifact_path == str(remediation_path)
    assert plan.dependency_execution_artifact_path == str(dependency_execution_path)
    assert plan.dependency_remediation_summary == "no blocked install probes required remediation"


def test_refine_draft_blueprint_plan_from_freeze_remediation_preserves_provenance(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Refinement should emit a new planning artifact with explicit blocked-freeze provenance."""

    source_plan_path = tmp_path / "draft_blueprint_plan.json"
    source_plan = DraftBlueprintPlanArtifact(
        discovery_artifact_path=str(tmp_path / "discovery_artifact.json"),
        requirements=["normalize discovered ticket input", "keep packets bounded"],
        discovery_open_concerns=["input tags may be sparse"],
        dependency_plan_path=str(tmp_path / "dependency_plan.json"),
        dependency_plan_summary="Reuse pydantic for typed schema contracts.",
        dependency_execution_artifact_path=str(tmp_path / "dependency_execution_artifact.json"),
        dependency_remediation_artifact_path=str(tmp_path / "dependency_remediation_artifact.json"),
        dependency_execution_summary="allow_install dependency probes: 1 confirmed, 0 blocked, 0 skipped",
        dependency_remediation_summary="confirmed prior blocked dependency",
        dependency_recommendations=["reuse pydantic: typed schema contracts"],
        confirmed_dependency_probes=["reuse pydantic: probe confirmed availability"],
        blocked_dependency_probes=[],
        dependency_probe_observations=["all dependency probes are confirmed after remediation"],
        dependency_open_questions=[],
        planning_summary="Use a source parser and one sink to keep packets bounded.",
        proposed_schemas=[
            PlannedSchema(
                schema_name="RawTicket",
                kind="record",
                description="Normalized raw ticket shape.",
                fields=[
                    PlannedSchemaField(
                        field_name="ticket_id",
                        field_type="str",
                        description="Stable ticket identifier.",
                    ),
                ],
            ),
        ],
        proposed_components=[
            PlannedComponent(
                component_id="ticket_ingest",
                semantic_responsibility="ingest_ticket",
                purpose="Normalize the discovered ticket input into a source schema.",
                input_ports=[],
                output_ports=[
                    PlannedPort(
                        port_name="raw_ticket",
                        schema_name="RawTicket",
                        description="Normalized ticket payload.",
                    ),
                ],
                packet_focus=["normalize incoming fields", "preserve ticket identity"],
                dependency_notes=["no external libraries required"],
            ),
        ],
        proposed_bindings=[],
        proposed_scenarios=[
            PlannedScenario(
                scenario_id="happy_path",
                kind="semantic_acceptance",
                description="Review one realistic ticket end to end.",
                requirement_focus=["normalize ticket input", "preserve meaning"],
            ),
        ],
        packetization_notes=["Keep the source component packet focused on normalization only."],
        dependency_decisions=["Stay within the current environment for the first slice."],
        open_questions=[],
    )
    source_plan_path.write_text(source_plan.model_dump_json(indent=2))

    remediation_plan_path = tmp_path / "freeze_remediation_plan.json"
    remediation_plan_path.write_text(
        json.dumps(
            {
                "blocked": True,
                "summary": "1 remediation task generated for blocked freeze",
                "task_count": 1,
                "upstream_plan_path": str(source_plan_path),
                "tasks": [
                    {
                        "task_id": "freeze-remediation-01",
                        "blocking": True,
                        "title": "Resolve blocked dependency probes",
                        "summary": "Update dependency evidence before retrying freeze.",
                        "target_files": [str(source_plan_path)],
                        "source_paths": ["metadata.dependencies"],
                        "finding_codes": ["E-DRAFT-DEPENDENCY-BLOCKED"],
                        "authoring_actions": ["Update dependency decisions and open questions."],
                        "retry_command": "python -m ac14 materialize-draft-bundle",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    freeze_decision_path = tmp_path / "freeze_decision.json"
    freeze_decision_path.write_text(
        json.dumps(
            {
                "approved": False,
                "decision_summary": "bundle blocked by freeze-readiness findings",
                "findings": [
                    {
                        "code": "E-DRAFT-DEPENDENCY-BLOCKED",
                        "message": "Blocked dependency probe remains unresolved.",
                        "path": "metadata.dependencies",
                    }
                ],
                "remediation_plan_path": str(remediation_plan_path),
            },
            indent=2,
            sort_keys=True,
        )
    )

    fake_response = RefinedDraftBlueprintPlanResponse(
        refinement_summary="Updated dependency decisions and clarified the retry story.",
        planning_summary="Keep the same bounded graph but make dependency handling explicit.",
        proposed_schemas=source_plan.proposed_schemas,
        proposed_components=source_plan.proposed_components,
        proposed_bindings=source_plan.proposed_bindings,
        proposed_scenarios=source_plan.proposed_scenarios,
        packetization_notes=[
            "Keep the source packet bounded and call out dependency expectations explicitly.",
        ],
        dependency_decisions=[
            "Reuse pydantic and keep optional formatting libraries out of the first frozen slice.",
        ],
        open_questions=[
            PlanningQuestion(
                question="Should richer formatting remain deferred until after the first freeze?",
                why_it_matters="It affects whether any new dependency is still in scope.",
            ),
        ],
    )
    fake_call = AsyncMock(return_value=(fake_response, object()))
    monkeypatch.setattr("ac14.blueprint_planning.acall_llm_structured", fake_call)

    refined_plan = build_refined_draft_blueprint_plan(
        plan_artifact_path=source_plan_path,
        freeze_decision_path=freeze_decision_path,
        output_dir=tmp_path / "refined_plan",
        max_budget=0.1,
    )

    assert refined_plan.source_draft_blueprint_plan_path == str(source_plan_path)
    assert refined_plan.source_freeze_decision_path == str(freeze_decision_path)
    assert refined_plan.source_freeze_remediation_plan_path == str(remediation_plan_path)
    assert refined_plan.refinement_summary == fake_response.refinement_summary
    assert refined_plan.refinement_round == 1
    assert refined_plan.dependency_remediation_artifact_path == source_plan.dependency_remediation_artifact_path
    assert (tmp_path / "refined_plan" / "draft_blueprint_plan.json").exists()
    assert fake_call.await_count == 1

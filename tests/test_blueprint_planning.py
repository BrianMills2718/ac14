"""Tests for draft blueprint planning artifacts."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from ac14.blueprint_planning import (
    DraftBlueprintPlanResponse,
    PlannedComponent,
    PlannedPort,
    PlannedScenario,
    PlannedSchema,
    PlannedSchemaField,
    PlanningQuestion,
    build_draft_blueprint_plan,
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
    assert plan.dependency_probe_observations == ["install mutation was disabled for this run"]


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

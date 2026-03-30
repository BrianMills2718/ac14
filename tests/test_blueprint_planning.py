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
        max_budget=0.1,
    )

    assert plan.requirements == [
        "normalize discovered ticket input",
        "keep packets bounded",
    ]
    assert plan.proposed_components[0].component_id == "ticket_ingest"
    assert (tmp_path / "plan" / "draft_blueprint_plan.json").exists()
    assert fake_call.await_count == 1
    assert fake_call.await_args is not None
    kwargs = fake_call.await_args.kwargs
    assert kwargs["task"] == "ac14_draft_blueprint_plan"
    assert kwargs["max_budget"] == 0.1


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

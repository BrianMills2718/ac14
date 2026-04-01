"""Tests for explicit freeze-retry artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ac14.blueprint_planning import (
    DraftBlueprintPlanArtifact,
    PlannedComponent,
    PlannedPort,
    PlannedScenario,
    PlannedSchema,
    PlannedSchemaField,
    PlanningQuestion,
)
from ac14.freeze_retry import build_freeze_retry_artifact


def _write_plan_artifact(path: Path) -> Path:
    """Persist a deterministic planning artifact for retry-chain tests."""

    artifact = DraftBlueprintPlanArtifact(
        discovery_artifact_path=str(path.parent / "discovery_artifact.json"),
        requirements=["normalize discovered ticket input", "keep packets bounded"],
        discovery_open_concerns=[],
        planning_summary="Use a single source component as the first draft bundle.",
        proposed_schemas=[
            PlannedSchema(
                schema_name="RawTicket",
                kind="record",
                description="Normalized raw ticket input.",
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
                purpose="Normalize the discovered input into RawTicket.",
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
        packetization_notes=["Keep the first packet focused on source normalization only."],
        dependency_decisions=["Stay within the current environment for the first draft."],
        open_questions=[
            PlanningQuestion(
                question="Should tags be preserved as a field in RawTicket?",
                why_it_matters="It changes schema shape before freeze.",
            ),
        ],
    )
    path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))
    return path


def _write_blocked_freeze_inputs(tmp_path: Path, plan_path: Path) -> tuple[Path, Path]:
    """Persist one blocked freeze decision plus remediation plan."""

    remediation_plan_path = tmp_path / "freeze_remediation_plan.json"
    remediation_plan_path.write_text(
        json.dumps(
            {
                "blocked": True,
                "summary": "1 remediation task generated for blocked freeze",
                "task_count": 1,
                "upstream_plan_path": str(plan_path),
                "tasks": [
                    {
                        "task_id": "freeze-remediation-01",
                        "blocking": True,
                        "title": "Resolve blocked dependency probes",
                        "summary": "Update dependency evidence before retrying freeze.",
                        "target_files": [str(plan_path)],
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
    return freeze_decision_path, remediation_plan_path


def test_build_freeze_retry_artifact_runs_refine_materialize_and_refreeze(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Retry artifacts should keep every intermediate step explicit and persisted."""

    plan_path = _write_plan_artifact(tmp_path / "draft_blueprint_plan.json")
    freeze_decision_path, _remediation_plan_path = _write_blocked_freeze_inputs(tmp_path, plan_path)
    fixture_path = tmp_path / "refine_draft_blueprint_plan_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "refinement_summary": "Clarified dependency scope after the blocked freeze.",
                "planning_summary": "Keep the bounded graph and tighten dependency decisions.",
                "proposed_schemas": [
                    {
                        "schema_name": "RawTicket",
                        "kind": "record",
                        "description": "Normalized raw ticket input.",
                        "fields": [
                            {
                                "field_name": "ticket_id",
                                "field_type": "str",
                                "description": "Stable ticket identifier.",
                            }
                        ],
                    }
                ],
                "proposed_components": [
                    {
                        "component_id": "ticket_ingest",
                        "semantic_responsibility": "ingest_ticket",
                        "purpose": "Normalize the discovered input into RawTicket.",
                        "input_ports": [],
                        "output_ports": [
                            {
                                "port_name": "raw_ticket",
                                "schema_name": "RawTicket",
                                "description": "Normalized ticket payload.",
                            }
                        ],
                        "packet_focus": ["normalize incoming fields", "preserve ticket identity"],
                        "dependency_notes": ["no external libraries required"],
                    }
                ],
                "proposed_bindings": [],
                "proposed_scenarios": [
                    {
                        "scenario_id": "happy_path",
                        "kind": "semantic_acceptance",
                        "description": "Review one realistic ticket end to end.",
                        "requirement_focus": ["normalize ticket input", "preserve meaning"],
                    }
                ],
                "packetization_notes": ["Keep the packet boundary unchanged."],
                "dependency_decisions": ["Keep optional formatting dependencies out of the first freeze."],
                "open_questions": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    monkeypatch.setenv("AC14_REFINE_BLUEPRINT_PLAN_FIXTURE", str(fixture_path))
    freeze_semantic_fixture_path = tmp_path / "freeze_semantic_review_fixture.json"
    freeze_semantic_fixture_path.write_text(
        json.dumps(
            {
                "overall_verdict": "concern",
                "freeze_verdict": "promising_but_blocked",
                "summary": "The draft is strategically plausible, but draft-quality blockers still prevent freeze.",
                "strengths": [
                    "The planning summary preserves the realistic ticket intent.",
                ],
                "concerns": [
                    "Fixture coverage and concrete invariants remain incomplete.",
                ],
                "requirement_assessments": [
                    {
                        "requirement": "normalize discovered ticket input",
                        "verdict": "satisfied",
                        "rationale": "The discovered fields still preserve the ticket meaning.",
                    },
                    {
                        "requirement": "keep packets bounded",
                        "verdict": "satisfied",
                        "rationale": "The source packet remains narrowly scoped.",
                    },
                ],
                "recommended_next_steps": [
                    "Add concrete fixtures and invariants before retrying freeze.",
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    monkeypatch.setenv("AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE", str(freeze_semantic_fixture_path))

    artifact = build_freeze_retry_artifact(
        plan_artifact_path=plan_path,
        freeze_decision_path=freeze_decision_path,
        output_dir=tmp_path / "freeze_retry",
        max_budget=0.1,
    )

    assert Path(artifact.refined_draft_blueprint_plan_path).exists()
    assert Path(artifact.refined_draft_bundle_dir).exists()
    assert Path(artifact.refreshed_freeze_readiness_report_path).exists()
    assert Path(artifact.refreshed_freeze_decision_path).exists()
    assert artifact.source_draft_blueprint_plan_path == str(plan_path)
    assert artifact.source_freeze_decision_path == str(freeze_decision_path)
    assert artifact.refinement_round == 1
    assert (tmp_path / "freeze_retry" / "freeze_retry_artifact.json").exists()

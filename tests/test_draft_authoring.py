"""Tests for draft bundle authoring and freeze-readiness reporting."""

from __future__ import annotations

import json
from pathlib import Path

from ac14.blueprint_planning import (
    DraftBlueprintPlanArtifact,
    PlannedComponent,
    PlannedPort,
    PlannedScenario,
    PlannedSchema,
    PlannedSchemaField,
    PlanningQuestion,
)
from ac14.draft_authoring import materialize_draft_blueprint_bundle


def _write_plan_artifact(path: Path) -> Path:
    """Persist a small deterministic planning artifact for authoring tests."""

    artifact = DraftBlueprintPlanArtifact(
        discovery_artifact_path=str(path.parent / "discovery_artifact.json"),
        requirements=["normalize discovered ticket input", "keep packets bounded"],
        discovery_open_concerns=["field priority is sparse across samples"],
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


def test_materialize_draft_blueprint_bundle_persists_bundle_and_report(tmp_path: Path) -> None:
    """Draft authoring should write the bundle files and a readiness report."""

    plan_path = _write_plan_artifact(tmp_path / "draft_blueprint_plan.json")

    manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=plan_path,
        output_dir=tmp_path / "draft_bundle",
    )

    bundle_dir = tmp_path / "draft_bundle"
    assert manifest.draft_bundle_dir == str(bundle_dir)
    assert (bundle_dir / "metadata.yaml").exists()
    assert (bundle_dir / "schemas.yaml").exists()
    assert (bundle_dir / "components.yaml").exists()
    assert (bundle_dir / "architecture.yaml").exists()
    assert (bundle_dir / "validation.yaml").exists()
    assert (bundle_dir / "fixtures.yaml").exists()
    report_path = bundle_dir / "freeze_readiness_report.json"
    assert report_path.exists()

    report = json.loads(report_path.read_text())
    assert report["ready"] is False
    codes = {finding["code"] for finding in report["findings"]}
    assert "E-B1-COMPONENT-FIXTURE-COVERAGE-MISSING" in codes
    assert "W-DRAFT-PLACEHOLDER-INVARIANT" in codes
    assert "W-DRAFT-OPEN-QUESTION" in codes

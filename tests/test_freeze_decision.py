"""Tests for explicit freeze decisions and promotion."""

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
from ac14.freeze_decision import build_freeze_decision


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "examples" / "support_ticket_digest" / "blueprint"


def _write_plan_artifact(path: Path) -> Path:
    """Persist a deterministic planning artifact for freeze-decision tests."""

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


def test_build_freeze_decision_blocks_draft_bundle(tmp_path: Path) -> None:
    """Draft bundles with readiness blockers should produce blocked decisions."""

    plan_path = _write_plan_artifact(tmp_path / "draft_blueprint_plan.json")
    manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=plan_path,
        output_dir=tmp_path / "draft_bundle",
    )

    decision = build_freeze_decision(
        bundle_dir=Path(manifest.draft_bundle_dir),
        output_dir=tmp_path / "freeze_decision",
        readiness_report_path=Path(manifest.freeze_readiness_report_path),
    )

    assert decision.approved is False
    assert decision.promoted_bundle_dir is None
    codes = {finding.code for finding in decision.findings}
    assert "E-B1-COMPONENT-FIXTURE-COVERAGE-MISSING" in codes
    assert "W-DRAFT-PLACEHOLDER-INVARIANT" in codes
    assert (tmp_path / "freeze_decision" / "freeze_decision.json").exists()


def test_build_freeze_decision_promotes_ready_bundle(tmp_path: Path) -> None:
    """Already-ready bundles should be promoted into a frozen bundle directory."""

    decision = build_freeze_decision(
        bundle_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "freeze_decision",
    )

    assert decision.approved is True
    assert decision.promoted_bundle_dir is not None
    promoted_dir = Path(decision.promoted_bundle_dir)
    assert (promoted_dir / "metadata.yaml").exists()
    assert (promoted_dir / "schemas.yaml").exists()

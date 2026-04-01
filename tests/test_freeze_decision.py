"""Tests for explicit freeze decisions and promotion."""

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
        dependency_execution_artifact_path=str(path.parent / "dependency_execution_artifact.json"),
        dependency_execution_summary="check_only dependency probes: 1 confirmed, 0 blocked, 0 skipped",
        confirmed_dependency_probes=[
            "reuse pydantic: reuse probe confirmed the package is already available",
        ],
        blocked_dependency_probes=[],
        dependency_probe_observations=["install mutation was disabled for this run"],
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


def _write_freeze_semantic_review_fixture(path: Path) -> Path:
    """Persist a deterministic freeze-semantic review fixture."""

    path.write_text(
        json.dumps(
            {
                "overall_verdict": "concern",
                "freeze_verdict": "promising_but_blocked",
                "summary": "The draft is strategically plausible, but still blocked by concrete draft quality gaps.",
                "strengths": [
                    "The planning artifact preserves the core requirements.",
                    "The draft packetization remains bounded and locally implementable.",
                ],
                "concerns": [
                    "The draft still lacks fixture coverage and concrete invariants.",
                    "An unresolved schema-shape question remains before freeze.",
                ],
                "requirement_assessments": [
                    {
                        "requirement": "normalize discovered ticket input",
                        "verdict": "satisfied",
                        "rationale": "The source component and schema preserve the normalization goal.",
                    },
                    {
                        "requirement": "keep packets bounded",
                        "verdict": "satisfied",
                        "rationale": "The proposed packet scope is still narrow and local.",
                    },
                ],
                "recommended_next_steps": [
                    "Add concrete fixtures and invariants before retrying freeze.",
                    "Resolve the remaining schema question before promotion.",
                ],
            },
            indent=2,
            sort_keys=True,
        ),
    )
    return path


def test_build_freeze_decision_blocks_draft_bundle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Draft bundles with readiness blockers should produce blocked worklists."""

    plan_path = _write_plan_artifact(tmp_path / "draft_blueprint_plan.json")
    monkeypatch.setenv(
        "AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE",
        str(_write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json")),
    )
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
    assert decision.semantic_review_path is not None
    semantic_review_payload = json.loads(Path(decision.semantic_review_path).read_text())
    assert semantic_review_payload["review"]["freeze_verdict"] == "promising_but_blocked"
    remediation_payload = json.loads(Path(decision.remediation_plan_path).read_text())
    assert remediation_payload["blocked"] is True
    assert remediation_payload["task_count"] >= 2
    target_files = {
        Path(target_file).name
        for task in remediation_payload["tasks"]
        for target_file in task["target_files"]
    }
    assert "components.yaml" in target_files
    assert "fixtures.yaml" in target_files
    assert remediation_payload["bundle_retry_command"].startswith("python -m ac14 decide-freeze")


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
    assert decision.semantic_review_path is None
    remediation_payload = json.loads(Path(decision.remediation_plan_path).read_text())
    assert remediation_payload["blocked"] is False
    assert remediation_payload["task_count"] == 0


def test_build_freeze_decision_groups_dependency_probe_blockers(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Dependency probe blockers should become a dedicated remediation task bucket."""

    plan_path = _write_plan_artifact(tmp_path / "draft_blueprint_plan.json")
    monkeypatch.setenv(
        "AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE",
        str(_write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json")),
    )
    artifact = DraftBlueprintPlanArtifact.model_validate_json(plan_path.read_text())
    artifact.blocked_dependency_probes = [
        "install rich: install probe blocked because environment mutation is disabled",
    ]
    plan_path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=plan_path,
        output_dir=tmp_path / "draft_bundle",
    )
    decision = build_freeze_decision(
        bundle_dir=Path(manifest.draft_bundle_dir),
        output_dir=tmp_path / "freeze_decision",
        readiness_report_path=Path(manifest.freeze_readiness_report_path),
    )

    remediation_payload = json.loads(Path(decision.remediation_plan_path).read_text())
    dependency_tasks = [
        task
        for task in remediation_payload["tasks"]
        if "E-DRAFT-DEPENDENCY-PROBE-BLOCKED" in task["finding_codes"]
    ]
    assert len(dependency_tasks) == 1
    dependency_task = dependency_tasks[0]
    assert dependency_task["blocking"] is True
    assert any(target.endswith("draft_blueprint_plan.json") for target in dependency_task["target_files"])
    assert any(
        target.endswith("dependency_execution_artifact.json")
        for target in dependency_task["target_files"]
    )

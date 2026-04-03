"""Tests for draft bundle authoring and freeze-readiness reporting."""

from __future__ import annotations

import json
from pathlib import Path

import yaml  # type: ignore[import-untyped]

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
        dependency_plan_path=str(path.parent / "dependency_plan.json"),
        dependency_plan_summary="Reuse pydantic and leave richer UI libraries unresolved.",
        dependency_recommendations=["reuse pydantic: typed schema contracts"],
        dependency_execution_artifact_path=str(path.parent / "dependency_execution_artifact.json"),
        dependency_execution_summary="check_only dependency probes: 1 confirmed, 0 blocked, 0 skipped",
        confirmed_dependency_probes=[
            "reuse pydantic: reuse probe confirmed the package is already available",
        ],
        blocked_dependency_probes=[],
        dependency_probe_observations=["install mutation was disabled for this run"],
        dependency_open_questions=[
            PlanningQuestion(
                question="Should richer terminal rendering stay out of the first draft slice?",
                why_it_matters="It affects dependency scope before freeze.",
            ),
        ],
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
    assert "W-DRAFT-DEPENDENCY-QUESTION" in codes


def test_materialize_draft_blueprint_bundle_blocks_on_dependency_probe_results(
    tmp_path: Path,
) -> None:
    """Blocked dependency probes should become explicit freeze-readiness blockers."""

    plan_path = tmp_path / "draft_blueprint_plan.json"
    artifact = DraftBlueprintPlanArtifact.model_validate_json(_write_plan_artifact(plan_path).read_text())
    artifact.blocked_dependency_probes = [
        "install rich: install probe blocked because environment mutation is disabled",
    ]
    plan_path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=plan_path,
        output_dir=tmp_path / "draft_bundle",
    )

    report = json.loads(Path(manifest.freeze_readiness_report_path).read_text())
    assert report["ready"] is False
    blocked_findings = [
        finding for finding in report["findings"] if finding["code"] == "E-DRAFT-DEPENDENCY-PROBE-BLOCKED"
    ]
    assert len(blocked_findings) == 1
    assert "install rich" in blocked_findings[0]["message"]


def test_materialize_draft_blueprint_bundle_uses_structured_spec_provenance_for_metadata(
    tmp_path: Path,
) -> None:
    """Structured-spec planning provenance should flow into draft metadata ids and names."""

    plan_path = tmp_path / "draft_blueprint_plan.json"
    artifact = DraftBlueprintPlanArtifact.model_validate_json(_write_plan_artifact(plan_path).read_text())
    artifact.planning_input_kind = "structured_spec"
    artifact.discovery_artifact_path = None
    artifact.structured_spec_artifact_path = str(tmp_path / "structured_spec_artifact.json")
    artifact.planning_input_artifact_path = artifact.structured_spec_artifact_path
    artifact.planning_input_name = "Resource Scaling Contract"
    plan_path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))

    manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=plan_path,
        output_dir=tmp_path / "draft_bundle",
    )

    metadata = yaml.safe_load((Path(manifest.draft_bundle_dir) / "metadata.yaml").read_text())
    assert metadata["metadata"]["blueprint_id"] == "resource_scaling_contract_draft_v0"
    assert metadata["metadata"]["name"] == "Resource Scaling Contract"


def test_materialize_draft_blueprint_bundle_warns_on_dependency_probe_results_when_policy_warn(
    tmp_path: Path,
) -> None:
    """Warn policy should downgrade blocked dependency probes to non-error findings."""

    plan_path = tmp_path / "draft_blueprint_plan.json"
    artifact = DraftBlueprintPlanArtifact.model_validate_json(_write_plan_artifact(plan_path).read_text())
    artifact.blocked_dependency_probes = [
        "install rich: install probe blocked because environment mutation is disabled",
    ]
    plan_path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))
    config_path = tmp_path / "meta-process.yaml"
    config_path.write_text(
        "\n".join(
            [
                "meta_process:",
                "  version: \"1.0\"",
                "  planning:",
                "    dependency_probe_policy: warn",
            ],
        ),
    )

    manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=plan_path,
        output_dir=tmp_path / "draft_bundle",
        meta_process_config_path=config_path,
    )

    report = json.loads(Path(manifest.freeze_readiness_report_path).read_text())
    codes = {finding["code"] for finding in report["findings"]}
    assert "W-DRAFT-DEPENDENCY-PROBE-BLOCKED" in codes
    assert "E-DRAFT-DEPENDENCY-PROBE-BLOCKED" not in codes


def test_materialize_draft_blueprint_bundle_ignores_dependency_probe_results_when_policy_ignore(
    tmp_path: Path,
) -> None:
    """Ignore policy should omit blocked dependency probe findings entirely."""

    plan_path = tmp_path / "draft_blueprint_plan.json"
    artifact = DraftBlueprintPlanArtifact.model_validate_json(_write_plan_artifact(plan_path).read_text())
    artifact.blocked_dependency_probes = [
        "install rich: install probe blocked because environment mutation is disabled",
    ]
    plan_path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))
    config_path = tmp_path / "meta-process.yaml"
    config_path.write_text(
        "\n".join(
            [
                "meta_process:",
                "  version: \"1.0\"",
                "  planning:",
                "    dependency_probe_policy: ignore",
            ],
        ),
    )

    manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=plan_path,
        output_dir=tmp_path / "draft_bundle",
        meta_process_config_path=config_path,
    )

    report = json.loads(Path(manifest.freeze_readiness_report_path).read_text())
    codes = {finding["code"] for finding in report["findings"]}
    assert "W-DRAFT-DEPENDENCY-PROBE-BLOCKED" not in codes
    assert "E-DRAFT-DEPENDENCY-PROBE-BLOCKED" not in codes

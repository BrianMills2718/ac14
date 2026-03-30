"""Explicit freeze decisions and promotion for AC14 bundles."""

from __future__ import annotations

import json
import shutil
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel, Field
import yaml  # type: ignore[import-untyped]

from ac14.draft_authoring import FreezeReadinessReport
from ac14.loader import REQUIRED_FILES, load_blueprint_dir
from ac14.models import ValidationFinding
from ac14.validation import validate_blueprint


class FreezeDecisionArtifact(BaseModel):
    """Persisted approve/block decision for bundle promotion."""

    source_bundle_dir: str = Field(description="Bundle directory evaluated for promotion.")
    readiness_report_path: str | None = Field(
        default=None,
        description="Readiness report used for the decision when available.",
    )
    approved: bool = Field(description="Whether the bundle is approved for freeze promotion.")
    decision_summary: str = Field(description="Compact summary of the freeze decision.")
    findings: list[ValidationFinding] = Field(
        description="Blocking or qualifying findings carried into the decision artifact.",
    )
    promoted_bundle_dir: str | None = Field(
        default=None,
        description="Promoted frozen bundle directory when approval succeeds.",
    )
    remediation_plan_path: str = Field(
        description="Path to the persisted remediation plan for this decision.",
    )


class FreezeRemediationTask(BaseModel):
    """Single actionable task derived from blocked freeze findings."""

    task_id: str = Field(description="Stable task identifier inside the remediation plan.")
    blocking: bool = Field(description="Whether the task must be resolved before retrying freeze.")
    title: str = Field(description="Short actionable title for the remediation task.")
    summary: str = Field(description="Compact explanation of the grouped findings.")
    target_files: list[str] = Field(
        description="Concrete bundle files or upstream artifacts that should be edited.",
    )
    source_paths: list[str] = Field(
        description="Source finding paths that produced this remediation task.",
    )
    finding_codes: list[str] = Field(
        description="Grouped finding codes captured by the task.",
    )
    authoring_actions: list[str] = Field(
        description="Concrete authoring actions to resolve the grouped findings.",
    )
    retry_command: str = Field(
        description="Command to rerun after completing the task.",
    )


class FreezeRemediationPlan(BaseModel):
    """Persisted worklist that turns blocked decisions into authoring loops."""

    source_bundle_dir: str = Field(description="Bundle directory that needs review.")
    readiness_report_path: str | None = Field(
        default=None,
        description="Readiness report used by the decision when available.",
    )
    decision_summary: str = Field(description="Decision summary copied from the freeze artifact.")
    blocked: bool = Field(description="Whether remediation work remains before promotion.")
    task_count: int = Field(description="Number of grouped remediation tasks.")
    summary: str = Field(description="Compact summary of the remediation state.")
    bundle_retry_command: str = Field(
        description="Direct command to rerun freeze after editing the bundle.",
    )
    upstream_plan_path: str | None = Field(
        default=None,
        description="Upstream planning artifact when the bundle was materialized from one.",
    )
    upstream_regeneration_command: str | None = Field(
        default=None,
        description="Optional command to regenerate the draft bundle from its upstream plan.",
    )
    tasks: list[FreezeRemediationTask] = Field(
        description="Grouped remediation tasks for the blocked bundle.",
    )


def build_freeze_decision(
    bundle_dir: Path | str,
    output_dir: Path | str,
    *,
    readiness_report_path: Path | str | None = None,
) -> FreezeDecisionArtifact:
    """Persist a freeze decision and promote the bundle only when approved."""

    source_dir = Path(bundle_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    if readiness_report_path is not None:
        readiness_path = Path(readiness_report_path)
        readiness_report = FreezeReadinessReport.model_validate_json(readiness_path.read_text())
        findings = readiness_report.findings
        approved = readiness_report.ready
        decision_summary = (
            "bundle approved for freeze promotion"
            if approved
            else "bundle blocked by freeze-readiness findings"
        )
    else:
        blueprint = load_blueprint_dir(source_dir)
        validation_result = validate_blueprint(blueprint)
        findings = validation_result.findings
        approved = validation_result.passed
        readiness_path = None
        decision_summary = (
            "bundle approved for freeze promotion"
            if approved
            else "bundle blocked by frozen-blueprint validation findings"
        )

    promoted_bundle_dir: str | None = None
    if approved:
        promoted_dir = destination / "frozen_bundle"
        promoted_dir.mkdir(parents=True, exist_ok=True)
        for filename in REQUIRED_FILES.values():
            shutil.copy2(source_dir / filename, promoted_dir / filename)
        promoted_bundle_dir = str(promoted_dir)

    remediation_plan = build_freeze_remediation_plan(
        source_bundle_dir=source_dir,
        output_dir=destination,
        readiness_report_path=readiness_path if readiness_report_path is not None else None,
        decision_summary=decision_summary,
        findings=findings,
        approved=approved,
    )
    remediation_path = destination / "freeze_remediation_plan.json"
    remediation_path.write_text(
        json.dumps(remediation_plan.model_dump(mode="json"), indent=2, sort_keys=True),
    )

    decision = FreezeDecisionArtifact(
        source_bundle_dir=str(source_dir),
        readiness_report_path=str(readiness_path) if readiness_report_path is not None else None,
        approved=approved,
        decision_summary=decision_summary,
        findings=findings,
        promoted_bundle_dir=promoted_bundle_dir,
        remediation_plan_path=str(remediation_path),
    )
    (destination / "freeze_decision.json").write_text(
        json.dumps(decision.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return decision


def build_freeze_remediation_plan(
    *,
    source_bundle_dir: Path | str,
    output_dir: Path | str,
    readiness_report_path: Path | str | None,
    decision_summary: str,
    findings: list[ValidationFinding],
    approved: bool,
) -> FreezeRemediationPlan:
    """Build a persisted authoring worklist from a freeze decision."""

    source_dir = Path(source_bundle_dir)
    destination = Path(output_dir)
    bundle_retry_command = (
        f'python -m ac14 decide-freeze "{source_dir}" --output-dir "{destination}"'
    )
    upstream_plan_path = _read_upstream_plan_path(source_dir)
    upstream_regeneration_command = None
    if upstream_plan_path is not None:
        upstream_regeneration_command = (
            f'python -m ac14 materialize-draft-bundle "{upstream_plan_path}" '
            f'--output-dir "{source_dir}"'
        )

    tasks = [] if approved else _group_remediation_tasks(
        source_dir=source_dir,
        findings=findings,
        upstream_plan_path=upstream_plan_path,
        bundle_retry_command=bundle_retry_command,
        upstream_regeneration_command=upstream_regeneration_command,
    )
    summary = (
        "no remediation required; bundle is ready for promotion"
        if approved
        else f"{len(tasks)} remediation tasks generated for blocked freeze"
    )
    return FreezeRemediationPlan(
        source_bundle_dir=str(source_dir),
        readiness_report_path=str(readiness_report_path) if readiness_report_path is not None else None,
        decision_summary=decision_summary,
        blocked=not approved,
        task_count=len(tasks),
        summary=summary,
        bundle_retry_command=bundle_retry_command,
        upstream_plan_path=upstream_plan_path,
        upstream_regeneration_command=upstream_regeneration_command,
        tasks=tasks,
    )


def _group_remediation_tasks(
    *,
    source_dir: Path,
    findings: list[ValidationFinding],
    upstream_plan_path: str | None,
    bundle_retry_command: str,
    upstream_regeneration_command: str | None,
) -> list[FreezeRemediationTask]:
    """Group findings into actionable bundle-authoring tasks."""

    grouped: dict[str, list[ValidationFinding]] = defaultdict(list)
    for finding in findings:
        grouped[_bucket_key_for_finding(finding)].append(finding)

    tasks: list[FreezeRemediationTask] = []
    for index, bucket_key in enumerate(sorted(grouped), start=1):
        bucket_findings = grouped[bucket_key]
        title, target_files, authoring_actions = _task_shape_for_bucket(
            bucket_key=bucket_key,
            source_dir=source_dir,
            upstream_plan_path=upstream_plan_path,
        )
        retry_command = (
            upstream_regeneration_command
            if bucket_key == "planning" and upstream_regeneration_command is not None
            else bundle_retry_command
        )
        tasks.append(
            FreezeRemediationTask(
                task_id=f"freeze-remediation-{index:02d}",
                blocking=any(finding.code.startswith("E-") for finding in bucket_findings),
                title=title,
                summary="; ".join(_dedupe(finding.message for finding in bucket_findings)),
                target_files=target_files,
                source_paths=_dedupe(finding.path for finding in bucket_findings),
                finding_codes=_dedupe(finding.code for finding in bucket_findings),
                authoring_actions=authoring_actions,
                retry_command=retry_command,
            ),
        )
    return tasks


def _bucket_key_for_finding(finding: ValidationFinding) -> str:
    """Return the remediation bucket for one finding."""

    if finding.code in {
        "E-B1-COMPONENT-FIXTURE-COVERAGE-MISSING",
        "E-B1-END-TO-END-SCENARIO-COVERAGE-MISSING",
        "E-B1-SCENARIO-FIXTURE-MISSING",
        "E-B1-FIXTURE-COMPONENT-MISSING",
        "E-B1-FIXTURE-SCENARIO-MISSING",
        "E-B1-FIXTURE-INPUT-PORT-MISSING",
        "E-B1-FIXTURE-OUTPUT-PORT-MISSING",
    }:
        return "fixtures"
    if finding.code in {
        "E-B1-SCENARIO-EVALUATORS-EMPTY",
        "E-B1-SCENARIO-EVALUATOR-MISSING",
        "E-B1-NEGATIVE-SCENARIO-EVALUATOR-MISSING",
        "E-B1-SEMANTIC-SCENARIO-REQUIREMENTS-MISSING",
        "E-B1-SEMANTIC-SCENARIO-LLM-EVALUATOR-MISSING",
        "E-B1-FULL-SCENARIO-MISSING",
        "E-B1-SEMANTIC-ACCEPTANCE-SCENARIO-MISSING",
        "E-B1-REALISTIC-INPUT-SCENARIO-MISSING",
    }:
        return "scenarios"
    if finding.code in {
        "W-DRAFT-PLACEHOLDER-INVARIANT",
        "W-DRAFT-PLACEHOLDER-FAILURE",
        "W-DRAFT-PLACEHOLDER-CONSTRAINT",
    }:
        return "components"
    if finding.code in {
        "W-DRAFT-UNSUPPORTED-SCHEMA-KIND",
        "E-B1-OPTIONAL-FIELD-INCOMPLETE",
        "E-B1-SCHEMA-FIELD-REF-MISSING",
        "E-B1-INPUT-SCHEMA-MISSING",
        "E-B1-OUTPUT-SCHEMA-MISSING",
    }:
        return "schemas"
    if finding.code in {
        "E-B1-BINDING-SOURCE-MISSING",
        "E-B1-BINDING-TARGET-MISSING",
        "E-B1-BINDING-SOURCE-PORT-MISSING",
        "E-B1-BINDING-TARGET-PORT-MISSING",
        "E-B1-BINDING-SCHEMA-MISMATCH",
        "E-B1-GRAPH-CYCLE",
        "E-B1-STATE-OWNER-MISSING",
        "E-B1-STATE-SCHEMA-MISSING",
    }:
        return "architecture"
    if finding.code in {
        "E-B1-DUPLICATE-INPUT-PORT",
        "E-B1-DUPLICATE-OUTPUT-PORT",
    }:
        return "component_interface"
    if finding.code == "W-DRAFT-OPEN-QUESTION":
        return "planning"
    return _fallback_bucket_from_path(finding.path)


def _fallback_bucket_from_path(path: str) -> str:
    """Infer a remediation bucket from the finding path when no code map exists."""

    if path.startswith("fixtures."):
        return "fixtures"
    if path.startswith("validation."):
        return "scenarios"
    if path.startswith("components."):
        return "component_interface"
    if path.startswith("schemas."):
        return "schemas"
    if path.startswith("architecture."):
        return "architecture"
    if path.startswith("planning."):
        return "planning"
    return "generic"


def _task_shape_for_bucket(
    *,
    bucket_key: str,
    source_dir: Path,
    upstream_plan_path: str | None,
) -> tuple[str, list[str], list[str]]:
    """Return the title, target files, and authoring actions for one bucket."""

    if bucket_key == "fixtures":
        return (
            "Add or repair fixture coverage",
            [str(source_dir / "fixtures.yaml"), str(source_dir / "validation.yaml")],
            [
                "Add component-local fixtures for every missing component.",
                "Ensure each full-system scenario references one fixture per component.",
                "Keep fixture input and output port names aligned with component ports.",
            ],
        )
    if bucket_key == "scenarios":
        return (
            "Repair scenario and evaluator coverage",
            [str(source_dir / "validation.yaml")],
            [
                "Add the missing evaluator IDs required by each scenario kind.",
                "Ensure semantic_acceptance scenarios declare requirements and an llm evaluator.",
                "Keep at least one full-system realistic-input scenario in the bundle.",
            ],
        )
    if bucket_key == "components":
        return (
            "Replace draft component placeholders",
            [str(source_dir / "components.yaml")],
            [
                "Replace placeholder invariants with concrete local guarantees.",
                "Replace placeholder failure semantics with explicit fail-loud behavior.",
                "Replace placeholder implementation constraints with real coding constraints.",
            ],
        )
    if bucket_key == "schemas":
        return (
            "Repair schema definitions and schema references",
            [str(source_dir / "schemas.yaml"), str(source_dir / "components.yaml")],
            [
                "Define missing schemas or correct schema_id references on ports.",
                "For optional fields, declare both optional_reason and absence_meaning.",
                "Replace unsupported draft schema placeholders with explicit object schemas.",
            ],
        )
    if bucket_key == "architecture":
        return (
            "Repair bindings, graph structure, or state ownership",
            [str(source_dir / "architecture.yaml")],
            [
                "Fix missing components or ports referenced by bindings.",
                "Keep source and target schemas identical on every binding.",
                "Remove graph cycles and keep state-store ownership explicit.",
            ],
        )
    if bucket_key == "component_interface":
        return (
            "Repair component interface declarations",
            [str(source_dir / "components.yaml")],
            [
                "Keep input and output port names unique within each component.",
                "Align port declarations with the fixtures and bindings that reference them.",
            ],
        )
    if bucket_key == "planning":
        target = upstream_plan_path if upstream_plan_path is not None else str(source_dir / "metadata.yaml")
        actions = [
            "Resolve the unresolved planning question explicitly before the next freeze attempt.",
            "Reflect the chosen answer in the draft bundle files so the freeze retry is unambiguous.",
        ]
        if upstream_plan_path is not None:
            actions.append("If you update the upstream plan, regenerate the draft bundle before retrying freeze.")
        return (
            "Resolve unresolved planning questions",
            [target],
            actions,
        )
    return (
        "Resolve uncategorized freeze findings",
        [str(source_dir / "validation.yaml")],
        [
            "Inspect the referenced findings and update the cited bundle files directly.",
            "Retry freeze once the bundle is consistent with the frozen AC14 contract.",
        ],
    )


def _read_upstream_plan_path(source_dir: Path) -> str | None:
    """Read the upstream planning artifact path from metadata when available."""

    metadata_payload = yaml.safe_load((source_dir / "metadata.yaml").read_text())
    source_kind = metadata_payload["metadata"].get("source_kind")
    created_from = metadata_payload["metadata"].get("created_from")
    if source_kind == "draft_plan_artifact" and isinstance(created_from, str):
        return created_from
    return None


def _dedupe(values: Iterable[str]) -> list[str]:
    """Return input strings without duplicates while preserving first-seen order."""

    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique

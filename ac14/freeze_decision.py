"""Explicit freeze decisions and promotion for AC14 bundles.

This module keeps structural freeze decisions and semantic freeze review
artifacts adjacent so front-half quality can be evaluated before final
system execution.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal, cast

from pydantic import BaseModel, Field
import yaml  # type: ignore[import-untyped]

from ac14.blueprint_planning import DraftBlueprintPlanArtifact
from ac14.draft_authoring import FreezeReadinessReport
from ac14.loader import REQUIRED_FILES, load_blueprint_dir
from ac14.models import ValidationFinding
from ac14.validation import validate_blueprint

FREEZE_SEMANTIC_REVIEW_PROMPT_PATH = (
    Path(__file__).resolve().parents[1] / "prompts" / "review_freeze_semantic.yaml"
)
DEFAULT_FREEZE_SEMANTIC_MODEL = "gemini/gemini-2.5-flash-lite"
DEFAULT_FREEZE_SEMANTIC_MAX_BUDGET = 0.50


async def acall_llm_structured(*args: Any, **kwargs: Any) -> Any:
    """Lazily import llm_client structured calls for freeze-semantic review."""

    from llm_client import acall_llm_structured as _acall_llm_structured  # type: ignore[import-not-found]

    return await _acall_llm_structured(*args, **kwargs)


def render_prompt(*args: Any, **kwargs: Any) -> Any:
    """Lazily import llm_client prompt rendering for freeze-semantic review."""

    from llm_client import render_prompt as _render_prompt

    return _render_prompt(*args, **kwargs)


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
    semantic_review_path: str | None = Field(
        default=None,
        description="Path to the persisted freeze-semantic review artifact when one was built.",
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


class FreezeSemanticRequirementAssessment(BaseModel):
    """Assessment of one requirement against the draft/freeze result."""

    requirement: str = Field(description="Requirement text under review.")
    verdict: Literal["satisfied", "partially_satisfied", "not_satisfied", "concern"] = Field(
        description="Assessment verdict for this requirement.",
    )
    rationale: str = Field(description="Concise reason for the verdict.")


class FreezeSemanticReviewResponse(BaseModel):
    """Structured semantic review of draft/freeze quality."""

    overall_verdict: Literal["accept", "concern", "reject"] = Field(
        description="Overall verdict for the draft/freeze result.",
    )
    freeze_verdict: Literal["ready", "promising_but_blocked", "blocked"] = Field(
        description="Whether the draft looks ready, promising but blocked, or blocked outright.",
    )
    summary: str = Field(description="Short semantic review summary.")
    strengths: list[str] = Field(description="Concrete strengths in the current draft/freeze result.")
    concerns: list[str] = Field(description="Concrete weaknesses or risks in the current draft/freeze result.")
    requirement_assessments: list[FreezeSemanticRequirementAssessment] = Field(
        description="Per-requirement assessments.",
    )
    recommended_next_steps: list[str] = Field(
        description="Concrete next steps to improve the draft/freeze result.",
    )


class FreezeSemanticReviewArtifact(BaseModel):
    """Persisted semantic review attached directly to a freeze decision."""

    source_bundle_dir: str = Field(description="Bundle directory reviewed semantically.")
    readiness_report_path: str = Field(description="Readiness report used for the semantic review.")
    upstream_plan_path: str = Field(description="Draft planning artifact used for the semantic review.")
    freeze_approved: bool = Field(description="Whether the draft bundle was structurally approved for freeze.")
    blocking_finding_codes: list[str] = Field(
        description="Blocking finding codes visible at freeze time.",
    )
    review: FreezeSemanticReviewResponse = Field(
        description="Structured semantic review of the draft/freeze result.",
    )


async def abuild_freeze_decision(
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

    semantic_review_path: str | None = None
    if readiness_report_path is not None:
        upstream_plan_path = _read_upstream_plan_path(source_dir)
        if upstream_plan_path is None:
            raise ValueError(
                "freeze semantic review requires an upstream planning artifact path in metadata.yaml",
            )
        if readiness_path is None:
            raise ValueError("freeze semantic review requires a readiness report path")
        await abuild_freeze_semantic_review(
            source_bundle_dir=source_dir,
            readiness_report_path=readiness_path,
            upstream_plan_path=Path(upstream_plan_path),
            output_dir=destination,
            freeze_approved=approved,
            findings=findings,
            remediation_plan=remediation_plan,
        )
        semantic_review_path = str(destination / "freeze_semantic_review.json")

    decision = FreezeDecisionArtifact(
        source_bundle_dir=str(source_dir),
        readiness_report_path=str(readiness_path) if readiness_report_path is not None else None,
        approved=approved,
        decision_summary=decision_summary,
        findings=findings,
        promoted_bundle_dir=promoted_bundle_dir,
        semantic_review_path=semantic_review_path,
        remediation_plan_path=str(remediation_path),
    )
    (destination / "freeze_decision.json").write_text(
        json.dumps(decision.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return decision


def build_freeze_decision(
    bundle_dir: Path | str,
    output_dir: Path | str,
    *,
    readiness_report_path: Path | str | None = None,
) -> FreezeDecisionArtifact:
    """Synchronous wrapper for persisted freeze decisions."""

    return asyncio.run(
        abuild_freeze_decision(
            bundle_dir=bundle_dir,
            output_dir=output_dir,
            readiness_report_path=readiness_report_path,
        ),
    )


async def abuild_freeze_semantic_review(
    *,
    source_bundle_dir: Path | str,
    readiness_report_path: Path | str,
    upstream_plan_path: Path | str,
    output_dir: Path | str,
    freeze_approved: bool,
    findings: list[ValidationFinding],
    remediation_plan: FreezeRemediationPlan,
) -> FreezeSemanticReviewArtifact:
    """Persist a semantic review artifact attached directly to the freeze decision."""

    source_dir = Path(source_bundle_dir)
    readiness_path = Path(readiness_report_path)
    plan_path = Path(upstream_plan_path)
    destination = Path(output_dir)

    review = await areview_freeze_semantic_quality(
        source_bundle_dir=source_dir,
        readiness_report_path=readiness_path,
        upstream_plan_path=plan_path,
        freeze_approved=freeze_approved,
        findings=findings,
        remediation_plan=remediation_plan,
    )
    artifact = FreezeSemanticReviewArtifact(
        source_bundle_dir=str(source_dir),
        readiness_report_path=str(readiness_path),
        upstream_plan_path=str(plan_path),
        freeze_approved=freeze_approved,
        blocking_finding_codes=sorted(
            {
                finding.code
                for finding in findings
                if finding.code.startswith("E-")
            },
        ),
        review=review,
    )
    (destination / "freeze_semantic_review.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def build_freeze_semantic_review(
    *,
    source_bundle_dir: Path | str,
    readiness_report_path: Path | str,
    upstream_plan_path: Path | str,
    output_dir: Path | str,
    freeze_approved: bool,
    findings: list[ValidationFinding],
    remediation_plan: FreezeRemediationPlan,
) -> FreezeSemanticReviewArtifact:
    """Synchronous wrapper for attached freeze-semantic review artifacts."""

    return asyncio.run(
        abuild_freeze_semantic_review(
            source_bundle_dir=source_bundle_dir,
            readiness_report_path=readiness_report_path,
            upstream_plan_path=upstream_plan_path,
            output_dir=output_dir,
            freeze_approved=freeze_approved,
            findings=findings,
            remediation_plan=remediation_plan,
        ),
    )


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
    if finding.code in {
        "W-DRAFT-DEPENDENCY-QUESTION",
        "E-DRAFT-DEPENDENCY-PROBE-BLOCKED",
    }:
        return "dependencies"
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
    if bucket_key == "dependencies":
        target_files = []
        if upstream_plan_path is not None:
            target_files.append(upstream_plan_path)
            dependency_execution_path = _read_upstream_dependency_execution_path(upstream_plan_path)
            if dependency_execution_path is not None:
                target_files.append(dependency_execution_path)
        if not target_files:
            target_files.append(str(source_dir / "metadata.yaml"))
        actions = [
            "Inspect blocked dependency probes and decide whether to revise the dependency plan or rerun probing with explicit operator approval.",
            "Do not retry freeze until every dependency needed by the draft plan is either confirmed or removed from scope.",
        ]
        if upstream_plan_path is not None:
            actions.append(
                "If you update the upstream plan or dependency execution artifact, regenerate the draft bundle before retrying freeze.",
            )
        return (
            "Resolve blocked dependency probes",
            target_files,
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


def _read_upstream_dependency_execution_path(upstream_plan_path: str) -> str | None:
    """Read the dependency execution artifact path from an upstream plan when available."""

    payload = json.loads(Path(upstream_plan_path).read_text())
    path = payload.get("dependency_execution_artifact_path")
    return path if isinstance(path, str) and path else None


def _dedupe(values: Iterable[str]) -> list[str]:
    """Return input strings without duplicates while preserving first-seen order."""

    unique: list[str] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique


async def areview_freeze_semantic_quality(
    *,
    source_bundle_dir: Path,
    readiness_report_path: Path,
    upstream_plan_path: Path,
    freeze_approved: bool,
    findings: list[ValidationFinding],
    remediation_plan: FreezeRemediationPlan,
) -> FreezeSemanticReviewResponse:
    """Run one semantic review over draft/freeze quality."""

    fixture_path = os.environ.get("AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE")
    if fixture_path:
        return FreezeSemanticReviewResponse.model_validate_json(Path(fixture_path).read_text())

    plan = DraftBlueprintPlanArtifact.model_validate_json(upstream_plan_path.read_text())
    readiness_report = FreezeReadinessReport.model_validate_json(readiness_report_path.read_text())
    messages = render_prompt(
        FREEZE_SEMANTIC_REVIEW_PROMPT_PATH,
        source_bundle_dir=str(source_bundle_dir),
        requirements=plan.requirements,
        planning_summary=plan.planning_summary,
        packetization_notes=plan.packetization_notes,
        dependency_decisions=plan.dependency_decisions,
        open_questions=[
            {
                "question": question.question,
                "why_it_matters": question.why_it_matters,
            }
            for question in plan.open_questions
        ],
        readiness_summary={
            "ready": readiness_report.ready,
            "validation_passed": readiness_report.validation_passed,
            "findings": [
                {
                    "code": finding.code,
                    "path": finding.path,
                    "message": finding.message,
                }
                for finding in readiness_report.findings
            ],
        },
        freeze_summary={
            "freeze_approved": freeze_approved,
            "blocking_finding_codes": sorted(
                {
                    finding.code
                    for finding in findings
                    if finding.code.startswith("E-")
                },
            ),
            "remediation_summary": remediation_plan.summary,
            "remediation_tasks": [
                {
                    "title": task.title,
                    "summary": task.summary,
                    "target_files": task.target_files,
                    "authoring_actions": task.authoring_actions,
                }
                for task in remediation_plan.tasks
            ],
        },
    )
    response, _meta = cast(
        tuple[FreezeSemanticReviewResponse, object],
        await acall_llm_structured(
            DEFAULT_FREEZE_SEMANTIC_MODEL,
            messages,
            response_model=FreezeSemanticReviewResponse,
            task="ac14_freeze_semantic_review",
            trace_id=f"ac14/freeze_semantic/{source_bundle_dir.name}",
            max_budget=DEFAULT_FREEZE_SEMANTIC_MAX_BUDGET,
        ),
    )
    return response


def _review_freeze_semantic_quality(
    *,
    source_bundle_dir: Path,
    readiness_report_path: Path,
    upstream_plan_path: Path,
    freeze_approved: bool,
    findings: list[ValidationFinding],
    remediation_plan: FreezeRemediationPlan,
) -> FreezeSemanticReviewResponse:
    """Synchronous wrapper for freeze semantic review."""

    return asyncio.run(
        areview_freeze_semantic_quality(
            source_bundle_dir=source_bundle_dir,
            readiness_report_path=readiness_report_path,
            upstream_plan_path=upstream_plan_path,
            freeze_approved=freeze_approved,
            findings=findings,
            remediation_plan=remediation_plan,
        ),
    )

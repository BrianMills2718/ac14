"""Realistic-input front-half acceptance for discovery-through-freeze workflows."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal, cast

from pydantic import BaseModel, Field

from ac14.blueprint_planning import abuild_draft_blueprint_plan
from ac14.dependency_execution import build_dependency_execution_artifact
from ac14.dependency_planning import abuild_dependency_plan
from ac14.discovery import DiscoveryArtifact, build_discovery_artifact
from ac14.draft_authoring import materialize_draft_blueprint_bundle
from ac14.freeze_decision import FreezeDecisionArtifact, build_freeze_decision
from llm_client import acall_llm_structured, render_prompt  # type: ignore[import-not-found]


DEFAULT_FRONT_HALF_ACCEPTANCE_MODEL = "gemini/gemini-2.5-flash-lite"
DEFAULT_FRONT_HALF_ACCEPTANCE_MAX_BUDGET = 0.50
FRONT_HALF_ACCEPTANCE_PROMPT_PATH = (
    Path(__file__).resolve().parents[1] / "prompts" / "review_front_half_acceptance.yaml"
)


class FrontHalfRequirementAssessment(BaseModel):
    """Assessment of one requirement against the front-half result."""

    requirement: str = Field(description="Requirement text under review.")
    verdict: Literal["satisfied", "partially_satisfied", "not_satisfied", "concern"] = Field(
        description="Assessment verdict for this requirement.",
    )
    rationale: str = Field(description="Concise reason for the verdict.")


class FrontHalfReviewResponse(BaseModel):
    """Structured LLM review of the realistic-input front half."""

    overall_verdict: Literal["accept", "concern", "reject"] = Field(
        description="Overall verdict for the front-half result.",
    )
    freeze_verdict: Literal["ready", "promising_but_blocked", "blocked"] = Field(
        description="Whether the front half looks ready, promising but blocked, or blocked outright.",
    )
    summary: str = Field(description="Short review summary.")
    strengths: list[str] = Field(description="Strong aspects of the front-half result.")
    concerns: list[str] = Field(description="Concrete concerns found in the front-half result.")
    requirement_assessments: list[FrontHalfRequirementAssessment] = Field(
        description="Per-requirement assessments.",
    )
    recommended_next_steps: list[str] = Field(
        description="Concrete next steps to improve the front-half result.",
    )


class FrontHalfArtifactPaths(BaseModel):
    """Persisted paths for each front-half artifact."""

    discovery_artifact_path: str = Field(description="Path to the persisted discovery artifact.")
    dependency_plan_path: str = Field(description="Path to the persisted dependency plan.")
    dependency_execution_artifact_path: str = Field(
        description="Path to the persisted dependency execution artifact.",
    )
    draft_blueprint_plan_path: str = Field(
        description="Path to the persisted draft blueprint planning artifact.",
    )
    draft_bundle_dir: str = Field(description="Directory containing the authored draft bundle.")
    freeze_readiness_report_path: str = Field(
        description="Path to the persisted freeze-readiness report.",
    )
    freeze_decision_path: str = Field(description="Path to the persisted freeze decision artifact.")


class FrontHalfAcceptanceArtifact(BaseModel):
    """Persisted realistic-input acceptance artifact for the AC14 front half."""

    input_path: str = Field(description="Input file inspected by the front half.")
    requirements: list[str] = Field(description="Requirements reviewed by the front-half artifact.")
    requested_packages: list[str] = Field(
        description="Packages explicitly requested for discovery and planning.",
    )
    retrieval_artifact_paths: list[str] = Field(
        description="External retrieval artifact paths carried into discovery when provided.",
    )
    allow_install: bool = Field(description="Whether dependency probing was allowed to install packages.")
    artifact_paths: FrontHalfArtifactPaths = Field(
        description="Persisted paths for the sub-artifacts produced by the front-half pipeline.",
    )
    freeze_approved: bool = Field(description="Whether the resulting draft bundle was approved for freeze.")
    blocking_finding_codes: list[str] = Field(
        description="Blocking finding codes carried by the freeze decision.",
    )
    review: FrontHalfReviewResponse = Field(
        description="Structured review of the front-half result against the requirements.",
    )


async def abuild_front_half_acceptance_report(
    input_path: Path | str,
    output_dir: Path | str,
    *,
    requirements: list[str],
    project_root: Path | str | None = None,
    requested_packages: list[str] | None = None,
    retrieval_artifact_paths: Sequence[Path | str] | None = None,
    allow_install: bool = False,
    model: str = DEFAULT_FRONT_HALF_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_FRONT_HALF_ACCEPTANCE_MAX_BUDGET,
    max_samples: int = 5,
) -> FrontHalfAcceptanceArtifact:
    """Build a persisted realistic-input front-half acceptance artifact."""

    if not requirements:
        raise ValueError("front-half acceptance requires at least one requirement")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    normalized_input_path = Path(input_path)
    normalized_project_root = Path(project_root) if project_root is not None else None
    normalized_requested_packages = requested_packages or []
    normalized_retrieval_paths = [Path(path) for path in retrieval_artifact_paths or []]

    discovery_artifact = build_discovery_artifact(
        input_path=normalized_input_path,
        output_dir=destination / "discovery",
        project_root=normalized_project_root,
        requested_packages=normalized_requested_packages,
        retrieval_artifact_paths=normalized_retrieval_paths,
        max_samples=max_samples,
    )
    discovery_artifact_path = destination / "discovery" / "discovery_artifact.json"

    await abuild_dependency_plan(
        discovery_artifact_path=discovery_artifact_path,
        output_dir=destination / "dependency_plan",
        requirements=requirements,
    )
    dependency_plan_path = destination / "dependency_plan" / "dependency_plan.json"

    build_dependency_execution_artifact(
        dependency_plan_path=dependency_plan_path,
        output_dir=destination / "dependency_probe",
        allow_install=allow_install,
        project_root=normalized_project_root,
    )
    dependency_execution_path = destination / "dependency_probe" / "dependency_execution_artifact.json"

    await abuild_draft_blueprint_plan(
        discovery_artifact_path=discovery_artifact_path,
        output_dir=destination / "draft_plan",
        requirements=requirements,
        dependency_plan_path=dependency_plan_path,
        dependency_execution_artifact_path=dependency_execution_path,
    )
    draft_plan_path = destination / "draft_plan" / "draft_blueprint_plan.json"

    draft_bundle_manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=draft_plan_path,
        output_dir=destination / "draft_bundle",
    )
    freeze_decision = build_freeze_decision(
        bundle_dir=Path(draft_bundle_manifest.draft_bundle_dir),
        output_dir=destination / "freeze_decision",
        readiness_report_path=Path(draft_bundle_manifest.freeze_readiness_report_path),
    )
    freeze_decision_path = destination / "freeze_decision" / "freeze_decision.json"

    review = await _review_front_half_acceptance(
        input_path=normalized_input_path,
        requirements=requirements,
        discovery_artifact=discovery_artifact,
        dependency_plan_path=dependency_plan_path,
        dependency_execution_path=dependency_execution_path,
        draft_plan_path=draft_plan_path,
        freeze_decision=freeze_decision,
        model=model,
        max_budget=max_budget,
    )

    artifact = FrontHalfAcceptanceArtifact(
        input_path=str(normalized_input_path),
        requirements=requirements,
        requested_packages=normalized_requested_packages,
        retrieval_artifact_paths=[str(path) for path in normalized_retrieval_paths],
        allow_install=allow_install,
        artifact_paths=FrontHalfArtifactPaths(
            discovery_artifact_path=str(discovery_artifact_path),
            dependency_plan_path=str(dependency_plan_path),
            dependency_execution_artifact_path=str(dependency_execution_path),
            draft_blueprint_plan_path=str(draft_plan_path),
            draft_bundle_dir=draft_bundle_manifest.draft_bundle_dir,
            freeze_readiness_report_path=draft_bundle_manifest.freeze_readiness_report_path,
            freeze_decision_path=str(freeze_decision_path),
        ),
        freeze_approved=freeze_decision.approved,
        blocking_finding_codes=sorted(
            {
                finding.code
                for finding in freeze_decision.findings
                if finding.code.startswith("E-")
            },
        ),
        review=review,
    )
    (destination / "front_half_acceptance_report.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def build_front_half_acceptance_report(
    input_path: Path | str,
    output_dir: Path | str,
    *,
    requirements: list[str],
    project_root: Path | str | None = None,
    requested_packages: list[str] | None = None,
    retrieval_artifact_paths: Sequence[Path | str] | None = None,
    allow_install: bool = False,
    model: str = DEFAULT_FRONT_HALF_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_FRONT_HALF_ACCEPTANCE_MAX_BUDGET,
    max_samples: int = 5,
) -> FrontHalfAcceptanceArtifact:
    """Synchronous wrapper for realistic-input front-half acceptance."""

    return asyncio.run(
        abuild_front_half_acceptance_report(
            input_path=input_path,
            output_dir=output_dir,
            requirements=requirements,
            project_root=project_root,
            requested_packages=requested_packages,
            retrieval_artifact_paths=retrieval_artifact_paths,
            allow_install=allow_install,
            model=model,
            max_budget=max_budget,
            max_samples=max_samples,
        ),
    )


async def _review_front_half_acceptance(
    *,
    input_path: Path,
    requirements: list[str],
    discovery_artifact: DiscoveryArtifact,
    dependency_plan_path: Path,
    dependency_execution_path: Path,
    draft_plan_path: Path,
    freeze_decision: FreezeDecisionArtifact,
    model: str,
    max_budget: float,
) -> FrontHalfReviewResponse:
    """Run the LLM reviewer for the realistic-input front half."""

    fixture_path = os.environ.get("AC14_FRONT_HALF_ACCEPTANCE_FIXTURE")
    if fixture_path:
        return FrontHalfReviewResponse.model_validate_json(Path(fixture_path).read_text())

    dependency_plan_payload = json.loads(dependency_plan_path.read_text())
    dependency_execution_payload = json.loads(dependency_execution_path.read_text())
    draft_plan_payload = json.loads(draft_plan_path.read_text())
    messages = render_prompt(
        FRONT_HALF_ACCEPTANCE_PROMPT_PATH,
        input_path=str(input_path),
        requirements=requirements,
        discovery_summary=_build_discovery_summary(discovery_artifact),
        dependency_plan_summary=_build_dependency_plan_summary(dependency_plan_payload),
        dependency_execution_summary=_build_dependency_execution_summary(
            dependency_execution_payload,
        ),
        draft_plan_summary=_build_draft_plan_summary(draft_plan_payload),
        freeze_summary=_build_freeze_summary(freeze_decision),
    )
    response, _meta = await acall_llm_structured(
        model,
        messages,
        response_model=FrontHalfReviewResponse,
        task="ac14_front_half_acceptance_review",
        trace_id=f"ac14/front_half_acceptance/{input_path.stem}",
        max_budget=max_budget,
    )
    return cast(FrontHalfReviewResponse, response)


def _build_discovery_summary(artifact: DiscoveryArtifact) -> dict[str, object]:
    """Build a compact review summary from the discovery artifact."""

    inspection = artifact.input_inspection
    return {
        "input_path": inspection.input_path,
        "input_format": inspection.input_format,
        "root_kind": inspection.root_kind,
        "sample_count": inspection.sample_count,
        "truncated": inspection.truncated,
        "samples": inspection.sample_records,
        "field_summaries": [
            {
                "path": field.path,
                "observed_types": field.observed_types,
                "sample_values": field.sample_values,
            }
            for field in inspection.field_summaries[:10]
        ],
        "open_concerns": artifact.open_concerns,
    }


def _build_dependency_plan_summary(payload: dict[str, Any]) -> dict[str, object]:
    """Build a compact summary from the dependency-planning artifact."""

    recommendations = payload.get("recommendations", [])
    open_questions = payload.get("open_questions", [])
    return {
        "planning_summary": payload.get("planning_summary"),
        "recommendations": [
            {
                "package_name": recommendation["package_name"],
                "action": recommendation["action"],
                "capability_need": recommendation["capability_need"],
            }
            for recommendation in recommendations[:10]
        ],
        "open_questions": [question["question"] for question in open_questions[:10]],
    }


def _build_dependency_execution_summary(payload: dict[str, Any]) -> dict[str, object]:
    """Build a compact summary from the dependency execution artifact."""

    results = payload.get("results", [])
    return {
        "execution_mode": payload.get("execution_mode"),
        "environment_observations": payload.get("environment_observations", []),
        "results": [
            {
                "package_name": result["package_name"],
                "action": result["action"],
                "result": result["result"],
                "summary": result["summary"],
            }
            for result in results[:10]
        ],
    }


def _build_draft_plan_summary(payload: dict[str, Any]) -> dict[str, object]:
    """Build a compact summary from the draft blueprint plan."""

    components = payload.get("proposed_components", [])
    schemas = payload.get("proposed_schemas", [])
    return {
        "planning_summary": payload.get("planning_summary"),
        "proposed_schemas": [schema["schema_name"] for schema in schemas[:20]],
        "proposed_components": [
            {
                "component_id": component["component_id"],
                "semantic_responsibility": component["semantic_responsibility"],
                "packet_focus": component["packet_focus"],
            }
            for component in components[:20]
        ],
        "open_questions": [question["question"] for question in payload.get("open_questions", [])[:10]],
        "dependency_decisions": payload.get("dependency_decisions", [])[:10],
    }


def _build_freeze_summary(decision: FreezeDecisionArtifact) -> dict[str, object]:
    """Build a compact summary from the freeze decision artifact."""

    return {
        "approved": decision.approved,
        "decision_summary": decision.decision_summary,
        "blocking_finding_codes": [
            finding.code
            for finding in decision.findings
            if finding.code.startswith("E-")
        ],
        "finding_messages": [finding.message for finding in decision.findings[:12]],
    }

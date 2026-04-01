"""Realistic-input front-half acceptance for discovery-through-freeze workflows."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal, cast

from pydantic import BaseModel, Field

from ac14.blueprint_planning import (
    DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    DEFAULT_BLUEPRINT_PLAN_MODEL,
    abuild_draft_blueprint_plan,
)
from ac14.dependency_execution import build_dependency_execution_artifact
from ac14.dependency_planning import abuild_dependency_plan
from ac14.discovery import DiscoveryArtifact, build_discovery_artifact
from ac14.draft_authoring import materialize_draft_blueprint_bundle
from ac14.examples import ShippedBlueprintExample, discover_shipped_blueprints, resolve_realistic_input_path
from ac14.freeze_decision import FreezeDecisionArtifact, build_freeze_decision
from ac14.freeze_retry import FreezeRetryArtifact, abuild_freeze_retry_artifact
from ac14.loader import load_blueprint_dir
from llm_client import acall_llm_structured, render_prompt  # type: ignore[import-not-found]


DEFAULT_FRONT_HALF_ACCEPTANCE_MODEL = "gemini/gemini-2.5-flash-lite"
DEFAULT_FRONT_HALF_ACCEPTANCE_MAX_BUDGET = 0.50
DEFAULT_FRONT_HALF_RETRY_MODEL = DEFAULT_BLUEPRINT_PLAN_MODEL
DEFAULT_FRONT_HALF_RETRY_MAX_BUDGET = DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET
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
    freeze_semantic_review_path: str | None = Field(
        default=None,
        description="Path to the persisted freeze-semantic review artifact when one was built.",
    )
    retry_freeze_artifact_path: str | None = Field(
        default=None,
        description="Path to the persisted retry-chain artifact when retry was attempted.",
    )


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
    final_freeze_approved: bool = Field(
        description="Whether the front-half result ended in freeze approval after any bounded retry.",
    )
    retry_freeze_attempted: bool = Field(
        description="Whether one explicit retry chain was attempted after blocked freeze.",
    )
    retry_freeze_approved: bool | None = Field(
        default=None,
        description="Whether the retry chain reached freeze approval when one was attempted.",
    )
    blocking_finding_codes: list[str] = Field(
        description="Blocking finding codes carried by the freeze decision.",
    )
    review: FrontHalfReviewResponse = Field(
        description="Structured review of the front-half result against the requirements.",
    )


class FrontHalfSuiteExampleResult(BaseModel):
    """Per-example front-half breadth result across shipped examples."""

    example_id: str = Field(description="Shipped example identifier.")
    blueprint_dir: str = Field(description="Blueprint directory reviewed for this result.")
    realistic_input_path: str | None = Field(
        default=None,
        description="Realistic-input artifact used for this example when available.",
    )
    realistic_input_profile: str | None = Field(
        default=None,
        description="Requested realistic-input profile used for this example when one was selected.",
    )
    requirements: list[str] = Field(
        description="Requirements used for this example's front-half review.",
    )
    overall_verdict: Literal["accept", "concern", "reject", "missing_input", "missing_profile"] = Field(
        description="Compact suite-level verdict for this example.",
    )
    freeze_approved: bool | None = Field(
        default=None,
        description="Whether the per-example front-half freeze decision approved promotion.",
    )
    final_freeze_approved: bool | None = Field(
        default=None,
        description="Whether the per-example front-half result ended in freeze approval after any retry.",
    )
    retry_freeze_attempted: bool = Field(
        default=False,
        description="Whether one retry chain was attempted for this example.",
    )
    retry_freeze_approved: bool | None = Field(
        default=None,
        description="Whether the retry chain reached freeze approval for this example.",
    )
    retry_freeze_artifact_path: str | None = Field(
        default=None,
        description="Retry-chain artifact path for this example when retry was attempted.",
    )
    freeze_semantic_review_path: str | None = Field(
        default=None,
        description="Attached freeze-semantic review path from the per-example artifact.",
    )
    report_path: str | None = Field(
        default=None,
        description="Per-example front-half acceptance report path when one was produced.",
    )
    reason: str | None = Field(
        default=None,
        description="Reason for a missing-input or rejected example result.",
    )


class FrontHalfSuiteAcceptanceReport(BaseModel):
    """Persisted suite-level front-half acceptance breadth artifact."""

    realistic_input_profile: str | None = Field(
        default=None,
        description="Requested realistic-input profile used across the suite when one was selected.",
    )
    example_count: int = Field(description="Number of shipped examples considered in the suite.")
    accepted_examples: int = Field(description="Examples with accept front-half verdicts.")
    concern_examples: int = Field(description="Examples with concern front-half verdicts.")
    rejected_examples: int = Field(description="Examples with reject front-half verdicts.")
    missing_input_examples: int = Field(
        description="Examples that could not run because realistic-input artifacts were missing.",
    )
    missing_profile_examples: int = Field(
        description="Examples that could not run because the requested realistic-input profile was absent.",
    )
    freeze_approved_examples: int = Field(
        description="Examples whose front-half freeze decision approved promotion.",
    )
    freeze_blocked_examples: int = Field(
        description="Examples whose front-half freeze decision remained blocked.",
    )
    final_freeze_approved_examples: int = Field(
        description="Examples whose front-half result ended in freeze approval after any retry.",
    )
    retry_attempted_examples: int = Field(
        description="Examples where one retry chain was attempted.",
    )
    retry_approved_examples: int = Field(
        description="Examples where the retry chain reached freeze approval.",
    )
    examples: list[FrontHalfSuiteExampleResult] = Field(
        description="Per-example front-half breadth results.",
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
    retry_blocked_freeze: bool = False,
    retry_model: str = DEFAULT_FRONT_HALF_RETRY_MODEL,
    retry_max_budget: float = DEFAULT_FRONT_HALF_RETRY_MAX_BUDGET,
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
    retry_artifact: FreezeRetryArtifact | None = None
    if retry_blocked_freeze and not freeze_decision.approved:
        retry_artifact = await abuild_freeze_retry_artifact(
            plan_artifact_path=draft_plan_path,
            freeze_decision_path=freeze_decision_path,
            output_dir=destination / "freeze_retry",
            model=retry_model,
            max_budget=retry_max_budget,
        )

    review = await _review_front_half_acceptance(
        input_path=normalized_input_path,
        requirements=requirements,
        discovery_artifact=discovery_artifact,
        dependency_plan_path=dependency_plan_path,
        dependency_execution_path=dependency_execution_path,
        draft_plan_path=draft_plan_path,
        freeze_decision=freeze_decision,
        retry_artifact=retry_artifact,
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
            freeze_semantic_review_path=freeze_decision.semantic_review_path,
            retry_freeze_artifact_path=(
                str(destination / "freeze_retry" / "freeze_retry_artifact.json")
                if retry_artifact is not None
                else None
            ),
        ),
        freeze_approved=freeze_decision.approved,
        final_freeze_approved=retry_artifact.approved if retry_artifact is not None else freeze_decision.approved,
        retry_freeze_attempted=retry_artifact is not None,
        retry_freeze_approved=retry_artifact.approved if retry_artifact is not None else None,
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
    retry_blocked_freeze: bool = False,
    retry_model: str = DEFAULT_FRONT_HALF_RETRY_MODEL,
    retry_max_budget: float = DEFAULT_FRONT_HALF_RETRY_MAX_BUDGET,
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
            retry_blocked_freeze=retry_blocked_freeze,
            retry_model=retry_model,
            retry_max_budget=retry_max_budget,
            max_samples=max_samples,
        ),
    )


async def abuild_front_half_acceptance_suite_report(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    realistic_input_profile: str | None = None,
    allow_install: bool = False,
    model: str = DEFAULT_FRONT_HALF_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_FRONT_HALF_ACCEPTANCE_MAX_BUDGET,
    retry_blocked_freeze: bool = False,
    retry_model: str = DEFAULT_FRONT_HALF_RETRY_MODEL,
    retry_max_budget: float = DEFAULT_FRONT_HALF_RETRY_MAX_BUDGET,
    max_samples: int = 5,
) -> FrontHalfSuiteAcceptanceReport:
    """Build persisted front-half acceptance artifacts across shipped examples."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    examples: list[FrontHalfSuiteExampleResult] = []
    accepted_examples = 0
    concern_examples = 0
    rejected_examples = 0
    missing_input_examples = 0
    missing_profile_examples = 0
    freeze_approved_examples = 0
    freeze_blocked_examples = 0
    final_freeze_approved_examples = 0
    retry_attempted_examples = 0
    retry_approved_examples = 0

    for example in discover_shipped_blueprints(examples_root):
        try:
            realistic_input_path = (
                resolve_realistic_input_path(example, profile=realistic_input_profile)
                if realistic_input_profile is not None
                else _discover_realistic_input_path(example)
            )
        except ValueError as exc:
            missing_verdict: Literal["missing_profile", "missing_input"] = (
                "missing_profile" if realistic_input_profile is not None else "missing_input"
            )
            examples.append(
                FrontHalfSuiteExampleResult(
                    example_id=example.example_id,
                    blueprint_dir=example.blueprint_dir,
                    realistic_input_path=None,
                    realistic_input_profile=realistic_input_profile,
                    requirements=[],
                    overall_verdict=missing_verdict,
                    freeze_approved=None,
                    freeze_semantic_review_path=None,
                    report_path=None,
                    reason=str(exc),
                ),
            )
            if realistic_input_profile is not None:
                missing_profile_examples += 1
            else:
                missing_input_examples += 1
            continue

        requirements = _front_half_suite_requirements(example)
        report = await abuild_front_half_acceptance_report(
            input_path=realistic_input_path,
            output_dir=destination / example.example_id,
            requirements=requirements,
            project_root=Path(example.blueprint_dir).resolve().parents[2],
            requested_packages=[],
            retrieval_artifact_paths=[],
            allow_install=allow_install,
            model=model,
            max_budget=max_budget,
            retry_blocked_freeze=retry_blocked_freeze,
            retry_model=retry_model,
            retry_max_budget=retry_max_budget,
            max_samples=max_samples,
        )
        overall_verdict = report.review.overall_verdict
        if overall_verdict == "accept":
            accepted_examples += 1
        elif overall_verdict == "concern":
            concern_examples += 1
        else:
            rejected_examples += 1
        if report.freeze_approved:
            freeze_approved_examples += 1
        else:
            freeze_blocked_examples += 1
        if report.final_freeze_approved:
            final_freeze_approved_examples += 1
        if report.retry_freeze_attempted:
            retry_attempted_examples += 1
        if report.retry_freeze_approved:
            retry_approved_examples += 1
        examples.append(
            FrontHalfSuiteExampleResult(
                example_id=example.example_id,
                blueprint_dir=example.blueprint_dir,
                realistic_input_path=str(realistic_input_path),
                realistic_input_profile=realistic_input_profile,
                requirements=requirements,
                overall_verdict=overall_verdict,
                freeze_approved=report.freeze_approved,
                final_freeze_approved=report.final_freeze_approved,
                retry_freeze_attempted=report.retry_freeze_attempted,
                retry_freeze_approved=report.retry_freeze_approved,
                retry_freeze_artifact_path=report.artifact_paths.retry_freeze_artifact_path,
                freeze_semantic_review_path=report.artifact_paths.freeze_semantic_review_path,
                report_path=str(destination / example.example_id / "front_half_acceptance_report.json"),
                reason=None,
            ),
        )

    suite_report = FrontHalfSuiteAcceptanceReport(
        realistic_input_profile=realistic_input_profile,
        example_count=len(examples),
        accepted_examples=accepted_examples,
        concern_examples=concern_examples,
        rejected_examples=rejected_examples,
        missing_input_examples=missing_input_examples,
        missing_profile_examples=missing_profile_examples,
        freeze_approved_examples=freeze_approved_examples,
        freeze_blocked_examples=freeze_blocked_examples,
        final_freeze_approved_examples=final_freeze_approved_examples,
        retry_attempted_examples=retry_attempted_examples,
        retry_approved_examples=retry_approved_examples,
        examples=examples,
    )
    (destination / "front_half_acceptance_suite_report.json").write_text(
        json.dumps(suite_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return suite_report


def build_front_half_acceptance_suite_report(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    realistic_input_profile: str | None = None,
    allow_install: bool = False,
    model: str = DEFAULT_FRONT_HALF_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_FRONT_HALF_ACCEPTANCE_MAX_BUDGET,
    retry_blocked_freeze: bool = False,
    retry_model: str = DEFAULT_FRONT_HALF_RETRY_MODEL,
    retry_max_budget: float = DEFAULT_FRONT_HALF_RETRY_MAX_BUDGET,
    max_samples: int = 5,
) -> FrontHalfSuiteAcceptanceReport:
    """Synchronous wrapper for suite-level front-half acceptance."""

    return asyncio.run(
        abuild_front_half_acceptance_suite_report(
            output_dir=output_dir,
            examples_root=examples_root,
            realistic_input_profile=realistic_input_profile,
            allow_install=allow_install,
            model=model,
            max_budget=max_budget,
            retry_blocked_freeze=retry_blocked_freeze,
            retry_model=retry_model,
            retry_max_budget=retry_max_budget,
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
    retry_artifact: FreezeRetryArtifact | None,
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
        retry_freeze_summary=_build_retry_freeze_summary(retry_artifact),
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


def _build_retry_freeze_summary(
    artifact: FreezeRetryArtifact | None,
) -> dict[str, object] | None:
    """Build a compact summary from the optional retry-chain artifact."""

    if artifact is None:
        return None
    return {
        "refinement_round": artifact.refinement_round,
        "approved": artifact.approved,
        "summary": artifact.summary,
        "refined_draft_blueprint_plan_path": artifact.refined_draft_blueprint_plan_path,
        "refreshed_freeze_decision_path": artifact.refreshed_freeze_decision_path,
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


def _discover_realistic_input_path(example: ShippedBlueprintExample | object) -> Path:
    """Return the default realistic-input artifact for one shipped example."""

    typed_example = (
        example
        if isinstance(example, ShippedBlueprintExample)
        else ShippedBlueprintExample.model_validate(example)
    )
    if typed_example.realistic_input_policy is not None:
        return resolve_realistic_input_path(typed_example)
    example_dir = Path(typed_example.blueprint_dir).parent
    input_dir = example_dir / "input"
    if not input_dir.is_dir():
        raise ValueError(f"no input directory found for shipped example {typed_example.example_id}")
    candidates = sorted(input_dir.glob("*.json"))
    if not candidates:
        raise ValueError(
            f"no realistic-input json artifact found for shipped example {typed_example.example_id}",
        )
    return candidates[0]


def _front_half_suite_requirements(example: ShippedBlueprintExample | object) -> list[str]:
    """Derive explicit suite requirements from realistic-input semantic scenarios."""

    typed_example = (
        example
        if isinstance(example, ShippedBlueprintExample)
        else ShippedBlueprintExample.model_validate(example)
    )
    blueprint = load_blueprint_dir(typed_example.blueprint_dir)
    requirements = [
        requirement
        for scenario in blueprint.scenarios.values()
        if scenario.kind == "semantic_acceptance" and scenario.realistic_input
        for requirement in scenario.requirements
    ]
    deduped_requirements: list[str] = []
    for requirement in requirements:
        if requirement not in deduped_requirements:
            deduped_requirements.append(requirement)
    if not deduped_requirements:
        raise ValueError(
            f"no realistic-input semantic requirements found for shipped example {typed_example.example_id}",
        )
    return deduped_requirements

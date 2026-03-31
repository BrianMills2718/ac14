"""Evidence-backed dependency and library planning before blueprint freeze."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, Field

from ac14.discovery import DependencyStatus, DiscoveryArtifact
from llm_client import acall_llm_structured, render_prompt  # type: ignore[import-not-found]


DEFAULT_DEPENDENCY_PLAN_MODEL = "gemini/gemini-2.5-flash-lite"
DEFAULT_DEPENDENCY_PLAN_MAX_BUDGET = 0.50
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "plan_dependencies.yaml"
DependencyAction = Literal["reuse", "install", "investigate", "avoid"]
EvidenceSource = Literal[
    "requirement",
    "input_discovery",
    "environment",
    "project_context",
    "external_retrieval",
    "open_concern",
]


class DependencyEvidence(BaseModel):
    """One explicit piece of evidence supporting a dependency decision."""

    source: EvidenceSource = Field(description="Where this supporting evidence came from.")
    locator: str = Field(description="Compact locator or identifier for this evidence.")
    detail: str = Field(description="Why this evidence matters for the recommendation.")


class DependencyRecommendation(BaseModel):
    """One advisory dependency or library decision grounded in discovery evidence."""

    package_name: str = Field(description="Third-party package name under consideration.")
    action: DependencyAction = Field(
        description="Advisory action: reuse, install, investigate, or avoid.",
    )
    capability_need: str = Field(
        description="What capability or requirement this package decision is meant to satisfy.",
    )
    justification: str = Field(description="Why this action is the best current recommendation.")
    already_installed: bool = Field(
        description="Whether the package is already installed in the current environment.",
    )
    install_command: str | None = Field(
        default=None,
        description="Explicit install command when action is install.",
    )
    evidence: list[DependencyEvidence] = Field(
        description="Explicit evidence supporting this recommendation.",
    )


class DependencyQuestion(BaseModel):
    """One dependency or library question that must be resolved before freeze."""

    question: str = Field(description="Concrete unresolved dependency or library question.")
    why_it_matters: str = Field(description="Why the question matters before blueprint freeze.")


class DependencyPlanningResponse(BaseModel):
    """Structured LLM response for dependency and library planning."""

    planning_summary: str = Field(
        description="Short summary of the dependency/library strategy before freeze.",
    )
    recommendations: list[DependencyRecommendation] = Field(
        description="Advisory dependency recommendations grounded in discovery context.",
    )
    standard_library_notes: list[str] = Field(
        description="Notes where Python standard library is sufficient and third-party packages are unnecessary.",
    )
    open_questions: list[DependencyQuestion] = Field(
        description="Dependency or library questions still unresolved.",
    )


class DependencyPlanningArtifact(BaseModel):
    """Persisted dependency-planning artifact built from discovery plus requirements."""

    discovery_artifact_path: str = Field(
        description="Path to the persisted discovery artifact used as input.",
    )
    requirements: list[str] = Field(description="Requirements used for dependency planning.")
    carried_forward_concerns: list[str] = Field(
        description="Discovery concerns that still matter for dependency planning.",
    )
    planning_summary: str = Field(
        description="Short summary of the dependency/library strategy before freeze.",
    )
    recommendations: list[DependencyRecommendation] = Field(
        description="Advisory dependency recommendations grounded in discovery context.",
    )
    standard_library_notes: list[str] = Field(
        description="Notes where standard library coverage is sufficient.",
    )
    open_questions: list[DependencyQuestion] = Field(
        description="Dependency or library questions still unresolved.",
    )


async def abuild_dependency_plan(
    discovery_artifact_path: Path | str,
    output_dir: Path | str,
    *,
    requirements: list[str],
    model: str = DEFAULT_DEPENDENCY_PLAN_MODEL,
    max_budget: float = DEFAULT_DEPENDENCY_PLAN_MAX_BUDGET,
    task: str = "ac14_dependency_plan",
) -> DependencyPlanningArtifact:
    """Build a persisted dependency and library planning artifact from discovery."""

    if not requirements:
        raise ValueError("dependency planning requires at least one requirement")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    artifact_path = Path(discovery_artifact_path)
    discovery_artifact = DiscoveryArtifact.model_validate_json(artifact_path.read_text())

    fixture_path = os.environ.get("AC14_DEPENDENCY_PLAN_FIXTURE")
    if fixture_path:
        response = DependencyPlanningResponse.model_validate_json(Path(fixture_path).read_text())
    else:
        messages = render_prompt(
            PROMPT_PATH,
            discovery_artifact=discovery_artifact.model_dump(mode="json"),
            requirements=requirements,
        )
        llm_response, _meta = await acall_llm_structured(
            model,
            messages,
            response_model=DependencyPlanningResponse,
            task=task,
            trace_id=f"ac14/dependency_plan/{artifact_path.stem}",
            max_budget=max_budget,
        )
        response = cast(DependencyPlanningResponse, llm_response)

    _validate_dependency_plan(response, discovery_artifact)
    plan = DependencyPlanningArtifact(
        discovery_artifact_path=str(artifact_path),
        requirements=requirements,
        carried_forward_concerns=discovery_artifact.open_concerns,
        planning_summary=response.planning_summary,
        recommendations=response.recommendations,
        standard_library_notes=response.standard_library_notes,
        open_questions=response.open_questions,
    )
    (destination / "dependency_plan.json").write_text(
        json.dumps(plan.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return plan


def build_dependency_plan(
    discovery_artifact_path: Path | str,
    output_dir: Path | str,
    *,
    requirements: list[str],
    model: str = DEFAULT_DEPENDENCY_PLAN_MODEL,
    max_budget: float = DEFAULT_DEPENDENCY_PLAN_MAX_BUDGET,
    task: str = "ac14_dependency_plan",
) -> DependencyPlanningArtifact:
    """Synchronous wrapper for persisted dependency planning."""

    return asyncio.run(
        abuild_dependency_plan(
            discovery_artifact_path=discovery_artifact_path,
            output_dir=output_dir,
            requirements=requirements,
            model=model,
            max_budget=max_budget,
            task=task,
        ),
    )


def _validate_dependency_plan(
    plan: DependencyPlanningResponse,
    discovery_artifact: DiscoveryArtifact,
) -> None:
    """Fail loud when dependency planning is internally inconsistent."""

    installed_lookup = {
        status.package_name: status
        for status in discovery_artifact.environment_inventory.dependency_statuses
    }
    package_names = [recommendation.package_name for recommendation in plan.recommendations]
    if len(package_names) != len(set(package_names)):
        raise ValueError("dependency plan contains duplicate package recommendations")

    for recommendation in plan.recommendations:
        if not recommendation.evidence:
            raise ValueError(
                f"dependency recommendation {recommendation.package_name!r} must cite evidence",
            )
        installed_status = installed_lookup.get(recommendation.package_name)
        expected_installed = installed_status.installed if installed_status is not None else False
        if recommendation.already_installed != expected_installed:
            raise ValueError(
                f"dependency recommendation {recommendation.package_name!r} does not match environment inventory",
            )
        if recommendation.action == "reuse":
            if not recommendation.already_installed:
                raise ValueError(
                    f"dependency recommendation {recommendation.package_name!r} cannot reuse a missing package",
                )
            if recommendation.install_command is not None:
                raise ValueError(
                    f"dependency recommendation {recommendation.package_name!r} should not carry an install command for reuse",
                )
        if recommendation.action == "install":
            if recommendation.already_installed:
                raise ValueError(
                    f"dependency recommendation {recommendation.package_name!r} should reuse instead of install when already present",
                )
            if not recommendation.install_command:
                raise ValueError(
                    f"dependency recommendation {recommendation.package_name!r} must include an install command",
                )
        if recommendation.action in {"investigate", "avoid"} and recommendation.install_command is not None:
            raise ValueError(
                f"dependency recommendation {recommendation.package_name!r} should not carry an install command for action {recommendation.action!r}",
            )
        _validate_dependency_evidence(
            recommendation=recommendation,
            installed_status=installed_status,
            discovery_artifact=discovery_artifact,
        )


def _validate_dependency_evidence(
    *,
    recommendation: DependencyRecommendation,
    installed_status: DependencyStatus | None,
    discovery_artifact: DiscoveryArtifact,
) -> None:
    """Fail loud when cited evidence does not exist in discovery context."""

    available_urls = {
        url
        for summary in discovery_artifact.external_retrieval_summaries
        for url in summary.web_urls
    }
    available_repo_paths = {
        path
        for summary in discovery_artifact.external_retrieval_summaries
        for path in summary.repo_paths
    }
    for evidence in recommendation.evidence:
        if evidence.source == "environment" and installed_status is None:
            raise ValueError(
                f"dependency recommendation {recommendation.package_name!r} cites environment evidence without inventory coverage",
            )
        if evidence.source == "project_context":
            available_doc_paths = {
                document.path for document in discovery_artifact.project_context_inventory.documents
            }
            if evidence.locator not in available_doc_paths:
                raise ValueError(
                    f"dependency recommendation {recommendation.package_name!r} cites unknown project document {evidence.locator!r}",
                )
        if evidence.source == "external_retrieval":
            if evidence.locator not in available_urls and evidence.locator not in available_repo_paths:
                raise ValueError(
                    f"dependency recommendation {recommendation.package_name!r} cites unknown retrieval locator {evidence.locator!r}",
                )
        if evidence.source == "open_concern" and evidence.locator not in discovery_artifact.open_concerns:
            raise ValueError(
                f"dependency recommendation {recommendation.package_name!r} cites unknown open concern {evidence.locator!r}",
            )

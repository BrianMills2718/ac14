"""LLM-backed draft blueprint planning from persisted discovery artifacts."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, Field, model_validator

from ac14.dependency_execution import (
    DependencyExecutionArtifact,
    DependencyRemediationArtifact,
)
from ac14.dependency_planning import DependencyPlanningArtifact
from ac14.discovery import DiscoveryArtifact
from ac14.models import ValidationFinding
from ac14.structured_spec import StructuredSpecArtifact
from llm_client import acall_llm_structured, render_prompt  # type: ignore[import-not-found]


DEFAULT_BLUEPRINT_PLAN_MODEL = "gemini/gemini-2.5-flash-lite"
DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET = 0.75
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "draft_blueprint_plan.yaml"
STRUCTURED_SPEC_PROMPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "prompts"
    / "draft_blueprint_plan_from_structured_spec.yaml"
)
REFINE_PROMPT_PATH = (
    Path(__file__).resolve().parents[1] / "prompts" / "refine_draft_blueprint_plan.yaml"
)


class PlannedSchemaField(BaseModel):
    """One proposed field in a draft schema."""

    field_name: str = Field(description="Stable field name for the draft schema.")
    field_type: str = Field(description="Compact field type label for the draft schema field.")
    description: str = Field(description="Why this field exists and what it carries.")


class PlannedSchema(BaseModel):
    """One proposed draft schema inferred from discovery and requirements."""

    schema_name: str = Field(description="Stable schema name for the draft blueprint.")
    kind: Literal["record", "enum"] = Field(description="Draft schema kind.")
    description: str = Field(description="Why this schema exists in the draft blueprint.")
    fields: list[PlannedSchemaField] = Field(
        description="Draft schema fields when the schema kind is record.",
    )


class PlannedPort(BaseModel):
    """One proposed component port in the draft blueprint plan."""

    port_name: str = Field(description="Port name for the draft component.")
    schema_name: str = Field(description="Schema carried through this port.")
    description: str = Field(description="Why this port exists and what it carries.")


class PlannedComponent(BaseModel):
    """One proposed component in the draft blueprint plan."""

    component_id: str = Field(description="Stable draft component identifier.")
    semantic_responsibility: str = Field(
        description="Stable semantic responsibility label for this draft component.",
    )
    purpose: str = Field(description="Why this component exists in the draft blueprint.")
    input_ports: list[PlannedPort] = Field(description="Draft input ports for the component.")
    output_ports: list[PlannedPort] = Field(description="Draft output ports for the component.")
    packet_focus: list[str] = Field(
        description="What the local coder packet must emphasize for this component.",
    )
    dependency_notes: list[str] = Field(
        description="Dependency or library considerations relevant to this component.",
    )


class PlannedBinding(BaseModel):
    """One proposed binding in the draft blueprint plan."""

    from_component: str = Field(description="Upstream component identifier.")
    from_port: str = Field(description="Upstream output port name.")
    to_component: str = Field(description="Downstream component identifier.")
    to_port: str = Field(description="Downstream input port name.")
    rationale: str = Field(description="Why this binding exists.")


class PlannedScenario(BaseModel):
    """One proposed scenario in the draft blueprint plan."""

    scenario_id: str = Field(description="Stable scenario identifier.")
    kind: Literal["full_recomposition", "negative", "semantic_acceptance"] = Field(
        description="Scenario kind proposed for later proof.",
    )
    description: str = Field(description="Why this scenario matters.")
    requirement_focus: list[str] = Field(
        description="Requirements or risks that this scenario is meant to cover.",
    )


class PlanningQuestion(BaseModel):
    """One open question that should be resolved before blueprint freeze."""

    question: str = Field(description="Concrete unresolved planning question.")
    why_it_matters: str = Field(description="Why the question matters before freeze.")


class DraftBlueprintPlanResponse(BaseModel):
    """Structured LLM response for draft blueprint planning."""

    planning_summary: str = Field(
        description="Short summary of the proposed decomposition and why it fits the discovery artifact.",
    )
    proposed_schemas: list[PlannedSchema] = Field(
        description="Schemas proposed for the draft blueprint.",
    )
    proposed_components: list[PlannedComponent] = Field(
        description="Components proposed for the draft blueprint.",
    )
    proposed_bindings: list[PlannedBinding] = Field(
        description="Bindings proposed between draft components.",
    )
    proposed_scenarios: list[PlannedScenario] = Field(
        description="Proof scenarios proposed for the draft blueprint.",
    )
    packetization_notes: list[str] = Field(
        description="Notes about packet boundaries, local context, and decomposition risks.",
    )
    dependency_decisions: list[str] = Field(
        description="Dependency or environment decisions implied by the draft plan.",
    )
    open_questions: list[PlanningQuestion] = Field(
        description="Questions that should be resolved before blueprint freeze.",
    )


class RefinedDraftBlueprintPlanResponse(DraftBlueprintPlanResponse):
    """Structured LLM response for remediation-driven draft plan refinement."""

    refinement_summary: str = Field(
        description="Short summary of what changed in response to the blocked freeze decision.",
    )


class RefinementFreezeDecisionArtifact(BaseModel):
    """Minimal freeze decision shape needed for draft-plan refinement."""

    approved: bool = Field(description="Whether the source freeze decision was approved.")
    decision_summary: str = Field(description="Compact summary of the source freeze decision.")
    findings: list[ValidationFinding] = Field(
        description="Findings carried on the source freeze decision.",
    )
    remediation_plan_path: str = Field(
        description="Path to the remediation plan that explains the blocked retry work.",
    )


class RefinementFreezeRemediationTask(BaseModel):
    """Minimal remediation task shape needed for draft-plan refinement."""

    task_id: str = Field(description="Stable remediation task identifier.")
    blocking: bool = Field(description="Whether the task remains blocking.")
    title: str = Field(description="Short title for the task.")
    summary: str = Field(description="Compact explanation of the task.")
    target_files: list[str] = Field(description="Files or artifacts the task points at.")
    source_paths: list[str] = Field(description="Source finding paths behind the task.")
    finding_codes: list[str] = Field(description="Finding codes grouped into the task.")
    authoring_actions: list[str] = Field(description="Concrete actions suggested by the task.")
    retry_command: str = Field(description="Retry command suggested by the task.")


class RefinementFreezeRemediationPlan(BaseModel):
    """Minimal remediation plan shape needed for draft-plan refinement."""

    blocked: bool = Field(description="Whether remediation work remains before retrying freeze.")
    summary: str = Field(description="Compact summary of the remediation plan.")
    task_count: int = Field(description="Number of remediation tasks.")
    upstream_plan_path: str | None = Field(
        default=None,
        description="Upstream draft planning artifact path when one was recorded.",
    )
    tasks: list[RefinementFreezeRemediationTask] = Field(
        description="Remediation tasks carried into the refinement loop.",
    )


class DraftBlueprintPlanArtifact(BaseModel):
    """Persisted draft blueprint planning artifact built from discovery plus requirements."""

    planning_input_kind: Literal["discovery", "structured_spec"] = Field(
        default="discovery",
        description="Which bounded front-half input surface produced this plan.",
    )
    planning_input_name: str | None = Field(
        default=None,
        description="Human-facing name for the source planning input when one is known.",
    )
    planning_input_artifact_path: str | None = Field(
        default=None,
        description="Canonical source artifact path for this planning run.",
    )
    discovery_artifact_path: str | None = Field(
        default=None,
        description="Path to the persisted discovery artifact used as input when discovery drove this plan.",
    )
    structured_spec_artifact_path: str | None = Field(
        default=None,
        description="Path to the persisted structured-spec artifact when structured spec drove this plan.",
    )
    requirements: list[str] = Field(description="Requirements used for planning.")
    planning_input_open_concerns: list[str] = Field(
        default_factory=list,
        description="Open concerns carried forward from the active planning input surface.",
    )
    discovery_open_concerns: list[str] = Field(
        description="Open concerns carried forward from the discovery artifact.",
    )
    dependency_plan_path: str | None = Field(
        default=None,
        description="Optional dependency-planning artifact used as additional planning input.",
    )
    dependency_plan_summary: str | None = Field(
        default=None,
        description="Summary of the dependency-planning artifact when one was provided.",
    )
    dependency_execution_artifact_path: str | None = Field(
        default=None,
        description="Optional dependency execution artifact used as additional planning input.",
    )
    dependency_remediation_artifact_path: str | None = Field(
        default=None,
        description="Optional dependency remediation artifact used to select the execution artifact.",
    )
    dependency_execution_summary: str | None = Field(
        default=None,
        description="Compact summary of dependency probe results when one was provided.",
    )
    dependency_remediation_summary: str | None = Field(
        default=None,
        description="Compact summary of dependency remediation when one was provided.",
    )
    source_draft_blueprint_plan_path: str | None = Field(
        default=None,
        description="Source planning artifact path when this plan was produced by refinement.",
    )
    source_freeze_decision_path: str | None = Field(
        default=None,
        description="Source freeze decision path when this plan was produced by refinement.",
    )
    source_freeze_remediation_plan_path: str | None = Field(
        default=None,
        description="Source freeze remediation plan path when this plan was produced by refinement.",
    )
    refinement_summary: str | None = Field(
        default=None,
        description="Compact summary of how a refinement pass changed the plan.",
    )
    refinement_round: int = Field(
        default=0,
        description="How many refinement passes produced this planning artifact.",
    )
    dependency_recommendations: list[str] = Field(
        default_factory=list,
        description="Compact advisory dependency actions carried into draft planning.",
    )
    confirmed_dependency_probes: list[str] = Field(
        default_factory=list,
        description="Probe results that confirmed dependency availability before freeze.",
    )
    blocked_dependency_probes: list[str] = Field(
        default_factory=list,
        description="Probe results that still block dependency decisions before freeze.",
    )
    dependency_probe_observations: list[str] = Field(
        default_factory=list,
        description="Cross-cutting observations carried forward from dependency execution.",
    )
    dependency_open_questions: list[PlanningQuestion] = Field(
        default_factory=list,
        description="Dependency questions carried into draft planning from the dependency plan.",
    )
    planning_summary: str = Field(
        description="Short summary of the proposed decomposition and its fit.",
    )
    proposed_schemas: list[PlannedSchema] = Field(description="Draft schemas.")
    proposed_components: list[PlannedComponent] = Field(description="Draft components.")
    proposed_bindings: list[PlannedBinding] = Field(description="Draft bindings.")
    proposed_scenarios: list[PlannedScenario] = Field(description="Draft proof scenarios.")
    packetization_notes: list[str] = Field(description="Draft packet planning notes.")
    dependency_decisions: list[str] = Field(description="Dependency decisions for the draft plan.")
    open_questions: list[PlanningQuestion] = Field(
        description="Questions to resolve before blueprint freeze.",
    )

    @model_validator(mode="after")
    def _normalize_planning_input_provenance(self) -> "DraftBlueprintPlanArtifact":
        """Keep older discovery-based artifacts compatible while adding new input provenance."""

        if self.planning_input_kind == "discovery":
            if not self.discovery_artifact_path and self.planning_input_artifact_path:
                self.discovery_artifact_path = self.planning_input_artifact_path
            if not self.planning_input_artifact_path:
                self.planning_input_artifact_path = self.discovery_artifact_path
            if not self.planning_input_artifact_path:
                raise ValueError("discovery-based draft plan is missing discovery artifact provenance")
        else:
            if not self.structured_spec_artifact_path and self.planning_input_artifact_path:
                self.structured_spec_artifact_path = self.planning_input_artifact_path
            if not self.planning_input_artifact_path:
                self.planning_input_artifact_path = self.structured_spec_artifact_path
            if not self.planning_input_artifact_path:
                raise ValueError("structured-spec draft plan is missing structured-spec provenance")

        if not self.planning_input_name and self.planning_input_artifact_path:
            self.planning_input_name = Path(self.planning_input_artifact_path).stem.replace(
                "_artifact",
                "",
            )
        if not self.planning_input_open_concerns:
            self.planning_input_open_concerns = list(self.discovery_open_concerns)
        return self


async def abuild_draft_blueprint_plan(
    discovery_artifact_path: Path | str,
    output_dir: Path | str,
    *,
    requirements: list[str],
    dependency_plan_path: Path | str | None = None,
    dependency_execution_artifact_path: Path | str | None = None,
    dependency_remediation_artifact_path: Path | str | None = None,
    model: str = DEFAULT_BLUEPRINT_PLAN_MODEL,
    max_budget: float = DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    task: str = "ac14_draft_blueprint_plan",
) -> DraftBlueprintPlanArtifact:
    """Build a persisted draft blueprint planning artifact from discovery."""

    if not requirements:
        raise ValueError("draft blueprint planning requires at least one requirement")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    artifact_path = Path(discovery_artifact_path)
    discovery_artifact = DiscoveryArtifact.model_validate_json(artifact_path.read_text())
    dependency_remediation_artifact = (
        DependencyRemediationArtifact.model_validate_json(
            Path(dependency_remediation_artifact_path).read_text(),
        )
        if dependency_remediation_artifact_path is not None
        else None
    )
    normalized_dependency_execution_path = _resolve_dependency_execution_artifact_path(
        dependency_execution_artifact_path=dependency_execution_artifact_path,
        dependency_remediation_artifact=dependency_remediation_artifact,
    )
    dependency_execution_artifact = (
        DependencyExecutionArtifact.model_validate_json(
            Path(normalized_dependency_execution_path).read_text(),
        )
        if normalized_dependency_execution_path is not None
        else None
    )
    normalized_dependency_plan_path = _resolve_dependency_plan_path(
        dependency_plan_path=dependency_plan_path,
        dependency_execution_artifact=dependency_execution_artifact,
    )
    dependency_plan = (
        DependencyPlanningArtifact.model_validate_json(normalized_dependency_plan_path.read_text())
        if normalized_dependency_plan_path is not None
        else None
    )

    fixture_path = os.environ.get("AC14_BLUEPRINT_PLAN_FIXTURE")
    if fixture_path:
        typed_response = DraftBlueprintPlanResponse.model_validate_json(Path(fixture_path).read_text())
    else:
        messages = render_prompt(
            PROMPT_PATH,
            discovery_artifact=discovery_artifact.model_dump(mode="json"),
            dependency_plan=(
                dependency_plan.model_dump(mode="json")
                if dependency_plan is not None
                else None
            ),
            dependency_execution=(
                dependency_execution_artifact.model_dump(mode="json")
                if dependency_execution_artifact is not None
                else None
            ),
            dependency_remediation=(
                dependency_remediation_artifact.model_dump(mode="json")
                if dependency_remediation_artifact is not None
                else None
            ),
            requirements=requirements,
        )
        response, _meta = await acall_llm_structured(
            model,
            messages,
            response_model=DraftBlueprintPlanResponse,
            task=task,
            trace_id=f"ac14/draft_blueprint_plan/{artifact_path.stem}",
            max_budget=max_budget,
        )
        typed_response = cast(DraftBlueprintPlanResponse, response)
    _validate_draft_blueprint_plan(typed_response)
    plan = DraftBlueprintPlanArtifact(
        planning_input_kind="discovery",
        planning_input_name=_planning_input_name_from_discovery(discovery_artifact),
        planning_input_artifact_path=str(artifact_path),
        discovery_artifact_path=str(artifact_path),
        requirements=requirements,
        planning_input_open_concerns=discovery_artifact.open_concerns,
        discovery_open_concerns=discovery_artifact.open_concerns,
        dependency_plan_path=(
            str(normalized_dependency_plan_path)
            if normalized_dependency_plan_path is not None
            else None
        ),
        dependency_plan_summary=(
            dependency_plan.planning_summary if dependency_plan is not None else None
        ),
        dependency_execution_artifact_path=(
            str(Path(normalized_dependency_execution_path))
            if normalized_dependency_execution_path is not None
            else None
        ),
        dependency_remediation_artifact_path=(
            str(Path(dependency_remediation_artifact_path))
            if dependency_remediation_artifact_path is not None
            else None
        ),
        dependency_execution_summary=(
            _summarize_dependency_execution(dependency_execution_artifact)
            if dependency_execution_artifact is not None
            else None
        ),
        dependency_remediation_summary=(
            dependency_remediation_artifact.summary
            if dependency_remediation_artifact is not None
            else None
        ),
        dependency_recommendations=(
            [
                (
                    f"{recommendation.action} {recommendation.package_name}: "
                    f"{recommendation.capability_need}"
                )
                for recommendation in dependency_plan.recommendations
            ]
            if dependency_plan is not None
            else []
        ),
        confirmed_dependency_probes=(
            _confirmed_dependency_probe_summaries(dependency_execution_artifact)
            if dependency_execution_artifact is not None
            else []
        ),
        blocked_dependency_probes=(
            _blocked_dependency_probe_summaries(dependency_execution_artifact)
            if dependency_execution_artifact is not None
            else []
        ),
        dependency_probe_observations=(
            dependency_execution_artifact.environment_observations
            if dependency_execution_artifact is not None
            else []
        ),
        dependency_open_questions=(
            [
                PlanningQuestion(
                    question=question.question,
                    why_it_matters=question.why_it_matters,
                )
                for question in dependency_plan.open_questions
            ]
            if dependency_plan is not None
            else []
        ),
        planning_summary=typed_response.planning_summary,
        proposed_schemas=typed_response.proposed_schemas,
        proposed_components=typed_response.proposed_components,
        proposed_bindings=typed_response.proposed_bindings,
        proposed_scenarios=typed_response.proposed_scenarios,
        packetization_notes=typed_response.packetization_notes,
        dependency_decisions=typed_response.dependency_decisions,
        open_questions=typed_response.open_questions,
    )
    (destination / "draft_blueprint_plan.json").write_text(
        json.dumps(plan.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return plan


async def abuild_draft_blueprint_plan_from_structured_spec(
    structured_spec_artifact_path: Path | str,
    output_dir: Path | str,
    *,
    model: str = DEFAULT_BLUEPRINT_PLAN_MODEL,
    max_budget: float = DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    task: str = "ac14_draft_blueprint_plan_from_structured_spec",
) -> DraftBlueprintPlanArtifact:
    """Build a persisted draft blueprint planning artifact from a structured-spec input surface."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    artifact_path = Path(structured_spec_artifact_path)
    structured_spec_artifact = StructuredSpecArtifact.model_validate_json(artifact_path.read_text())

    fixture_path = os.environ.get("AC14_BLUEPRINT_PLAN_FIXTURE")
    if fixture_path:
        typed_response = DraftBlueprintPlanResponse.model_validate_json(Path(fixture_path).read_text())
    else:
        messages = render_prompt(
            STRUCTURED_SPEC_PROMPT_PATH,
            structured_spec_artifact=structured_spec_artifact.model_dump(mode="json"),
        )
        response, _meta = await acall_llm_structured(
            model,
            messages,
            response_model=DraftBlueprintPlanResponse,
            task=task,
            trace_id=f"ac14/draft_blueprint_plan_from_structured_spec/{artifact_path.stem}",
            max_budget=max_budget,
        )
        typed_response = cast(DraftBlueprintPlanResponse, response)

    _validate_draft_blueprint_plan(typed_response)
    plan = DraftBlueprintPlanArtifact(
        planning_input_kind="structured_spec",
        planning_input_name=structured_spec_artifact.spec.system_name,
        planning_input_artifact_path=str(artifact_path),
        structured_spec_artifact_path=str(artifact_path),
        requirements=structured_spec_artifact.spec.requirements,
        planning_input_open_concerns=structured_spec_artifact.open_concerns,
        discovery_open_concerns=[],
        planning_summary=typed_response.planning_summary,
        proposed_schemas=typed_response.proposed_schemas,
        proposed_components=typed_response.proposed_components,
        proposed_bindings=typed_response.proposed_bindings,
        proposed_scenarios=typed_response.proposed_scenarios,
        packetization_notes=typed_response.packetization_notes,
        dependency_decisions=typed_response.dependency_decisions,
        open_questions=typed_response.open_questions,
    )
    (destination / "draft_blueprint_plan.json").write_text(
        json.dumps(plan.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return plan


def build_draft_blueprint_plan(
    discovery_artifact_path: Path | str,
    output_dir: Path | str,
    *,
    requirements: list[str],
    dependency_plan_path: Path | str | None = None,
    dependency_execution_artifact_path: Path | str | None = None,
    dependency_remediation_artifact_path: Path | str | None = None,
    model: str = DEFAULT_BLUEPRINT_PLAN_MODEL,
    max_budget: float = DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    task: str = "ac14_draft_blueprint_plan",
) -> DraftBlueprintPlanArtifact:
    """Synchronous wrapper for persisted draft blueprint planning."""

    return asyncio.run(
        abuild_draft_blueprint_plan(
            discovery_artifact_path=discovery_artifact_path,
            output_dir=output_dir,
            requirements=requirements,
            dependency_plan_path=dependency_plan_path,
            dependency_execution_artifact_path=dependency_execution_artifact_path,
            dependency_remediation_artifact_path=dependency_remediation_artifact_path,
            model=model,
            max_budget=max_budget,
            task=task,
        ),
    )


def build_draft_blueprint_plan_from_structured_spec(
    structured_spec_artifact_path: Path | str,
    output_dir: Path | str,
    *,
    model: str = DEFAULT_BLUEPRINT_PLAN_MODEL,
    max_budget: float = DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    task: str = "ac14_draft_blueprint_plan_from_structured_spec",
) -> DraftBlueprintPlanArtifact:
    """Synchronous wrapper for structured-spec-driven draft planning."""

    return asyncio.run(
        abuild_draft_blueprint_plan_from_structured_spec(
            structured_spec_artifact_path=structured_spec_artifact_path,
            output_dir=output_dir,
            model=model,
            max_budget=max_budget,
            task=task,
        ),
    )


async def abuild_refined_draft_blueprint_plan(
    plan_artifact_path: Path | str,
    freeze_decision_path: Path | str,
    output_dir: Path | str,
    *,
    model: str = DEFAULT_BLUEPRINT_PLAN_MODEL,
    max_budget: float = DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    task: str = "ac14_refine_draft_blueprint_plan",
) -> DraftBlueprintPlanArtifact:
    """Build a refined draft planning artifact from a blocked freeze decision."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    source_plan_path = Path(plan_artifact_path)
    source_plan = DraftBlueprintPlanArtifact.model_validate_json(source_plan_path.read_text())
    decision_path = Path(freeze_decision_path)
    freeze_decision = RefinementFreezeDecisionArtifact.model_validate_json(
        decision_path.read_text(),
    )
    remediation_plan_path = Path(freeze_decision.remediation_plan_path)
    remediation_plan = RefinementFreezeRemediationPlan.model_validate_json(
        remediation_plan_path.read_text(),
    )
    _validate_refinement_request(
        source_plan_path=source_plan_path,
        source_plan=source_plan,
        freeze_decision=freeze_decision,
        remediation_plan=remediation_plan,
    )

    fixture_path = os.environ.get("AC14_REFINE_BLUEPRINT_PLAN_FIXTURE")
    if fixture_path:
        typed_response = RefinedDraftBlueprintPlanResponse.model_validate_json(
            Path(fixture_path).read_text(),
        )
    else:
        messages = render_prompt(
            REFINE_PROMPT_PATH,
            source_plan=source_plan.model_dump(mode="json"),
            freeze_decision=freeze_decision.model_dump(mode="json"),
            remediation_plan=remediation_plan.model_dump(mode="json"),
        )
        response, _meta = await acall_llm_structured(
            model,
            messages,
            response_model=RefinedDraftBlueprintPlanResponse,
            task=task,
            trace_id=f"ac14/refine_draft_blueprint_plan/{source_plan_path.stem}",
            max_budget=max_budget,
        )
        typed_response = cast(RefinedDraftBlueprintPlanResponse, response)

    _validate_draft_blueprint_plan(typed_response)
    refined_plan = DraftBlueprintPlanArtifact(
        discovery_artifact_path=source_plan.discovery_artifact_path,
        requirements=source_plan.requirements,
        discovery_open_concerns=source_plan.discovery_open_concerns,
        dependency_plan_path=source_plan.dependency_plan_path,
        dependency_plan_summary=source_plan.dependency_plan_summary,
        dependency_execution_artifact_path=source_plan.dependency_execution_artifact_path,
        dependency_remediation_artifact_path=source_plan.dependency_remediation_artifact_path,
        dependency_execution_summary=source_plan.dependency_execution_summary,
        dependency_remediation_summary=source_plan.dependency_remediation_summary,
        source_draft_blueprint_plan_path=str(source_plan_path),
        source_freeze_decision_path=str(decision_path),
        source_freeze_remediation_plan_path=str(remediation_plan_path),
        refinement_summary=typed_response.refinement_summary,
        refinement_round=source_plan.refinement_round + 1,
        dependency_recommendations=source_plan.dependency_recommendations,
        confirmed_dependency_probes=source_plan.confirmed_dependency_probes,
        blocked_dependency_probes=source_plan.blocked_dependency_probes,
        dependency_probe_observations=source_plan.dependency_probe_observations,
        dependency_open_questions=source_plan.dependency_open_questions,
        planning_summary=typed_response.planning_summary,
        proposed_schemas=typed_response.proposed_schemas,
        proposed_components=typed_response.proposed_components,
        proposed_bindings=typed_response.proposed_bindings,
        proposed_scenarios=typed_response.proposed_scenarios,
        packetization_notes=typed_response.packetization_notes,
        dependency_decisions=typed_response.dependency_decisions,
        open_questions=typed_response.open_questions,
    )
    (destination / "draft_blueprint_plan.json").write_text(
        json.dumps(refined_plan.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return refined_plan


def build_refined_draft_blueprint_plan(
    plan_artifact_path: Path | str,
    freeze_decision_path: Path | str,
    output_dir: Path | str,
    *,
    model: str = DEFAULT_BLUEPRINT_PLAN_MODEL,
    max_budget: float = DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    task: str = "ac14_refine_draft_blueprint_plan",
) -> DraftBlueprintPlanArtifact:
    """Synchronous wrapper for remediation-driven draft plan refinement."""

    return asyncio.run(
        abuild_refined_draft_blueprint_plan(
            plan_artifact_path=plan_artifact_path,
            freeze_decision_path=freeze_decision_path,
            output_dir=output_dir,
            model=model,
            max_budget=max_budget,
            task=task,
        ),
    )


def _validate_draft_blueprint_plan(plan: DraftBlueprintPlanResponse) -> None:
    """Fail loud when the structured draft plan is internally inconsistent."""

    schema_names = {schema.schema_name for schema in plan.proposed_schemas}
    component_ids = {component.component_id for component in plan.proposed_components}
    if len(schema_names) != len(plan.proposed_schemas):
        raise ValueError("draft blueprint plan contains duplicate schema names")
    if len(component_ids) != len(plan.proposed_components):
        raise ValueError("draft blueprint plan contains duplicate component ids")

    port_lookup: dict[str, set[str]] = {}
    for component in plan.proposed_components:
        for port in [*component.input_ports, *component.output_ports]:
            if port.schema_name not in schema_names:
                raise ValueError(
                    "draft blueprint plan references unknown schema "
                    f"{port.schema_name!r} in component {component.component_id}"
                )
        port_lookup[component.component_id] = {port.port_name for port in component.input_ports}
        port_lookup[f"{component.component_id}::out"] = {
            port.port_name for port in component.output_ports
        }

    for binding in plan.proposed_bindings:
        if binding.from_component not in component_ids:
            raise ValueError(
                f"draft blueprint plan binding references unknown from_component {binding.from_component!r}",
            )
        if binding.to_component not in component_ids:
            raise ValueError(
                f"draft blueprint plan binding references unknown to_component {binding.to_component!r}",
            )
        if binding.from_port not in port_lookup[f"{binding.from_component}::out"]:
            raise ValueError(
                f"draft blueprint plan binding references unknown from_port {binding.from_port!r}",
            )
        if binding.to_port not in port_lookup[binding.to_component]:
            raise ValueError(
                f"draft blueprint plan binding references unknown to_port {binding.to_port!r}",
            )


def _validate_refinement_request(
    *,
    source_plan_path: Path,
    source_plan: DraftBlueprintPlanArtifact,
    freeze_decision: RefinementFreezeDecisionArtifact,
    remediation_plan: RefinementFreezeRemediationPlan,
) -> None:
    """Fail loud when refinement input artifacts disagree."""

    if freeze_decision.approved:
        raise ValueError("cannot refine a draft plan from an approved freeze decision")
    if not remediation_plan.blocked or remediation_plan.task_count == 0:
        raise ValueError("cannot refine a draft plan without blocked remediation tasks")
    if remediation_plan.upstream_plan_path is not None and Path(
        remediation_plan.upstream_plan_path,
    ) != source_plan_path:
        raise ValueError(
            "freeze remediation plan points at a different draft plan than the one provided",
        )
    if not source_plan.planning_input_artifact_path:
        raise ValueError("source draft plan is missing planning input provenance")


def _planning_input_name_from_discovery(discovery_artifact: DiscoveryArtifact) -> str:
    """Return a stable human-facing name for discovery-driven planning input."""

    source_path = (
        discovery_artifact.input_inspection.primary_input_path
        or discovery_artifact.input_inspection.input_path
    )
    return Path(source_path).stem.replace("_artifact", "")


def _resolve_dependency_plan_path(
    *,
    dependency_plan_path: Path | str | None,
    dependency_execution_artifact: DependencyExecutionArtifact | None,
) -> Path | None:
    """Return the authoritative dependency-plan path for this planning run."""

    explicit_path = Path(dependency_plan_path) if dependency_plan_path is not None else None
    if dependency_execution_artifact is None:
        return explicit_path
    execution_path = Path(dependency_execution_artifact.dependency_plan_path)
    if explicit_path is not None and explicit_path != execution_path:
        raise ValueError(
            "dependency execution artifact points at a different dependency plan than the one provided",
        )
    return explicit_path or execution_path


def _resolve_dependency_execution_artifact_path(
    *,
    dependency_execution_artifact_path: Path | str | None,
    dependency_remediation_artifact: DependencyRemediationArtifact | None,
) -> Path | None:
    """Return the authoritative dependency-execution artifact path for planning."""

    explicit_path = (
        Path(dependency_execution_artifact_path)
        if dependency_execution_artifact_path is not None
        else None
    )
    if dependency_remediation_artifact is None:
        return explicit_path
    remediation_path = Path(
        dependency_remediation_artifact.remediated_dependency_execution_artifact_path,
    )
    if explicit_path is not None and explicit_path != remediation_path:
        raise ValueError(
            "dependency remediation artifact points at a different execution artifact than the one provided",
        )
    return explicit_path or remediation_path


def _summarize_dependency_execution(artifact: DependencyExecutionArtifact) -> str:
    """Return a compact summary of dependency execution results."""

    confirmed = sum(1 for result in artifact.results if result.result == "confirmed")
    blocked = sum(1 for result in artifact.results if result.result == "blocked")
    skipped = sum(1 for result in artifact.results if result.result == "skipped")
    return (
        f"{artifact.execution_mode} dependency probes: "
        f"{confirmed} confirmed, {blocked} blocked, {skipped} skipped"
    )


def _confirmed_dependency_probe_summaries(
    artifact: DependencyExecutionArtifact,
) -> list[str]:
    """Return compact confirmed probe summaries for later planning stages."""

    return [
        f"{result.action} {result.package_name}: {result.summary}"
        for result in artifact.results
        if result.result == "confirmed"
    ]


def _blocked_dependency_probe_summaries(
    artifact: DependencyExecutionArtifact,
) -> list[str]:
    """Return compact blocked probe summaries for later planning stages."""

    return [
        f"{result.action} {result.package_name}: {result.summary}"
        for result in artifact.results
        if result.result == "blocked"
    ]

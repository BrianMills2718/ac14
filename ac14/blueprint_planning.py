"""LLM-backed draft blueprint planning from persisted discovery artifacts."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, Field

from ac14.discovery import DiscoveryArtifact
from llm_client import acall_llm_structured, render_prompt  # type: ignore[import-not-found]


DEFAULT_BLUEPRINT_PLAN_MODEL = "gemini/gemini-2.5-flash-lite"
DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET = 0.75
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "draft_blueprint_plan.yaml"


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


class DraftBlueprintPlanArtifact(BaseModel):
    """Persisted draft blueprint planning artifact built from discovery plus requirements."""

    discovery_artifact_path: str = Field(
        description="Path to the persisted discovery artifact used as input.",
    )
    requirements: list[str] = Field(description="Requirements used for planning.")
    discovery_open_concerns: list[str] = Field(
        description="Open concerns carried forward from the discovery artifact.",
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


async def abuild_draft_blueprint_plan(
    discovery_artifact_path: Path | str,
    output_dir: Path | str,
    *,
    requirements: list[str],
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

    messages = render_prompt(
        PROMPT_PATH,
        discovery_artifact=discovery_artifact.model_dump(mode="json"),
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
        discovery_artifact_path=str(artifact_path),
        requirements=requirements,
        discovery_open_concerns=discovery_artifact.open_concerns,
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

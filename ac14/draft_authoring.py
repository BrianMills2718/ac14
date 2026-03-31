"""Draft bundle authoring and freeze-readiness reporting from planning artifacts."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field

from ac14.blueprint_planning import (
    DraftBlueprintPlanArtifact,
    PlannedComponent,
)
from ac14.loader import load_blueprint_dir
from ac14.models import (
    ArchitectureFile,
    Binding,
    CompilerProfile,
    ComponentDefinition,
    ComponentsFile,
    EvaluatorDefinition,
    FixturesFile,
    GenerationPolicy,
    GlobalInvariant,
    InputPort,
    Metadata,
    MetadataFile,
    OutputPort,
    SchemaDefinition,
    SchemaField,
    SchemasFile,
    Scenario,
    ValidationFile,
    ValidationFinding,
)
from ac14.validation import validate_blueprint


PLACEHOLDER_INVARIANT = "TODO: confirm local invariants before blueprint freeze"
PLACEHOLDER_FAILURE = "TODO: confirm failure semantics before blueprint freeze"
PLACEHOLDER_CONSTRAINT = "TODO: confirm implementation constraints before blueprint freeze"


class FreezeReadinessReport(BaseModel):
    """Persisted readiness report for a materialized draft bundle."""

    ready: bool = Field(description="Whether the draft bundle appears freeze-ready.")
    validation_passed: bool = Field(description="Whether frozen-blueprint validation passed.")
    findings: list[ValidationFinding] = Field(
        description="Validation and authoring findings that block or qualify freeze readiness.",
    )


class DraftBundleManifest(BaseModel):
    """Record of a materialized draft bundle and its readiness report."""

    draft_bundle_dir: str = Field(description="Directory containing the authored draft bundle.")
    freeze_readiness_report_path: str = Field(
        description="Path to the persisted freeze-readiness report.",
    )
    ready_to_freeze: bool = Field(description="Whether the authored bundle is freeze-ready.")


def materialize_draft_blueprint_bundle(
    plan_artifact_path: Path | str,
    output_dir: Path | str,
) -> DraftBundleManifest:
    """Materialize a six-file draft bundle and a freeze-readiness report."""

    plan_path = Path(plan_artifact_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    plan = DraftBlueprintPlanArtifact.model_validate_json(plan_path.read_text())

    metadata_file = _build_metadata_file(plan, plan_path)
    schema_findings: list[ValidationFinding] = []
    schemas_file = _build_schemas_file(plan, schema_findings)
    components_file = _build_components_file(plan)
    architecture_file = _build_architecture_file(plan)
    validation_file = _build_validation_file(plan)
    fixtures_file = FixturesFile(fixtures=[])

    _write_yaml(destination / "metadata.yaml", metadata_file.model_dump(mode="json", exclude_none=True))
    _write_yaml(destination / "schemas.yaml", schemas_file.model_dump(mode="json", exclude_none=True))
    _write_yaml(destination / "components.yaml", components_file.model_dump(mode="json", exclude_none=True))
    _write_yaml(
        destination / "architecture.yaml",
        architecture_file.model_dump(mode="json", exclude_none=True),
    )
    _write_yaml(destination / "validation.yaml", validation_file.model_dump(mode="json", exclude_none=True))
    _write_yaml(destination / "fixtures.yaml", fixtures_file.model_dump(mode="json", exclude_none=True))

    readiness_report = build_freeze_readiness_report(
        draft_bundle_dir=destination,
        plan=plan,
        extra_findings=schema_findings,
    )
    readiness_path = destination / "freeze_readiness_report.json"
    readiness_path.write_text(
        json.dumps(readiness_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )

    return DraftBundleManifest(
        draft_bundle_dir=str(destination),
        freeze_readiness_report_path=str(readiness_path),
        ready_to_freeze=readiness_report.ready,
    )


def build_freeze_readiness_report(
    *,
    draft_bundle_dir: Path | str,
    plan: DraftBlueprintPlanArtifact,
    extra_findings: list[ValidationFinding] | None = None,
) -> FreezeReadinessReport:
    """Build a persisted readiness report for a materialized draft bundle."""

    draft_dir = Path(draft_bundle_dir)
    blueprint = load_blueprint_dir(draft_dir)
    validation_result = validate_blueprint(blueprint)
    findings = [
        *validation_result.findings,
        *(extra_findings or []),
        *_authoring_findings(plan, blueprint.components.keys()),
    ]
    ready = validation_result.passed and not extra_findings and not _authoring_findings(
        plan,
        blueprint.components.keys(),
    )
    return FreezeReadinessReport(
        ready=ready,
        validation_passed=validation_result.passed,
        findings=findings,
    )


def _build_metadata_file(plan: DraftBlueprintPlanArtifact, plan_path: Path) -> MetadataFile:
    """Build draft metadata with frozen-profile defaults."""

    blueprint_stem = Path(plan.discovery_artifact_path).stem.replace("_artifact", "")
    blueprint_id = f"{blueprint_stem}_draft_v0"
    return MetadataFile(
        metadata=Metadata(
            blueprint_id=blueprint_id,
            name=blueprint_stem.replace("_", " ").title(),
            version="0.0.0-draft",
            purpose=plan.planning_summary,
            source_kind="draft_plan_artifact",
            created_from=str(plan_path),
        ),
        compiler_profile=CompilerProfile(
            target_backend="python",
            execution_model="latest_value_dag",
            component_model="typed_component_graph",
            validation_profile="code_component_v1",
        ),
        generation_policy=GenerationPolicy(
            packet_test_mode="fixture_first",
            codegen_target="python",
        ),
    )


def _build_schemas_file(
    plan: DraftBlueprintPlanArtifact,
    findings: list[ValidationFinding],
) -> SchemasFile:
    """Build draft schema definitions from planned schemas."""

    schemas: list[SchemaDefinition] = []
    for planned_schema in plan.proposed_schemas:
        if planned_schema.kind == "record":
            fields = [
                SchemaField(
                    name=field.field_name,
                    type=field.field_type,
                    required=True,
                    description=field.description,
                    optional_reason="DRAFT: requiredness not confirmed yet.",
                    absence_meaning="DRAFT: absence semantics not confirmed yet.",
                )
                for field in planned_schema.fields
            ]
        else:
            fields = []
            findings.append(
                ValidationFinding(
                    code="W-DRAFT-UNSUPPORTED-SCHEMA-KIND",
                    message=(
                        f"planned schema {planned_schema.schema_name} uses unsupported kind "
                        f"{planned_schema.kind!r}; emitted as empty placeholder object"
                    ),
                    path=f"schemas.{planned_schema.schema_name}",
                ),
            )
        schemas.append(
            SchemaDefinition(
                schema_id=planned_schema.schema_name,
                kind="object",
                description=planned_schema.description,
                fields=fields,
            ),
        )
    return SchemasFile(schemas=schemas)


def _build_components_file(plan: DraftBlueprintPlanArtifact) -> ComponentsFile:
    """Build draft component definitions from planned components."""

    components = [
        ComponentDefinition(
            component_id=component.component_id,
            kind=_component_kind(component),
            purpose=component.purpose,
            semantic_responsibility=component.semantic_responsibility,
            input_ports=[
                InputPort(
                    name=port.port_name,
                    schema_id=port.schema_name,
                    description=port.description,
                    required=True,
                    arrival_policy="required_latest",
                )
                for port in component.input_ports
            ],
            output_ports=[
                OutputPort(
                    name=port.port_name,
                    schema_id=port.schema_name,
                    description=port.description,
                )
                for port in component.output_ports
            ],
            local_invariants=[PLACEHOLDER_INVARIANT],
            failure_semantics=[PLACEHOLDER_FAILURE],
            implementation_constraints=[PLACEHOLDER_CONSTRAINT],
        )
        for component in plan.proposed_components
    ]
    return ComponentsFile(components=components)


def _build_architecture_file(plan: DraftBlueprintPlanArtifact) -> ArchitectureFile:
    """Build draft architecture bindings from the plan artifact."""

    return ArchitectureFile(
        bindings=[
            Binding(
                from_component=binding.from_component,
                from_port=binding.from_port,
                to_component=binding.to_component,
                to_port=binding.to_port,
            )
            for binding in plan.proposed_bindings
        ],
        state_stores=[],
    )


def _build_validation_file(plan: DraftBlueprintPlanArtifact) -> ValidationFile:
    """Build draft scenarios and evaluators from the planning artifact."""

    evaluators = [
        EvaluatorDefinition(
            evaluator_id="exact_outputs",
            kind="programmatic_exact",
            description="Compare actual outputs to declared fixture outputs exactly.",
        ),
        EvaluatorDefinition(
            evaluator_id="negative_failure",
            kind="programmatic_failure",
            description="Confirm that a negative scenario fails loudly.",
        ),
        EvaluatorDefinition(
            evaluator_id="requirements_acceptance",
            kind="llm_requirements_acceptance",
            description="Review outputs against scenario requirements and business logic.",
        ),
    ]
    scenarios = [
        Scenario(
            scenario_id=scenario.scenario_id,
            kind=scenario.kind,
            description=scenario.description,
            fixture_ids=[],
            evaluator_ids=_default_evaluators_for_kind(scenario.kind),
            realistic_input=scenario.kind == "semantic_acceptance",
            requirements=(
                scenario.requirement_focus if scenario.kind == "semantic_acceptance" else []
            ),
        )
        for scenario in plan.proposed_scenarios
    ]
    return ValidationFile(
        global_invariants=[GlobalInvariant(invariant_id="draft_bundle_provisional", description="Draft bundle contains provisional authoring placeholders until freeze.")],
        evaluators=evaluators,
        scenarios=scenarios,
    )


def _default_evaluators_for_kind(
    kind: Literal["full_recomposition", "negative", "semantic_acceptance"],
) -> list[str]:
    """Return default evaluator ids for a draft scenario kind."""

    if kind == "negative":
        return ["negative_failure"]
    if kind == "semantic_acceptance":
        return ["exact_outputs", "requirements_acceptance"]
    return ["exact_outputs"]


def _component_kind(
    component: PlannedComponent,
) -> Literal["source", "transform", "join", "sink"]:
    """Infer a frozen-component kind from planned port shapes."""

    input_count = len(component.input_ports)
    output_count = len(component.output_ports)
    if input_count == 0 and output_count > 0:
        return "source"
    if output_count == 0:
        return "sink"
    if input_count > 1:
        return "join"
    return "transform"


def _authoring_findings(
    plan: DraftBlueprintPlanArtifact,
    component_ids: Iterable[str],
) -> list[ValidationFinding]:
    """Build authoring-specific readiness findings that frozen validation cannot express."""

    resolved_component_ids = list(component_ids)
    findings: list[ValidationFinding] = []
    for component_id in resolved_component_ids:
        findings.extend(
            [
                ValidationFinding(
                    code="W-DRAFT-PLACEHOLDER-INVARIANT",
                    message="component still uses placeholder local invariants",
                    path=f"components.{component_id}.local_invariants",
                ),
                ValidationFinding(
                    code="W-DRAFT-PLACEHOLDER-FAILURE",
                    message="component still uses placeholder failure semantics",
                    path=f"components.{component_id}.failure_semantics",
                ),
                ValidationFinding(
                    code="W-DRAFT-PLACEHOLDER-CONSTRAINT",
                    message="component still uses placeholder implementation constraints",
                    path=f"components.{component_id}.implementation_constraints",
                ),
            ],
        )
    for question in plan.open_questions:
        findings.append(
            ValidationFinding(
                code="W-DRAFT-OPEN-QUESTION",
                message=f"open question before freeze: {question.question}",
                path="plan.open_questions",
            ),
        )
    for question in plan.dependency_open_questions:
        findings.append(
            ValidationFinding(
                code="W-DRAFT-DEPENDENCY-QUESTION",
                message=f"dependency question before freeze: {question.question}",
                path="plan.dependency_open_questions",
            ),
        )
    return findings


def _write_yaml(path: Path, payload: dict[str, object]) -> None:
    """Write one YAML artifact with stable key order."""

    path.write_text(yaml.safe_dump(payload, sort_keys=False))

"""Draft bundle authoring and freeze-readiness reporting from planning artifacts."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field

from ac14.blueprint_planning import (
    DraftBlueprintPlanArtifact,
    PlannedComponent,
)
from ac14.loader import load_blueprint_dir
from ac14.meta_process_policy import DependencyProbePolicy, load_dependency_probe_policy
from ac14.models import (
    ArchitectureFile,
    Binding,
    CompilerProfile,
    ComponentDefinition,
    ComponentsFile,
    EvaluatorDefinition,
    Fixture,
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
_FIELD_TYPE_ALIASES = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "record": "object",
    "dict": "object",
}


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
    *,
    meta_process_config_path: Path | str | None = None,
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
    fixtures_file, fixture_ids_by_scenario = _build_fixtures_file(
        plan,
        schemas_file=schemas_file,
        components_file=components_file,
    )
    architecture_file = _build_architecture_file(plan)
    validation_file = _build_validation_file(plan, fixture_ids_by_scenario=fixture_ids_by_scenario)

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
        meta_process_config_path=meta_process_config_path,
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
    meta_process_config_path: Path | str | None = None,
) -> FreezeReadinessReport:
    """Build a persisted readiness report for a materialized draft bundle."""

    draft_dir = Path(draft_bundle_dir)
    dependency_probe_policy = load_dependency_probe_policy(meta_process_config_path)
    blueprint = load_blueprint_dir(draft_dir)
    validation_result = validate_blueprint(blueprint)
    authoring_findings = _authoring_findings(
        plan,
        blueprint.components.keys(),
        dependency_probe_policy=dependency_probe_policy,
    )
    findings = [
        *validation_result.findings,
        *(extra_findings or []),
        *authoring_findings,
    ]
    ready = not any(_is_blocking_finding(finding) for finding in findings)
    return FreezeReadinessReport(
        ready=ready,
        validation_passed=validation_result.passed,
        findings=findings,
    )


def _build_metadata_file(plan: DraftBlueprintPlanArtifact, plan_path: Path) -> MetadataFile:
    """Build draft metadata with frozen-profile defaults."""

    display_name = plan.planning_input_name or "Draft Blueprint"
    blueprint_stem = _slugify_blueprint_name(display_name)
    blueprint_id = f"{blueprint_stem}_draft_v0"
    return MetadataFile(
        metadata=Metadata(
            blueprint_id=blueprint_id,
            name=display_name,
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


def _slugify_blueprint_name(value: str) -> str:
    """Return a stable slug for metadata ids derived from planning provenance."""

    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "draft_blueprint"


def _build_schemas_file(
    plan: DraftBlueprintPlanArtifact,
    findings: list[ValidationFinding],
) -> SchemasFile:
    """Build draft schema definitions from planned schemas."""

    schemas: list[SchemaDefinition] = []
    schema_names = {planned_schema.schema_name for planned_schema in plan.proposed_schemas}
    for planned_schema in plan.proposed_schemas:
        if planned_schema.kind == "record":
            fields = [
                SchemaField(
                    name=field.field_name,
                    type=_normalize_schema_field_type(
                        field.field_type,
                        schema_names=schema_names,
                    ),
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


def _normalize_schema_field_type(
    field_type: str,
    *,
    schema_names: set[str],
) -> str:
    """Normalize structured-spec compact field types into blueprint field types."""

    normalized = field_type.strip()
    if not normalized:
        return normalized
    if normalized.startswith("enum:"):
        return normalized
    if normalized in schema_names:
        return normalized
    if normalized.startswith("list[") and normalized.endswith("]"):
        inner = normalized[5:-1].strip()
        return f"list[{_normalize_schema_field_type(inner, schema_names=schema_names)}]"
    alias = _FIELD_TYPE_ALIASES.get(normalized.lower())
    return alias if alias is not None else normalized


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


def _build_validation_file(
    plan: DraftBlueprintPlanArtifact,
    *,
    fixture_ids_by_scenario: dict[str, list[str]],
) -> ValidationFile:
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
            fixture_ids=fixture_ids_by_scenario.get(scenario.scenario_id, []),
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


def _build_fixtures_file(
    plan: DraftBlueprintPlanArtifact,
    *,
    schemas_file: SchemasFile,
    components_file: ComponentsFile,
) -> tuple[FixturesFile, dict[str, list[str]]]:
    """Build synthetic typed fixture coverage for draft bundles."""

    schema_lookup = {schema.schema_id: schema for schema in schemas_file.schemas}
    fixtures = []
    fixture_ids_by_scenario: dict[str, list[str]] = {}
    for scenario in plan.proposed_scenarios:
        scenario_fixture_ids: list[str] = []
        for component in components_file.components:
            fixture_id = f"{scenario.scenario_id}_{component.component_id}".lower()
            scenario_fixture_ids.append(fixture_id)
            fixtures.append(
                Fixture(
                    fixture_id=fixture_id,
                    scenario_id=scenario.scenario_id,
                    component_id=component.component_id,
                    description=(
                        f"Draft synthetic fixture for {component.component_id} under "
                        f"{scenario.scenario_id}; replace with benchmark- or data-backed "
                        "examples before claiming strong packet evidence."
                    ),
                    inputs={
                        port.name: _draft_payload_for_schema_id(
                            port.schema_id,
                            schema_lookup=schema_lookup,
                        )
                        for port in component.input_ports
                    },
                    expected_outputs={
                        port.name: _draft_payload_for_schema_id(
                            port.schema_id,
                            schema_lookup=schema_lookup,
                        )
                        for port in component.output_ports
                    },
                ),
            )
        fixture_ids_by_scenario[scenario.scenario_id] = scenario_fixture_ids
    return FixturesFile(fixtures=fixtures), fixture_ids_by_scenario


def _draft_payload_for_schema_id(
    schema_id: str,
    *,
    schema_lookup: dict[str, SchemaDefinition],
    visited: set[str] | None = None,
) -> dict[str, Any]:
    """Build one bounded synthetic payload for a named schema."""

    schema = schema_lookup.get(schema_id)
    if schema is None:
        return {}
    next_visited = set(visited or set())
    if schema_id in next_visited:
        return {}
    next_visited.add(schema_id)
    payload: dict[str, Any] = {}
    for field in schema.fields:
        if field.required:
            payload[field.name] = _draft_value_for_field_type(
                field.type,
                field_name=field.name,
                schema_lookup=schema_lookup,
                visited=next_visited,
            )
    return payload


def _draft_value_for_field_type(
    field_type: str,
    *,
    field_name: str,
    schema_lookup: dict[str, SchemaDefinition],
    visited: set[str],
) -> Any:
    """Build one deterministic synthetic value for a normalized field type."""

    normalized = field_type.strip()
    if normalized.startswith("enum:"):
        members = [member.strip() for member in normalized[5:].split(",") if member.strip()]
        return members[0] if members else f"draft_{field_name}"
    if normalized.startswith("list[") and normalized.endswith("]"):
        inner = normalized[5:-1].strip()
        return [
            _draft_value_for_field_type(
                inner,
                field_name=field_name,
                schema_lookup=schema_lookup,
                visited=visited,
            ),
        ]
    if normalized.startswith("array[") and normalized.endswith("]"):
        inner = normalized[6:-1].strip()
        return [
            _draft_value_for_field_type(
                inner,
                field_name=field_name,
                schema_lookup=schema_lookup,
                visited=visited,
            ),
        ]
    if normalized in ("list", "array"):
        return []
    if normalized == "string":
        return f"draft_{field_name}"
    if normalized == "integer":
        return 0
    if normalized == "number":
        return 0.0
    if normalized == "boolean":
        return False
    if normalized == "object":
        return {}
    if normalized in schema_lookup:
        return _draft_payload_for_schema_id(
            normalized,
            schema_lookup=schema_lookup,
            visited=visited,
        )
    return f"draft_{field_name}"


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
    *,
    dependency_probe_policy: DependencyProbePolicy,
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
    if dependency_probe_policy != "ignore":
        code = (
            "E-DRAFT-DEPENDENCY-PROBE-BLOCKED"
            if dependency_probe_policy == "strict"
            else "W-DRAFT-DEPENDENCY-PROBE-BLOCKED"
        )
        for blocked_probe in plan.blocked_dependency_probes:
            findings.append(
                ValidationFinding(
                    code=code,
                    message=f"dependency probe still blocked before freeze: {blocked_probe}",
                    path="plan.blocked_dependency_probes",
                ),
            )
    if plan.proposed_scenarios and resolved_component_ids:
        findings.append(
            ValidationFinding(
                code="W-DRAFT-SYNTHETIC-FIXTURE-COVERAGE",
                message=(
                    "draft bundle uses synthetic typed fixtures generated from planned "
                    "schemas and ports; replace them with benchmark- or data-backed "
                    "fixtures before claiming strong packet evidence"
                ),
                path="fixtures",
            ),
        )
    return findings


def _is_blocking_finding(finding: ValidationFinding) -> bool:
    """Return whether one readiness finding should block freeze approval."""

    return finding.code.startswith("E-")


def _write_yaml(path: Path, payload: dict[str, object]) -> None:
    """Write one YAML artifact with stable key order."""

    path.write_text(yaml.safe_dump(payload, sort_keys=False))

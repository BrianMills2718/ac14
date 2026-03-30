"""B1 blueprint validation for AC14 frozen blueprints."""

from __future__ import annotations

from collections import Counter
from graphlib import CycleError, TopologicalSorter

from ac14.models import (
    ComponentDefinition,
    FrozenBlueprint,
    InputPort,
    OutputPort,
    ValidationFinding,
    ValidationResult,
)


def validate_blueprint(blueprint: FrozenBlueprint) -> ValidationResult:
    """Validate schema references, binding integrity, and graph structure."""

    findings: list[ValidationFinding] = []

    _validate_component_ports(blueprint, findings)
    _validate_schema_references(blueprint, findings)
    _validate_state_stores(blueprint, findings)
    _validate_bindings(blueprint, findings)
    _validate_fixture_references(blueprint, findings)
    _validate_scenarios_and_coverage(blueprint, findings)
    _validate_graph(blueprint, findings)

    return ValidationResult(passed=not findings, findings=findings)


def _validate_component_ports(
    blueprint: FrozenBlueprint,
    findings: list[ValidationFinding],
) -> None:
    """Fail on duplicate port names within a component."""

    for component in blueprint.components.values():
        _check_duplicate_names(
            component,
            [port.name for port in component.input_ports],
            "E-B1-DUPLICATE-INPUT-PORT",
            "input_ports",
            findings,
        )
        _check_duplicate_names(
            component,
            [port.name for port in component.output_ports],
            "E-B1-DUPLICATE-OUTPUT-PORT",
            "output_ports",
            findings,
        )


def _check_duplicate_names(
    component: ComponentDefinition,
    names: list[str],
    code: str,
    field_name: str,
    findings: list[ValidationFinding],
) -> None:
    """Append findings for duplicate port names."""

    duplicates = [name for name, count in Counter(names).items() if count > 1]
    for duplicate in duplicates:
        findings.append(
            ValidationFinding(
                code=code,
                message=f"duplicate port name '{duplicate}' in component {component.component_id}",
                path=f"components.{component.component_id}.{field_name}",
            ),
        )


def _validate_schema_references(
    blueprint: FrozenBlueprint,
    findings: list[ValidationFinding],
) -> None:
    """Ensure every port and schema field reference resolves."""

    for schema in blueprint.schemas.values():
        for field in schema.fields:
            if field.required is False and (not field.optional_reason or not field.absence_meaning):
                findings.append(
                    ValidationFinding(
                        code="E-B1-OPTIONAL-FIELD-INCOMPLETE",
                        message=(
                            f"optional field '{field.name}' in schema {schema.schema_id} "
                            "must declare optional_reason and absence_meaning"
                        ),
                        path=f"schemas.{schema.schema_id}.fields.{field.name}",
                    ),
                )
            if _is_named_schema_reference(field.type) and _strip_container(field.type) not in blueprint.schemas:
                findings.append(
                    ValidationFinding(
                        code="E-B1-SCHEMA-FIELD-REF-MISSING",
                        message=(
                            f"field '{field.name}' in schema {schema.schema_id} references "
                            f"unknown schema '{_strip_container(field.type)}'"
                        ),
                        path=f"schemas.{schema.schema_id}.fields.{field.name}",
                    ),
                )

    for component in blueprint.components.values():
        for input_port in component.input_ports:
            if input_port.schema_id not in blueprint.schemas:
                findings.append(
                    ValidationFinding(
                        code="E-B1-INPUT-SCHEMA-MISSING",
                        message=(
                            f"component {component.component_id} input port {input_port.name} "
                            f"references missing schema {input_port.schema_id}"
                        ),
                        path=f"components.{component.component_id}.input_ports.{input_port.name}",
                    ),
                )
        for output_port in component.output_ports:
            if output_port.schema_id not in blueprint.schemas:
                findings.append(
                    ValidationFinding(
                        code="E-B1-OUTPUT-SCHEMA-MISSING",
                        message=(
                            f"component {component.component_id} output port {output_port.name} "
                            f"references missing schema {output_port.schema_id}"
                        ),
                        path=f"components.{component.component_id}.output_ports.{output_port.name}",
                    ),
                )


def _validate_state_stores(
    blueprint: FrozenBlueprint,
    findings: list[ValidationFinding],
) -> None:
    """Validate state store owner and schema references."""

    for store in blueprint.state_stores.values():
        if store.owner_component not in blueprint.components:
            findings.append(
                ValidationFinding(
                    code="E-B1-STATE-OWNER-MISSING",
                    message=f"state store {store.store_id} references missing owner {store.owner_component}",
                    path=f"architecture.state_stores.{store.store_id}.owner_component",
                ),
            )
        if store.schema_id not in blueprint.schemas:
            findings.append(
                ValidationFinding(
                    code="E-B1-STATE-SCHEMA-MISSING",
                    message=f"state store {store.store_id} references missing schema {store.schema_id}",
                    path=f"architecture.state_stores.{store.store_id}.schema_id",
                ),
            )


def _validate_bindings(
    blueprint: FrozenBlueprint,
    findings: list[ValidationFinding],
) -> None:
    """Validate binding endpoints and exact schema compatibility."""

    for index, binding in enumerate(blueprint.bindings):
        source_component = blueprint.components.get(binding.from_component)
        target_component = blueprint.components.get(binding.to_component)

        if source_component is None:
            findings.append(
                ValidationFinding(
                    code="E-B1-BINDING-SOURCE-MISSING",
                    message=f"binding references missing source component {binding.from_component}",
                    path=f"architecture.bindings.{index}.from_component",
                ),
            )
            continue
        if target_component is None:
            findings.append(
                ValidationFinding(
                    code="E-B1-BINDING-TARGET-MISSING",
                    message=f"binding references missing target component {binding.to_component}",
                    path=f"architecture.bindings.{index}.to_component",
                ),
            )
            continue

        source_port = _find_output_port(source_component, binding.from_port)
        target_port = _find_input_port(target_component, binding.to_port)

        if source_port is None:
            findings.append(
                ValidationFinding(
                    code="E-B1-BINDING-SOURCE-PORT-MISSING",
                    message=(
                        f"binding references missing output port {binding.from_port} "
                        f"on {binding.from_component}"
                    ),
                    path=f"architecture.bindings.{index}.from_port",
                ),
            )
            continue
        if target_port is None:
            findings.append(
                ValidationFinding(
                    code="E-B1-BINDING-TARGET-PORT-MISSING",
                    message=(
                        f"binding references missing input port {binding.to_port} "
                        f"on {binding.to_component}"
                    ),
                    path=f"architecture.bindings.{index}.to_port",
                ),
            )
            continue
        if source_port.schema_id != target_port.schema_id:
            findings.append(
                ValidationFinding(
                    code="E-B1-BINDING-SCHEMA-MISMATCH",
                    message=(
                        f"binding {binding.from_component}.{binding.from_port} -> "
                        f"{binding.to_component}.{binding.to_port} mismatches "
                        f"{source_port.schema_id} vs {target_port.schema_id}"
                    ),
                    path=f"architecture.bindings.{index}",
                ),
            )


def _validate_fixture_references(
    blueprint: FrozenBlueprint,
    findings: list[ValidationFinding],
) -> None:
    """Ensure scenarios and fixtures refer to known objects and declared ports."""

    for scenario in blueprint.scenarios.values():
        for fixture_id in scenario.fixture_ids:
            if fixture_id not in blueprint.fixtures:
                findings.append(
                    ValidationFinding(
                        code="E-B1-SCENARIO-FIXTURE-MISSING",
                        message=f"scenario {scenario.scenario_id} references missing fixture {fixture_id}",
                        path=f"validation.scenarios.{scenario.scenario_id}.fixture_ids",
                    ),
                )
        for evaluator_id in scenario.evaluator_ids:
            if evaluator_id not in blueprint.evaluators:
                findings.append(
                    ValidationFinding(
                        code="E-B1-SCENARIO-EVALUATOR-MISSING",
                        message=(
                            f"scenario {scenario.scenario_id} references missing evaluator "
                            f"{evaluator_id}"
                        ),
                        path=f"validation.scenarios.{scenario.scenario_id}.evaluator_ids",
                    ),
                )

    for fixture in blueprint.fixtures.values():
        component = blueprint.components.get(fixture.component_id)
        if component is None:
            findings.append(
                ValidationFinding(
                    code="E-B1-FIXTURE-COMPONENT-MISSING",
                    message=f"fixture {fixture.fixture_id} references missing component {fixture.component_id}",
                    path=f"fixtures.{fixture.fixture_id}.component_id",
                ),
            )
            continue
        if fixture.scenario_id not in blueprint.scenarios:
            findings.append(
                ValidationFinding(
                    code="E-B1-FIXTURE-SCENARIO-MISSING",
                    message=f"fixture {fixture.fixture_id} references missing scenario {fixture.scenario_id}",
                    path=f"fixtures.{fixture.fixture_id}.scenario_id",
                ),
            )
        input_port_names = {port.name for port in component.input_ports}
        output_port_names = {port.name for port in component.output_ports}
        for input_name in fixture.inputs:
            if input_name not in input_port_names:
                findings.append(
                    ValidationFinding(
                        code="E-B1-FIXTURE-INPUT-PORT-MISSING",
                        message=(
                            f"fixture {fixture.fixture_id} references unknown input port "
                            f"{input_name} on {component.component_id}"
                        ),
                        path=f"fixtures.{fixture.fixture_id}.inputs.{input_name}",
                    ),
                )
        for output_name in fixture.expected_outputs:
            if output_name not in output_port_names:
                findings.append(
                    ValidationFinding(
                        code="E-B1-FIXTURE-OUTPUT-PORT-MISSING",
                        message=(
                            f"fixture {fixture.fixture_id} references unknown output port "
                            f"{output_name} on {component.component_id}"
                        ),
                        path=f"fixtures.{fixture.fixture_id}.expected_outputs.{output_name}",
                    ),
                )


def _validate_scenarios_and_coverage(
    blueprint: FrozenBlueprint,
    findings: list[ValidationFinding],
) -> None:
    """Validate scenario intent, evaluator usage, and fixture coverage rules."""

    fixture_ids_by_component: dict[str, list[str]] = {component_id: [] for component_id in blueprint.components}
    for fixture in blueprint.fixtures.values():
        if fixture.component_id in fixture_ids_by_component:
            fixture_ids_by_component[fixture.component_id].append(fixture.fixture_id)

    for component_id, fixture_ids in fixture_ids_by_component.items():
        if not fixture_ids:
            findings.append(
                ValidationFinding(
                    code="E-B1-COMPONENT-FIXTURE-COVERAGE-MISSING",
                    message=f"component {component_id} has no fixture coverage",
                    path=f"components.{component_id}",
                ),
            )

    recomposition_like_count = 0
    semantic_acceptance_count = 0
    realistic_input_count = 0
    all_component_ids = set(blueprint.components)

    for scenario in blueprint.scenarios.values():
        if not scenario.evaluator_ids:
            findings.append(
                ValidationFinding(
                    code="E-B1-SCENARIO-EVALUATORS-EMPTY",
                    message=f"scenario {scenario.scenario_id} must declare at least one evaluator",
                    path=f"validation.scenarios.{scenario.scenario_id}.evaluator_ids",
                ),
            )
        evaluator_kinds = {
            blueprint.evaluators[evaluator_id].kind
            for evaluator_id in scenario.evaluator_ids
            if evaluator_id in blueprint.evaluators
        }
        if scenario.kind == "negative" and "programmatic_failure" not in evaluator_kinds:
            findings.append(
                ValidationFinding(
                    code="E-B1-NEGATIVE-SCENARIO-EVALUATOR-MISSING",
                    message=(
                        f"negative scenario {scenario.scenario_id} must use a "
                        "programmatic_failure evaluator"
                    ),
                    path=f"validation.scenarios.{scenario.scenario_id}.evaluator_ids",
                ),
            )
        if scenario.kind == "semantic_acceptance":
            semantic_acceptance_count += 1
            if not scenario.requirements:
                findings.append(
                    ValidationFinding(
                        code="E-B1-SEMANTIC-SCENARIO-REQUIREMENTS-MISSING",
                        message=(
                            f"semantic_acceptance scenario {scenario.scenario_id} must declare requirements"
                        ),
                        path=f"validation.scenarios.{scenario.scenario_id}.requirements",
                    ),
                )
            if "llm_requirements_acceptance" not in evaluator_kinds:
                findings.append(
                    ValidationFinding(
                        code="E-B1-SEMANTIC-SCENARIO-LLM-EVALUATOR-MISSING",
                        message=(
                            f"semantic_acceptance scenario {scenario.scenario_id} must use an "
                            "llm_requirements_acceptance evaluator"
                        ),
                        path=f"validation.scenarios.{scenario.scenario_id}.evaluator_ids",
                    ),
                )
        if scenario.kind in {"full_recomposition", "semantic_acceptance"}:
            recomposition_like_count += 1
            if scenario.realistic_input:
                realistic_input_count += 1
            fixture_component_ids = {
                blueprint.fixtures[fixture_id].component_id
                for fixture_id in scenario.fixture_ids
                if fixture_id in blueprint.fixtures
            }
            missing_components = sorted(all_component_ids.difference(fixture_component_ids))
            if missing_components:
                findings.append(
                    ValidationFinding(
                        code="E-B1-END-TO-END-SCENARIO-COVERAGE-MISSING",
                        message=(
                            f"scenario {scenario.scenario_id} is missing component fixtures for: "
                            + ", ".join(missing_components)
                        ),
                        path=f"validation.scenarios.{scenario.scenario_id}.fixture_ids",
                    ),
                )

    if recomposition_like_count == 0:
        findings.append(
            ValidationFinding(
                code="E-B1-FULL-SCENARIO-MISSING",
                message="blueprint must declare at least one full_recomposition or semantic_acceptance scenario",
                path="validation.scenarios",
            ),
        )
    if semantic_acceptance_count == 0:
        findings.append(
            ValidationFinding(
                code="E-B1-SEMANTIC-ACCEPTANCE-SCENARIO-MISSING",
                message="blueprint must declare at least one semantic_acceptance scenario",
                path="validation.scenarios",
            ),
        )
    if realistic_input_count == 0:
        findings.append(
            ValidationFinding(
                code="E-B1-REALISTIC-INPUT-SCENARIO-MISSING",
                message=(
                    "blueprint must declare at least one realistic-input full-system scenario"
                ),
                path="validation.scenarios",
            ),
        )


def _validate_graph(
    blueprint: FrozenBlueprint,
    findings: list[ValidationFinding],
) -> None:
    """Fail loud when the component graph is cyclic."""

    graph: dict[str, set[str]] = {component_id: set() for component_id in blueprint.components}
    for binding in blueprint.bindings:
        if binding.from_component in graph and binding.to_component in graph:
            graph[binding.to_component].add(binding.from_component)
    try:
        tuple(TopologicalSorter(graph).static_order())
    except CycleError as exc:
        findings.append(
            ValidationFinding(
                code="E-B1-GRAPH-CYCLE",
                message=f"component graph contains a cycle: {exc.args[1]}",
                path="architecture.bindings",
            ),
        )


def _is_named_schema_reference(field_type: str) -> bool:
    """Return true when a field type points at another named schema."""

    if field_type.startswith("enum:"):
        return False
    stripped = _strip_container(field_type)
    primitives = {"string", "integer", "number", "boolean"}
    return stripped not in primitives


def _strip_container(field_type: str) -> str:
    """Strip simple list[...] wrappers from field types."""

    if field_type.startswith("list[") and field_type.endswith("]"):
        return field_type[5:-1]
    return field_type


def _find_output_port(component: ComponentDefinition, port_name: str) -> OutputPort | None:
    """Find one output port by name."""

    return next((port for port in component.output_ports if port.name == port_name), None)


def _find_input_port(component: ComponentDefinition, port_name: str) -> InputPort | None:
    """Find one input port by name."""

    return next((port for port in component.input_ports if port.name == port_name), None)

"""Packet compilation and B2 validation for AC14 blueprints."""

from __future__ import annotations

from graphlib import TopologicalSorter
from typing import Iterable

from ac14.models import (
    Binding,
    ComponentPacket,
    ComponentSummary,
    FrozenBlueprint,
    PacketBundle,
    RecompositionPlan,
    ValidationFinding,
    ValidationResult,
)


def compile_packets(blueprint: FrozenBlueprint) -> PacketBundle:
    """Compile bounded component-local packets from a frozen blueprint."""

    packets: dict[str, ComponentPacket] = {}
    for component_id, component in blueprint.components.items():
        inbound_bindings = [binding for binding in blueprint.bindings if binding.to_component == component_id]
        outbound_bindings = [binding for binding in blueprint.bindings if binding.from_component == component_id]
        schema_ids = {port.schema_id for port in component.input_ports + component.output_ports}
        owned_state_stores = {
            store_id: store
            for store_id, store in blueprint.state_stores.items()
            if store.owner_component == component_id
        }
        schema_ids.update(store.schema_id for store in owned_state_stores.values())
        local_fixtures = {
            fixture_id: fixture
            for fixture_id, fixture in blueprint.fixtures.items()
            if fixture.component_id == component_id
        }
        relevant_scenarios = {
            scenario_id: scenario
            for scenario_id, scenario in blueprint.scenarios.items()
            if any(fixture_id in local_fixtures for fixture_id in scenario.fixture_ids)
        }
        packets[component_id] = ComponentPacket(
            blueprint_id=blueprint.metadata.blueprint_id,
            component=component,
            local_schemas={schema_id: blueprint.schemas[schema_id] for schema_id in schema_ids},
            inbound_bindings=inbound_bindings,
            outbound_bindings=outbound_bindings,
            upstream_components={
                binding.from_component: _component_summary(blueprint, binding.from_component)
                for binding in inbound_bindings
            },
            downstream_components={
                binding.to_component: _component_summary(blueprint, binding.to_component)
                for binding in outbound_bindings
            },
            owned_state_stores=owned_state_stores,
            relevant_invariants=list(blueprint.global_invariants),
            relevant_scenarios=relevant_scenarios,
            local_fixtures=local_fixtures,
        )

    recomposition_plan = RecompositionPlan(
        execution_order=_topological_order(blueprint.bindings, blueprint.components.keys()),
        bindings=list(blueprint.bindings),
        state_store_owners={
            store_id: store.owner_component for store_id, store in blueprint.state_stores.items()
        },
    )
    return PacketBundle(
        blueprint_id=blueprint.metadata.blueprint_id,
        packets=packets,
        recomposition_plan=recomposition_plan,
    )


def validate_packets(packet_bundle: PacketBundle, blueprint: FrozenBlueprint) -> ValidationResult:
    """Validate packet completeness and local fixture compatibility."""

    findings: list[ValidationFinding] = []
    for component_id, component in blueprint.components.items():
        packet = packet_bundle.packets.get(component_id)
        if packet is None:
            findings.append(
                ValidationFinding(
                    code="E-B2-PACKET-MISSING",
                    message=f"missing packet for component {component_id}",
                    path=f"packets.{component_id}",
                ),
            )
            continue

        required_schema_ids = {port.schema_id for port in component.input_ports + component.output_ports}
        required_schema_ids.update(
            store.schema_id
            for store in blueprint.state_stores.values()
            if store.owner_component == component_id
        )
        missing_schema_ids = sorted(required_schema_ids - set(packet.local_schemas))
        for schema_id in missing_schema_ids:
            findings.append(
                ValidationFinding(
                    code="E-B2-PACKET-SCHEMA-MISSING",
                    message=f"packet {component_id} is missing schema {schema_id}",
                    path=f"packets.{component_id}.local_schemas.{schema_id}",
                ),
            )

        input_port_names = {port.name for port in component.input_ports}
        output_port_names = {port.name for port in component.output_ports}
        if not packet.local_fixtures:
            findings.append(
                ValidationFinding(
                    code="E-B2-PACKET-FIXTURE-MISSING",
                    message=f"packet {component_id} has no local fixtures",
                    path=f"packets.{component_id}.local_fixtures",
                ),
            )
        for fixture_id, fixture in packet.local_fixtures.items():
            for input_name in fixture.inputs:
                if input_name not in input_port_names:
                    findings.append(
                        ValidationFinding(
                            code="E-B2-PACKET-FIXTURE-INPUT-MISMATCH",
                            message=(
                                f"packet fixture {fixture_id} references unknown input port "
                                f"{input_name} for {component_id}"
                            ),
                            path=f"packets.{component_id}.local_fixtures.{fixture_id}.inputs.{input_name}",
                        ),
                    )
            for output_name in fixture.expected_outputs:
                if output_name not in output_port_names:
                    findings.append(
                        ValidationFinding(
                            code="E-B2-PACKET-FIXTURE-OUTPUT-MISMATCH",
                            message=(
                                f"packet fixture {fixture_id} references unknown output port "
                                f"{output_name} for {component_id}"
                            ),
                            path=(
                                f"packets.{component_id}.local_fixtures."
                                f"{fixture_id}.expected_outputs.{output_name}"
                            ),
                        ),
                    )
        missing_scenarios = sorted(
            {
                fixture.scenario_id
                for fixture in packet.local_fixtures.values()
                if fixture.scenario_id not in packet.relevant_scenarios
            },
        )
        for scenario_id in missing_scenarios:
            findings.append(
                ValidationFinding(
                    code="E-B2-PACKET-SCENARIO-MISSING",
                    message=f"packet {component_id} is missing scenario {scenario_id}",
                    path=f"packets.{component_id}.relevant_scenarios.{scenario_id}",
                ),
            )

    expected_order = set(blueprint.components)
    actual_order = set(packet_bundle.recomposition_plan.execution_order)
    if expected_order != actual_order:
        findings.append(
            ValidationFinding(
                code="E-B2-RECOMPOSITION-ORDER-INCOMPLETE",
                message="recomposition execution order does not cover all components",
                path="recomposition_plan.execution_order",
            ),
        )

    return ValidationResult(passed=not findings, findings=findings)


def _component_summary(blueprint: FrozenBlueprint, component_id: str) -> ComponentSummary:
    """Build a packet-local summary for one neighbor component."""

    component = blueprint.components[component_id]
    return ComponentSummary(
        component_id=component.component_id,
        purpose=component.purpose,
        semantic_responsibility=component.semantic_responsibility,
    )


def _topological_order(bindings: list[Binding], component_ids: Iterable[str]) -> list[str]:
    """Compute topological execution order from component bindings."""

    graph: dict[str, set[str]] = {component_id: set() for component_id in component_ids}
    for binding in bindings:
        graph[binding.to_component].add(binding.from_component)
    return list(TopologicalSorter(graph).static_order())

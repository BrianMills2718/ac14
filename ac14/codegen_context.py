"""Code-generation context built from packets and packet-local test cases."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ac14.models import ComponentPacket, ComponentSummary, SchemaDefinition, StateStore
from ac14.packet_tests import PacketTestCase


class CodegenContext(BaseModel):
    """Bounded local context that can be handed to a component generator."""

    component_id: str = Field(description="Target component identifier.")
    purpose: str = Field(description="Human-readable component purpose.")
    semantic_responsibility: str = Field(description="Stable semantic responsibility label.")
    input_ports: dict[str, str] = Field(description="Input port names keyed to schema ids.")
    output_ports: dict[str, str] = Field(description="Output port names keyed to schema ids.")
    local_invariants: list[str] = Field(description="Local invariants for the component.")
    failure_semantics: list[str] = Field(description="Failure semantics for the component.")
    implementation_constraints: list[str] = Field(
        description="Hard implementation constraints for the component.",
    )
    local_schemas: dict[str, SchemaDefinition] = Field(
        description="Schemas needed to implement the component.",
    )
    upstream_components: dict[str, ComponentSummary] = Field(
        description="Immediate upstream component summaries.",
    )
    downstream_components: dict[str, ComponentSummary] = Field(
        description="Immediate downstream component summaries.",
    )
    owned_state_stores: dict[str, StateStore] = Field(
        description="State stores owned by the component.",
    )
    packet_test_cases: list[PacketTestCase] = Field(
        description="Packet-local test cases derived from fixtures.",
    )


def build_codegen_context(
    packet: ComponentPacket,
    packet_test_cases: list[PacketTestCase],
) -> CodegenContext:
    """Project one component packet into the bounded code-generation context."""

    component = packet.component
    return CodegenContext(
        component_id=component.component_id,
        purpose=component.purpose,
        semantic_responsibility=component.semantic_responsibility,
        input_ports={port.name: port.schema_id for port in component.input_ports},
        output_ports={port.name: port.schema_id for port in component.output_ports},
        local_invariants=list(component.local_invariants),
        failure_semantics=list(component.failure_semantics),
        implementation_constraints=list(component.implementation_constraints),
        local_schemas=dict(packet.local_schemas),
        upstream_components=dict(packet.upstream_components),
        downstream_components=dict(packet.downstream_components),
        owned_state_stores=dict(packet.owned_state_stores),
        packet_test_cases=list(packet_test_cases),
    )


def render_codegen_context_text(context: CodegenContext) -> str:
    """Render a compact plain-text prompt surface for a future component generator."""

    input_ports = ", ".join(
        f"{port_name}:{schema_id}" for port_name, schema_id in sorted(context.input_ports.items())
    )
    output_ports = ", ".join(
        f"{port_name}:{schema_id}" for port_name, schema_id in sorted(context.output_ports.items())
    )
    upstream = ", ".join(sorted(context.upstream_components)) or "(none)"
    downstream = ", ".join(sorted(context.downstream_components)) or "(none)"
    tests = ", ".join(case.fixture_id for case in context.packet_test_cases) or "(none)"
    return "\n".join(
        [
            f"component_id: {context.component_id}",
            f"purpose: {context.purpose}",
            f"semantic_responsibility: {context.semantic_responsibility}",
            f"input_ports: {input_ports}",
            f"output_ports: {output_ports}",
            f"upstream_components: {upstream}",
            f"downstream_components: {downstream}",
            f"packet_test_cases: {tests}",
        ],
    )

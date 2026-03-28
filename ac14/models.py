"""Pydantic models for AC14 blueprint files, canonical blueprints, and packets."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """Identity and provenance metadata for a frozen blueprint."""

    blueprint_id: str = Field(description="Stable identifier for the blueprint.")
    name: str = Field(description="Human-readable blueprint name.")
    version: str = Field(description="Semantic or project-local version string.")
    purpose: str = Field(description="Why this blueprint exists.")
    source_kind: str = Field(description="Origin category for the blueprint.")
    created_from: str = Field(description="Provenance note for blueprint creation.")


class CompilerProfile(BaseModel):
    """Compilation-mode choices that affect how the blueprint is interpreted."""

    target_backend: Literal["python"] = Field(description="Current backend target.")
    execution_model: Literal["latest_value_dag"] = Field(
        description="Runtime execution model for v1.",
    )
    component_model: Literal["typed_component_graph"] = Field(
        description="Component graph model used by the compiler.",
    )
    validation_profile: Literal["code_component_v1"] = Field(
        description="Validation profile for the first proof slice.",
    )


class GenerationPolicy(BaseModel):
    """Generation choices that shape packet and code-generation behavior."""

    packet_test_mode: str = Field(description="How packet-local tests are sourced.")
    codegen_target: str = Field(description="Backend implementation target.")


class SchemaField(BaseModel):
    """Field definition inside a named object schema."""

    name: str = Field(description="Field name.")
    type: str = Field(description="Field type string.")
    required: bool = Field(description="Whether this field must be present.")
    description: str = Field(description="Semantic meaning of the field.")
    optional_reason: str | None = Field(
        default=None,
        description="Why the field may be absent when required is false.",
    )
    absence_meaning: str | None = Field(
        default=None,
        description="Meaning of absence for optional fields.",
    )


class SchemaDefinition(BaseModel):
    """Named object schema referenced by component ports and state stores."""

    schema_id: str = Field(description="Stable schema identifier.")
    kind: Literal["object"] = Field(description="Schema kind.")
    description: str = Field(description="What this schema represents.")
    fields: list[SchemaField] = Field(description="Named fields for the schema.")


class OutputPort(BaseModel):
    """Output port definition for a component."""

    name: str = Field(description="Port name.")
    schema_id: str = Field(description="Schema emitted from this port.")
    description: str = Field(description="Semantic meaning of the output.")


class InputPort(OutputPort):
    """Input port definition including arrival semantics."""

    required: bool = Field(description="Whether a value must arrive for execution.")
    arrival_policy: Literal["required_latest", "optional_latest"] = Field(
        description="Arrival policy for this input port.",
    )


class ComponentDefinition(BaseModel):
    """Frozen component definition inside the canonical blueprint."""

    component_id: str = Field(description="Stable component identifier.")
    kind: Literal["source", "transform", "join", "sink"] = Field(
        description="Execution role for the component.",
    )
    purpose: str = Field(description="Human-readable component purpose.")
    semantic_responsibility: str = Field(description="Stable machine-join label.")
    input_ports: list[InputPort] = Field(description="Input port definitions.")
    output_ports: list[OutputPort] = Field(description="Output port definitions.")
    local_invariants: list[str] = Field(description="Local component invariants.")
    failure_semantics: list[str] = Field(description="How the component must fail.")
    implementation_constraints: list[str] = Field(
        description="Hard constraints on implementation behavior.",
    )


class Binding(BaseModel):
    """Architecture edge between one component output port and one input port."""

    from_component: str = Field(description="Source component identifier.")
    from_port: str = Field(description="Source output port name.")
    to_component: str = Field(description="Destination component identifier.")
    to_port: str = Field(description="Destination input port name.")


class StateStore(BaseModel):
    """State owned by exactly one component."""

    store_id: str = Field(description="Stable state store identifier.")
    owner_component: str = Field(description="Component that owns updates.")
    schema_id: str = Field(description="Schema used for the store snapshot.")
    description: str = Field(description="What the store represents.")
    update_semantics: str = Field(description="State update rule for the store.")


class GlobalInvariant(BaseModel):
    """Cross-component invariant checked at validation or recomposition time."""

    invariant_id: str = Field(description="Stable invariant identifier.")
    description: str = Field(description="Invariant meaning.")


class Scenario(BaseModel):
    """Named validation scenario that points to one or more fixtures."""

    scenario_id: str = Field(description="Stable scenario identifier.")
    description: str = Field(description="Scenario meaning.")
    fixture_ids: list[str] = Field(description="Referenced fixture identifiers.")


class Fixture(BaseModel):
    """Component-local fixture used for packet tests or recomposition examples."""

    fixture_id: str = Field(description="Stable fixture identifier.")
    scenario_id: str = Field(description="Owning scenario identifier.")
    component_id: str = Field(description="Component this fixture targets.")
    description: str = Field(description="What this fixture proves.")
    inputs: dict[str, dict[str, Any]] = Field(
        description="Port-keyed input payloads for the fixture.",
    )
    expected_outputs: dict[str, dict[str, Any]] = Field(
        description="Port-keyed expected outputs for the fixture.",
    )


class MetadataFile(BaseModel):
    """On-disk metadata file shape."""

    metadata: Metadata = Field(description="Blueprint metadata block.")
    compiler_profile: CompilerProfile = Field(description="Compiler profile block.")
    generation_policy: GenerationPolicy = Field(description="Generation policy block.")


class SchemasFile(BaseModel):
    """On-disk schema file shape."""

    schemas: list[SchemaDefinition] = Field(description="Named schema definitions.")


class ComponentsFile(BaseModel):
    """On-disk component file shape."""

    components: list[ComponentDefinition] = Field(description="Frozen component definitions.")


class ArchitectureFile(BaseModel):
    """On-disk architecture file shape."""

    bindings: list[Binding] = Field(description="Explicit component bindings.")
    state_stores: list[StateStore] = Field(
        default_factory=list,
        description="Declared state stores and owners.",
    )


class ValidationFile(BaseModel):
    """On-disk validation file shape."""

    global_invariants: list[GlobalInvariant] = Field(
        default_factory=list,
        description="Cross-component invariants.",
    )
    scenarios: list[Scenario] = Field(description="Named validation scenarios.")


class FixturesFile(BaseModel):
    """On-disk fixtures file shape."""

    fixtures: list[Fixture] = Field(description="Component-local fixtures.")


class FrozenBlueprint(BaseModel):
    """Canonical in-memory blueprint used by validators and packet compilers."""

    metadata: Metadata = Field(description="Blueprint identity metadata.")
    compiler_profile: CompilerProfile = Field(description="Compilation mode.")
    schemas: dict[str, SchemaDefinition] = Field(description="Schemas keyed by schema_id.")
    components: dict[str, ComponentDefinition] = Field(
        description="Components keyed by component_id.",
    )
    bindings: list[Binding] = Field(description="Explicit architecture bindings.")
    state_stores: dict[str, StateStore] = Field(description="State stores keyed by store_id.")
    global_invariants: list[GlobalInvariant] = Field(
        description="Global invariants for validation and recomposition.",
    )
    scenarios: dict[str, Scenario] = Field(description="Scenarios keyed by scenario_id.")
    fixtures: dict[str, Fixture] = Field(description="Fixtures keyed by fixture_id.")
    generation_policy: GenerationPolicy = Field(description="Packet/code generation policy.")


class ValidationFinding(BaseModel):
    """Single validation failure or warning."""

    code: str = Field(description="Stable machine-readable code.")
    message: str = Field(description="Human-readable explanation.")
    path: str = Field(description="Path-like location for the problem.")


class ValidationResult(BaseModel):
    """Validation result for a blueprint or packet bundle."""

    passed: bool = Field(description="Whether validation succeeded.")
    findings: list[ValidationFinding] = Field(description="Collected findings.")


class ComponentSummary(BaseModel):
    """Neighbor summary stored in component packets."""

    component_id: str = Field(description="Neighbor component identifier.")
    purpose: str = Field(description="Neighbor purpose.")
    semantic_responsibility: str = Field(description="Neighbor semantic responsibility.")


class ComponentPacket(BaseModel):
    """Bounded local context packet compiled for one component."""

    component: ComponentDefinition = Field(description="Target component definition.")
    local_schemas: dict[str, SchemaDefinition] = Field(
        description="Schemas needed by the component packet.",
    )
    inbound_bindings: list[Binding] = Field(description="Inbound bindings.")
    outbound_bindings: list[Binding] = Field(description="Outbound bindings.")
    upstream_components: dict[str, ComponentSummary] = Field(
        description="Summaries of immediate upstream components.",
    )
    downstream_components: dict[str, ComponentSummary] = Field(
        description="Summaries of immediate downstream components.",
    )
    owned_state_stores: dict[str, StateStore] = Field(
        description="State stores owned by this component.",
    )
    relevant_invariants: list[GlobalInvariant] = Field(
        description="Invariants relevant to the packet.",
    )
    relevant_scenarios: dict[str, Scenario] = Field(
        description="Scenarios referenced by local fixtures.",
    )
    local_fixtures: dict[str, Fixture] = Field(
        description="Packet-local fixtures keyed by fixture_id.",
    )


class RecompositionPlan(BaseModel):
    """Execution-oriented recomposition view for a frozen blueprint."""

    execution_order: list[str] = Field(description="Topological component execution order.")
    bindings: list[Binding] = Field(description="Bindings preserved for recomposition.")
    state_store_owners: dict[str, str] = Field(
        description="Mapping from state store id to owner component.",
    )


class PacketBundle(BaseModel):
    """All component packets plus the recomposition plan."""

    packets: dict[str, ComponentPacket] = Field(
        description="Component packets keyed by component_id.",
    )
    recomposition_plan: RecompositionPlan = Field(
        description="Shared recomposition plan for the blueprint.",
    )

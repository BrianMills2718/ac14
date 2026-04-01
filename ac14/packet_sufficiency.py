"""Persisted structural packet-sufficiency artifacts for bounded local generation."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from ac14.codegen_context import build_codegen_context
from ac14.loader import load_blueprint_dir
from ac14.models import ComponentPacket, ValidationFinding
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets, validate_packets
from ac14.codegen_context import CodegenContext


class PacketSufficiencyEntry(BaseModel):
    """Structural sufficiency result for one packet."""

    component_id: str = Field(description="Target component identifier.")
    structurally_sufficient: bool = Field(
        description="Whether the packet satisfies the current structural sufficiency checks.",
    )
    input_port_names: list[str] = Field(description="Input ports exposed to the local generator.")
    output_port_names: list[str] = Field(description="Output ports exposed to the local generator.")
    local_schema_ids: list[str] = Field(description="Schema identifiers present in the local packet.")
    upstream_component_ids: list[str] = Field(
        description="Immediate upstream component identifiers present in the packet.",
    )
    downstream_component_ids: list[str] = Field(
        description="Immediate downstream component identifiers present in the packet.",
    )
    fixture_ids: list[str] = Field(description="Local fixture identifiers present in the packet.")
    packet_test_case_ids: list[str] = Field(
        description="Packet-local test case identifiers projected into the local generator context.",
    )
    scenario_ids: list[str] = Field(description="Scenario identifiers reachable from local fixtures.")
    missing_elements: list[str] = Field(
        description="Missing structural requirements detected for the packet.",
    )
    validation_findings: list[str] = Field(
        description="Packet-validation findings associated with the packet.",
    )
    notes: list[str] = Field(description="Compact notes describing the scope of the sufficiency claim.")


class PacketSufficiencyReport(BaseModel):
    """Persisted structural sufficiency report for one blueprint."""

    blueprint_dir: str = Field(description="Blueprint directory used to build the report.")
    blueprint_id: str = Field(description="Stable blueprint identifier.")
    packet_count: int = Field(description="Number of packets reviewed.")
    structurally_sufficient_packet_count: int = Field(
        description="Number of packets that passed the structural sufficiency checks.",
    )
    insufficient_packet_count: int = Field(
        description="Number of packets that failed the structural sufficiency checks.",
    )
    all_packets_structurally_sufficient: bool = Field(
        description="Whether every packet passed the structural sufficiency checks.",
    )
    packets: dict[str, PacketSufficiencyEntry] = Field(
        description="Per-component structural packet sufficiency results.",
    )


def build_packet_sufficiency_report(
    blueprint_dir: Path | str,
    output_dir: Path | str,
) -> PacketSufficiencyReport:
    """Build and persist one structural packet-sufficiency report."""

    blueprint_path = Path(blueprint_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    blueprint = load_blueprint_dir(blueprint_path)
    packet_bundle = compile_packets(blueprint)
    validation = validate_packets(packet_bundle, blueprint)
    cases_by_component = materialize_packet_test_cases(packet_bundle)

    packets: dict[str, PacketSufficiencyEntry] = {}
    for component_id, packet in packet_bundle.packets.items():
        packet_test_cases = cases_by_component.get(component_id, [])
        context = build_codegen_context(packet, packet_test_cases)
        missing_elements = _missing_structural_elements(packet, context)
        validation_findings = _packet_validation_findings(validation.findings, component_id)
        entry = PacketSufficiencyEntry(
            component_id=component_id,
            structurally_sufficient=not missing_elements and not validation_findings,
            input_port_names=sorted(context.input_ports),
            output_port_names=sorted(context.output_ports),
            local_schema_ids=sorted(context.local_schemas),
            upstream_component_ids=sorted(context.upstream_components),
            downstream_component_ids=sorted(context.downstream_components),
            fixture_ids=sorted(packet.local_fixtures),
            packet_test_case_ids=sorted(case.fixture_id for case in context.packet_test_cases),
            scenario_ids=sorted(packet.relevant_scenarios),
            missing_elements=missing_elements,
            validation_findings=validation_findings,
            notes=[
                "Structural/local-contract sufficiency only; semantic sufficiency is not claimed.",
            ],
        )
        packets[component_id] = entry

    sufficient_count = sum(1 for entry in packets.values() if entry.structurally_sufficient)
    report = PacketSufficiencyReport(
        blueprint_dir=str(blueprint_path),
        blueprint_id=blueprint.metadata.blueprint_id,
        packet_count=len(packets),
        structurally_sufficient_packet_count=sufficient_count,
        insufficient_packet_count=len(packets) - sufficient_count,
        all_packets_structurally_sufficient=sufficient_count == len(packets),
        packets=packets,
    )
    (destination / "packet_sufficiency_report.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return report


def _missing_structural_elements(
    packet: ComponentPacket,
    context: CodegenContext,
) -> list[str]:
    """Return missing structural elements for one packet/context pair."""

    missing: list[str] = []
    required_schema_ids = set(context.input_ports.values()) | set(context.output_ports.values())
    required_schema_ids.update(store.schema_id for store in context.owned_state_stores.values())
    for schema_id in sorted(required_schema_ids - set(context.local_schemas)):
        missing.append(f"local_schema:{schema_id}")
    if not packet.local_fixtures:
        missing.append("local_fixtures")
    if not context.packet_test_cases:
        missing.append("packet_test_cases")
    if set(case.fixture_id for case in context.packet_test_cases) != set(packet.local_fixtures):
        missing.append("fixture_to_packet_test_case_projection")
    if not packet.relevant_scenarios:
        missing.append("relevant_scenarios")
    return missing


def _packet_validation_findings(
    findings: list[ValidationFinding],
    component_id: str,
) -> list[str]:
    """Return packet-validation findings associated with one component."""

    prefix = f"packets.{component_id}"
    return [
        f"{finding.code}: {finding.message}"
        for finding in findings
        if finding.path.startswith(prefix)
    ]

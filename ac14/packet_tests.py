"""Packet-local test case materialization from compiled packets."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from ac14.models import PacketBundle


class PacketTestCase(BaseModel):
    """Executable packet-local test case derived from one fixture."""

    component_id: str = Field(description="Target component identifier.")
    fixture_id: str = Field(description="Source fixture identifier.")
    scenario_id: str = Field(description="Owning scenario identifier.")
    scenario_kind: str = Field(description="Owning scenario kind.")
    description: str = Field(description="Fixture description.")
    inputs: dict[str, dict[str, Any]] = Field(description="Port-keyed fixture inputs.")
    expected_outputs: dict[str, dict[str, Any]] = Field(
        description="Port-keyed expected outputs.",
    )


def materialize_packet_test_cases(
    packet_bundle: PacketBundle,
) -> dict[str, list[PacketTestCase]]:
    """Convert packet-local fixtures into explicit test case objects."""

    cases_by_component: dict[str, list[PacketTestCase]] = {}
    for component_id, packet in packet_bundle.packets.items():
        cases_by_component[component_id] = [
            PacketTestCase(
                component_id=component_id,
                fixture_id=fixture.fixture_id,
                scenario_id=fixture.scenario_id,
                scenario_kind=packet.relevant_scenarios[fixture.scenario_id].kind,
                description=fixture.description,
                inputs=fixture.inputs,
                expected_outputs=fixture.expected_outputs,
            )
            for fixture in packet.local_fixtures.values()
        ]
    return cases_by_component

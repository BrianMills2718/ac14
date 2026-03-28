"""Tests for packet compilation and B2 validation."""

from __future__ import annotations

from pathlib import Path

from ac14.loader import load_blueprint_dir
from ac14.packets import compile_packets, validate_packets


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def test_compile_packets_builds_packet_for_every_component() -> None:
    """Packet compilation should cover all blueprint components."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)

    assert set(packet_bundle.packets) == set(blueprint.components)
    digest_packet = packet_bundle.packets["digest_assembler"]
    assert "DigestEntry" in digest_packet.local_schemas
    assert "DigestStore" in digest_packet.local_schemas
    assert "digest_store" in digest_packet.owned_state_stores
    assert "happy_path_digest_assembler" in digest_packet.local_fixtures
    assert "missing_customer_context" in digest_packet.relevant_scenarios


def test_validate_packets_passes_for_example_bundle() -> None:
    """The shipped example should produce complete packets."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)
    result = validate_packets(packet_bundle, blueprint)
    assert result.passed, result.findings


def test_validate_packets_rejects_unknown_fixture_port() -> None:
    """Packet validation must fail when a local fixture references a bad port."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    broken_fixture = blueprint.fixtures["happy_path_issue_classifier"].model_copy(
        update={
            "inputs": {
                "wrong_port": blueprint.fixtures["happy_path_issue_classifier"].inputs["parsed_ticket"],
            },
        },
    )
    broken_blueprint = blueprint.model_copy(
        update={"fixtures": {**blueprint.fixtures, broken_fixture.fixture_id: broken_fixture}},
    )

    packet_bundle = compile_packets(broken_blueprint)
    result = validate_packets(packet_bundle, broken_blueprint)
    assert not result.passed
    assert any(finding.code == "E-B2-PACKET-FIXTURE-INPUT-MISMATCH" for finding in result.findings)

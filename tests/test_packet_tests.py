"""Tests for packet-local test materialization."""

from __future__ import annotations

from pathlib import Path

from ac14.loader import load_blueprint_dir
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def test_materialize_packet_test_cases_for_digest_assembler() -> None:
    """Digest assembler should expose one packet-local case per local fixture."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)

    cases_by_component = materialize_packet_test_cases(packet_bundle)
    digest_cases = cases_by_component["digest_assembler"]

    assert {case.fixture_id for case in digest_cases} == {
        "happy_path_digest_assembler",
        "missing_customer_context_digest_assembler",
        "schema_mismatch_rejected_digest_assembler",
    }


def test_materialize_packet_test_cases_preserves_empty_expected_outputs() -> None:
    """Packet-local cases must preserve omission fixtures cleanly."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)

    cases_by_component = materialize_packet_test_cases(packet_bundle)
    loader_cases = {
        case.fixture_id: case for case in cases_by_component["customer_context_loader"]
    }

    assert (
        loader_cases["missing_customer_context_customer_context_loader"].expected_outputs == {}
    )

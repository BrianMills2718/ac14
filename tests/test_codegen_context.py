"""Tests for packet-to-codegen-context projection."""

from __future__ import annotations

from pathlib import Path

from ac14.codegen_context import build_codegen_context, render_codegen_context_text
from ac14.loader import load_blueprint_dir
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def test_build_codegen_context_for_digest_assembler() -> None:
    """Codegen context should preserve the local contract and packet tests."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)
    packet_cases = materialize_packet_test_cases(packet_bundle)

    context = build_codegen_context(
        packet_bundle.packets["digest_assembler"],
        packet_cases["digest_assembler"],
    )

    assert context.component_id == "digest_assembler"
    assert context.input_ports["on_ticket"] == "ParsedTicket"
    assert "digest_store" in context.owned_state_stores
    assert {case.fixture_id for case in context.packet_test_cases} == {
        "happy_path_digest_assembler",
        "missing_customer_context_digest_assembler",
        "schema_mismatch_rejected_digest_assembler",
    }


def test_render_codegen_context_text_is_compact_and_informative() -> None:
    """Rendered codegen text should expose the key local generation surface."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)
    packet_cases = materialize_packet_test_cases(packet_bundle)
    context = build_codegen_context(
        packet_bundle.packets["issue_classifier"],
        packet_cases["issue_classifier"],
    )

    rendered = render_codegen_context_text(context)
    assert "component_id: issue_classifier" in rendered
    assert "input_ports: parsed_ticket:ParsedTicket" in rendered
    assert "packet_test_cases: happy_path_issue_classifier, missing_customer_context_issue_classifier" in rendered

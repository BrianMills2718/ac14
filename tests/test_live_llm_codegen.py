"""Optional live smoke test for the LLM-backed generator."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from ac14.codegen_context import build_codegen_context
from ac14.llm_codegen import generate_component_module_with_llm
from ac14.loader import load_blueprint_dir
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def _live_available() -> bool:
    """Return true when at least one likely LLM provider key is present."""

    return any(
        os.environ.get(name)
        for name in [
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
        ]
    )


@pytest.mark.live
def test_live_llm_generator_smoke() -> None:
    """Live smoke path should return importable module code when keys are available."""

    if not _live_available():
        pytest.skip("No live LLM API key available for smoke test.")

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)
    packet_cases = materialize_packet_test_cases(packet_bundle)
    context = build_codegen_context(
        packet_bundle.packets["ticket_parser"],
        packet_cases["ticket_parser"],
    )

    response = generate_component_module_with_llm(
        context,
        trace_id="test/live_llm_codegen",
        max_budget=0.10,
    )

    assert "class GeneratedComponent" in response.module_code
    assert "def build_component" in response.module_code

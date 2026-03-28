"""Tests for the manual reference runtime on the support_ticket_digest example."""

from __future__ import annotations

from pathlib import Path

from ac14.loader import load_blueprint_dir
from ac14.reference_components import build_support_ticket_digest_components
from ac14.runtime import run_blueprint_once


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def test_reference_runtime_recomposes_happy_path() -> None:
    """The reference runtime should reproduce the happy-path digest outputs."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    components = build_support_ticket_digest_components()
    raw_ticket = blueprint.fixtures["happy_path_ticket_parser"].inputs["raw_ticket"]

    outputs = run_blueprint_once(
        blueprint,
        components,
        initial_inputs={"ticket_parser": {"raw_ticket": raw_ticket}},
    )

    expected_outputs = blueprint.fixtures["happy_path_digest_assembler"].expected_outputs
    assert outputs["digest_assembler"] == expected_outputs


def test_reference_runtime_recomposes_missing_optional_context() -> None:
    """The join should still succeed when optional customer context is absent."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    components = build_support_ticket_digest_components()
    raw_ticket = blueprint.fixtures["missing_customer_context_ticket_parser"].inputs["raw_ticket"]

    outputs = run_blueprint_once(
        blueprint,
        components,
        initial_inputs={"ticket_parser": {"raw_ticket": raw_ticket}},
    )

    expected_outputs = blueprint.fixtures["missing_customer_context_digest_assembler"].expected_outputs
    assert outputs["digest_assembler"] == expected_outputs


def test_reference_runtime_accumulates_store_across_runs() -> None:
    """State-owning sink should accumulate entries across multiple different tickets."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    components = build_support_ticket_digest_components()
    first_ticket = blueprint.fixtures["happy_path_ticket_parser"].inputs["raw_ticket"]
    second_ticket = blueprint.fixtures["missing_customer_context_ticket_parser"].inputs["raw_ticket"]

    run_blueprint_once(
        blueprint,
        components,
        initial_inputs={"ticket_parser": {"raw_ticket": first_ticket}},
    )
    outputs = run_blueprint_once(
        blueprint,
        components,
        initial_inputs={"ticket_parser": {"raw_ticket": second_ticket}},
    )

    digest_entries = outputs["digest_assembler"]["digest_store"]["entries"]
    assert [entry["ticket_id"] for entry in digest_entries] == ["T-100", "T-101"]

"""Tests for the manual reference runtime across the shipped suite."""

from __future__ import annotations

from pathlib import Path

from ac14.examples import discover_shipped_blueprints
from ac14.loader import load_blueprint_dir
from ac14.recomposition import run_recomposition_proof
from ac14.reference_components import (
    build_reference_component_builders_for_blueprint,
    build_reference_components_for_blueprint,
)
from ac14.runtime import run_blueprint_once


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples"
PRIMARY_EXAMPLE_DIR = EXAMPLES_ROOT / "support_ticket_digest" / "blueprint"


def test_reference_runtime_matches_runnable_scenarios_for_shipped_examples() -> None:
    """Reference runtime should satisfy every runnable shipped scenario in the suite."""

    for example in discover_shipped_blueprints(EXAMPLES_ROOT):
        blueprint = load_blueprint_dir(example.blueprint_dir)
        report = run_recomposition_proof(blueprint, build_reference_component_builders_for_blueprint(blueprint))
        assert report.passed is True, example.example_id
        assert report.runnable_scenario_count >= 1


def test_reference_runtime_accumulates_store_across_runs() -> None:
    """State-owning sink should accumulate entries across multiple different tickets."""

    blueprint = load_blueprint_dir(PRIMARY_EXAMPLE_DIR)
    components = build_reference_components_for_blueprint(blueprint)
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

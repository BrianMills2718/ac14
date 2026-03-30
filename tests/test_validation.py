"""Tests for B1 blueprint validation."""

from __future__ import annotations

from pathlib import Path

from ac14.loader import load_blueprint_dir
from ac14.models import Binding
from ac14.validation import validate_blueprint


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def test_validate_blueprint_passes_for_example_bundle() -> None:
    """The shipped example bundle should satisfy B1 validation."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    result = validate_blueprint(blueprint)
    assert result.passed, result.findings


def test_validate_blueprint_rejects_missing_schema_reference() -> None:
    """Missing schema references must fail loud."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    broken_component = blueprint.components["priority_scorer"].model_copy(
        update={
            "output_ports": [
                blueprint.components["priority_scorer"].output_ports[0].model_copy(
                    update={"schema_id": "MissingSchema"},
                ),
            ],
        },
    )
    broken_blueprint = blueprint.model_copy(
        update={"components": {**blueprint.components, "priority_scorer": broken_component}},
    )

    result = validate_blueprint(broken_blueprint)
    assert not result.passed
    assert any(finding.code == "E-B1-OUTPUT-SCHEMA-MISSING" for finding in result.findings)


def test_validate_blueprint_rejects_binding_schema_mismatch() -> None:
    """Bindings must use exact schema matches in v1."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    broken_binding = blueprint.bindings[0].model_copy(
        update={"to_component": "digest_assembler", "to_port": "on_priority"},
    )
    broken_blueprint = blueprint.model_copy(
        update={"bindings": [broken_binding, *blueprint.bindings[1:]]},
    )

    result = validate_blueprint(broken_blueprint)
    assert not result.passed
    assert any(finding.code == "E-B1-BINDING-SCHEMA-MISMATCH" for finding in result.findings)


def test_validate_blueprint_rejects_graph_cycle() -> None:
    """Component cycles must be rejected explicitly."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    issue_classifier = blueprint.components["issue_classifier"].model_copy(
        update={
            "input_ports": [
                blueprint.components["issue_classifier"].input_ports[0].model_copy(
                    update={"schema_id": "DigestEntry"},
                ),
            ],
        },
    )
    cycle_binding = Binding(
        from_component="digest_assembler",
        from_port="digest_entry",
        to_component="issue_classifier",
        to_port="parsed_ticket",
    )
    broken_blueprint = blueprint.model_copy(
        update={
            "components": {**blueprint.components, "issue_classifier": issue_classifier},
            "bindings": [*blueprint.bindings, cycle_binding],
        },
    )

    result = validate_blueprint(broken_blueprint)
    assert not result.passed
    assert any(finding.code == "E-B1-GRAPH-CYCLE" for finding in result.findings)


def test_validate_blueprint_requires_semantic_acceptance_scenario() -> None:
    """Blueprints must declare at least one semantic-acceptance scenario."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    scenarios = {
        scenario_id: scenario
        for scenario_id, scenario in blueprint.scenarios.items()
        if scenario.kind != "semantic_acceptance"
    }
    broken_blueprint = blueprint.model_copy(update={"scenarios": scenarios})

    result = validate_blueprint(broken_blueprint)
    assert not result.passed
    assert any(
        finding.code == "E-B1-SEMANTIC-ACCEPTANCE-SCENARIO-MISSING"
        for finding in result.findings
    )


def test_validate_blueprint_requires_component_fixture_coverage() -> None:
    """Each component must retain at least one fixture."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    fixtures = {
        fixture_id: fixture
        for fixture_id, fixture in blueprint.fixtures.items()
        if fixture.component_id != "customer_context_loader"
    }
    broken_blueprint = blueprint.model_copy(update={"fixtures": fixtures})

    result = validate_blueprint(broken_blueprint)
    assert not result.passed
    assert any(
        finding.code == "E-B1-COMPONENT-FIXTURE-COVERAGE-MISSING"
        for finding in result.findings
    )


def test_validate_blueprint_requires_llm_evaluator_for_semantic_acceptance() -> None:
    """Semantic-acceptance scenarios must declare an LLM evaluator."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    happy_path = blueprint.scenarios["happy_path"].model_copy(
        update={"evaluator_ids": ["exact_outputs"]},
    )
    broken_blueprint = blueprint.model_copy(
        update={"scenarios": {**blueprint.scenarios, "happy_path": happy_path}},
    )

    result = validate_blueprint(broken_blueprint)
    assert not result.passed
    assert any(
        finding.code == "E-B1-SEMANTIC-SCENARIO-LLM-EVALUATOR-MISSING"
        for finding in result.findings
    )

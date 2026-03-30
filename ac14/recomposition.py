"""Blueprint-driven recomposition scenario selection and execution."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from ac14.models import FrozenBlueprint
from ac14.runtime import RuntimeComponent, run_blueprint_once


class SkippedScenario(BaseModel):
    """Scenario excluded from full recomposition proof under explicit rules."""

    scenario_id: str = Field(description="Scenario identifier.")
    reason: str = Field(description="Why the scenario was not run as a full recomposition case.")


class RecompositionScenarioCase(BaseModel):
    """Runnable full-graph recomposition scenario derived from blueprint fixtures."""

    scenario_id: str = Field(description="Scenario identifier.")
    description: str = Field(description="Scenario meaning.")
    initial_inputs: dict[str, dict[str, dict[str, Any]]] = Field(
        description="Source-component initial inputs keyed by component id.",
    )
    expected_outputs_by_component: dict[str, dict[str, dict[str, Any]]] = Field(
        description="Expected outputs for each component in the scenario.",
    )


class RecompositionScenarioCatalog(BaseModel):
    """Runnable and skipped recomposition scenarios for one blueprint."""

    runnable_scenarios: list[RecompositionScenarioCase] = Field(
        description="Scenarios that qualify for full-graph recomposition proof.",
    )
    skipped_scenarios: list[SkippedScenario] = Field(
        description="Scenarios excluded from full-graph recomposition proof.",
    )


class RecompositionScenarioResult(BaseModel):
    """Outcome for one runnable recomposition scenario."""

    scenario_id: str = Field(description="Scenario identifier.")
    passed: bool = Field(description="Whether the scenario passed.")
    error: str | None = Field(default=None, description="Failure explanation when the scenario fails.")


class RecompositionScenarioExecution(BaseModel):
    """Actual execution result for one runnable recomposition scenario."""

    scenario_id: str = Field(description="Scenario identifier.")
    outputs_by_component: dict[str, dict[str, dict[str, Any]]] | None = Field(
        default=None,
        description="Actual outputs keyed by component when execution succeeds.",
    )
    error: str | None = Field(default=None, description="Execution error when the scenario fails.")


class RecompositionReport(BaseModel):
    """Aggregate recomposition proof result for one blueprint and component set."""

    passed: bool = Field(description="Whether all runnable recomposition scenarios passed.")
    runnable_scenario_count: int = Field(description="Number of runnable recomposition scenarios.")
    skipped_scenarios: list[SkippedScenario] = Field(
        description="Scenarios that were explicitly skipped from full recomposition proof.",
    )
    results: list[RecompositionScenarioResult] = Field(
        description="Per-scenario execution outcomes.",
    )


def build_recomposition_scenario_catalog(
    blueprint: FrozenBlueprint,
) -> RecompositionScenarioCatalog:
    """Infer conservative full-recomposition scenarios from blueprint fixtures."""

    source_components = _source_components(blueprint)
    all_components = set(blueprint.components)
    runnable_scenarios: list[RecompositionScenarioCase] = []
    skipped_scenarios: list[SkippedScenario] = []

    for scenario in blueprint.scenarios.values():
        if scenario.kind == "negative":
            skipped_scenarios.append(
                SkippedScenario(
                    scenario_id=scenario.scenario_id,
                    reason="negative scenario reserved for packet-level failure checks",
                ),
            )
            continue

        fixtures = [blueprint.fixtures[fixture_id] for fixture_id in scenario.fixture_ids]
        fixtures_by_component: dict[str, dict[str, dict[str, Any]]] = {}
        expected_outputs_by_component: dict[str, dict[str, dict[str, Any]]] = {}
        seen_components: set[str] = set()
        for fixture in fixtures:
            if fixture.component_id in seen_components:
                raise ValueError(
                    "recomposition scenario contains more than one fixture for component "
                    f"{fixture.component_id}: {scenario.scenario_id}"
                )
            seen_components.add(fixture.component_id)
            fixtures_by_component[fixture.component_id] = fixture.inputs
            expected_outputs_by_component[fixture.component_id] = fixture.expected_outputs

        missing_components = sorted(all_components.difference(seen_components))
        if missing_components:
            skipped_scenarios.append(
                SkippedScenario(
                    scenario_id=scenario.scenario_id,
                    reason="missing component fixtures for full recomposition proof: "
                    + ", ".join(missing_components),
                ),
            )
            continue

        missing_sources = [component_id for component_id in source_components if component_id not in fixtures_by_component]
        if missing_sources:
            skipped_scenarios.append(
                SkippedScenario(
                    scenario_id=scenario.scenario_id,
                    reason="missing source-component fixtures: " + ", ".join(missing_sources),
                ),
            )
            continue

        runnable_scenarios.append(
            RecompositionScenarioCase(
                scenario_id=scenario.scenario_id,
                description=scenario.description,
                initial_inputs={
                    component_id: fixtures_by_component[component_id] for component_id in source_components
                },
                expected_outputs_by_component=expected_outputs_by_component,
            ),
        )

    return RecompositionScenarioCatalog(
        runnable_scenarios=runnable_scenarios,
        skipped_scenarios=skipped_scenarios,
    )


def run_recomposition_proof(
    blueprint: FrozenBlueprint,
    component_builders: dict[str, Callable[[], RuntimeComponent]],
) -> RecompositionReport:
    """Execute all runnable full-graph recomposition scenarios for one blueprint."""

    catalog, executions = execute_recomposition_scenarios(blueprint, component_builders)
    results: list[RecompositionScenarioResult] = []
    scenario_lookup = {
        scenario.scenario_id: scenario for scenario in catalog.runnable_scenarios
    }
    for execution in executions:
        scenario = scenario_lookup[execution.scenario_id]
        if execution.error is not None:
            results.append(
                RecompositionScenarioResult(
                    scenario_id=execution.scenario_id,
                    passed=False,
                    error=execution.error,
                ),
            )
            continue

        mismatch = _find_first_mismatch(
            execution.outputs_by_component or {},
            scenario.expected_outputs_by_component,
        )
        if mismatch is None:
            results.append(
                RecompositionScenarioResult(
                    scenario_id=execution.scenario_id,
                    passed=True,
                ),
            )
        else:
            results.append(
                RecompositionScenarioResult(
                    scenario_id=execution.scenario_id,
                    passed=False,
                    error=mismatch,
                ),
            )

    return RecompositionReport(
        passed=bool(results) and all(result.passed for result in results),
        runnable_scenario_count=len(results),
        skipped_scenarios=catalog.skipped_scenarios,
        results=results,
    )


def execute_recomposition_scenarios(
    blueprint: FrozenBlueprint,
    component_builders: dict[str, Callable[[], RuntimeComponent]],
) -> tuple[RecompositionScenarioCatalog, list[RecompositionScenarioExecution]]:
    """Execute all runnable recomposition scenarios and return actual outputs."""

    missing_builders = sorted(set(blueprint.components).difference(component_builders))
    if missing_builders:
        raise ValueError(
            "missing component builders for recomposition proof: " + ", ".join(missing_builders)
        )

    catalog = build_recomposition_scenario_catalog(blueprint)
    executions: list[RecompositionScenarioExecution] = []
    for scenario in catalog.runnable_scenarios:
        implementations = {
            component_id: component_builders[component_id]()
            for component_id in blueprint.components
        }
        try:
            outputs = run_blueprint_once(blueprint, implementations, scenario.initial_inputs)
            executions.append(
                RecompositionScenarioExecution(
                    scenario_id=scenario.scenario_id,
                    outputs_by_component=outputs,
                ),
            )
        except Exception as exc:  # pragma: no cover - explicit failure capture
            executions.append(
                RecompositionScenarioExecution(
                    scenario_id=scenario.scenario_id,
                    error=str(exc),
                ),
            )
    return catalog, executions


def _source_components(blueprint: FrozenBlueprint) -> list[str]:
    """Return components with no inbound bindings, in blueprint order."""

    inbound_components = {binding.to_component for binding in blueprint.bindings}
    return [
        component_id
        for component_id in blueprint.components
        if component_id not in inbound_components
    ]


def _find_first_mismatch(
    actual_outputs: dict[str, dict[str, dict[str, Any]]],
    expected_outputs_by_component: dict[str, dict[str, dict[str, Any]]],
) -> str | None:
    """Return a compact mismatch description or ``None`` when outputs match."""

    for component_id, expected_outputs in expected_outputs_by_component.items():
        actual_component_outputs = actual_outputs.get(component_id)
        if actual_component_outputs != expected_outputs:
            return (
                f"component {component_id} outputs did not match expected outputs: "
                f"expected {expected_outputs!r}, got {actual_component_outputs!r}"
            )
    return None


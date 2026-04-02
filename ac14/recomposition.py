"""Blueprint-driven recomposition scenario selection and execution."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
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
    fixture_descriptions_by_component: dict[str, str] = Field(
        default_factory=dict,
        description="Fixture description for each component, used for LLM semantic evaluation.",
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
        fixture_descriptions_by_component: dict[str, str] = {}
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
            fixture_descriptions_by_component[fixture.component_id] = fixture.description

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
                fixture_descriptions_by_component=fixture_descriptions_by_component,
            ),
        )

    return RecompositionScenarioCatalog(
        runnable_scenarios=runnable_scenarios,
        skipped_scenarios=skipped_scenarios,
    )


def run_recomposition_proof(
    blueprint: FrozenBlueprint,
    component_builders: dict[str, Callable[[], RuntimeComponent]],
    *,
    llm_model: str | None = None,
    trace_id: str | None = None,
    llm_max_budget: float = 0.10,
) -> RecompositionReport:
    """Execute all runnable full-graph recomposition scenarios for one blueprint.

    When ``llm_model`` is provided, free-form text fields in scenario outputs are
    additionally evaluated for semantic correctness after categorical checks pass.
    A single LLM call is made per scenario covering all components' outputs at once.
    """

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
        if mismatch is not None:
            results.append(
                RecompositionScenarioResult(
                    scenario_id=execution.scenario_id,
                    passed=False,
                    error=mismatch,
                ),
            )
            continue

        # Categorical check passed. Optionally run LLM semantic eval for the whole scenario.
        if llm_model is not None and _scenario_has_llm_eval_fields(scenario.expected_outputs_by_component):
            sem_result = asyncio.run(
                _aevaluate_recomposition_scenario_semantically(
                    scenario=scenario,
                    actual_outputs_by_component=execution.outputs_by_component or {},
                    model=llm_model,
                    trace_id=f"{trace_id or 'recomp_eval'}/{execution.scenario_id}/semantic",
                    max_budget=llm_max_budget,
                )
            )
            if sem_result.semantic_fields_acceptable:
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
                        error="; ".join(sem_result.concerns),
                    ),
                )
        else:
            results.append(
                RecompositionScenarioResult(
                    scenario_id=execution.scenario_id,
                    passed=True,
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


_RECOMP_LLM_EVAL_FIELDS: frozenset[str] = frozenset({"reason", "action_summary"})
"""Subset of free-form fields that carry semantic meaning and should be LLM-evaluated."""

_RECOMP_FREE_FORM_FIELDS: frozenset[str] = frozenset({
    "reason",
    "score",
    "action_summary",
    "generated_at",
})
"""Fields excluded from recomposition exact comparison.

LLM-generated components cannot deterministically reproduce free-form text
(reason strings, action summaries) or wall-clock timestamps. Stripping these
fields from both sides keeps recomposition checks focused on categorical
correctness — the routing and classification fields that matter.
"""


def _strip_recomp_free_form_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Remove free-form text and timestamp fields at any nesting depth."""
    result: dict[str, Any] = {}
    for k, v in data.items():
        if k in _RECOMP_FREE_FORM_FIELDS:
            continue
        if isinstance(v, dict):
            result[k] = _strip_recomp_free_form_fields(v)
        elif isinstance(v, list):
            result[k] = [
                _strip_recomp_free_form_fields(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            result[k] = v
    return result


def _has_llm_eval_fields_in_dict(data: dict[str, Any]) -> bool:
    """Return True if data (at any nesting depth) contains an LLM-eval field."""
    for k, v in data.items():
        if k in _RECOMP_LLM_EVAL_FIELDS:
            return True
        if isinstance(v, dict) and _has_llm_eval_fields_in_dict(v):
            return True
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict) and _has_llm_eval_fields_in_dict(item):
                    return True
    return False


def _scenario_has_llm_eval_fields(
    expected_outputs_by_component: dict[str, dict[str, dict[str, Any]]],
) -> bool:
    """Return True if any component's expected outputs contain an LLM-eval field."""
    for component_outputs in expected_outputs_by_component.values():
        if _has_llm_eval_fields_in_dict(component_outputs):
            return True
    return False


class _RecompSemanticEval(BaseModel):
    """LLM evaluation of free-form fields across all components in one recomposition scenario."""

    semantic_fields_acceptable: bool = Field(
        description=(
            "True if all free-form text fields (reason, action_summary) across all components "
            "are semantically correct given the scenario inputs and component responsibilities"
        )
    )
    concerns: list[str] = Field(
        description="Specific concerns about semantic correctness; empty list if all fields are acceptable"
    )


async def _aevaluate_recomposition_scenario_semantically(
    scenario: RecompositionScenarioCase,
    actual_outputs_by_component: dict[str, dict[str, dict[str, Any]]],
    model: str,
    trace_id: str,
    max_budget: float = 0.10,
) -> _RecompSemanticEval:
    """Single LLM call evaluating free-form fields for all components in one recomposition scenario."""

    from ac14.acceptance import acall_llm_structured, render_prompt  # lazy — avoids import-time llm_client dep

    _PACKET_EVALUATE_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "evaluate_packet_case.yaml"
    messages = render_prompt(
        _PACKET_EVALUATE_PROMPT_PATH,
        component_id="full_scenario",
        fixture_description=scenario.description,
        inputs=scenario.initial_inputs,
        expected_outputs=scenario.expected_outputs_by_component,
        actual_outputs=actual_outputs_by_component,
    )
    result, _ = await acall_llm_structured(
        model,
        messages,
        response_model=_RecompSemanticEval,
        task="ac14_evaluate_packet_case_semantics",
        trace_id=trace_id,
        max_budget=max_budget,
    )
    return result


def _find_first_mismatch(
    actual_outputs: dict[str, dict[str, dict[str, Any]]],
    expected_outputs_by_component: dict[str, dict[str, dict[str, Any]]],
) -> str | None:
    """Return a compact mismatch description or ``None`` when outputs match.

    Free-form text fields (reason strings, action summaries, timestamps) are
    stripped from both sides before comparison so that only categorical routing
    and classification fields are checked exactly.
    """

    for component_id, expected_outputs in expected_outputs_by_component.items():
        actual_component_outputs = actual_outputs.get(component_id)
        stripped_actual = (
            _strip_recomp_free_form_fields(actual_component_outputs)
            if actual_component_outputs is not None
            else None
        )
        stripped_expected = _strip_recomp_free_form_fields(expected_outputs)
        if stripped_actual != stripped_expected:
            return (
                f"component {component_id} outputs did not match expected outputs: "
                f"expected {stripped_expected!r}, got {stripped_actual!r}"
            )
    return None


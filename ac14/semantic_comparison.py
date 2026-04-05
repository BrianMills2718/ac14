"""Semantic comparison artifacts across reference and generated execution modes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

try:
    from data_contracts import boundary, BoundaryModel
except ImportError:
    def boundary(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        def decorator(fn: Any) -> Any:
            return fn
        return decorator
    BoundaryModel = object  # type: ignore[assignment,misc]

from ac14.generated_codegen import emit_generated_package, load_generated_component_builders
from ac14.loader import load_blueprint_dir
from ac14.models import FrozenBlueprint
from ac14.packets import compile_packets
from ac14.recomposition import (
    RecompositionScenarioCase,
    RecompositionScenarioExecution,
    SkippedScenario,
    build_recomposition_scenario_catalog,
    execute_recomposition_scenarios,
)
from ac14.reference_components import build_reference_component_builders_for_blueprint


ComparisonMode = Literal["reference", "deterministic", "llm"]


class SemanticScenarioComparison(BaseModel):
    """Semantic comparison result for one mode on one runnable scenario."""

    scenario_id: str = Field(description="Scenario identifier.")
    matches_expected: bool = Field(description="Whether outputs match the scenario expectations.")
    mismatched_components_vs_expected: list[str] = Field(
        description="Component ids whose outputs differ from expected outputs.",
    )
    matches_reference: bool | None = Field(
        default=None,
        description="Whether outputs match the reference execution when applicable.",
    )
    mismatched_components_vs_reference: list[str] = Field(
        default_factory=list,
        description="Component ids whose outputs differ from the reference execution.",
    )
    error: str | None = Field(default=None, description="Execution error when the scenario failed.")


class SemanticModeReport(BaseModel):
    """Aggregate semantic comparison result for one execution mode."""

    mode: ComparisonMode = Field(description="Compared execution mode.")
    matched_expected_scenarios: int = Field(
        description="Runnable scenarios that matched expected outputs.",
    )
    failed_expected_scenarios: int = Field(
        description="Runnable scenarios that failed expected-output comparison.",
    )
    matched_reference_scenarios: int | None = Field(
        default=None,
        description="Runnable scenarios that matched the reference execution when applicable.",
    )
    failed_reference_scenarios: int | None = Field(
        default=None,
        description="Runnable scenarios that diverged from the reference execution when applicable.",
    )
    scenario_results: list[SemanticScenarioComparison] = Field(
        description="Per-scenario semantic comparison results.",
    )


class SemanticComparisonReport(BaseModel):
    """Persisted semantic comparison report for one blueprint."""

    blueprint_dir: str = Field(description="Blueprint directory used for comparison.")
    runnable_scenario_count: int = Field(description="Number of runnable recomposition scenarios.")
    skipped_scenarios: list[SkippedScenario] = Field(
        description="Scenarios skipped from full recomposition comparison.",
    )
    modes: list[SemanticModeReport] = Field(description="Per-mode semantic comparison results.")


@boundary(
    name="ac14.semantic_comparison",
    version="0.1.0",
    producer="ac14",
    consumers=["benchmark_pipeline"],
)
def build_semantic_comparison_report(
    blueprint_dir: Path | str,
    output_dir: Path | str,
    *,
    modes: list[ComparisonMode] | None = None,
    llm_model: str = "gemini/gemini-2.5-flash-lite",
    llm_max_budget: float = 0.50,
) -> SemanticComparisonReport:
    """Build a semantic comparison report for one blueprint."""

    blueprint_path = Path(blueprint_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    selected_modes = modes or ["reference", "deterministic"]

    blueprint = load_blueprint_dir(blueprint_path)
    catalog = build_recomposition_scenario_catalog(blueprint)
    scenario_lookup = {
        scenario.scenario_id: scenario for scenario in catalog.runnable_scenarios
    }
    reference_outputs = _run_reference_mode(blueprint, scenario_lookup)

    reports: list[SemanticModeReport] = []
    for mode in selected_modes:
        if mode == "reference":
            mode_outputs = reference_outputs
        else:
            mode_outputs = _run_generated_mode(
                blueprint_path=blueprint_path,
                mode=mode,
                output_dir=destination / mode,
                llm_model=llm_model,
                llm_max_budget=llm_max_budget,
            )

        scenario_results: list[SemanticScenarioComparison] = []
        for scenario_id, scenario in scenario_lookup.items():
            execution = mode_outputs[scenario_id]
            reference_execution = reference_outputs[scenario_id]
            mismatched_expected = _mismatched_components(
                execution.outputs_by_component,
                scenario.expected_outputs_by_component,
            )
            if mode == "reference":
                matches_reference: bool | None = None
                mismatched_reference: list[str] = []
            else:
                mismatched_reference = _mismatched_components(
                    execution.outputs_by_component,
                    reference_execution.outputs_by_component,
                )
                matches_reference = (
                    execution.error is None
                    and reference_execution.error is None
                    and not mismatched_reference
                )
            scenario_results.append(
                SemanticScenarioComparison(
                    scenario_id=scenario_id,
                    matches_expected=execution.error is None and not mismatched_expected,
                    mismatched_components_vs_expected=mismatched_expected,
                    matches_reference=matches_reference,
                    mismatched_components_vs_reference=mismatched_reference,
                    error=execution.error,
                ),
            )

        reports.append(
            SemanticModeReport(
                mode=mode,
                matched_expected_scenarios=sum(
                    1 for result in scenario_results if result.matches_expected
                ),
                failed_expected_scenarios=sum(
                    1 for result in scenario_results if not result.matches_expected
                ),
                matched_reference_scenarios=(
                    None
                    if mode == "reference"
                    else sum(1 for result in scenario_results if result.matches_reference)
                ),
                failed_reference_scenarios=(
                    None
                    if mode == "reference"
                    else sum(1 for result in scenario_results if result.matches_reference is False)
                ),
                scenario_results=scenario_results,
            ),
        )

    report = SemanticComparisonReport(
        blueprint_dir=str(blueprint_path),
        runnable_scenario_count=len(catalog.runnable_scenarios),
        skipped_scenarios=catalog.skipped_scenarios,
        modes=reports,
    )
    (destination / "semantic_comparison_report.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return report


def _run_reference_mode(
    blueprint: FrozenBlueprint,
    scenario_lookup: dict[str, RecompositionScenarioCase],
) -> dict[str, RecompositionScenarioExecution]:
    """Execute the reference lane for one blueprint."""

    builders = build_reference_component_builders_for_blueprint(blueprint)
    _catalog, executions = execute_recomposition_scenarios(blueprint, builders)
    return {execution.scenario_id: execution for execution in executions if execution.scenario_id in scenario_lookup}


def _run_generated_mode(
    *,
    blueprint_path: Path,
    mode: ComparisonMode,
    output_dir: Path,
    llm_model: str,
    llm_max_budget: float,
) -> dict[str, RecompositionScenarioExecution]:
    """Execute one generated mode and return scenario outputs keyed by scenario id."""

    blueprint = load_blueprint_dir(blueprint_path)
    packet_bundle = compile_packets(blueprint)
    generated_package = emit_generated_package(
        packet_bundle,
        output_dir / "generated",
        generator_kind="deterministic" if mode == "deterministic" else "llm",
        llm_model=llm_model,
        llm_max_budget=llm_max_budget,
        trace_id_prefix=f"ac14/semantic_compare/{mode}",
    )
    builders = load_generated_component_builders(generated_package)
    _catalog, executions = execute_recomposition_scenarios(blueprint, builders)
    return {execution.scenario_id: execution for execution in executions}


def _mismatched_components(
    actual_outputs_by_component: dict[str, dict[str, dict[str, Any]]] | None,
    expected_outputs_by_component: dict[str, dict[str, dict[str, Any]]] | None,
) -> list[str]:
    """Return component ids whose outputs differ between two scenario executions."""

    if actual_outputs_by_component is None or expected_outputs_by_component is None:
        return []
    mismatched: list[str] = []
    for component_id, expected_outputs in expected_outputs_by_component.items():
        if actual_outputs_by_component.get(component_id) != expected_outputs:
            mismatched.append(component_id)
    return mismatched

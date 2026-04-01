"""Requirements-aware semantic acceptance for AC14 semantic-acceptance scenarios."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Literal, cast

from pydantic import BaseModel, Field

from ac14.examples import ShippedBlueprintExample, discover_shipped_blueprints
from ac14.generated_codegen import aemit_generated_package, load_generated_component_builders
from ac14.loader import load_blueprint_dir
from ac14.models import FrozenBlueprint, Scenario
from ac14.packets import compile_packets
from ac14.recomposition import (
    RecompositionScenarioExecution,
    build_recomposition_scenario_catalog,
    execute_recomposition_scenarios,
)
from ac14.reference_components import build_reference_component_builders_for_blueprint
from ac14.runtime import run_blueprint_once
from llm_client import acall_llm_structured, render_prompt  # type: ignore[import-not-found]


DEFAULT_ACCEPTANCE_MODEL = "gemini/gemini-2.5-flash-lite"
DEFAULT_ACCEPTANCE_MAX_BUDGET = 0.50
ACCEPTANCE_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "review_acceptance.yaml"
AcceptanceMode = Literal["reference", "deterministic", "llm"]


class RequirementAssessment(BaseModel):
    """Assessment of one acceptance requirement."""

    requirement: str = Field(description="Requirement text under review.")
    verdict: Literal["satisfied", "partially_satisfied", "not_satisfied", "concern"] = Field(
        description="Assessment verdict for this requirement.",
    )
    rationale: str = Field(description="Concise reason for the verdict.")


class AcceptanceReviewResponse(BaseModel):
    """Structured LLM review of one semantic-acceptance scenario."""

    overall_verdict: Literal["accept", "concern", "reject"] = Field(
        description="Overall verdict for the scenario outputs.",
    )
    summary: str = Field(description="Short acceptance summary.")
    concerns: list[str] = Field(description="Specific concerns the reviewer found.")
    requirement_assessments: list[RequirementAssessment] = Field(
        description="Per-requirement assessments.",
    )


class AcceptanceScenarioResult(BaseModel):
    """Persisted acceptance result for one scenario and execution mode."""

    scenario_id: str = Field(description="Scenario identifier.")
    mode: AcceptanceMode = Field(description="Execution mode under review.")
    realistic_input: bool = Field(description="Whether the scenario is marked realistic.")
    requirements: list[str] = Field(description="Requirements reviewed by the LLM.")
    realistic_input_path: str | None = Field(
        default=None,
        description="Path to the realistic input artifact when one was supplied.",
    )
    realistic_input_record: object | None = Field(
        default=None,
        description="Realistic input record reviewed and executed when one was supplied.",
    )
    execution_error: str | None = Field(default=None, description="Execution error when the run failed.")
    outputs_by_component: dict[str, dict[str, dict[str, object]]] | None = Field(
        default=None,
        description="Actual outputs produced by the execution mode.",
    )
    review: AcceptanceReviewResponse | None = Field(
        default=None,
        description="Structured LLM review when execution succeeded.",
    )


class AcceptanceReport(BaseModel):
    """Persisted acceptance artifact for one blueprint and execution mode."""

    blueprint_dir: str = Field(description="Blueprint directory used for acceptance.")
    mode: AcceptanceMode = Field(description="Execution mode under review.")
    scenario_results: list[AcceptanceScenarioResult] = Field(
        description="Per-scenario acceptance results.",
    )


class SuiteAcceptanceReport(BaseModel):
    """Persisted acceptance artifact across shipped examples."""

    mode: AcceptanceMode = Field(description="Execution mode under review.")
    example_count: int = Field(description="Number of shipped examples reviewed.")
    accepted_examples: int = Field(description="Examples with only accept verdicts.")
    concern_examples: int = Field(description="Examples with any concern verdicts.")
    rejected_examples: int = Field(description="Examples with any reject or execution failure.")
    reports: dict[str, str] = Field(description="Per-example persisted report paths.")


class RealisticSuiteModeSummary(BaseModel):
    """Aggregate realistic-input acceptance summary for one execution mode."""

    mode: AcceptanceMode = Field(description="Execution mode reviewed across the suite.")
    example_count: int = Field(description="Number of shipped examples reviewed in this mode.")
    accepted_examples: int = Field(description="Examples with only accept verdicts.")
    concern_examples: int = Field(description="Examples with any concern verdicts.")
    rejected_examples: int = Field(description="Examples with any reject or execution failure.")
    reports: dict[str, str] = Field(description="Per-example persisted report paths for this mode.")


class RealisticSuiteAcceptanceReport(BaseModel):
    """Persisted realistic-input acceptance artifact across shipped examples and modes."""

    modes: list[AcceptanceMode] = Field(description="Execution modes reviewed across the suite.")
    example_count: int = Field(description="Number of shipped examples covered by the suite.")
    record_index: int = Field(description="Realistic-input record index used for every example.")
    realistic_input_paths: dict[str, str] = Field(
        description="Persisted realistic-input paths keyed by shipped example identifier.",
    )
    mode_summaries: dict[str, RealisticSuiteModeSummary] = Field(
        description="Per-mode realistic-input acceptance summaries.",
    )


class RealisticModeComparisonReport(BaseModel):
    """Persisted realistic-input acceptance comparison for one blueprint and multiple modes."""

    blueprint_dir: str = Field(description="Blueprint directory used for comparison.")
    realistic_input_path: str = Field(description="Path to the realistic input artifact used for comparison.")
    record_index: int = Field(description="Realistic-input record index used for every mode.")
    modes: list[AcceptanceMode] = Field(description="Execution modes compared for this blueprint.")
    verdicts_by_mode: dict[str, Literal["accept", "concern", "reject"]] = Field(
        description="Overall acceptance verdict keyed by execution mode.",
    )
    reports: dict[str, str] = Field(description="Per-mode persisted acceptance report paths.")


async def abuild_acceptance_report(
    blueprint_dir: Path | str,
    output_dir: Path | str,
    *,
    mode: AcceptanceMode = "deterministic",
    realistic_input_path: Path | str | None = None,
    realistic_input_record_index: int = 0,
    model: str = DEFAULT_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_ACCEPTANCE_MAX_BUDGET,
) -> AcceptanceReport:
    """Build a persisted acceptance artifact for one blueprint."""

    blueprint_path = Path(blueprint_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    blueprint = load_blueprint_dir(blueprint_path)

    acceptance_scenarios = {
        scenario_id: scenario
        for scenario_id, scenario in blueprint.scenarios.items()
        if scenario.kind == "semantic_acceptance"
    }
    if not acceptance_scenarios:
        raise ValueError(f"blueprint {blueprint.metadata.blueprint_id} has no semantic_acceptance scenarios")

    realistic_input_record: dict[str, Any] | None = (
        _load_realistic_input_record(
            realistic_input_path=realistic_input_path,
            record_index=realistic_input_record_index,
        )
        if realistic_input_path is not None
        else None
    )
    if realistic_input_record is None:
        scenario_executions = await _execute_mode_for_acceptance(
            blueprint=blueprint,
            mode=mode,
            output_dir=destination / mode,
            model=model,
            max_budget=max_budget,
        )
    else:
        scenario_executions = await _execute_mode_for_realistic_input_acceptance(
            blueprint=blueprint,
            mode=mode,
            output_dir=destination / mode,
            realistic_input_record=realistic_input_record,
            model=model,
            max_budget=max_budget,
        )

    results: list[AcceptanceScenarioResult] = []
    for scenario_id, scenario in acceptance_scenarios.items():
        if realistic_input_record is not None and not scenario.realistic_input:
            continue
        execution = scenario_executions[scenario_id]
        if execution.error is not None:
            results.append(
                AcceptanceScenarioResult(
                    scenario_id=scenario_id,
                    mode=mode,
                    realistic_input=scenario.realistic_input,
                    requirements=scenario.requirements,
                    realistic_input_path=(
                        str(Path(realistic_input_path))
                        if realistic_input_path is not None and scenario.realistic_input
                        else None
                    ),
                    realistic_input_record=(
                        realistic_input_record
                        if realistic_input_record is not None and scenario.realistic_input
                        else None
                    ),
                    execution_error=execution.error,
                ),
            )
            continue

        review = await _review_acceptance_scenario(
            blueprint=blueprint,
            scenario=scenario,
            outputs_by_component=execution.outputs_by_component or {},
            realistic_input_payload=(
                realistic_input_record if scenario.realistic_input else None
            ),
            model=model,
            max_budget=max_budget,
            trace_id=f"ac14/acceptance/{mode}/{scenario_id}",
        )
        results.append(
            AcceptanceScenarioResult(
                scenario_id=scenario_id,
                mode=mode,
                realistic_input=scenario.realistic_input,
                requirements=scenario.requirements,
                realistic_input_path=(
                    str(Path(realistic_input_path))
                    if realistic_input_path is not None and scenario.realistic_input
                    else None
                ),
                realistic_input_record=(
                    realistic_input_record
                    if realistic_input_record is not None and scenario.realistic_input
                    else None
                ),
                outputs_by_component=execution.outputs_by_component,
                review=review,
            ),
        )

    report = AcceptanceReport(
        blueprint_dir=str(blueprint_path),
        mode=mode,
        scenario_results=results,
    )
    (destination / "acceptance_report.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return report


def build_acceptance_report(
    blueprint_dir: Path | str,
    output_dir: Path | str,
    *,
    mode: AcceptanceMode = "deterministic",
    realistic_input_path: Path | str | None = None,
    realistic_input_record_index: int = 0,
    model: str = DEFAULT_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_ACCEPTANCE_MAX_BUDGET,
) -> AcceptanceReport:
    """Synchronous wrapper for one-blueprint acceptance review."""

    return asyncio.run(
        abuild_acceptance_report(
            blueprint_dir=blueprint_dir,
            output_dir=output_dir,
            mode=mode,
            realistic_input_path=realistic_input_path,
            realistic_input_record_index=realistic_input_record_index,
            model=model,
            max_budget=max_budget,
        ),
    )


async def abuild_suite_acceptance_report(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    mode: AcceptanceMode = "deterministic",
    model: str = DEFAULT_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_ACCEPTANCE_MAX_BUDGET,
) -> SuiteAcceptanceReport:
    """Build persisted acceptance artifacts across all shipped examples."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    reports: dict[str, str] = {}
    accepted_examples = 0
    concern_examples = 0
    rejected_examples = 0

    for example in discover_shipped_blueprints(examples_root):
        report = await abuild_acceptance_report(
            blueprint_dir=example.blueprint_dir,
            output_dir=destination / example.example_id,
            mode=mode,
            model=model,
            max_budget=max_budget,
        )
        reports[example.example_id] = str(destination / example.example_id / "acceptance_report.json")
        example_verdict = _example_verdict(report)
        if example_verdict == "accept":
            accepted_examples += 1
        elif example_verdict == "concern":
            concern_examples += 1
        else:
            rejected_examples += 1

    suite_report = SuiteAcceptanceReport(
        mode=mode,
        example_count=len(reports),
        accepted_examples=accepted_examples,
        concern_examples=concern_examples,
        rejected_examples=rejected_examples,
        reports=reports,
    )
    (destination / "suite_acceptance_report.json").write_text(
        json.dumps(suite_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return suite_report


def build_suite_acceptance_report(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    mode: AcceptanceMode = "deterministic",
    model: str = DEFAULT_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_ACCEPTANCE_MAX_BUDGET,
) -> SuiteAcceptanceReport:
    """Synchronous wrapper for suite acceptance review."""

    return asyncio.run(
        abuild_suite_acceptance_report(
            output_dir=output_dir,
            examples_root=examples_root,
            mode=mode,
            model=model,
            max_budget=max_budget,
        ),
    )


async def abuild_realistic_suite_acceptance_report(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    modes: list[AcceptanceMode] | None = None,
    realistic_input_record_index: int = 0,
    model: str = DEFAULT_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_ACCEPTANCE_MAX_BUDGET,
) -> RealisticSuiteAcceptanceReport:
    """Build persisted realistic-input acceptance artifacts across shipped examples and modes."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    shipped_examples = discover_shipped_blueprints(examples_root)
    selected_modes = modes or ["reference", "deterministic"]
    realistic_input_paths = {
        example.example_id: str(_discover_realistic_input_path(example))
        for example in shipped_examples
    }

    mode_summaries: dict[str, RealisticSuiteModeSummary] = {}
    for mode in selected_modes:
        reports: dict[str, str] = {}
        accepted_examples = 0
        concern_examples = 0
        rejected_examples = 0
        for example in shipped_examples:
            report = await abuild_acceptance_report(
                blueprint_dir=example.blueprint_dir,
                output_dir=destination / mode / example.example_id,
                mode=mode,
                realistic_input_path=realistic_input_paths[example.example_id],
                realistic_input_record_index=realistic_input_record_index,
                model=model,
                max_budget=max_budget,
            )
            reports[example.example_id] = str(
                destination / mode / example.example_id / "acceptance_report.json",
            )
            example_verdict = _example_verdict(report)
            if example_verdict == "accept":
                accepted_examples += 1
            elif example_verdict == "concern":
                concern_examples += 1
            else:
                rejected_examples += 1
        mode_summaries[mode] = RealisticSuiteModeSummary(
            mode=mode,
            example_count=len(reports),
            accepted_examples=accepted_examples,
            concern_examples=concern_examples,
            rejected_examples=rejected_examples,
            reports=reports,
        )

    suite_report = RealisticSuiteAcceptanceReport(
        modes=selected_modes,
        example_count=len(shipped_examples),
        record_index=realistic_input_record_index,
        realistic_input_paths=realistic_input_paths,
        mode_summaries=mode_summaries,
    )
    (destination / "realistic_suite_acceptance_report.json").write_text(
        json.dumps(suite_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return suite_report


def build_realistic_suite_acceptance_report(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    modes: list[AcceptanceMode] | None = None,
    realistic_input_record_index: int = 0,
    model: str = DEFAULT_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_ACCEPTANCE_MAX_BUDGET,
) -> RealisticSuiteAcceptanceReport:
    """Synchronous wrapper for realistic-input suite acceptance review."""

    return asyncio.run(
        abuild_realistic_suite_acceptance_report(
            output_dir=output_dir,
            examples_root=examples_root,
            modes=modes,
            realistic_input_record_index=realistic_input_record_index,
            model=model,
            max_budget=max_budget,
        ),
    )


async def abuild_realistic_mode_comparison_report(
    blueprint_dir: Path | str,
    output_dir: Path | str,
    *,
    modes: list[AcceptanceMode] | None = None,
    realistic_input_path: Path | str,
    realistic_input_record_index: int = 0,
    model: str = DEFAULT_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_ACCEPTANCE_MAX_BUDGET,
) -> RealisticModeComparisonReport:
    """Build persisted realistic-input acceptance reports across modes for one blueprint."""

    blueprint_path = Path(blueprint_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    selected_modes = modes or ["reference", "deterministic", "llm"]

    verdicts_by_mode: dict[str, Literal["accept", "concern", "reject"]] = {}
    reports: dict[str, str] = {}
    for mode in selected_modes:
        report = await abuild_acceptance_report(
            blueprint_dir=blueprint_path,
            output_dir=destination / mode,
            mode=mode,
            realistic_input_path=realistic_input_path,
            realistic_input_record_index=realistic_input_record_index,
            model=model,
            max_budget=max_budget,
        )
        verdicts_by_mode[mode] = _example_verdict(report)
        reports[mode] = str(destination / mode / "acceptance_report.json")

    comparison_report = RealisticModeComparisonReport(
        blueprint_dir=str(blueprint_path),
        realistic_input_path=str(Path(realistic_input_path)),
        record_index=realistic_input_record_index,
        modes=selected_modes,
        verdicts_by_mode=verdicts_by_mode,
        reports=reports,
    )
    (destination / "realistic_mode_comparison_report.json").write_text(
        json.dumps(comparison_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return comparison_report


def build_realistic_mode_comparison_report(
    blueprint_dir: Path | str,
    output_dir: Path | str,
    *,
    modes: list[AcceptanceMode] | None = None,
    realistic_input_path: Path | str,
    realistic_input_record_index: int = 0,
    model: str = DEFAULT_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_ACCEPTANCE_MAX_BUDGET,
) -> RealisticModeComparisonReport:
    """Synchronous wrapper for realistic-input acceptance comparison."""

    return asyncio.run(
        abuild_realistic_mode_comparison_report(
            blueprint_dir=blueprint_dir,
            output_dir=output_dir,
            modes=modes,
            realistic_input_path=realistic_input_path,
            realistic_input_record_index=realistic_input_record_index,
            model=model,
            max_budget=max_budget,
        ),
    )


async def _review_acceptance_scenario(
    *,
    blueprint: FrozenBlueprint,
    scenario: Scenario,
    outputs_by_component: dict[str, dict[str, dict[str, object]]],
    realistic_input_payload: object | None,
    model: str,
    max_budget: float,
    trace_id: str,
) -> AcceptanceReviewResponse:
    """Run the LLM reviewer for one semantic-acceptance scenario."""

    fixture_path = os.environ.get("AC14_ACCEPTANCE_REVIEW_FIXTURE")
    if fixture_path:
        return AcceptanceReviewResponse.model_validate_json(Path(fixture_path).read_text())

    messages = render_prompt(
        ACCEPTANCE_PROMPT_PATH,
        blueprint_metadata=blueprint.metadata.model_dump(mode="json"),
        scenario=scenario.model_dump(mode="json"),
        realistic_input_payload=realistic_input_payload,
        outputs_by_component=outputs_by_component,
    )
    response, _meta = await acall_llm_structured(
        model,
        messages,
        response_model=AcceptanceReviewResponse,
        task="ac14_review_acceptance",
        trace_id=trace_id,
        max_budget=max_budget,
    )
    return cast(AcceptanceReviewResponse, response)


async def _execute_mode_for_acceptance(
    *,
    blueprint: FrozenBlueprint,
    mode: AcceptanceMode,
    output_dir: Path,
    model: str,
    max_budget: float,
) -> dict[str, RecompositionScenarioExecution]:
    """Execute one mode and return runnable scenario outputs keyed by scenario id."""

    builders = await _builders_for_mode(
        blueprint=blueprint,
        mode=mode,
        output_dir=output_dir,
        model=model,
        max_budget=max_budget,
    )
    catalog = build_recomposition_scenario_catalog(blueprint)
    _catalog, executions = execute_recomposition_scenarios(blueprint, builders)
    execution_by_id = {execution.scenario_id: execution for execution in executions}
    return {
        scenario.scenario_id: execution_by_id[scenario.scenario_id]
        for scenario in catalog.runnable_scenarios
        if scenario.scenario_id in execution_by_id
    }


async def _execute_mode_for_realistic_input_acceptance(
    *,
    blueprint: FrozenBlueprint,
    mode: AcceptanceMode,
    output_dir: Path,
    realistic_input_record: dict[str, Any],
    model: str,
    max_budget: float,
) -> dict[str, RecompositionScenarioExecution]:
    """Execute realistic-input semantic-acceptance scenarios from one real input record."""

    realistic_scenarios = [
        scenario
        for scenario in blueprint.scenarios.values()
        if scenario.kind == "semantic_acceptance" and scenario.realistic_input
    ]
    if len(realistic_scenarios) != 1:
        raise ValueError(
            "realistic-input acceptance currently requires exactly one realistic semantic_acceptance scenario",
        )
    source_components = _source_components(blueprint)
    if len(source_components) != 1:
        raise ValueError(
            "realistic-input acceptance currently requires exactly one source component",
        )
    source_component_id = source_components[0]
    source_component = blueprint.components[source_component_id]
    if len(source_component.input_ports) != 1:
        raise ValueError(
            "realistic-input acceptance currently requires exactly one source input port",
        )
    source_port_name = source_component.input_ports[0].name
    builders = await _builders_for_mode(
        blueprint=blueprint,
        mode=mode,
        output_dir=output_dir,
        model=model,
        max_budget=max_budget,
    )
    implementations = {
        component_id: builders[component_id]()
        for component_id in blueprint.components
    }
    _seed_realistic_runtime_state(
        implementations=implementations,
        realistic_input_record=realistic_input_record,
    )
    scenario = realistic_scenarios[0]
    try:
        outputs = run_blueprint_once(
            blueprint,
            implementations,
            {str(source_component_id): {source_port_name: realistic_input_record}},
        )
        return {
            scenario.scenario_id: RecompositionScenarioExecution(
                scenario_id=scenario.scenario_id,
                outputs_by_component=outputs,
            )
        }
    except Exception as exc:  # pragma: no cover - explicit failure capture
        return {
            scenario.scenario_id: RecompositionScenarioExecution(
                scenario_id=scenario.scenario_id,
                error=str(exc),
            )
        }


async def _builders_for_mode(
    *,
    blueprint: FrozenBlueprint,
    mode: AcceptanceMode,
    output_dir: Path,
    model: str,
    max_budget: float,
) -> dict[str, Any]:
    """Build component factories for one acceptance mode."""

    if mode == "reference":
        return build_reference_component_builders_for_blueprint(blueprint)
    packet_bundle = compile_packets(blueprint)
    generated_package = await aemit_generated_package(
        packet_bundle,
        output_dir / "generated",
        generator_kind="deterministic" if mode == "deterministic" else "llm",
        llm_model=model,
        llm_max_budget=max_budget,
        trace_id_prefix=f"ac14/acceptance/{mode}",
    )
    return load_generated_component_builders(generated_package)


def _load_realistic_input_record(
    *,
    realistic_input_path: Path | str,
    record_index: int,
) -> dict[str, Any]:
    """Load one realistic input record from a persisted JSON artifact."""

    path = Path(realistic_input_path)
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ValueError("realistic-input acceptance currently requires a top-level JSON list")
    if record_index < 0 or record_index >= len(payload):
        raise ValueError("realistic-input record index is out of range")
    record = payload[record_index]
    if not isinstance(record, dict):
        raise ValueError("realistic-input acceptance currently requires object records")
    return cast(dict[str, Any], record)


def _discover_realistic_input_path(example: ShippedBlueprintExample | object) -> Path:
    """Return the default realistic-input artifact for one shipped example."""

    typed_example = (
        example
        if isinstance(example, ShippedBlueprintExample)
        else ShippedBlueprintExample.model_validate(example)
    )
    example_dir = Path(typed_example.blueprint_dir).parent
    input_dir = example_dir / "input"
    if not input_dir.is_dir():
        raise ValueError(f"no input directory found for shipped example {typed_example.example_id}")
    candidates = sorted(input_dir.glob("*.json"))
    if not candidates:
        raise ValueError(
            f"no realistic-input json artifact found for shipped example {typed_example.example_id}",
        )
    return candidates[0]


def _source_components(blueprint: FrozenBlueprint) -> list[str]:
    """Return source components in blueprint order."""

    inbound_components = {binding.to_component for binding in blueprint.bindings}
    return [
        component_id
        for component_id in blueprint.components
        if component_id not in inbound_components
    ]


def _seed_realistic_runtime_state(
    *,
    implementations: dict[str, Any],
    realistic_input_record: dict[str, Any],
) -> None:
    """Seed runtime state for unseen realistic-input identifiers."""

    ticket_id = realistic_input_record.get("ticket_id")
    opened_at = realistic_input_record.get("opened_at") or realistic_input_record.get("submitted_at")
    if isinstance(ticket_id, str) and isinstance(opened_at, str):
        for implementation in implementations.values():
            generated_at_by_ticket_id = getattr(implementation, "_generated_at_by_ticket_id", None)
            if isinstance(generated_at_by_ticket_id, dict):
                generated_at_by_ticket_id.setdefault(ticket_id, opened_at)
            module_ticket_map = getattr(type(implementation).execute, "__globals__", {}).get(
                "GENERATED_AT_BY_TICKET_ID",
            )
            if isinstance(module_ticket_map, dict):
                module_ticket_map.setdefault(ticket_id, opened_at)

    alert_id = realistic_input_record.get("alert_id")
    observed_at = realistic_input_record.get("observed_at") or realistic_input_record.get("opened_at")
    if isinstance(alert_id, str) and isinstance(observed_at, str):
        for implementation in implementations.values():
            generated_at_by_alert_id = getattr(implementation, "_generated_at_by_alert_id", None)
            if isinstance(generated_at_by_alert_id, dict):
                generated_at_by_alert_id.setdefault(alert_id, observed_at)
            module_alert_map = getattr(type(implementation).execute, "__globals__", {}).get(
                "GENERATED_AT_BY_ALERT_ID",
            )
            if isinstance(module_alert_map, dict):
                module_alert_map.setdefault(alert_id, observed_at)


def _example_verdict(report: AcceptanceReport) -> Literal["accept", "concern", "reject"]:
    """Reduce one report to an overall example verdict."""

    if any(result.execution_error is not None for result in report.scenario_results):
        return "reject"
    verdicts = [result.review.overall_verdict for result in report.scenario_results if result.review]
    if any(verdict == "reject" for verdict in verdicts):
        return "reject"
    if any(verdict == "concern" for verdict in verdicts):
        return "concern"
    return "accept"

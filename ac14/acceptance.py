"""Requirements-aware semantic acceptance for AC14 semantic-acceptance scenarios."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, Field

from ac14.examples import discover_shipped_blueprints
from ac14.generated_codegen import emit_generated_package, load_generated_component_builders
from ac14.loader import load_blueprint_dir
from ac14.models import FrozenBlueprint, Scenario
from ac14.packets import compile_packets
from ac14.recomposition import (
    RecompositionScenarioExecution,
    build_recomposition_scenario_catalog,
    execute_recomposition_scenarios,
)
from ac14.reference_components import build_reference_component_builders_for_blueprint
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


async def abuild_acceptance_report(
    blueprint_dir: Path | str,
    output_dir: Path | str,
    *,
    mode: AcceptanceMode = "deterministic",
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

    scenario_executions = await _execute_mode_for_acceptance(
        blueprint=blueprint,
        mode=mode,
        output_dir=destination / mode,
        model=model,
        max_budget=max_budget,
    )

    results: list[AcceptanceScenarioResult] = []
    for scenario_id, scenario in acceptance_scenarios.items():
        execution = scenario_executions[scenario_id]
        if execution.error is not None:
            results.append(
                AcceptanceScenarioResult(
                    scenario_id=scenario_id,
                    mode=mode,
                    realistic_input=scenario.realistic_input,
                    requirements=scenario.requirements,
                    execution_error=execution.error,
                ),
            )
            continue

        review = await _review_acceptance_scenario(
            blueprint=blueprint,
            scenario=scenario,
            outputs_by_component=execution.outputs_by_component or {},
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
    model: str = DEFAULT_ACCEPTANCE_MODEL,
    max_budget: float = DEFAULT_ACCEPTANCE_MAX_BUDGET,
) -> AcceptanceReport:
    """Synchronous wrapper for one-blueprint acceptance review."""

    return asyncio.run(
        abuild_acceptance_report(
            blueprint_dir=blueprint_dir,
            output_dir=output_dir,
            mode=mode,
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


async def _review_acceptance_scenario(
    *,
    blueprint: FrozenBlueprint,
    scenario: Scenario,
    outputs_by_component: dict[str, dict[str, dict[str, object]]],
    model: str,
    max_budget: float,
    trace_id: str,
) -> AcceptanceReviewResponse:
    """Run the LLM reviewer for one semantic-acceptance scenario."""

    messages = render_prompt(
        ACCEPTANCE_PROMPT_PATH,
        blueprint_metadata=blueprint.metadata.model_dump(mode="json"),
        scenario=scenario.model_dump(mode="json"),
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

    if mode == "reference":
        builders = build_reference_component_builders_for_blueprint(blueprint)
    else:
        packet_bundle = compile_packets(blueprint)
        generated_package = emit_generated_package(
            packet_bundle,
            output_dir / "generated",
            generator_kind="deterministic" if mode == "deterministic" else "llm",
            llm_model=model,
            llm_max_budget=max_budget,
            trace_id_prefix=f"ac14/acceptance/{mode}",
        )
        builders = load_generated_component_builders(generated_package)

    catalog = build_recomposition_scenario_catalog(blueprint)
    _catalog, executions = execute_recomposition_scenarios(blueprint, builders)
    execution_by_id = {execution.scenario_id: execution for execution in executions}
    return {
        scenario.scenario_id: execution_by_id[scenario.scenario_id]
        for scenario in catalog.runnable_scenarios
        if scenario.scenario_id in execution_by_id
    }


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

"""Suite-level semantic comparison across shipped blueprint examples."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from ac14.examples import discover_shipped_blueprints
from ac14.semantic_comparison import (
    ComparisonMode,
    SemanticModeReport,
    build_semantic_comparison_report,
)


class SuiteExampleSemanticSummary(BaseModel):
    """Semantic comparison summary for one shipped example."""

    example_id: str = Field(description="Directory-derived shipped example identifier.")
    blueprint_id: str = Field(description="Blueprint identifier.")
    blueprint_dir: str = Field(description="Blueprint directory path.")
    report_path: str = Field(description="Persisted semantic comparison report path.")
    modes: list[SemanticModeReport] = Field(description="Per-mode semantic comparison results.")


class SuiteModeSemanticAggregate(BaseModel):
    """Aggregate semantic comparison totals for one execution mode."""

    mode: ComparisonMode = Field(description="Compared execution mode.")
    fully_matching_expected_examples: int = Field(
        description="Examples with zero expected-output semantic failures.",
    )
    failing_expected_examples: int = Field(
        description="Examples with any expected-output semantic failure.",
    )
    fully_matching_reference_examples: int | None = Field(
        default=None,
        description="Examples with zero reference mismatches when applicable.",
    )
    failing_reference_examples: int | None = Field(
        default=None,
        description="Examples with any reference mismatch when applicable.",
    )
    total_expected_mismatched_components: int = Field(
        description="Total component mismatches against expected outputs across the suite.",
    )
    total_reference_mismatched_components: int | None = Field(
        default=None,
        description="Total component mismatches against the reference lane when applicable.",
    )


class SuiteSemanticComparisonReport(BaseModel):
    """Persisted suite-level semantic comparison report."""

    example_count: int = Field(description="Number of shipped examples in the suite.")
    examples: list[SuiteExampleSemanticSummary] = Field(
        description="Per-example semantic comparison summaries.",
    )
    mode_aggregates: list[SuiteModeSemanticAggregate] = Field(
        description="Aggregate totals by execution mode.",
    )


def build_suite_semantic_comparison_report(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    modes: list[ComparisonMode] | None = None,
    llm_model: str = "gemini/gemini-2.5-flash-lite",
    llm_max_budget: float = 0.50,
) -> SuiteSemanticComparisonReport:
    """Build semantic comparison artifacts across all shipped examples."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    selected_modes = modes or ["reference", "deterministic"]
    examples = discover_shipped_blueprints(examples_root)

    summaries: list[SuiteExampleSemanticSummary] = []
    for example in examples:
        example_dir = destination / example.example_id
        report = build_semantic_comparison_report(
            blueprint_dir=example.blueprint_dir,
            output_dir=example_dir,
            modes=selected_modes,
            llm_model=llm_model,
            llm_max_budget=llm_max_budget,
        )
        summaries.append(
            SuiteExampleSemanticSummary(
                example_id=example.example_id,
                blueprint_id=example.blueprint_id,
                blueprint_dir=example.blueprint_dir,
                report_path=str(example_dir / "semantic_comparison_report.json"),
                modes=report.modes,
            ),
        )

    suite_report = SuiteSemanticComparisonReport(
        example_count=len(summaries),
        examples=summaries,
        mode_aggregates=_aggregate_modes(summaries, selected_modes),
    )
    (destination / "suite_semantic_comparison_report.json").write_text(
        json.dumps(suite_report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return suite_report


def _aggregate_modes(
    summaries: list[SuiteExampleSemanticSummary],
    modes: list[ComparisonMode],
) -> list[SuiteModeSemanticAggregate]:
    """Aggregate semantic comparison totals across the shipped suite."""

    aggregates: list[SuiteModeSemanticAggregate] = []
    for mode in modes:
        mode_reports = [
            _mode_report_for_summary(summary, mode)
            for summary in summaries
        ]
        has_reference = mode != "reference"
        aggregates.append(
            SuiteModeSemanticAggregate(
                mode=mode,
                fully_matching_expected_examples=sum(
                    1 for report in mode_reports if report.failed_expected_scenarios == 0
                ),
                failing_expected_examples=sum(
                    1 for report in mode_reports if report.failed_expected_scenarios != 0
                ),
                fully_matching_reference_examples=(
                    None
                    if not has_reference
                    else sum(
                        1
                        for report in mode_reports
                        if (report.failed_reference_scenarios or 0) == 0
                    )
                ),
                failing_reference_examples=(
                    None
                    if not has_reference
                    else sum(
                        1
                        for report in mode_reports
                        if (report.failed_reference_scenarios or 0) != 0
                    )
                ),
                total_expected_mismatched_components=sum(
                    len(result.mismatched_components_vs_expected)
                    for report in mode_reports
                    for result in report.scenario_results
                ),
                total_reference_mismatched_components=(
                    None
                    if not has_reference
                    else sum(
                        len(result.mismatched_components_vs_reference)
                        for report in mode_reports
                        for result in report.scenario_results
                    )
                ),
            ),
        )
    return aggregates


def _mode_report_for_summary(
    summary: SuiteExampleSemanticSummary,
    mode: ComparisonMode,
) -> SemanticModeReport:
    """Return the semantic mode report for one example summary."""

    for report in summary.modes:
        if report.mode == mode:
            return report
    raise ValueError(f"missing semantic mode report for mode {mode!r} in {summary.example_id}")

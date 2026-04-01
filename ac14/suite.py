"""Suite-level proof and comparison workflows across shipped examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from ac14.comparison import GeneratorRunSummary, build_generator_comparison_report
from ac14.generated_codegen import GeneratorKind
from ac14.evidence_bundle import build_evidence_bundle
from ac14.examples import discover_shipped_blueprints


class SuiteExampleProofSummary(BaseModel):
    """Proof summary for one shipped blueprint example."""

    example_id: str = Field(description="Directory-derived shipped example identifier.")
    blueprint_id: str = Field(description="Blueprint identifier.")
    blueprint_dir: str = Field(description="Blueprint directory path.")
    bundle_dir: str = Field(description="Directory containing the persisted evidence bundle.")
    generator_kind: GeneratorKind = Field(description="Generator mode used for the proof run.")
    packet_tests_passed: bool = Field(description="Whether packet-local tests passed.")
    recomposition_passed: bool = Field(description="Whether recomposition scenarios passed.")
    fresh_run_passed_trials: int = Field(description="Number of passing fresh-run trials.")
    fresh_run_failed_trials: int = Field(description="Number of failing fresh-run trials.")
    realistic_input_gate_status: Literal["included", "missing", "unsupported"] = Field(
        description="Whether realistic-input final-gate acceptance was included for this example.",
    )
    realistic_input_gate_path: str = Field(
        description="Persisted realistic-input final-gate artifact path for this example.",
    )
    realistic_input_gate_reason: str = Field(
        description="Concise explanation for the realistic-input gate status.",
    )


class SuiteProofReport(BaseModel):
    """Aggregate proof report across shipped blueprint examples."""

    example_count: int = Field(description="Number of shipped examples in the suite.")
    passed_examples: int = Field(description="Number of examples with a fully passing proof run.")
    failed_examples: int = Field(description="Number of examples with any failing proof check.")
    realistic_input_gate_included_examples: int = Field(
        description="Examples whose default proof bundle included realistic-input final-gate acceptance.",
    )
    realistic_input_gate_missing_examples: int = Field(
        description="Examples missing a realistic-input artifact in the default suite proof story.",
    )
    realistic_input_gate_unsupported_examples: int = Field(
        description="Examples where the current generator mode does not support the default realistic-input gate.",
    )
    examples: list[SuiteExampleProofSummary] = Field(description="Per-example proof summaries.")


class SuiteExampleComparisonSummary(BaseModel):
    """Comparison summary for one shipped blueprint example."""

    example_id: str = Field(description="Directory-derived shipped example identifier.")
    blueprint_id: str = Field(description="Blueprint identifier.")
    blueprint_dir: str = Field(description="Blueprint directory path.")
    comparison_report_path: str = Field(description="Persisted per-example comparison report path.")
    runs: list[GeneratorRunSummary] = Field(description="Generator runs for this example.")


class SuiteGeneratorAggregate(BaseModel):
    """Aggregate comparison totals for one generator mode across the shipped suite."""

    generator_kind: GeneratorKind = Field(description="Generator mode covered by this aggregate.")
    passed_examples: int = Field(description="Examples that fully passed under this generator mode.")
    failed_examples: int = Field(description="Examples that failed any proof check under this generator mode.")
    total_runnable_scenarios: int = Field(description="Sum of runnable recomposition scenarios across examples.")
    total_skipped_scenarios: int = Field(description="Sum of skipped recomposition scenarios across examples.")


class SuiteComparisonReport(BaseModel):
    """Aggregate comparison report across shipped blueprint examples."""

    example_count: int = Field(description="Number of shipped examples in the suite.")
    examples: list[SuiteExampleComparisonSummary] = Field(
        description="Per-example comparison summaries.",
    )
    generator_aggregates: list[SuiteGeneratorAggregate] = Field(
        description="Aggregate totals by generator mode.",
    )


def build_suite_proof_report(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    fresh_run_trials: int = 2,
    generator_kind: GeneratorKind = "deterministic",
    llm_model: str = "gemini/gemini-2.5-flash-lite",
    llm_max_budget: float = 0.50,
) -> SuiteProofReport:
    """Build persisted proof artifacts across all shipped examples."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    examples = discover_shipped_blueprints(examples_root)

    summaries: list[SuiteExampleProofSummary] = []
    for example in examples:
        bundle_dir = destination / example.example_id
        manifest = build_evidence_bundle(
            blueprint_dir=example.blueprint_dir,
            output_dir=bundle_dir,
            fresh_run_trials=fresh_run_trials,
            generator_kind=generator_kind,
            llm_model=llm_model,
            llm_max_budget=llm_max_budget,
        )
        packet_test_report = json.loads(Path(manifest.packet_test_report_path).read_text())
        recomposition_report = json.loads(Path(manifest.recomposition_report_path).read_text())
        fresh_run_summary = json.loads(Path(manifest.fresh_run_summary_path).read_text())
        realistic_input_gate = json.loads(Path(manifest.realistic_input_gate_path).read_text())
        summaries.append(
            SuiteExampleProofSummary(
                example_id=example.example_id,
                blueprint_id=example.blueprint_id,
                blueprint_dir=example.blueprint_dir,
                bundle_dir=str(bundle_dir),
                generator_kind=generator_kind,
                packet_tests_passed=packet_test_report["passed"],
                recomposition_passed=recomposition_report["passed"],
                fresh_run_passed_trials=fresh_run_summary["passed_trials"],
                fresh_run_failed_trials=fresh_run_summary["failed_trials"],
                realistic_input_gate_status=realistic_input_gate["status"],
                realistic_input_gate_path=manifest.realistic_input_gate_path,
                realistic_input_gate_reason=realistic_input_gate["reason"],
            ),
        )

    report = SuiteProofReport(
        example_count=len(summaries),
        passed_examples=sum(1 for summary in summaries if _proof_summary_passed(summary)),
        failed_examples=sum(1 for summary in summaries if not _proof_summary_passed(summary)),
        realistic_input_gate_included_examples=sum(
            1 for summary in summaries if summary.realistic_input_gate_status == "included"
        ),
        realistic_input_gate_missing_examples=sum(
            1 for summary in summaries if summary.realistic_input_gate_status == "missing"
        ),
        realistic_input_gate_unsupported_examples=sum(
            1 for summary in summaries if summary.realistic_input_gate_status == "unsupported"
        ),
        examples=summaries,
    )
    (destination / "suite_proof_report.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return report


def build_suite_comparison_report(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    generator_kinds: list[GeneratorKind] | None = None,
    fresh_run_trials: int = 2,
    llm_model: str = "gemini/gemini-2.5-flash-lite",
    llm_max_budget: float = 0.50,
) -> SuiteComparisonReport:
    """Build persisted comparison artifacts across all shipped examples."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    examples = discover_shipped_blueprints(examples_root)
    selected_generators = generator_kinds or ["deterministic", "llm"]

    comparison_summaries: list[SuiteExampleComparisonSummary] = []
    for example in examples:
        example_dir = destination / example.example_id
        comparison_report = build_generator_comparison_report(
            blueprint_dir=example.blueprint_dir,
            output_dir=example_dir,
            generator_kinds=selected_generators,
            fresh_run_trials=fresh_run_trials,
            llm_model=llm_model,
            llm_max_budget=llm_max_budget,
        )
        comparison_summaries.append(
            SuiteExampleComparisonSummary(
                example_id=example.example_id,
                blueprint_id=example.blueprint_id,
                blueprint_dir=example.blueprint_dir,
                comparison_report_path=str(example_dir / "comparison_report.json"),
                runs=comparison_report.runs,
            ),
        )

    report = SuiteComparisonReport(
        example_count=len(comparison_summaries),
        examples=comparison_summaries,
        generator_aggregates=_aggregate_suite_generators(comparison_summaries, selected_generators),
    )
    (destination / "suite_comparison_report.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return report


def _aggregate_suite_generators(
    example_summaries: list[SuiteExampleComparisonSummary],
    generator_kinds: list[GeneratorKind],
) -> list[SuiteGeneratorAggregate]:
    """Aggregate per-generator totals across all example comparison reports."""

    aggregates: list[SuiteGeneratorAggregate] = []
    for generator_kind in generator_kinds:
        generator_runs = [
            run
            for example in example_summaries
            for run in example.runs
            if run.generator_kind == generator_kind
        ]
        aggregates.append(
            SuiteGeneratorAggregate(
                generator_kind=generator_kind,
                passed_examples=sum(1 for run in generator_runs if _run_summary_passed(run)),
                failed_examples=sum(1 for run in generator_runs if not _run_summary_passed(run)),
                total_runnable_scenarios=sum(
                    run.recomposition_runnable_scenarios for run in generator_runs
                ),
                total_skipped_scenarios=sum(
                    run.recomposition_skipped_scenarios for run in generator_runs
                ),
            ),
        )
    return aggregates


def _proof_summary_passed(summary: SuiteExampleProofSummary) -> bool:
    """Return whether one suite proof example fully passed."""

    return (
        summary.packet_tests_passed
        and summary.recomposition_passed
        and summary.fresh_run_failed_trials == 0
    )


def _run_summary_passed(summary: GeneratorRunSummary) -> bool:
    """Return whether one generator run fully passed."""

    return (
        summary.packet_tests_passed
        and summary.recomposition_passed
        and summary.fresh_run_failed_trials == 0
    )

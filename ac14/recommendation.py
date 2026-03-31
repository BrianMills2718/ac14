"""Evidence-backed default-generator recommendation for AC14."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from ac14.generated_codegen import GeneratorKind
from ac14.examples import discover_shipped_blueprints
from ac14.semantic_comparison import ComparisonMode
from ac14.semantic_suite import (
    SuiteModeSemanticAggregate,
    SuiteSemanticComparisonReport,
    build_suite_semantic_comparison_report,
)
from ac14.suite import (
    SuiteComparisonReport,
    SuiteGeneratorAggregate,
    build_suite_comparison_report,
)


class DefaultGeneratorRecommendation(BaseModel):
    """Persisted recommendation about the current default generator choice."""

    recommended_default: GeneratorKind = Field(
        description="Generator that should remain the default today.",
    )
    llm_promotion_ready: bool = Field(
        description="Whether the current evidence is strong enough to promote the LLM generator.",
    )
    evaluated_generators: list[GeneratorKind] = Field(
        description="Generator modes evaluated during this recommendation run.",
    )
    proof_breadth_count: int = Field(
        description="Distinct workflow-signature slices across the shipped suite.",
    )
    suite_comparison_report_path: str = Field(
        description="Persisted suite comparison report used by this recommendation.",
    )
    suite_semantic_report_path: str = Field(
        description="Persisted suite semantic comparison report used by this recommendation.",
    )
    reasons: list[str] = Field(description="Human-readable reasons for the recommendation.")


def build_default_generator_recommendation(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    generator_kinds: list[GeneratorKind] | None = None,
    fresh_run_trials: int = 2,
    llm_model: str = "gemini/gemini-2.5-flash-lite",
    llm_max_budget: float = 0.50,
) -> DefaultGeneratorRecommendation:
    """Build suite reports and derive the current default-generator recommendation."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    selected_generators = generator_kinds or ["deterministic"]
    semantic_modes: list[ComparisonMode] = ["reference", *selected_generators]

    suite_comparison = build_suite_comparison_report(
        output_dir=destination / "suite_comparison",
        examples_root=examples_root,
        generator_kinds=selected_generators,
        fresh_run_trials=fresh_run_trials,
        llm_model=llm_model,
        llm_max_budget=llm_max_budget,
    )
    suite_semantic = build_suite_semantic_comparison_report(
        output_dir=destination / "suite_semantic",
        examples_root=examples_root,
        modes=semantic_modes,
        llm_model=llm_model,
        llm_max_budget=llm_max_budget,
    )

    proof_breadth_count = _proof_breadth_count(examples_root)
    reasons: list[str] = []
    llm_promotion_ready = _llm_promotion_ready(
        selected_generators,
        suite_comparison,
        suite_semantic,
        proof_breadth_count,
        reasons,
    )
    recommendation = DefaultGeneratorRecommendation(
        recommended_default="llm" if llm_promotion_ready else "deterministic",
        llm_promotion_ready=llm_promotion_ready,
        evaluated_generators=selected_generators,
        proof_breadth_count=proof_breadth_count,
        suite_comparison_report_path=str(
            destination / "suite_comparison" / "suite_comparison_report.json"
        ),
        suite_semantic_report_path=str(
            destination / "suite_semantic" / "suite_semantic_comparison_report.json"
        ),
        reasons=reasons,
    )
    (destination / "default_generator_recommendation.json").write_text(
        json.dumps(recommendation.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return recommendation


def _proof_breadth_count(examples_root: Path | str | None) -> int:
    """Return the number of distinct workflow signatures in the shipped suite."""

    from ac14.loader import load_blueprint_dir

    signatures = set()
    for example in discover_shipped_blueprints(examples_root):
        blueprint = load_blueprint_dir(example.blueprint_dir)
        signatures.add(
            tuple(
                sorted(
                    component.semantic_responsibility
                    for component in blueprint.components.values()
                )
            ),
        )
    return len(signatures)


def _llm_promotion_ready(
    selected_generators: list[GeneratorKind],
    suite_comparison: SuiteComparisonReport,
    suite_semantic: SuiteSemanticComparisonReport,
    proof_breadth_count: int,
    reasons: list[str],
) -> bool:
    """Evaluate whether current evidence is strong enough to promote the LLM generator."""

    if "llm" not in selected_generators:
        reasons.append("LLM generator was not evaluated in this recommendation run.")
        reasons.append("Deterministic remains the default control lane.")
        return False

    llm_comparison = _suite_generator_aggregate(suite_comparison, "llm")
    llm_semantic = _suite_mode_aggregate(suite_semantic, "llm")

    if llm_comparison.failed_examples != 0:
        reasons.append("LLM generator has failing suite-proof examples.")
    if llm_semantic.failing_expected_examples != 0:
        reasons.append("LLM generator diverges from expected outputs on the shipped suite.")
    if (llm_semantic.failing_reference_examples or 0) != 0:
        reasons.append("LLM generator diverges from the reference lane on the shipped suite.")
    if proof_breadth_count <= 1:
        reasons.append("The shipped suite still covers only one proof-breadth slice.")

    promotion_ready = (
        llm_comparison.failed_examples == 0
        and llm_semantic.failing_expected_examples == 0
        and (llm_semantic.failing_reference_examples or 0) == 0
        and proof_breadth_count > 1
    )
    if promotion_ready:
        reasons.append("LLM generator satisfies the current promotion criteria.")
    else:
        reasons.append("Deterministic remains the default control lane.")
    return promotion_ready


def _suite_generator_aggregate(
    report: SuiteComparisonReport,
    generator_kind: GeneratorKind,
) -> SuiteGeneratorAggregate:
    """Return the suite comparison aggregate for one generator mode."""

    for aggregate in report.generator_aggregates:
        if aggregate.generator_kind == generator_kind:
            return aggregate
    raise ValueError(f"missing suite comparison aggregate for generator {generator_kind!r}")


def _suite_mode_aggregate(
    report: SuiteSemanticComparisonReport,
    mode: ComparisonMode,
) -> SuiteModeSemanticAggregate:
    """Return the suite semantic aggregate for one execution mode."""

    for aggregate in report.mode_aggregates:
        if aggregate.mode == mode:
            return aggregate
    raise ValueError(f"missing suite semantic aggregate for mode {mode!r}")

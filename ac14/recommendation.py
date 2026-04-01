"""Evidence-backed live-readiness and default-generator recommendation for AC14."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal

from pydantic import BaseModel, Field

from ac14.acceptance import build_acceptance_report
from ac14.generated_codegen import GeneratorKind
from ac14.examples import ShippedBlueprintExample, discover_shipped_blueprints
from ac14.semantic_comparison import ComparisonMode
from ac14.semantic_suite import (
    SuiteModeSemanticAggregate,
    SuiteSemanticComparisonReport,
    build_suite_semantic_comparison_report,
)
from ac14.suite import (
    SuiteComparisonReport,
    SuiteGeneratorAggregate,
    SuiteProofReport,
    build_suite_comparison_report,
    build_suite_proof_report,
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
    live_readiness_status: Literal["ready", "blocked", "skipped"] = Field(
        description="Live realistic-input readiness verdict for the LLM lane.",
    )
    live_readiness_artifact_path: str = Field(
        description="Persisted live-readiness artifact used by this recommendation.",
    )
    suite_comparison_report_path: str = Field(
        description="Persisted suite comparison report used by this recommendation.",
    )
    suite_proof_report_path: str = Field(
        description="Persisted suite proof report used by this recommendation.",
    )
    suite_semantic_report_path: str = Field(
        description="Persisted suite semantic comparison report used by this recommendation.",
    )
    suite_default_gate_included_examples: int = Field(
        description="Suite examples whose default proof bundle included the realistic-input final gate.",
    )
    suite_default_gate_missing_examples: int = Field(
        description="Suite examples missing realistic-input default-gate coverage.",
    )
    suite_default_gate_unsupported_examples: int = Field(
        description="Suite examples whose current generator mode does not support the default realistic-input gate.",
    )
    reasons: list[str] = Field(description="Human-readable reasons for the recommendation.")


class LlmLiveReadinessArtifact(BaseModel):
    """Persisted realistic-input live-readiness artifact for the LLM lane."""

    status: Literal["ready", "blocked", "skipped"] = Field(
        description="Whether live realistic-input LLM acceptance is ready, blocked, or skipped.",
    )
    reason: str = Field(description="Concise explanation for the current readiness status.")
    example_id: str | None = Field(
        default=None,
        description="Shipped example used for the live-readiness check when one was attempted.",
    )
    blueprint_dir: str | None = Field(
        default=None,
        description="Blueprint directory used for the live-readiness check when one was attempted.",
    )
    realistic_input_path: str | None = Field(
        default=None,
        description="Realistic-input path used for the live-readiness check when one was attempted.",
    )
    acceptance_report_path: str | None = Field(
        default=None,
        description="Persisted nested acceptance report path when a live run was attempted.",
    )
    provider_env_vars: list[str] = Field(
        description="Live provider environment variables detected for the readiness check.",
    )
    live_execution_enabled: bool = Field(
        description="Whether the operator explicitly enabled a live readiness attempt.",
    )


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
    suite_proof = build_suite_proof_report(
        output_dir=destination / "suite_proof",
        examples_root=examples_root,
        fresh_run_trials=fresh_run_trials,
        generator_kind="deterministic",
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
    live_readiness = build_llm_live_readiness_artifact(
        output_dir=destination / "live_llm_readiness",
        examples_root=examples_root,
        llm_model=llm_model,
        llm_max_budget=llm_max_budget,
    )

    proof_breadth_count = _proof_breadth_count(examples_root)
    reasons: list[str] = []
    llm_promotion_ready = _llm_promotion_ready(
        selected_generators,
        suite_comparison,
        suite_proof,
        suite_semantic,
        proof_breadth_count,
        live_readiness,
        reasons,
    )
    recommendation = DefaultGeneratorRecommendation(
        recommended_default="llm" if llm_promotion_ready else "deterministic",
        llm_promotion_ready=llm_promotion_ready,
        evaluated_generators=selected_generators,
        proof_breadth_count=proof_breadth_count,
        live_readiness_status=live_readiness.status,
        live_readiness_artifact_path=str(
            destination / "live_llm_readiness" / "live_llm_readiness.json"
        ),
        suite_comparison_report_path=str(
            destination / "suite_comparison" / "suite_comparison_report.json"
        ),
        suite_proof_report_path=str(
            destination / "suite_proof" / "suite_proof_report.json"
        ),
        suite_semantic_report_path=str(
            destination / "suite_semantic" / "suite_semantic_comparison_report.json"
        ),
        suite_default_gate_included_examples=suite_proof.realistic_input_gate_included_examples,
        suite_default_gate_missing_examples=suite_proof.realistic_input_gate_missing_examples,
        suite_default_gate_unsupported_examples=suite_proof.realistic_input_gate_unsupported_examples,
        reasons=reasons,
    )
    (destination / "default_generator_recommendation.json").write_text(
        json.dumps(recommendation.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return recommendation


def build_llm_live_readiness_artifact(
    output_dir: Path | str,
    *,
    examples_root: Path | str | None = None,
    llm_model: str = "gemini/gemini-2.5-flash-lite",
    llm_max_budget: float = 0.50,
) -> LlmLiveReadinessArtifact:
    """Persist one realistic-input live-readiness artifact for the LLM lane."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    if not _live_readiness_enabled():
        artifact = LlmLiveReadinessArtifact(
            status="skipped",
            reason=(
                "Live LLM readiness was not explicitly enabled; "
                "set AC14_ENABLE_LIVE_LLM_READINESS=1 to attempt a live run."
            ),
            provider_env_vars=[],
            live_execution_enabled=False,
        )
        _persist_live_readiness_artifact(destination, artifact)
        return artifact

    provider_env_vars = _provider_env_vars()
    if not provider_env_vars:
        artifact = LlmLiveReadinessArtifact(
            status="skipped",
            reason="No live LLM provider key is available in the current environment.",
            provider_env_vars=[],
            live_execution_enabled=True,
        )
        _persist_live_readiness_artifact(destination, artifact)
        return artifact

    example = _select_live_readiness_example(examples_root)
    realistic_input_path = _resolve_realistic_input_path(Path(example.blueprint_dir))
    try:
        with _temporary_env_without_fixture():
            build_acceptance_report(
                blueprint_dir=example.blueprint_dir,
                output_dir=destination / "acceptance",
                mode="llm",
                realistic_input_path=realistic_input_path,
                realistic_input_record_index=0,
                model=llm_model,
                max_budget=llm_max_budget,
            )
    except Exception as exc:
        artifact = LlmLiveReadinessArtifact(
            status="blocked",
            reason=(
                "Live realistic-input LLM acceptance failed during readiness probing: "
                f"{exc.__class__.__name__}: {exc}"
            ),
            example_id=example.example_id,
            blueprint_dir=example.blueprint_dir,
            realistic_input_path=str(realistic_input_path),
            provider_env_vars=provider_env_vars,
            live_execution_enabled=True,
        )
        _persist_live_readiness_artifact(destination, artifact)
        return artifact

    artifact = LlmLiveReadinessArtifact(
        status="ready",
        reason="Live realistic-input LLM acceptance completed successfully.",
        example_id=example.example_id,
        blueprint_dir=example.blueprint_dir,
        realistic_input_path=str(realistic_input_path),
        acceptance_report_path=str(destination / "acceptance" / "acceptance_report.json"),
        provider_env_vars=provider_env_vars,
        live_execution_enabled=True,
    )
    _persist_live_readiness_artifact(destination, artifact)
    return artifact


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
    suite_proof: SuiteProofReport,
    suite_semantic: SuiteSemanticComparisonReport,
    proof_breadth_count: int,
    live_readiness: LlmLiveReadinessArtifact,
    reasons: list[str],
) -> bool:
    """Evaluate whether current evidence is strong enough to promote the LLM generator."""

    if "llm" not in selected_generators:
        _append_suite_default_gate_reasons(suite_proof, reasons)
        reasons.append("LLM generator was not evaluated in this recommendation run.")
        reasons.append(
            "Live LLM readiness remains "
            f"{live_readiness.status}: {live_readiness.reason}"
        )
        reasons.append("Deterministic remains the default control lane.")
        return False

    llm_comparison = _suite_generator_aggregate(suite_comparison, "llm")
    llm_semantic = _suite_mode_aggregate(suite_semantic, "llm")
    _append_suite_default_gate_reasons(suite_proof, reasons)

    if llm_comparison.failed_examples != 0:
        reasons.append("LLM generator has failing suite-proof examples.")
    if llm_semantic.failing_expected_examples != 0:
        reasons.append("LLM generator diverges from expected outputs on the shipped suite.")
    if (llm_semantic.failing_reference_examples or 0) != 0:
        reasons.append("LLM generator diverges from the reference lane on the shipped suite.")
    if proof_breadth_count <= 1:
        reasons.append("The shipped suite still covers only one proof-breadth slice.")
    if live_readiness.status != "ready":
        reasons.append(
            "Live LLM readiness is "
            f"{live_readiness.status}: {live_readiness.reason}"
        )
    if suite_proof.realistic_input_gate_included_examples != suite_proof.example_count:
        reasons.append(
            "Suite default-gate coverage is incomplete: "
            f"{suite_proof.realistic_input_gate_included_examples}/"
            f"{suite_proof.example_count} examples included realistic-input final-gate acceptance."
        )

    promotion_ready = (
        llm_comparison.failed_examples == 0
        and llm_semantic.failing_expected_examples == 0
        and (llm_semantic.failing_reference_examples or 0) == 0
        and proof_breadth_count > 1
        and live_readiness.status == "ready"
        and suite_proof.realistic_input_gate_included_examples == suite_proof.example_count
    )
    if promotion_ready:
        reasons.append("LLM generator satisfies the current promotion criteria.")
    else:
        reasons.append("Deterministic remains the default control lane.")
    return promotion_ready


def _append_suite_default_gate_reasons(
    suite_proof: SuiteProofReport,
    reasons: list[str],
) -> None:
    """Append explicit suite default-gate coverage reasons for recommendation review."""

    reasons.append(
        "Suite default-gate coverage is "
        f"{suite_proof.realistic_input_gate_included_examples}/{suite_proof.example_count} included, "
        f"{suite_proof.realistic_input_gate_missing_examples} missing, "
        f"{suite_proof.realistic_input_gate_unsupported_examples} unsupported."
    )


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


def _persist_live_readiness_artifact(
    destination: Path,
    artifact: LlmLiveReadinessArtifact,
) -> None:
    """Write one persisted live-readiness artifact to disk."""

    (destination / "live_llm_readiness.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )


def _provider_env_vars() -> list[str]:
    """Return the detected live provider environment variables."""

    return [
        name
        for name in [
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
        ]
        if os.environ.get(name)
    ]


def _live_readiness_enabled() -> bool:
    """Return true when the operator explicitly enables live readiness attempts."""

    return os.environ.get("AC14_ENABLE_LIVE_LLM_READINESS") == "1"


def _select_live_readiness_example(
    examples_root: Path | str | None,
) -> ShippedBlueprintExample:
    """Return the first shipped example with a realistic-input artifact."""

    for example in discover_shipped_blueprints(examples_root):
        blueprint_dir = Path(example.blueprint_dir)
        if any((blueprint_dir.parent / "input").glob("*.json")):
            return example
    raise ValueError("no shipped example with a realistic-input artifact is available")


def _resolve_realistic_input_path(blueprint_dir: Path) -> Path:
    """Return the single realistic-input JSON path for one shipped example."""

    candidates = sorted((blueprint_dir.parent / "input").glob("*.json"))
    if not candidates:
        raise ValueError(f"no realistic-input JSON files found for {blueprint_dir}")
    return candidates[0]


@contextmanager
def _temporary_env_without_fixture() -> Iterator[None]:
    """Temporarily disable fixture-backed LLM generation during live readiness."""

    fixture_value = os.environ.pop("AC14_LLM_CODEGEN_FIXTURE", None)
    try:
        yield
    finally:
        if fixture_value is not None:
            os.environ["AC14_LLM_CODEGEN_FIXTURE"] = fixture_value

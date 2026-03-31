"""Tests for the default-generator recommendation artifact."""

from __future__ import annotations

from pathlib import Path

from ac14.recommendation import build_default_generator_recommendation


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples"


def test_build_default_generator_recommendation_keeps_deterministic_default(
    tmp_path: Path,
) -> None:
    """Without LLM evidence and broader proof breadth, deterministic stays default."""

    recommendation = build_default_generator_recommendation(
        output_dir=tmp_path / "recommendation",
        examples_root=EXAMPLES_ROOT,
        generator_kinds=["deterministic"],
        fresh_run_trials=1,
    )

    report_path = tmp_path / "recommendation" / "default_generator_recommendation.json"
    assert report_path.exists()
    assert recommendation.recommended_default == "deterministic"
    assert recommendation.llm_promotion_ready is False
    assert recommendation.proof_breadth_count >= 2

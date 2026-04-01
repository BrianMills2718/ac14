"""Tests for the default-generator recommendation artifact."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ac14.recommendation import (
    LlmLiveReadinessArtifact,
    build_default_generator_recommendation,
    build_llm_live_readiness_artifact,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples"


def _write_acceptance_review_fixture(path: Path) -> Path:
    """Persist one deterministic acceptance-review fixture for recommendation tests."""

    path.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Fixture-backed acceptance review approved the outputs.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return path


def test_build_default_generator_recommendation_keeps_deterministic_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Without LLM evidence and broader proof breadth, deterministic stays default."""

    for key in [
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "AC14_ENABLE_LIVE_LLM_READINESS",
    ]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(
        "ac14.recommendation.build_llm_live_readiness_artifact",
        lambda *args, **kwargs: LlmLiveReadinessArtifact(
            status="skipped",
            reason="Test fixture keeps recommendation focused on recommendation logic.",
            provider_env_vars=[],
            live_execution_enabled=False,
        ),
    )
    monkeypatch.setenv(
        "AC14_ACCEPTANCE_REVIEW_FIXTURE",
        str(_write_acceptance_review_fixture(tmp_path / "acceptance_review_fixture.json")),
    )

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
    assert recommendation.live_readiness_status == "skipped"
    assert recommendation.live_readiness_artifact_path.endswith("live_llm_readiness.json")


def test_build_llm_live_readiness_artifact_skips_without_live_keys(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Live-readiness artifact should persist an explicit skipped result without keys."""

    for key in [
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "AC14_ENABLE_LIVE_LLM_READINESS",
    ]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("AC14_LLM_CODEGEN_FIXTURE", str(tmp_path / "unused_fixture.json"))

    artifact = build_llm_live_readiness_artifact(
        output_dir=tmp_path / "live_readiness",
        examples_root=EXAMPLES_ROOT,
    )

    artifact_path = tmp_path / "live_readiness" / "live_llm_readiness.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text())
    assert artifact.status == "skipped"
    assert payload["status"] == "skipped"
    assert payload["provider_env_vars"] == []

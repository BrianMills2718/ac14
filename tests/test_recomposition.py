"""Tests for recomposition-specific semantic evaluation behavior."""

from __future__ import annotations

import asyncio
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pytest

from ac14.loader import load_blueprint_dir
from ac14.recomposition import (
    _RecompSemanticEval,
    _aevaluate_recomposition_scenario_semantically,
    build_recomposition_scenario_catalog,
)


BENCHMARK_BLUEPRINT_DIR = (
    Path(__file__).resolve().parents[1] / "benchmarks" / "order_exception_resolution" / "blueprint"
)


def _contains_datetime(value: Any) -> bool:
    """Return true when a nested structure still contains date-like values."""

    if isinstance(value, (datetime, date)):
        return True
    if isinstance(value, dict):
        return any(_contains_datetime(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_datetime(item) for item in value)
    return False


def test_recomposition_semantic_eval_handles_datetime_fixture_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Recomposition semantic-eval prompt inputs should be JSON-safe for datetime-bearing fixtures."""

    blueprint = load_blueprint_dir(BENCHMARK_BLUEPRINT_DIR)
    scenario = build_recomposition_scenario_catalog(blueprint).runnable_scenarios[0]
    calls = 0

    def _fake_render_prompt(prompt_path: Path, **kwargs: Any) -> list[dict[str, str]]:
        nonlocal calls
        calls += 1
        assert _contains_datetime(kwargs["inputs"]) is False
        assert _contains_datetime(kwargs["expected_outputs"]) is False
        assert _contains_datetime(kwargs["actual_outputs"]) is False
        return [{"role": "user", "content": "ok"}]

    async def _fake_acall_llm_structured(*args: Any, **kwargs: Any) -> tuple[_RecompSemanticEval, object]:
        return _RecompSemanticEval(semantic_fields_acceptable=True, concerns=[]), object()

    monkeypatch.setattr("ac14.acceptance.render_prompt", _fake_render_prompt)
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", _fake_acall_llm_structured)

    result = asyncio.run(
        _aevaluate_recomposition_scenario_semantically(
            scenario=scenario,
            actual_outputs_by_component=scenario.expected_outputs_by_component,
            model="test-model",
            trace_id="test/recomposition_datetime",
        )
    )

    assert result.semantic_fields_acceptable is True
    assert calls == 1

"""Tests for generated packet tests, recomposition, and repeated fresh runs."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pytest

import asyncio

from ac14.generated_codegen import emit_generated_package
from ac14.generated_evidence import (
    PacketCaseSemanticEval,
    _aevaluate_packet_case_semantically,
    run_fresh_generation_trials,
    run_generated_packet_tests,
    run_generated_recomposition_proof,
)
from ac14.loader import load_blueprint_dir
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"
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


def test_generated_components_pass_packet_tests(tmp_path: Path) -> None:
    """Generated components should pass all packet-local fixtures."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)
    generated_package = emit_generated_package(packet_bundle, tmp_path / "generated")

    report = run_generated_packet_tests(packet_bundle, generated_package)
    assert report.passed, report.results


def test_generated_components_pass_recomposition_proof(tmp_path: Path) -> None:
    """Generated components should satisfy the shipped recomposition scenarios."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)
    generated_package = emit_generated_package(packet_bundle, tmp_path / "generated")

    report = run_generated_recomposition_proof(EXAMPLE_DIR, generated_package)
    assert report.passed is True
    assert report.runnable_scenario_count == 2
    assert len(report.skipped_scenarios) == 1
    assert report.skipped_scenarios[0].scenario_id == "schema_mismatch_rejected"


def test_run_fresh_generation_trials_writes_summary_artifact(tmp_path: Path) -> None:
    """Repeated fresh runs should produce a persisted summary artifact."""

    summary = run_fresh_generation_trials(
        blueprint_dir=EXAMPLE_DIR,
        trial_count=3,
        output_dir=tmp_path / "fresh_runs",
    )

    summary_path = tmp_path / "fresh_runs" / "fresh_run_summary.json"
    assert summary.passed_trials == 3
    assert summary.failed_trials == 0
    assert summary_path.exists()
    persisted = json.loads(summary_path.read_text())
    assert persisted["trial_count"] == 3


def test_packet_case_semantic_eval_handles_datetime_fixture_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Packet semantic-eval prompt inputs should be JSON-safe for datetime-bearing fixtures."""

    blueprint = load_blueprint_dir(BENCHMARK_BLUEPRINT_DIR)
    packet_bundle = compile_packets(blueprint)
    packet_cases = materialize_packet_test_cases(packet_bundle)
    case = packet_cases["case_parser"][0]
    calls = 0

    def _fake_render_prompt(prompt_path: Path, **kwargs: Any) -> list[dict[str, str]]:
        nonlocal calls
        calls += 1
        assert _contains_datetime(kwargs["inputs"]) is False
        assert _contains_datetime(kwargs["expected_outputs"]) is False
        assert _contains_datetime(kwargs["actual_outputs"]) is False
        return [{"role": "user", "content": "ok"}]

    async def _fake_acall_llm_structured(*args: Any, **kwargs: Any) -> tuple[PacketCaseSemanticEval, object]:
        return PacketCaseSemanticEval(semantic_fields_acceptable=True, concerns=[]), object()

    monkeypatch.setattr("ac14.acceptance.render_prompt", _fake_render_prompt)
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", _fake_acall_llm_structured)

    result = asyncio.run(
        _aevaluate_packet_case_semantically(
            component_id="case_parser",
            fixture_description=case.description,
            inputs=case.inputs,
            expected_outputs=case.expected_outputs,
            actual_outputs=case.expected_outputs,
            model="test-model",
            trace_id="test/packet_datetime",
        )
    )

    assert result.semantic_fields_acceptable is True
    assert calls == 1

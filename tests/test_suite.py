"""Tests for suite-level proof and comparison workflows."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ac14.suite import build_suite_comparison_report, build_suite_proof_report


EXAMPLES_ROOT = Path(__file__).resolve().parents[1] / "examples"


def test_build_suite_proof_report_for_deterministic_generator(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Suite proof should execute across all shipped examples."""

    fixture_path = tmp_path / "acceptance_review_fixture.json"
    fixture_path.write_text(
        """
{
  "overall_verdict": "accept",
  "summary": "Fixture-backed suite acceptance review approved the outputs.",
  "concerns": [],
  "requirement_assessments": []
}
""".strip()
    )
    monkeypatch.setenv("AC14_ACCEPTANCE_REVIEW_FIXTURE", str(fixture_path))

    report = build_suite_proof_report(
        output_dir=tmp_path / "suite_proof",
        examples_root=EXAMPLES_ROOT,
        fresh_run_trials=1,
        generator_kind="deterministic",
    )

    report_path = tmp_path / "suite_proof" / "suite_proof_report.json"
    assert report_path.exists()
    assert report.example_count >= 2
    assert report.passed_examples == report.example_count
    assert report.failed_examples == 0
    assert report.realistic_input_gate_included_examples == report.example_count
    assert report.realistic_input_gate_missing_examples == 0


def test_build_suite_comparison_report_for_deterministic_generator(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Suite comparison should aggregate deterministic runs across shipped examples."""

    fixture_path = tmp_path / "acceptance_review_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Fixture-backed suite comparison review approved the outputs.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    monkeypatch.setenv("AC14_ACCEPTANCE_REVIEW_FIXTURE", str(fixture_path))

    report = build_suite_comparison_report(
        output_dir=tmp_path / "suite_compare",
        examples_root=EXAMPLES_ROOT,
        generator_kinds=["deterministic"],
        fresh_run_trials=1,
    )

    report_path = tmp_path / "suite_compare" / "suite_comparison_report.json"
    assert report_path.exists()
    assert report.example_count >= 2
    assert len(report.generator_aggregates) == 1
    aggregate = report.generator_aggregates[0]
    assert aggregate.generator_kind == "deterministic"
    assert aggregate.passed_examples == report.example_count
    assert aggregate.failed_examples == 0
    assert aggregate.total_runnable_scenarios >= 4

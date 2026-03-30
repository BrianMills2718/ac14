"""Tests for semantic comparison artifacts."""

from __future__ import annotations

from pathlib import Path

from ac14.semantic_comparison import build_semantic_comparison_report
from ac14.semantic_suite import build_suite_semantic_comparison_report


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "examples" / "support_ticket_digest" / "blueprint"
EXAMPLES_ROOT = REPO_ROOT / "examples"


def test_build_semantic_comparison_report_for_reference_and_deterministic(
    tmp_path: Path,
) -> None:
    """Semantic comparison should show deterministic parity on the shipped example."""

    report = build_semantic_comparison_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "semantic",
        modes=["reference", "deterministic"],
    )

    report_path = tmp_path / "semantic" / "semantic_comparison_report.json"
    assert report_path.exists()
    assert report.runnable_scenario_count == 2

    deterministic = next(mode for mode in report.modes if mode.mode == "deterministic")
    assert deterministic.failed_expected_scenarios == 0
    assert deterministic.failed_reference_scenarios == 0


def test_build_suite_semantic_comparison_report_for_reference_and_deterministic(
    tmp_path: Path,
) -> None:
    """Suite semantic comparison should aggregate deterministic parity across shipped examples."""

    report = build_suite_semantic_comparison_report(
        output_dir=tmp_path / "suite_semantic",
        examples_root=EXAMPLES_ROOT,
        modes=["reference", "deterministic"],
    )

    report_path = tmp_path / "suite_semantic" / "suite_semantic_comparison_report.json"
    assert report_path.exists()
    assert report.example_count >= 2
    deterministic = next(mode for mode in report.mode_aggregates if mode.mode == "deterministic")
    assert deterministic.failing_expected_examples == 0
    assert deterministic.failing_reference_examples == 0

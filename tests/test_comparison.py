"""Tests for persisted generator comparison artifacts."""

from __future__ import annotations

from pathlib import Path

from ac14.comparison import build_generator_comparison_report


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def test_build_generator_comparison_report_for_deterministic_mode(tmp_path: Path) -> None:
    """Comparison artifact should persist generator summaries to disk."""

    report = build_generator_comparison_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "comparison",
        generator_kinds=["deterministic"],
        fresh_run_trials=2,
    )

    report_path = tmp_path / "comparison" / "comparison_report.json"
    assert report_path.exists()
    assert len(report.runs) == 1
    run = report.runs[0]
    assert run.generator_kind == "deterministic"
    assert run.packet_tests_passed is True
    assert run.recomposition_passed is True
    assert run.recomposition_runnable_scenarios == 2
    assert run.recomposition_skipped_scenarios == 1
    assert run.fresh_run_passed_trials == 2
    assert "ticket_parser" in run.module_hashes

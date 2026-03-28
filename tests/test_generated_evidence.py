"""Tests for generated packet tests, recomposition, and repeated fresh runs."""

from __future__ import annotations

import json
from pathlib import Path

from ac14.generated_codegen import emit_generated_package
from ac14.generated_evidence import (
    run_fresh_generation_trials,
    run_generated_packet_tests,
    run_generated_recomposition_proof,
)
from ac14.loader import load_blueprint_dir
from ac14.packets import compile_packets


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


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

    assert run_generated_recomposition_proof(EXAMPLE_DIR, generated_package)


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

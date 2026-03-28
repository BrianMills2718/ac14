"""Tests for persisted AC14 proof bundles."""

from __future__ import annotations

import json
from pathlib import Path

from ac14.evidence_bundle import build_evidence_bundle


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def test_build_evidence_bundle_writes_expected_artifacts(tmp_path: Path) -> None:
    """Evidence bundle should persist the core reports for a proof run."""

    manifest = build_evidence_bundle(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "bundle",
        fresh_run_trials=2,
    )

    manifest_path = tmp_path / "bundle" / "manifest.json"
    packet_summary_path = tmp_path / "bundle" / "packet_bundle_summary.json"
    generated_manifest_path = tmp_path / "bundle" / "generated_package_manifest.json"
    packet_test_report_path = tmp_path / "bundle" / "packet_test_report.json"
    recomposition_report_path = tmp_path / "bundle" / "recomposition_report.json"
    fresh_run_summary_path = tmp_path / "bundle" / "fresh_run_summary.json"

    assert manifest.packet_component_count == 5
    assert manifest_path.exists()
    assert packet_summary_path.exists()
    assert generated_manifest_path.exists()
    assert packet_test_report_path.exists()
    assert recomposition_report_path.exists()
    assert fresh_run_summary_path.exists()

    packet_test_report = json.loads(packet_test_report_path.read_text())
    recomposition_report = json.loads(recomposition_report_path.read_text())
    fresh_run_summary = json.loads(fresh_run_summary_path.read_text())

    assert packet_test_report["passed"] is True
    assert recomposition_report["passed"] is True
    assert fresh_run_summary["passed_trials"] == 2

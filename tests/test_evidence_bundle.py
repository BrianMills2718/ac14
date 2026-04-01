"""Tests for persisted AC14 proof bundles."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from ac14.evidence_bundle import build_evidence_bundle


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def _write_acceptance_review_fixture(tmp_path: Path) -> Path:
    """Persist one deterministic acceptance-review response for proof-bundle tests."""

    fixture_path = tmp_path / "acceptance_review_fixture.json"
    fixture_path.write_text(
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
    return fixture_path


def test_build_evidence_bundle_writes_expected_artifacts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Evidence bundle should persist the core reports for a proof run."""

    monkeypatch.setenv(
        "AC14_ACCEPTANCE_REVIEW_FIXTURE",
        str(_write_acceptance_review_fixture(tmp_path)),
    )
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
    realistic_input_gate_path = tmp_path / "bundle" / "realistic_input_gate.json"

    assert manifest.packet_component_count == 5
    assert manifest_path.exists()
    assert packet_summary_path.exists()
    assert generated_manifest_path.exists()
    assert packet_test_report_path.exists()
    assert recomposition_report_path.exists()
    assert fresh_run_summary_path.exists()
    assert realistic_input_gate_path.exists()

    packet_test_report = json.loads(packet_test_report_path.read_text())
    recomposition_report = json.loads(recomposition_report_path.read_text())
    fresh_run_summary = json.loads(fresh_run_summary_path.read_text())
    realistic_input_gate = json.loads(realistic_input_gate_path.read_text())

    assert packet_test_report["passed"] is True
    assert recomposition_report["passed"] is True
    assert fresh_run_summary["passed_trials"] == 2
    assert realistic_input_gate["status"] == "included"


def test_build_evidence_bundle_marks_missing_realistic_input_explicitly(
    tmp_path: Path,
) -> None:
    """Evidence bundle should persist an explicit missing realistic-input gate status."""

    blueprint_root = tmp_path / "copied_example"
    shutil.copytree(EXAMPLE_DIR, blueprint_root / "blueprint")

    manifest = build_evidence_bundle(
        blueprint_dir=blueprint_root / "blueprint",
        output_dir=tmp_path / "bundle_missing_realistic",
        fresh_run_trials=1,
    )

    realistic_input_gate_path = tmp_path / "bundle_missing_realistic" / "realistic_input_gate.json"
    realistic_input_gate = json.loads(realistic_input_gate_path.read_text())

    assert Path(manifest.realistic_input_gate_path).exists()
    assert realistic_input_gate["status"] == "missing"

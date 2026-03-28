"""Evidence bundle creation for AC14 proof runs."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from ac14.generated_codegen import emit_generated_package
from ac14.generated_evidence import (
    run_fresh_generation_trials,
    run_generated_packet_tests,
    run_generated_recomposition_proof,
)
from ac14.loader import load_blueprint_dir
from ac14.models import PacketBundle
from ac14.packets import compile_packets


class EvidenceBundleManifest(BaseModel):
    """Manifest describing the persisted proof bundle contents."""

    blueprint_dir: str = Field(description="Blueprint directory used for the proof run.")
    packet_component_count: int = Field(description="Number of compiled component packets.")
    generated_package_dir: str = Field(description="Directory containing emitted generated modules.")
    packet_test_report_path: str = Field(description="JSON file path for packet-test results.")
    recomposition_report_path: str = Field(description="JSON file path for recomposition results.")
    fresh_run_summary_path: str = Field(description="JSON file path for fresh-run summary.")


class RecompositionReport(BaseModel):
    """Stored result for generated recomposition proof."""

    passed: bool = Field(description="Whether all shipped recomposition scenarios passed.")


def build_evidence_bundle(
    blueprint_dir: Path | str,
    output_dir: Path | str,
    fresh_run_trials: int = 3,
) -> EvidenceBundleManifest:
    """Build and persist a complete proof bundle for the shipped example."""

    blueprint_path = Path(blueprint_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    blueprint = load_blueprint_dir(blueprint_path)
    packet_bundle = compile_packets(blueprint)

    generated_dir = destination / "generated"
    generated_package = emit_generated_package(packet_bundle, generated_dir)
    packet_test_report = run_generated_packet_tests(packet_bundle, generated_package)
    recomposition_report = RecompositionReport(
        passed=run_generated_recomposition_proof(blueprint_path, generated_package),
    )
    fresh_run_summary = run_fresh_generation_trials(
        blueprint_dir=blueprint_path,
        trial_count=fresh_run_trials,
        output_dir=destination / "fresh_runs",
    )

    _write_json(destination / "packet_bundle_summary.json", _packet_bundle_summary(packet_bundle))
    _write_json(
        destination / "generated_package_manifest.json",
        generated_package.model_dump(mode="json"),
    )
    _write_json(destination / "packet_test_report.json", packet_test_report.model_dump(mode="json"))
    _write_json(
        destination / "recomposition_report.json",
        recomposition_report.model_dump(mode="json"),
    )
    _write_json(
        destination / "fresh_run_summary.json",
        fresh_run_summary.model_dump(mode="json"),
    )

    manifest = EvidenceBundleManifest(
        blueprint_dir=str(blueprint_path),
        packet_component_count=len(packet_bundle.packets),
        generated_package_dir=str(generated_dir),
        packet_test_report_path=str(destination / "packet_test_report.json"),
        recomposition_report_path=str(destination / "recomposition_report.json"),
        fresh_run_summary_path=str(destination / "fresh_run_summary.json"),
    )
    _write_json(destination / "manifest.json", manifest.model_dump(mode="json"))
    return manifest


def _packet_bundle_summary(packet_bundle: PacketBundle) -> dict[str, object]:
    """Summarize packet counts and recomposition order for persisted evidence."""

    return {
        "component_ids": list(packet_bundle.packets.keys()),
        "execution_order": list(packet_bundle.recomposition_plan.execution_order),
        "state_store_owners": dict(packet_bundle.recomposition_plan.state_store_owners),
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    """Write one JSON artifact with stable formatting."""

    path.write_text(json.dumps(payload, indent=2, sort_keys=True))

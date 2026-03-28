"""Comparison reports across deterministic and LLM-backed generation modes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, Field

from ac14.evidence_bundle import build_evidence_bundle
from ac14.generated_codegen import GeneratorKind


class GeneratorRunSummary(BaseModel):
    """Summary of one generator mode in a comparison run."""

    generator_kind: GeneratorKind = Field(description="Generator mode for this run.")
    bundle_dir: str = Field(description="Directory containing the persisted evidence bundle.")
    packet_tests_passed: bool = Field(description="Whether packet-local tests passed.")
    recomposition_passed: bool = Field(description="Whether generated recomposition passed.")
    fresh_run_passed_trials: int = Field(description="Number of passing fresh-run trials.")
    fresh_run_failed_trials: int = Field(description="Number of failing fresh-run trials.")
    module_hashes: dict[str, str] = Field(description="SHA256 hashes keyed by component id.")


class GeneratorComparisonReport(BaseModel):
    """Persisted comparison artifact across generator modes."""

    blueprint_dir: str = Field(description="Blueprint directory used for comparison.")
    runs: list[GeneratorRunSummary] = Field(description="Per-generator run summaries.")


def build_generator_comparison_report(
    blueprint_dir: Path | str,
    output_dir: Path | str,
    *,
    generator_kinds: list[GeneratorKind],
    llm_model: str = "gemini/gemini-2.5-flash-lite",
    llm_max_budget: float = 0.50,
    fresh_run_trials: int = 2,
) -> GeneratorComparisonReport:
    """Build a persisted comparison report across one or more generator modes."""

    blueprint_path = Path(blueprint_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    runs: list[GeneratorRunSummary] = []
    for generator_kind in generator_kinds:
        bundle_dir = destination / generator_kind
        manifest = build_evidence_bundle(
            blueprint_dir=blueprint_path,
            output_dir=bundle_dir,
            fresh_run_trials=fresh_run_trials,
            generator_kind=generator_kind,
            llm_model=llm_model,
            llm_max_budget=llm_max_budget,
        )
        packet_test_report = json.loads(Path(manifest.packet_test_report_path).read_text())
        recomposition_report = json.loads(Path(manifest.recomposition_report_path).read_text())
        fresh_run_summary = json.loads(Path(manifest.fresh_run_summary_path).read_text())
        generated_package_manifest = json.loads(
            (bundle_dir / "generated_package_manifest.json").read_text(),
        )
        runs.append(
            GeneratorRunSummary(
                generator_kind=generator_kind,
                bundle_dir=str(bundle_dir),
                packet_tests_passed=packet_test_report["passed"],
                recomposition_passed=recomposition_report["passed"],
                fresh_run_passed_trials=fresh_run_summary["passed_trials"],
                fresh_run_failed_trials=fresh_run_summary["failed_trials"],
                module_hashes=_module_hashes(generated_package_manifest["module_paths"]),
            ),
        )

    report = GeneratorComparisonReport(
        blueprint_dir=str(blueprint_path),
        runs=runs,
    )
    (destination / "comparison_report.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return report


def _module_hashes(module_paths: dict[str, str]) -> dict[str, str]:
    """Compute content hashes for generated modules."""

    hashes: dict[str, str] = {}
    for component_id, module_path in module_paths.items():
        digest = hashlib.sha256(Path(module_path).read_bytes()).hexdigest()
        hashes[component_id] = digest
    return hashes

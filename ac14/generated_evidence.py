"""Execution helpers for generated components and repeated fresh-run evidence."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from ac14.generated_codegen import (
    GeneratedPackage,
    GeneratorKind,
    emit_generated_package,
    load_generated_component_builders,
)
from ac14.loader import load_blueprint_dir
from ac14.models import PacketBundle
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets
from ac14.recomposition import RecompositionReport, run_recomposition_proof


class PacketCaseResult(BaseModel):
    """Result of one packet-local generated component test case."""

    component_id: str = Field(description="Component under test.")
    fixture_id: str = Field(description="Fixture identifier.")
    passed: bool = Field(description="Whether the case passed.")
    error: str | None = Field(default=None, description="Failure message when the case fails.")


class PacketTestReport(BaseModel):
    """Aggregated results for all packet-local generated component tests."""

    passed: bool = Field(description="Whether all packet-local cases passed.")
    results: list[PacketCaseResult] = Field(description="Per-case results.")


class FreshRunTrial(BaseModel):
    """Outcome for one fresh generation and verification run."""

    trial_id: int = Field(description="Sequential trial identifier.")
    package_dir: str = Field(description="Directory containing emitted modules for the trial.")
    packet_tests_passed: bool = Field(description="Whether packet-local tests passed.")
    recomposition_passed: bool = Field(description="Whether recomposition scenarios passed.")


class FreshRunSummary(BaseModel):
    """Summary artifact for repeated fresh generation trials."""

    trial_count: int = Field(description="Number of executed trials.")
    passed_trials: int = Field(description="Number of trials with all checks passing.")
    failed_trials: int = Field(description="Number of failed trials.")
    trials: list[FreshRunTrial] = Field(description="Per-trial outcomes.")


def run_generated_packet_tests(
    packet_bundle: PacketBundle,
    generated_package: GeneratedPackage,
) -> PacketTestReport:
    """Run packet-local fixtures against generated components."""

    packet_cases = materialize_packet_test_cases(packet_bundle)
    builders = load_generated_component_builders(generated_package)
    results: list[PacketCaseResult] = []

    for component_id, cases in packet_cases.items():
        for case in cases:
            component = builders[component_id]()
            error: str | None
            try:
                outputs = component.execute(case.inputs)
                if _expects_failure(case.scenario_id):
                    passed = False
                    error = "negative case unexpectedly succeeded"
                else:
                    passed = outputs == case.expected_outputs
                    error = None if passed else "generated outputs did not match expected outputs"
            except Exception as exc:  # pragma: no cover - explicit failure capture
                if _expects_failure(case.scenario_id):
                    passed = True
                    error = None
                else:
                    passed = False
                    error = str(exc)
            results.append(
                PacketCaseResult(
                    component_id=component_id,
                    fixture_id=case.fixture_id,
                    passed=passed,
                    error=error,
                ),
            )

    return PacketTestReport(
        passed=all(result.passed for result in results),
        results=results,
    )


def run_generated_recomposition_proof(
    blueprint_dir: Path | str,
    generated_package: GeneratedPackage,
) -> RecompositionReport:
    """Run blueprint-driven recomposition scenarios against generated components."""

    blueprint = load_blueprint_dir(blueprint_dir)
    builders = load_generated_component_builders(generated_package)
    return run_recomposition_proof(blueprint, builders)


def run_fresh_generation_trials(
    blueprint_dir: Path | str,
    trial_count: int,
    output_dir: Path | str,
    *,
    generator_kind: GeneratorKind = "deterministic",
    llm_model: str = "gemini/gemini-2.5-flash-lite",
    llm_max_budget: float = 0.50,
) -> FreshRunSummary:
    """Run repeated fresh generation trials and write a summary artifact."""

    blueprint = load_blueprint_dir(blueprint_dir)
    packet_bundle = compile_packets(blueprint)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    trials: list[FreshRunTrial] = []
    for trial_id in range(1, trial_count + 1):
        package_dir = destination / f"trial_{trial_id}"
        generated_package = emit_generated_package(
            packet_bundle,
            package_dir,
            generator_kind=generator_kind,
            llm_model=llm_model,
            llm_max_budget=llm_max_budget,
            trace_id_prefix=f"ac14/fresh_run_trial_{trial_id}",
        )
        packet_report = run_generated_packet_tests(packet_bundle, generated_package)
        recomposition_report = run_generated_recomposition_proof(blueprint_dir, generated_package)
        trials.append(
            FreshRunTrial(
                trial_id=trial_id,
                package_dir=str(package_dir),
                packet_tests_passed=packet_report.passed,
                recomposition_passed=recomposition_report.passed,
            ),
        )

    summary = FreshRunSummary(
        trial_count=trial_count,
        passed_trials=sum(
            1 for trial in trials if trial.packet_tests_passed and trial.recomposition_passed
        ),
        failed_trials=sum(
            1 for trial in trials if not (trial.packet_tests_passed and trial.recomposition_passed)
        ),
        trials=trials,
    )
    (destination / "fresh_run_summary.json").write_text(
        json.dumps(summary.model_dump(mode="json"), indent=2),
    )
    return summary


def _expects_failure(scenario_id: str) -> bool:
    """Return true for negative packet-test scenarios that should fail loudly."""

    return scenario_id.endswith("_rejected")

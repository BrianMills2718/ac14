"""Tests for persisted dependency execution-probe artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from ac14.dependency_execution import build_dependency_execution_artifact
from ac14.dependency_planning import (
    DependencyEvidence,
    DependencyPlanningArtifact,
    DependencyQuestion,
    DependencyRecommendation,
)


def _write_dependency_plan(path: Path) -> Path:
    """Persist a deterministic dependency-planning artifact for probe tests."""

    artifact = DependencyPlanningArtifact(
        discovery_artifact_path=str(path.parent / "discovery_artifact.json"),
        requirements=["preserve typed schema contracts"],
        carried_forward_concerns=["dependency ac14-missing-lib is not installed in the current environment"],
        planning_summary="Reuse pydantic, block install by default, and keep open questions explicit.",
        recommendations=[
            DependencyRecommendation(
                package_name="pydantic",
                action="reuse",
                capability_need="Typed schema contracts for blueprint models.",
                justification="Already installed and directly used throughout AC14.",
                already_installed=True,
                install_command=None,
                evidence=[
                    DependencyEvidence(
                        source="environment",
                        locator="pydantic",
                        detail="pydantic is already installed in the current environment.",
                    ),
                ],
            ),
            DependencyRecommendation(
                package_name="ac14-missing-lib",
                action="install",
                capability_need="Demonstrate explicit install probing for missing packages.",
                justification="The package is missing and needs an explicit install recommendation.",
                already_installed=False,
                install_command="pip install ac14-missing-lib",
                evidence=[
                    DependencyEvidence(
                        source="environment",
                        locator="ac14-missing-lib",
                        detail="The package is not installed.",
                    ),
                ],
            ),
            DependencyRecommendation(
                package_name="rich",
                action="investigate",
                capability_need="Investigate richer terminal formatting later.",
                justification="Formatting is not yet required in the proof slice.",
                already_installed=False,
                install_command=None,
                evidence=[
                    DependencyEvidence(
                        source="requirement",
                        locator="operator output",
                        detail="The current proof slice does not require richer terminal formatting.",
                    ),
                ],
            ),
        ],
        standard_library_notes=["Prefer json and pathlib unless richer output is proven necessary."],
        open_questions=[
            DependencyQuestion(
                question="Should install probes eventually support review-only dry runs?",
                why_it_matters="It affects how much environment mutation the default lane should allow.",
            ),
        ],
    )
    path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))
    return path


def test_probe_artifact_persists_reviewable_state(tmp_path: Path) -> None:
    """Dependency execution should persist explicit reviewable probe results."""

    plan_path = _write_dependency_plan(tmp_path / "dependency_plan.json")

    artifact = build_dependency_execution_artifact(
        dependency_plan_path=plan_path,
        output_dir=tmp_path / "dependency_probe",
        allow_install=False,
    )

    result_lookup = {result.package_name: result for result in artifact.results}
    assert artifact.execution_mode == "check_only"
    assert result_lookup["pydantic"].result == "confirmed"
    assert result_lookup["ac14-missing-lib"].result == "blocked"
    assert result_lookup["ac14-missing-lib"].mutation_attempted is False
    assert result_lookup["rich"].result == "skipped"
    assert artifact.carried_forward_questions == [
        "Should install probes eventually support review-only dry runs?",
    ]
    assert (tmp_path / "dependency_probe" / "dependency_execution_artifact.json").exists()


def test_probe_failure_is_fail_loud(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Install probe failures should be explicit blocked results, not silent success."""

    plan_path = _write_dependency_plan(tmp_path / "dependency_plan.json")

    def _fake_run(*_args: object, **_kwargs: object) -> CompletedProcess[str]:
        return CompletedProcess(
            args=["python", "-m", "pip", "install", "ac14-missing-lib"],
            returncode=1,
            stdout="",
            stderr="No matching distribution found",
        )

    monkeypatch.setattr("ac14.dependency_execution.subprocess.run", _fake_run)

    artifact = build_dependency_execution_artifact(
        dependency_plan_path=plan_path,
        output_dir=tmp_path / "dependency_probe",
        allow_install=True,
    )

    failed_install = next(
        result for result in artifact.results if result.package_name == "ac14-missing-lib"
    )
    assert failed_install.result == "blocked"
    assert failed_install.mutation_attempted is True
    assert failed_install.command_exit_code == 1
    assert any("stderr:" in observation for observation in failed_install.observations)

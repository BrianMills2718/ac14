"""Reviewable dependency execution probes for approved planning recommendations."""

from __future__ import annotations

import importlib.util
import json
import shlex
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, distribution, version
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from ac14.dependency_planning import DependencyAction, DependencyPlanningArtifact


ProbeResult = Literal["confirmed", "blocked", "skipped"]
ExecutionMode = Literal["check_only", "allow_install"]


class DependencySnapshot(BaseModel):
    """Observed package state before or after one execution probe."""

    package_name: str = Field(description="Dependency package name being observed.")
    installed: bool = Field(description="Whether the distribution is installed.")
    version: str | None = Field(default=None, description="Installed version if present.")
    top_level_modules: list[str] = Field(
        default_factory=list,
        description="Top-level modules declared by the installed distribution when available.",
    )
    discoverable_modules: list[str] = Field(
        default_factory=list,
        description="Top-level modules discoverable via importlib without importing them.",
    )


class DependencyExecutionResult(BaseModel):
    """Persisted result for one dependency recommendation probe."""

    package_name: str = Field(description="Dependency package name under probe.")
    action: DependencyAction = Field(description="Planned dependency action being probed.")
    result: ProbeResult = Field(description="Explicit result state for the probe.")
    summary: str = Field(description="Compact reviewable explanation of the probe result.")
    mutation_permitted: bool = Field(
        description="Whether this execution run was allowed to mutate the environment.",
    )
    mutation_attempted: bool = Field(
        description="Whether the probe attempted an environment-changing command.",
    )
    attempted_command: str | None = Field(
        default=None,
        description="Resolved command actually attempted for install probes.",
    )
    command_exit_code: int | None = Field(
        default=None,
        description="Exit code for the attempted command when one ran.",
    )
    before: DependencySnapshot = Field(description="Observed state before probing.")
    after: DependencySnapshot = Field(description="Observed state after probing.")
    observations: list[str] = Field(
        default_factory=list,
        description="Compact observations that explain what the probe checked.",
    )


class DependencyExecutionArtifact(BaseModel):
    """Persisted artifact summarizing execution probes for one dependency plan."""

    dependency_plan_path: str = Field(
        description="Path to the dependency-planning artifact used as input.",
    )
    execution_mode: ExecutionMode = Field(
        description="Whether install actions were blocked or allowed to execute.",
    )
    planning_summary: str = Field(
        description="Planning summary carried forward from the dependency plan.",
    )
    carried_forward_questions: list[str] = Field(
        description="Open dependency questions carried forward from the dependency plan.",
    )
    results: list[DependencyExecutionResult] = Field(
        description="Explicit persisted results for each dependency recommendation probe.",
    )
    environment_observations: list[str] = Field(
        default_factory=list,
        description="Cross-cutting environment observations from this execution run.",
    )


class DependencyRemediationArtifact(BaseModel):
    """Persisted summary of one explicit dependency-remediation rerun."""

    prior_dependency_execution_artifact_path: str = Field(
        description="Previously persisted dependency execution artifact being remediated.",
    )
    remediated_dependency_execution_artifact_path: str = Field(
        description="Fresh dependency execution artifact produced by the remediation rerun.",
    )
    attempted_packages: list[str] = Field(
        description="Previously blocked install packages targeted by the remediation rerun.",
    )
    newly_confirmed_packages: list[str] = Field(
        description="Attempted packages that became confirmed after remediation.",
    )
    still_blocked_packages: list[str] = Field(
        description="Attempted packages that remained blocked after remediation.",
    )
    summary: str = Field(
        description="Compact reviewable summary of the remediation outcome.",
    )


def build_dependency_execution_artifact(
    dependency_plan_path: Path | str,
    output_dir: Path | str,
    *,
    allow_install: bool = False,
    python_executable: str = sys.executable,
    project_root: Path | None = None,
) -> DependencyExecutionArtifact:
    """Probe dependency recommendations and persist explicit execution results."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    artifact_path = Path(dependency_plan_path)
    dependency_plan = DependencyPlanningArtifact.model_validate_json(artifact_path.read_text())

    results = [
        _probe_recommendation(
            recommendation=recommendation,
            allow_install=allow_install,
            python_executable=python_executable,
            cwd=project_root,
        )
        for recommendation in dependency_plan.recommendations
    ]
    environment_observations = _build_environment_observations(results, allow_install=allow_install)
    artifact = DependencyExecutionArtifact(
        dependency_plan_path=str(artifact_path),
        execution_mode="allow_install" if allow_install else "check_only",
        planning_summary=dependency_plan.planning_summary,
        carried_forward_questions=[
            question.question for question in dependency_plan.open_questions
        ],
        results=results,
        environment_observations=environment_observations,
    )
    (destination / "dependency_execution_artifact.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def build_dependency_remediation_artifact(
    dependency_execution_artifact_path: Path | str,
    output_dir: Path | str,
    *,
    python_executable: str = sys.executable,
    project_root: Path | None = None,
) -> DependencyRemediationArtifact:
    """Rerun blocked install probes and persist a reviewable remediation delta."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    prior_path = Path(dependency_execution_artifact_path)
    prior_artifact = DependencyExecutionArtifact.model_validate_json(prior_path.read_text())
    attempted_packages = sorted(
        {
            result.package_name
            for result in prior_artifact.results
            if result.action == "install" and result.result == "blocked"
        },
    )

    rerun_output_dir = destination / "remediated_dependency_probe"
    remediated_artifact = build_dependency_execution_artifact(
        dependency_plan_path=prior_artifact.dependency_plan_path,
        output_dir=rerun_output_dir,
        allow_install=True,
        python_executable=python_executable,
        project_root=project_root,
    )
    result_lookup = {
        result.package_name: result
        for result in remediated_artifact.results
    }
    newly_confirmed_packages = [
        package_name
        for package_name in attempted_packages
        if result_lookup[package_name].result == "confirmed"
    ]
    still_blocked_packages = [
        package_name
        for package_name in attempted_packages
        if result_lookup[package_name].result == "blocked"
    ]
    if not attempted_packages:
        summary = "no blocked install probes required remediation"
    elif still_blocked_packages:
        summary = (
            f"remediation reran {len(attempted_packages)} blocked install probes; "
            f"{len(newly_confirmed_packages)} confirmed and {len(still_blocked_packages)} remained blocked"
        )
    else:
        summary = (
            f"remediation reran {len(attempted_packages)} blocked install probes and all became confirmed"
        )

    artifact = DependencyRemediationArtifact(
        prior_dependency_execution_artifact_path=str(prior_path),
        remediated_dependency_execution_artifact_path=str(
            rerun_output_dir / "dependency_execution_artifact.json",
        ),
        attempted_packages=attempted_packages,
        newly_confirmed_packages=newly_confirmed_packages,
        still_blocked_packages=still_blocked_packages,
        summary=summary,
    )
    (destination / "dependency_remediation_artifact.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def _probe_recommendation(
    *,
    recommendation: object,
    allow_install: bool,
    python_executable: str,
    cwd: Path | None,
) -> DependencyExecutionResult:
    """Probe one dependency recommendation and return an explicit result."""

    from ac14.dependency_planning import DependencyRecommendation  # local import for typing cycle safety

    typed_recommendation = (
        recommendation
        if isinstance(recommendation, DependencyRecommendation)
        else DependencyRecommendation.model_validate(recommendation)
    )
    before = _snapshot_distribution(typed_recommendation.package_name)
    observations: list[str] = []

    if typed_recommendation.action == "reuse":
        observations.append(
            f"checked installed distribution state for {typed_recommendation.package_name}",
        )
        after = _snapshot_distribution(typed_recommendation.package_name)
        if not before.installed:
            return DependencyExecutionResult(
                package_name=typed_recommendation.package_name,
                action=typed_recommendation.action,
                result="blocked",
                summary="reuse probe failed because the package is not installed",
                mutation_permitted=allow_install,
                mutation_attempted=False,
                before=before,
                after=after,
                observations=observations,
            )
        if before.top_level_modules and not before.discoverable_modules:
            observations.append(
                "distribution is installed but no declared top-level modules were discoverable",
            )
            return DependencyExecutionResult(
                package_name=typed_recommendation.package_name,
                action=typed_recommendation.action,
                result="blocked",
                summary="reuse probe failed because installed modules were not discoverable",
                mutation_permitted=allow_install,
                mutation_attempted=False,
                before=before,
                after=after,
                observations=observations,
            )
        observations.append("reuse probe confirmed installed package availability")
        return DependencyExecutionResult(
            package_name=typed_recommendation.package_name,
            action=typed_recommendation.action,
            result="confirmed",
            summary="reuse probe confirmed the package is already available",
            mutation_permitted=allow_install,
            mutation_attempted=False,
            before=before,
            after=after,
            observations=observations,
        )

    if typed_recommendation.action == "install":
        observations.append(
            f"install probe reviewed recommendation for {typed_recommendation.package_name}",
        )
        if typed_recommendation.install_command is None:
            raise ValueError(
                f"install probe for {typed_recommendation.package_name!r} is missing an install command",
            )
        if not allow_install:
            observations.append("install command was not executed because mutation is disabled")
            return DependencyExecutionResult(
                package_name=typed_recommendation.package_name,
                action=typed_recommendation.action,
                result="blocked",
                summary="install probe blocked because environment mutation is disabled",
                mutation_permitted=False,
                mutation_attempted=False,
                attempted_command=_render_command(
                    _normalize_install_command(typed_recommendation.install_command, python_executable),
                ),
                before=before,
                after=before,
                observations=observations,
            )

        command = _normalize_install_command(
            typed_recommendation.install_command,
            python_executable,
        )
        completed = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
        after = _snapshot_distribution(typed_recommendation.package_name)
        observations.extend(_summarize_command_output(completed))
        if completed.returncode == 0 and after.installed:
            observations.append("install probe confirmed package availability after execution")
            return DependencyExecutionResult(
                package_name=typed_recommendation.package_name,
                action=typed_recommendation.action,
                result="confirmed",
                summary="install probe confirmed the package became available",
                mutation_permitted=True,
                mutation_attempted=True,
                attempted_command=_render_command(command),
                command_exit_code=completed.returncode,
                before=before,
                after=after,
                observations=observations,
            )
        observations.append("install probe remained blocked after command execution")
        return DependencyExecutionResult(
            package_name=typed_recommendation.package_name,
            action=typed_recommendation.action,
            result="blocked",
            summary="install probe did not make the package available",
            mutation_permitted=True,
            mutation_attempted=True,
            attempted_command=_render_command(command),
            command_exit_code=completed.returncode,
            before=before,
            after=after,
            observations=observations,
        )

    summary = (
        "investigate recommendation requires follow-on review before execution"
        if typed_recommendation.action == "investigate"
        else "avoid recommendation intentionally skips execution probing"
    )
    observations.append(summary)
    return DependencyExecutionResult(
        package_name=typed_recommendation.package_name,
        action=typed_recommendation.action,
        result="skipped",
        summary=summary,
        mutation_permitted=allow_install,
        mutation_attempted=False,
        before=before,
        after=before,
        observations=observations,
    )


def _snapshot_distribution(package_name: str) -> DependencySnapshot:
    """Capture a compact distribution snapshot for one package name."""

    try:
        installed_version = version(package_name)
        dist = distribution(package_name)
    except PackageNotFoundError:
        return DependencySnapshot(
            package_name=package_name,
            installed=False,
            version=None,
            top_level_modules=[],
            discoverable_modules=[],
        )

    top_level_modules = [
        module.strip()
        for module in (dist.read_text("top_level.txt") or "").splitlines()
        if module.strip()
    ]
    discoverable_modules = [
        module
        for module in top_level_modules
        if importlib.util.find_spec(module) is not None
    ]
    return DependencySnapshot(
        package_name=package_name,
        installed=True,
        version=installed_version,
        top_level_modules=top_level_modules,
        discoverable_modules=discoverable_modules,
    )


def _normalize_install_command(install_command: str, python_executable: str) -> list[str]:
    """Normalize install commands so they run in the current Python environment."""

    argv = shlex.split(install_command)
    if not argv:
        raise ValueError("install command is empty")
    first = argv[0]
    if first == "pip":
        return [python_executable, "-m", "pip", *argv[1:]]
    if first in {"python", "python3"}:
        return [python_executable, *argv[1:]]
    return argv


def _render_command(argv: list[str]) -> str:
    """Render an argv list as a compact shell-style command string."""

    return " ".join(shlex.quote(part) for part in argv)


def _summarize_command_output(completed: subprocess.CompletedProcess[str]) -> list[str]:
    """Return compact observations from a completed subprocess."""

    observations = [f"command exit code: {completed.returncode}"]
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if stdout:
        observations.append(f"stdout: {stdout.splitlines()[0][:200]}")
    if stderr:
        observations.append(f"stderr: {stderr.splitlines()[0][:200]}")
    return observations


def _build_environment_observations(
    results: list[DependencyExecutionResult],
    *,
    allow_install: bool,
) -> list[str]:
    """Build cross-cutting environment observations from probe results."""

    blocked_count = sum(1 for result in results if result.result == "blocked")
    confirmed_count = sum(1 for result in results if result.result == "confirmed")
    skipped_count = sum(1 for result in results if result.result == "skipped")
    observations = [
        (
            "install mutation was permitted for this run"
            if allow_install
            else "install mutation was disabled for this run"
        ),
        f"confirmed results: {confirmed_count}",
        f"blocked results: {blocked_count}",
        f"skipped results: {skipped_count}",
    ]
    if blocked_count and not allow_install:
        observations.append(
            "one or more install recommendations remained blocked because mutation was disabled",
        )
    return observations

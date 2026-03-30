"""Pre-freeze discovery artifacts for local input inspection and dependency planning."""

from __future__ import annotations

import csv
import json
import platform
import re
import sys
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Literal

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field


InputFormat = Literal["json", "jsonl", "csv", "yaml", "text"]
RootKind = Literal["record", "record_stream", "list", "scalar", "text"]
DependencySource = Literal["project", "requested"]


class InferredFieldSummary(BaseModel):
    """Compact summary of one inferred field path observed during discovery."""

    path: str = Field(description="Field path using dotted object access and [] for list items.")
    observed_types: list[str] = Field(description="Observed value kinds for this field path.")
    present_count: int = Field(description="How many sampled records exposed this field path.")
    sample_values: list[str] = Field(description="Compact sample values for reviewer context.")


class InputInspection(BaseModel):
    """Persisted summary of a local input inspected before blueprint freeze."""

    input_path: str = Field(description="Local input path inspected during discovery.")
    input_format: InputFormat = Field(description="Detected input file format.")
    root_kind: RootKind = Field(description="Observed top-level structural kind.")
    sample_count: int = Field(description="Number of samples inspected.")
    truncated: bool = Field(description="Whether discovery truncated the inspected samples.")
    sample_records: list[object] = Field(description="Compact input samples for reviewer context.")
    field_summaries: list[InferredFieldSummary] = Field(
        description="Flattened field summaries inferred from the inspected samples.",
    )
    concerns: list[str] = Field(description="Discovery concerns raised from the inspected input.")


class DependencyStatus(BaseModel):
    """Observed installation state for one dependency relevant to discovery."""

    package_name: str = Field(description="Dependency package name.")
    sources: list[DependencySource] = Field(
        description="Why this package appears in discovery, such as project or requested.",
    )
    installed: bool = Field(description="Whether the package is installed in the current environment.")
    version: str | None = Field(default=None, description="Installed version when available.")


class EnvironmentInventory(BaseModel):
    """Persisted summary of environment capabilities relevant to discovery."""

    project_root: str | None = Field(
        default=None,
        description="Project root used to inspect baseline dependencies.",
    )
    python_version: str = Field(description="Python runtime version used for discovery.")
    platform: str = Field(description="Platform string for the current runtime.")
    dependency_statuses: list[DependencyStatus] = Field(
        description="Dependency installation status summaries.",
    )
    concerns: list[str] = Field(description="Environment or dependency concerns.")


class DiscoveryArtifact(BaseModel):
    """Persisted artifact combining local input inspection and environment planning."""

    input_inspection: InputInspection = Field(
        description="Input inspection results captured before blueprint freeze.",
    )
    environment_inventory: EnvironmentInventory = Field(
        description="Environment planning context captured for the same discovery run.",
    )
    open_concerns: list[str] = Field(
        description="Combined open concerns that should be resolved before blueprint freeze.",
    )


class _FieldAccumulator:
    """Mutable accumulator for one inferred field path during discovery."""

    def __init__(self) -> None:
        self.observed_types: set[str] = set()
        self.present_count = 0
        self.sample_values: list[str] = []

    def record(self, value: Any) -> None:
        """Update the accumulator with one observed field value."""

        self.present_count += 1
        self.observed_types.add(_type_label(value))
        rendered = _render_sample_value(value)
        if rendered not in self.sample_values and len(self.sample_values) < 3:
            self.sample_values.append(rendered)


def build_discovery_artifact(
    input_path: Path | str,
    output_dir: Path | str,
    *,
    project_root: Path | str | None = None,
    requested_packages: list[str] | None = None,
    max_samples: int = 5,
) -> DiscoveryArtifact:
    """Inspect a local input and persist a discovery artifact before blueprint freeze."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    inspection = inspect_input_path(input_path, max_samples=max_samples)
    environment = build_environment_inventory(
        project_root=project_root,
        requested_packages=requested_packages or [],
    )
    open_concerns = _dedupe_preserve_order(
        [*inspection.concerns, *environment.concerns],
    )
    artifact = DiscoveryArtifact(
        input_inspection=inspection,
        environment_inventory=environment,
        open_concerns=open_concerns,
    )
    (destination / "discovery_artifact.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def inspect_input_path(input_path: Path | str, *, max_samples: int = 5) -> InputInspection:
    """Inspect a local input file and infer a compact structural summary."""

    path = Path(input_path)
    input_format = _detect_input_format(path)
    root_value = _load_input(path, input_format)
    root_kind, sample_records, truncated = _extract_samples(root_value, input_format, max_samples)
    field_summaries = _infer_field_summaries(sample_records, root_kind)
    concerns = _build_input_concerns(
        root_kind=root_kind,
        sample_count=len(sample_records),
        field_summaries=field_summaries,
        truncated=truncated,
        max_samples=max_samples,
    )
    return InputInspection(
        input_path=str(path),
        input_format=input_format,
        root_kind=root_kind,
        sample_count=len(sample_records),
        truncated=truncated,
        sample_records=sample_records,
        field_summaries=field_summaries,
        concerns=concerns,
    )


def build_environment_inventory(
    *,
    project_root: Path | str | None = None,
    requested_packages: list[str] | None = None,
) -> EnvironmentInventory:
    """Inspect currently installed packages relevant to discovery and planning."""

    requested = requested_packages or []
    project_path = Path(project_root) if project_root is not None else None
    dependency_sources: dict[str, set[DependencySource]] = {}
    for package_name in _load_project_dependency_names(project_path):
        dependency_sources.setdefault(package_name, set()).add("project")
    for package_name in requested:
        dependency_sources.setdefault(package_name, set()).add("requested")

    statuses: list[DependencyStatus] = []
    concerns: list[str] = []
    for package_name in sorted(dependency_sources):
        installed_version = _installed_package_version(package_name)
        installed = installed_version is not None
        statuses.append(
            DependencyStatus(
                package_name=package_name,
                sources=sorted(dependency_sources[package_name]),
                installed=installed,
                version=installed_version,
            ),
        )
        if not installed:
            concerns.append(
                f"dependency {package_name} is not installed in the current environment"
            )

    return EnvironmentInventory(
        project_root=str(project_path) if project_path is not None else None,
        python_version=sys.version.split()[0],
        platform=platform.platform(),
        dependency_statuses=statuses,
        concerns=concerns,
    )


def persist_environment_inventory(
    output_dir: Path | str,
    *,
    project_root: Path | str | None = None,
    requested_packages: list[str] | None = None,
) -> EnvironmentInventory:
    """Persist the environment inventory used during discovery planning."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    inventory = build_environment_inventory(
        project_root=project_root,
        requested_packages=requested_packages or [],
    )
    (destination / "environment_inventory.json").write_text(
        json.dumps(inventory.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return inventory


def _detect_input_format(path: Path) -> InputFormat:
    """Detect the supported input format from the file suffix."""

    suffix = path.suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".jsonl":
        return "jsonl"
    if suffix == ".csv":
        return "csv"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    return "text"


def _load_input(path: Path, input_format: InputFormat) -> object:
    """Load a supported local input file."""

    if input_format == "json":
        return json.loads(path.read_text())
    if input_format == "jsonl":
        return [
            json.loads(line)
            for line in path.read_text().splitlines()
            if line.strip()
        ]
    if input_format == "csv":
        with path.open(newline="") as handle:
            return list(csv.DictReader(handle))
    if input_format == "yaml":
        return yaml.safe_load(path.read_text())
    return path.read_text().splitlines()


def _extract_samples(
    root_value: object,
    input_format: InputFormat,
    max_samples: int,
) -> tuple[RootKind, list[object], bool]:
    """Extract bounded samples and root-kind metadata from loaded input."""

    if input_format == "text":
        lines = list(root_value) if isinstance(root_value, list) else [root_value]
        return "text", lines[:max_samples], len(lines) > max_samples

    if isinstance(root_value, dict):
        return "record", [root_value], False
    if isinstance(root_value, list):
        truncated = len(root_value) > max_samples
        samples = root_value[:max_samples]
        if all(isinstance(item, dict) for item in samples):
            return "record_stream", samples, truncated
        return "list", samples, truncated
    return "scalar", [root_value], False


def _infer_field_summaries(
    sample_records: list[object],
    root_kind: RootKind,
) -> list[InferredFieldSummary]:
    """Infer flattened field summaries from sampled structured inputs."""

    if root_kind in {"scalar", "text"}:
        return []

    accumulators: dict[str, _FieldAccumulator] = {}
    for sample in sample_records:
        if isinstance(sample, dict):
            _observe_mapping(sample, accumulators, prefix="")
        elif isinstance(sample, list):
            _observe_sequence(sample, accumulators, prefix="")
        else:
            _observe_value(sample, accumulators, prefix="")

    return [
        InferredFieldSummary(
            path=path,
            observed_types=sorted(accumulator.observed_types),
            present_count=accumulator.present_count,
            sample_values=accumulator.sample_values,
        )
        for path, accumulator in sorted(accumulators.items())
    ]


def _observe_mapping(
    mapping: dict[str, Any],
    accumulators: dict[str, _FieldAccumulator],
    *,
    prefix: str,
) -> None:
    """Record observations for one mapping sample."""

    for key, value in mapping.items():
        path = f"{prefix}.{key}" if prefix else key
        _observe_value(value, accumulators, prefix=path)


def _observe_sequence(
    sequence: list[Any],
    accumulators: dict[str, _FieldAccumulator],
    *,
    prefix: str,
) -> None:
    """Record observations for one sequence sample."""

    list_path = f"{prefix}[]" if prefix else "[]"
    for item in sequence[:3]:
        _observe_value(item, accumulators, prefix=list_path)


def _observe_value(
    value: Any,
    accumulators: dict[str, _FieldAccumulator],
    *,
    prefix: str,
) -> None:
    """Record one value and recurse into nested structured content."""

    if prefix:
        accumulator = accumulators.setdefault(prefix, _FieldAccumulator())
        accumulator.record(value)
    if isinstance(value, dict):
        _observe_mapping(value, accumulators, prefix=prefix)
    elif isinstance(value, list):
        _observe_sequence(value, accumulators, prefix=prefix)


def _build_input_concerns(
    *,
    root_kind: RootKind,
    sample_count: int,
    field_summaries: list[InferredFieldSummary],
    truncated: bool,
    max_samples: int,
) -> list[str]:
    """Build deterministic concerns from the inspected samples."""

    concerns: list[str] = []
    if truncated:
        concerns.append(f"discovery truncated input inspection to {max_samples} samples")
    if root_kind in {"scalar", "text"}:
        concerns.append("input does not expose structured record fields during discovery")
    if sample_count == 0:
        concerns.append("input contains no samples for discovery")
    if root_kind in {"record", "record_stream", "list"} and not field_summaries:
        concerns.append("no field structure was inferred from the inspected samples")
    for field_summary in field_summaries:
        if len(field_summary.observed_types) > 1:
            concerns.append(
                f"field {field_summary.path} has mixed observed types: "
                + ", ".join(field_summary.observed_types)
            )
        if sample_count > 1 and field_summary.present_count < sample_count:
            concerns.append(
                f"field {field_summary.path} is sparse across sampled inputs "
                f"({field_summary.present_count}/{sample_count})"
            )
    return _dedupe_preserve_order(concerns)


def _load_project_dependency_names(project_root: Path | None) -> list[str]:
    """Load baseline dependency names from a project ``pyproject.toml`` when present."""

    if project_root is None:
        return []
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        return []
    data = tomllib.loads(pyproject_path.read_text())
    dependency_specs = data.get("project", {}).get("dependencies", [])
    names: list[str] = []
    for dependency_spec in dependency_specs:
        match = re.match(r"^[A-Za-z0-9_.-]+", dependency_spec)
        if match is not None:
            names.append(match.group(0))
    return names


def _installed_package_version(package_name: str) -> str | None:
    """Return the installed package version, or ``None`` when unavailable."""

    try:
        return version(package_name)
    except PackageNotFoundError:
        return None


def _type_label(value: Any) -> str:
    """Return a compact value-kind label for discovery summaries."""

    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "list"
    return type(value).__name__


def _render_sample_value(value: Any) -> str:
    """Render a compact sample value suitable for persisted discovery context."""

    rendered = json.dumps(value, sort_keys=True, default=str)
    return rendered if len(rendered) <= 120 else rendered[:117] + "..."


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    """Deduplicate strings while preserving first-seen order."""

    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered

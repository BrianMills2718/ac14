"""Pre-freeze discovery artifacts for local input, docs, and dependency planning."""

from __future__ import annotations

import json
import platform
import re
import sys
import tomllib
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Literal
from pydantic import BaseModel, Field

from ac14.structured_inputs import InputFormat, detect_input_format, load_input
RootKind = Literal["record", "record_stream", "list", "scalar", "text"]
DependencySource = Literal["project", "requested"]
DocumentCategory = Literal["readme", "claude", "doc"]


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


class ProjectDocumentSummary(BaseModel):
    """Compact summary of one local project document relevant to blueprint planning."""

    path: str = Field(description="Path to the discovered local document.")
    category: DocumentCategory = Field(description="Document category inferred from its location.")
    title: str = Field(description="Best-effort document title for review.")
    preview: str = Field(description="Compact preview of the document contents.")
    line_count: int = Field(description="Line count for rough document size context.")


class ProjectContextInventory(BaseModel):
    """Persisted summary of local project documents relevant to blueprint planning."""

    project_root: str | None = Field(
        default=None,
        description="Project root used to inspect local planning documents.",
    )
    document_count: int = Field(description="Number of discovered local planning documents.")
    truncated: bool = Field(description="Whether discovery truncated the document inventory.")
    documents: list[ProjectDocumentSummary] = Field(
        description="Discovered local planning documents with compact summaries.",
    )
    concerns: list[str] = Field(description="Project-document concerns raised during discovery.")


class ExternalRetrievalSummary(BaseModel):
    """Compact summary of one persisted external retrieval artifact."""

    artifact_path: str = Field(description="Path to the external retrieval artifact.")
    web_document_count: int = Field(description="Number of retrieved web documents.")
    repo_match_count: int = Field(description="Number of retrieved repo matches.")
    web_urls: list[str] = Field(description="Top retrieved web URLs for reviewer context.")
    repo_paths: list[str] = Field(description="Top retrieved repo paths for reviewer context.")
    concerns: list[str] = Field(description="Concerns carried forward from the retrieval artifact.")


class DiscoveryArtifact(BaseModel):
    """Persisted artifact combining local input inspection and environment planning."""

    input_inspection: InputInspection = Field(
        description="Input inspection results captured before blueprint freeze.",
    )
    environment_inventory: EnvironmentInventory = Field(
        description="Environment planning context captured for the same discovery run.",
    )
    project_context_inventory: ProjectContextInventory = Field(
        description="Local project-document context captured for the same discovery run.",
    )
    external_retrieval_summaries: list[ExternalRetrievalSummary] = Field(
        default_factory=list,
        description="Reviewable summaries of external retrieval artifacts consumed during discovery.",
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
    retrieval_artifact_paths: Sequence[Path | str] | None = None,
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
    project_context = build_project_context_inventory(project_root=project_root)
    external_retrieval_summaries = _load_external_retrieval_summaries(
        retrieval_artifact_paths or [],
    )
    open_concerns = _dedupe_preserve_order(
        [
            *inspection.concerns,
            *environment.concerns,
            *project_context.concerns,
            *[
                concern
                for summary in external_retrieval_summaries
                for concern in summary.concerns
            ],
        ],
    )
    artifact = DiscoveryArtifact(
        input_inspection=inspection,
        environment_inventory=environment,
        project_context_inventory=project_context,
        external_retrieval_summaries=external_retrieval_summaries,
        open_concerns=open_concerns,
    )
    (destination / "discovery_artifact.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def inspect_input_path(input_path: Path | str, *, max_samples: int = 5) -> InputInspection:
    """Inspect a local input file and infer a compact structural summary."""

    path = Path(input_path)
    input_format = detect_input_format(path)
    root_value = load_input(path, input_format)
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


def build_project_context_inventory(
    *,
    project_root: Path | str | None = None,
    max_documents: int = 20,
) -> ProjectContextInventory:
    """Inspect local project documents relevant to blueprint planning."""

    project_path = Path(project_root) if project_root is not None else None
    if project_path is None:
        return ProjectContextInventory(
            project_root=None,
            document_count=0,
            truncated=False,
            documents=[],
            concerns=[],
        )

    candidate_paths = _candidate_project_document_paths(project_path)
    truncated = len(candidate_paths) > max_documents
    selected_paths = candidate_paths[:max_documents]
    documents = [
        _summarize_project_document(project_path, document_path)
        for document_path in selected_paths
    ]
    concerns: list[str] = []
    if not documents:
        concerns.append("project root exposes no README, CLAUDE, or docs markdown files")
    if truncated:
        concerns.append(
            f"project document inventory truncated to {max_documents} files during discovery"
        )
    return ProjectContextInventory(
        project_root=str(project_path),
        document_count=len(documents),
        truncated=truncated,
        documents=documents,
        concerns=concerns,
    )


def persist_project_context_inventory(
    output_dir: Path | str,
    *,
    project_root: Path | str | None = None,
    max_documents: int = 20,
) -> ProjectContextInventory:
    """Persist the local project-document inventory used during discovery."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    inventory = build_project_context_inventory(
        project_root=project_root,
        max_documents=max_documents,
    )
    (destination / "project_context_inventory.json").write_text(
        json.dumps(inventory.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return inventory


def _load_external_retrieval_summaries(
    artifact_paths: Sequence[Path | str],
) -> list[ExternalRetrievalSummary]:
    """Load compact summaries from persisted external retrieval artifacts."""

    if not artifact_paths:
        return []

    from ac14.retrieval import ExternalRetrievalArtifact

    summaries: list[ExternalRetrievalSummary] = []
    for artifact_path in artifact_paths:
        path = Path(artifact_path)
        artifact = ExternalRetrievalArtifact.model_validate_json(path.read_text())
        summaries.append(
            ExternalRetrievalSummary(
                artifact_path=str(path),
                web_document_count=len(artifact.web_documents),
                repo_match_count=len(artifact.repo_matches),
                web_urls=[document.url for document in artifact.web_documents[:3]],
                repo_paths=[
                    f"{match.repository}:{match.path}"
                    for match in artifact.repo_matches[:3]
                ],
                concerns=artifact.concerns,
            ),
        )
    return summaries


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


def _candidate_project_document_paths(project_root: Path) -> list[Path]:
    """Return local project documents that should seed pre-freeze context."""

    candidates: list[Path] = []
    for direct_name in ("README.md", "CLAUDE.md"):
        candidate = project_root / direct_name
        if candidate.exists():
            candidates.append(candidate)
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        candidates.extend(sorted(path for path in docs_dir.rglob("*.md") if path.is_file()))
    deduped: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(candidate)
    return deduped


def _summarize_project_document(project_root: Path, document_path: Path) -> ProjectDocumentSummary:
    """Build a compact summary for one local project document."""

    text = document_path.read_text(errors="ignore")
    lines = text.splitlines()
    title = _document_title(lines, fallback=document_path.stem.replace("_", " ").title())
    preview = _document_preview(lines)
    return ProjectDocumentSummary(
        path=str(document_path.relative_to(project_root)),
        category=_document_category(project_root, document_path),
        title=title,
        preview=preview,
        line_count=len(lines),
    )


def _document_category(project_root: Path, document_path: Path) -> DocumentCategory:
    """Infer a compact category for one project document."""

    if document_path == project_root / "README.md":
        return "readme"
    if document_path == project_root / "CLAUDE.md":
        return "claude"
    return "doc"


def _document_title(lines: list[str], *, fallback: str) -> str:
    """Extract a best-effort title from markdown lines."""

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def _document_preview(lines: list[str]) -> str:
    """Extract a compact preview from non-empty markdown lines."""

    preview_lines = [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]
    if not preview_lines:
        return ""
    preview = " ".join(preview_lines[:3])
    return preview if len(preview) <= 200 else preview[:197] + "..."


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

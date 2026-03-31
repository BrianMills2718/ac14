"""Tests for pre-freeze discovery artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from ac14.discovery import (
    build_discovery_artifact,
    build_environment_inventory,
    build_project_context_inventory,
    inspect_input_path,
    persist_environment_inventory,
    persist_project_context_inventory,
)
from ac14.retrieval import (
    RepoRetrievalQuery,
    RetrievedRepoMatch,
    RetrievedWebDocument,
    WebRetrievalQuery,
    build_external_retrieval_artifact,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_inspect_input_path_infers_field_summaries_and_concerns(tmp_path: Path) -> None:
    """Discovery should infer compact field summaries from structured local input."""

    input_path = tmp_path / "sample.json"
    input_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "name": "alpha",
                    "meta": {"active": True},
                    "tags": ["bug", "urgent"],
                },
                {
                    "id": "2",
                    "name": "beta",
                    "tags": [],
                },
            ],
        ),
    )

    inspection = inspect_input_path(input_path, max_samples=5)

    assert inspection.input_format == "json"
    assert inspection.root_kind == "record_stream"
    field_lookup = {field.path: field for field in inspection.field_summaries}
    assert field_lookup["id"].observed_types == ["int", "str"]
    assert field_lookup["tags"].observed_types == ["list"]
    assert field_lookup["meta.active"].observed_types == ["bool"]
    assert field_lookup["tags[]"].observed_types == ["str"]
    assert any("field id has mixed observed types" in concern for concern in inspection.concerns)
    assert any("field meta.active is sparse" in concern for concern in inspection.concerns)


def test_build_discovery_artifact_persists_environment_and_input(tmp_path: Path) -> None:
    """Discovery artifact should persist input, environment, and project-doc context."""

    input_path = tmp_path / "sample.csv"
    input_path.write_text("ticket_id,priority\n1,high\n2,low\n")

    artifact = build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
        requested_packages=["pydantic", "definitely-missing-package-ac14"],
        max_samples=5,
    )

    assert artifact.input_inspection.input_format == "csv"
    assert any(
        status.package_name == "pydantic" and status.installed
        for status in artifact.environment_inventory.dependency_statuses
    )
    assert any(
        status.package_name == "definitely-missing-package-ac14" and not status.installed
        for status in artifact.environment_inventory.dependency_statuses
    )
    assert any(
        "definitely-missing-package-ac14" in concern for concern in artifact.open_concerns
    )
    assert artifact.project_context_inventory.document_count >= 2
    document_paths = {document.path for document in artifact.project_context_inventory.documents}
    assert "README.md" in document_paths
    assert "CLAUDE.md" in document_paths
    assert (tmp_path / "discovery" / "discovery_artifact.json").exists()


def test_build_discovery_artifact_loads_external_retrieval_summaries(tmp_path: Path) -> None:
    """Discovery should summarize persisted external retrieval artifacts when provided."""

    input_path = tmp_path / "sample.csv"
    input_path.write_text("ticket_id,priority\n1,high\n")
    build_external_retrieval_artifact(
        output_dir=tmp_path / "retrieval",
        web_queries=[WebRetrievalQuery(query="incident response playbook")],
        repo_queries=[RepoRetrievalQuery(query="structured output helper")],
        web_retriever=lambda _query: [
            RetrievedWebDocument(
                query="incident response playbook",
                provider="fixture",
                url="https://example.com/playbook",
                title="Playbook",
                publisher="Example",
                snippet="playbook snippet",
                preview="playbook preview",
            ),
        ],
        repo_retriever=lambda _query: [
            RetrievedRepoMatch(
                query="structured output helper",
                repository="example/repo",
                path="src/helper.py",
                url="https://github.com/example/repo/blob/main/src/helper.py",
            ),
        ],
    )

    artifact = build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
        retrieval_artifact_paths=[
            tmp_path / "retrieval" / "external_retrieval_artifact.json",
        ],
        max_samples=5,
    )

    assert len(artifact.external_retrieval_summaries) == 1
    summary = artifact.external_retrieval_summaries[0]
    assert summary.web_document_count == 1
    assert summary.repo_match_count == 1
    assert "https://example.com/playbook" in summary.web_urls
    assert "example/repo:src/helper.py" in summary.repo_paths


def test_build_environment_inventory_reads_project_dependencies() -> None:
    """Environment inventory should include baseline project dependencies."""

    inventory = build_environment_inventory(project_root=REPO_ROOT)

    dependency_names = {status.package_name for status in inventory.dependency_statuses}
    assert "pydantic" in dependency_names
    assert "pyyaml" in dependency_names


def test_persist_environment_inventory_writes_artifact(tmp_path: Path) -> None:
    """Environment inventory should be persisted as its own artifact when requested."""

    inventory = persist_environment_inventory(
        output_dir=tmp_path / "environment",
        project_root=REPO_ROOT,
        requested_packages=["pydantic"],
    )

    assert inventory.project_root == str(REPO_ROOT)
    assert (tmp_path / "environment" / "environment_inventory.json").exists()


def test_build_project_context_inventory_reads_local_docs() -> None:
    """Project-context inventory should summarize local planning documents."""

    inventory = build_project_context_inventory(project_root=REPO_ROOT)

    assert inventory.project_root == str(REPO_ROOT)
    assert inventory.document_count >= 2
    categories = {document.category for document in inventory.documents}
    assert "readme" in categories
    assert "claude" in categories


def test_persist_project_context_inventory_writes_artifact(tmp_path: Path) -> None:
    """Project-context inventory should persist as its own discovery artifact."""

    inventory = persist_project_context_inventory(
        output_dir=tmp_path / "project_context",
        project_root=REPO_ROOT,
    )

    assert inventory.project_root == str(REPO_ROOT)
    assert (tmp_path / "project_context" / "project_context_inventory.json").exists()

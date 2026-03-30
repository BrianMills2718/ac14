"""Tests for pre-freeze discovery artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from ac14.discovery import (
    build_discovery_artifact,
    build_environment_inventory,
    inspect_input_path,
    persist_environment_inventory,
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
    """Discovery artifact should persist both input and environment context."""

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
    assert (tmp_path / "discovery" / "discovery_artifact.json").exists()


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

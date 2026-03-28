"""Tests for loading six-file AC14 blueprint bundles."""

from __future__ import annotations

from pathlib import Path

import pytest

from ac14.loader import load_blueprint_dir


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def test_load_blueprint_dir_reads_example_bundle() -> None:
    """The shipped example bundle should load into the canonical frozen blueprint model."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    assert blueprint.metadata.blueprint_id == "support_ticket_digest_v1"
    assert set(blueprint.components) == {
        "ticket_parser",
        "issue_classifier",
        "priority_scorer",
        "customer_context_loader",
        "digest_assembler",
    }
    assert "DigestStore" in blueprint.schemas
    assert "happy_path_digest_assembler" in blueprint.fixtures


def test_load_blueprint_dir_fails_loud_on_missing_file(tmp_path: Path) -> None:
    """Missing required blueprint files must raise immediately."""

    with pytest.raises(FileNotFoundError):
        load_blueprint_dir(tmp_path)

"""Tests for shared meta-process policy loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from ac14.meta_process_policy import load_dependency_probe_policy


def test_load_dependency_probe_policy_defaults_to_strict(tmp_path: Path) -> None:
    """Missing config should fall back to strict dependency-probe behavior."""

    assert load_dependency_probe_policy(tmp_path / "missing-meta-process.yaml") == "strict"


def test_load_dependency_probe_policy_reads_configured_value(tmp_path: Path) -> None:
    """Configured dependency-probe policy should be loaded from meta-process.yaml."""

    config_path = tmp_path / "meta-process.yaml"
    config_path.write_text(
        "\n".join(
            [
                "meta_process:",
                "  version: \"1.0\"",
                "  planning:",
                "    dependency_probe_policy: ignore",
            ],
        ),
    )

    assert load_dependency_probe_policy(config_path) == "ignore"


def test_load_dependency_probe_policy_rejects_unknown_value(tmp_path: Path) -> None:
    """Unknown dependency-probe policies should fail loud."""

    config_path = tmp_path / "meta-process.yaml"
    config_path.write_text(
        "\n".join(
            [
                "meta_process:",
                "  version: \"1.0\"",
                "  planning:",
                "    dependency_probe_policy: maybe",
            ],
        ),
    )

    with pytest.raises(ValueError, match="unsupported dependency_probe_policy"):
        load_dependency_probe_policy(config_path)

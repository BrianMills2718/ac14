"""Smoke tests for Makefile proof-surface targets."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "examples" / "support_ticket_digest" / "blueprint"
EXAMPLES_ROOT = REPO_ROOT / "examples"


def test_make_help_lists_proof_targets() -> None:
    """Make help should expose the proof-surface targets."""

    result = subprocess.run(
        ["make", "help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "verify-blueprint" in result.stdout
    assert "discover-input" in result.stdout
    assert "inspect-environment" in result.stdout
    assert "draft-blueprint-plan" in result.stdout
    assert "prove-example" in result.stdout
    assert "fresh-runs" in result.stdout
    assert "compare-generators" in result.stdout
    assert "acceptance-review" in result.stdout
    assert "semantic-compare" in result.stdout
    assert "prove-suite" in result.stdout
    assert "compare-suite" in result.stdout
    assert "semantic-compare-suite" in result.stdout
    assert "acceptance-review-suite" in result.stdout
    assert "recommend-default-generator" in result.stdout


def test_make_prove_example_runs_end_to_end(tmp_path: Path) -> None:
    """Make proof target should build a persisted bundle without manual Python imports."""

    output_dir = tmp_path / "proof_bundle"
    result = subprocess.run(
        [
            "make",
            "prove-example",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
            "TRIALS=2",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "manifest.json").exists()


def test_make_discover_input_runs_end_to_end(tmp_path: Path) -> None:
    """Make discovery target should persist a discovery artifact."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"id": 1, "status": "open"}, {"id": "2", "status": "closed"}]')
    output_dir = tmp_path / "discovery"
    result = subprocess.run(
        [
            "make",
            "discover-input",
            f"INPUT={input_path}",
            f"OUTPUT={output_dir}",
            "PACKAGES=pydantic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "discovery_artifact.json").exists()


def test_make_inspect_environment_runs_end_to_end(tmp_path: Path) -> None:
    """Make environment target should persist an environment inventory artifact."""

    output_dir = tmp_path / "environment"
    result = subprocess.run(
        [
            "make",
            "inspect-environment",
            f"OUTPUT={output_dir}",
            "PACKAGES=pydantic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "environment_inventory.json").exists()


def test_make_prove_suite_runs_end_to_end(tmp_path: Path) -> None:
    """Make suite proof target should build aggregate suite artifacts."""

    output_dir = tmp_path / "suite_proof"
    result = subprocess.run(
        [
            "make",
            "prove-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "TRIALS=1",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "suite_proof_report.json").exists()


def test_make_compare_suite_deterministic_only(tmp_path: Path) -> None:
    """Make suite comparison target should build aggregate comparison artifacts."""

    output_dir = tmp_path / "suite_compare"
    result = subprocess.run(
        [
            "make",
            "compare-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "TRIALS=1",
            "GENERATORS=deterministic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "suite_comparison_report.json").exists()


def test_make_semantic_compare_suite_deterministic_only(tmp_path: Path) -> None:
    """Make semantic suite target should build aggregate semantic artifacts."""

    output_dir = tmp_path / "suite_semantic"
    result = subprocess.run(
        [
            "make",
            "semantic-compare-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "MODES=reference deterministic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "suite_semantic_comparison_report.json").exists()


def test_make_recommend_default_generator_deterministic_only(tmp_path: Path) -> None:
    """Make recommendation target should produce the default-generator artifact."""

    output_dir = tmp_path / "recommendation"
    result = subprocess.run(
        [
            "make",
            "recommend-default-generator",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "GENERATORS=deterministic",
            "TRIALS=1",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "default_generator_recommendation.json").exists()

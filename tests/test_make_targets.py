"""Smoke tests for Makefile proof-surface targets."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "examples" / "support_ticket_digest" / "blueprint"


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
    assert "prove-example" in result.stdout
    assert "fresh-runs" in result.stdout


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

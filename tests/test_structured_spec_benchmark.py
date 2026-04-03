"""Tests for structured-spec benchmark bundles."""

from __future__ import annotations

from pathlib import Path

from ac14.structured_spec_benchmark import load_structured_spec_benchmark_bundle


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_load_structured_spec_benchmark_bundle_resource_scaling() -> None:
    """Structured-spec benchmark loader should resolve the front-half bundle cleanly."""

    bundle = load_structured_spec_benchmark_bundle(
        REPO_ROOT / "benchmarks" / "resource_scaling_structured_spec",
    )

    assert bundle.config.benchmark_id == "resource_scaling_structured_spec_v1"
    assert bundle.structured_spec.system_name == "Resource Scaling Decision System"
    assert bundle.reference_benchmark_dir.endswith("benchmarks/resource_scaling")
    assert "front-half-first" in bundle.requirements_text

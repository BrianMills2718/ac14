"""Typed benchmark bundles for front-half-first structured-spec comparisons.

This module freezes the shared input contract for front-half empirical work
without yet committing to the full comparison runner implementation. The bundle
points at a structured spec plus the existing back-half evaluation assets that a
later smoke gate can reuse.
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field

from ac14.structured_spec import StructuredSpecDocument, load_structured_spec_document


class StructuredSpecBenchmarkConfig(BaseModel):
    """Benchmark-level configuration for a front-half-first structured-spec bundle."""

    benchmark_id: str = Field(description="Stable benchmark identifier.")
    name: str = Field(description="Human-readable benchmark name.")
    purpose: str = Field(description="Why this front-half-first benchmark exists.")
    comparison_scope: str = Field(description="What this structured-spec benchmark isolates.")
    structured_spec_path: str = Field(description="Relative path to the raw structured-spec input.")
    requirements_path: str = Field(description="Relative path to the benchmark requirements text.")
    reference_benchmark_dir: str = Field(
        description="Relative path to the existing back-half benchmark assets reused for runtime evaluation.",
    )
    source_artifacts: list[str] = Field(
        description="Raw artifacts that both comparison conditions must consume.",
    )


class StructuredSpecBenchmarkFile(BaseModel):
    """On-disk shape of ``benchmark.yaml`` for a structured-spec bundle."""

    benchmark: StructuredSpecBenchmarkConfig = Field(description="Structured-spec benchmark configuration.")


class StructuredSpecBenchmarkBundle(BaseModel):
    """Frozen structured-spec benchmark bundle used before the new smoke gate exists."""

    benchmark_dir: str = Field(description="Root directory containing the benchmark assets.")
    config: StructuredSpecBenchmarkConfig = Field(description="Structured-spec benchmark configuration.")
    requirements_text: str = Field(description="Human-readable requirements document.")
    structured_spec: StructuredSpecDocument = Field(
        description="Validated structured-spec input consumed by both comparison conditions.",
    )
    reference_benchmark_dir: str = Field(
        description="Resolved directory containing the existing back-half evaluation assets.",
    )


def load_structured_spec_benchmark_bundle(
    benchmark_dir: Path | str,
) -> StructuredSpecBenchmarkBundle:
    """Load one structured-spec benchmark bundle from disk."""

    root = Path(benchmark_dir)
    config_path = root / "benchmark.yaml"
    benchmark_file = StructuredSpecBenchmarkFile.model_validate(
        yaml.safe_load(config_path.read_text()),
    )
    config = benchmark_file.benchmark
    structured_spec_path = root / config.structured_spec_path
    requirements_path = root / config.requirements_path
    reference_benchmark_dir = (root / config.reference_benchmark_dir).resolve()

    return StructuredSpecBenchmarkBundle(
        benchmark_dir=str(root),
        config=config,
        requirements_text=requirements_path.read_text(),
        structured_spec=load_structured_spec_document(structured_spec_path),
        reference_benchmark_dir=str(reference_benchmark_dir),
    )

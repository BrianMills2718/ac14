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
    assert bundle.structured_spec.inputs[0].name == "raw_scaling_event"
    assert [field.field_name for field in bundle.structured_spec.inputs[0].fields] == [
        "case_id",
        "received_at",
        "service_id",
        "service_tier",
        "cpu_utilization",
        "memory_utilization",
        "error_rate",
        "request_rate_rps",
        "last_deploy_hours",
        "in_change_freeze",
        "in_maintenance_window",
    ]
    assert [field.field_name for field in bundle.structured_spec.outputs[0].fields] == [
        "case_id",
        "service_id",
        "action",
        "urgency",
        "strategy",
        "target_adjustment",
        "approval_tier",
        "authorization_mode",
        "alert_tier",
        "scale_tier",
        "blocked",
        "requires_approval",
        "min_healthy_instances",
        "cooldown_minutes",
    ]

"""Tests for bounded structured-spec artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ac14.structured_spec import build_structured_spec_artifact


def test_build_structured_spec_artifact_persists_normalized_contract(tmp_path: Path) -> None:
    """Structured-spec preparation should persist a normalized review artifact."""

    source_path = tmp_path / "resource_scaling_spec.yaml"
    source_path.write_text(
        "\n".join(
            [
                "system_name: Resource Scaling Contract",
                "purpose: Decide when infrastructure should scale.",
                "requirements:",
                "  - produce a scaling decision for each metrics snapshot",
                "success_criteria:",
                "  - each decision includes an explicit rationale",
                "business_rules:",
                "  - cpu-only breaches may still require scale-up",
                "inputs:",
                "  - name: metrics_snapshot",
                "    kind: record",
                "    description: Current utilization and capacity metrics.",
                "    fields:",
                "      - field_name: cpu_utilization",
                "        field_type: float",
                "        description: Current CPU utilization ratio.",
                "        required: true",
                "outputs:",
                "  - name: scaling_decision",
                "    kind: record",
                "    description: Final scale or no-scale decision.",
                "    fields:",
                "      - field_name: action",
                "        field_type: str",
                "        description: One scaling action label.",
                "        required: true",
                "workflow_hints:",
                "  - hint_id: evaluate_thresholds",
                "    summary: Evaluate the snapshot against business rules.",
                "    input_names: [metrics_snapshot]",
                "    output_names: [scaling_decision]",
                "human_context_notes:",
                "  - Start with a small bounded component graph.",
            ],
        ),
    )

    artifact = build_structured_spec_artifact(
        input_path=source_path,
        output_dir=tmp_path / "artifact",
    )

    assert artifact.spec.system_name == "Resource Scaling Contract"
    assert artifact.open_concerns == []
    persisted_path = tmp_path / "artifact" / "structured_spec_artifact.json"
    assert persisted_path.exists()
    payload = json.loads(persisted_path.read_text())
    assert payload["spec"]["workflow_hints"][0]["hint_id"] == "evaluate_thresholds"


def test_build_structured_spec_artifact_rejects_unknown_workflow_names(tmp_path: Path) -> None:
    """Workflow hints should fail loud when they reference undeclared interfaces."""

    source_path = tmp_path / "bad_spec.json"
    source_path.write_text(
        json.dumps(
            {
                "system_name": "Broken Contract",
                "purpose": "Demonstrate loud validation.",
                "requirements": ["produce a decision"],
                "inputs": [
                    {
                        "name": "metrics_snapshot",
                        "kind": "record",
                        "description": "Current metrics.",
                        "fields": [],
                    }
                ],
                "outputs": [],
                "workflow_hints": [
                    {
                        "hint_id": "bad_hint",
                        "summary": "References an undeclared output.",
                        "input_names": ["metrics_snapshot"],
                        "output_names": ["missing_output"],
                    }
                ],
            },
        ),
    )

    with pytest.raises(ValueError, match="unknown outputs"):
        build_structured_spec_artifact(
            input_path=source_path,
            output_dir=tmp_path / "artifact",
        )

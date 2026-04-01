"""Tests for realistic-input front-half acceptance artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ac14.front_half_acceptance import (
    build_front_half_acceptance_report,
    build_front_half_acceptance_suite_report,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_dependency_plan_fixture(path: Path) -> Path:
    """Persist a deterministic dependency-plan fixture for front-half tests."""

    path.write_text(
        json.dumps(
            {
                "planning_summary": "Reuse pydantic for typed schema contracts.",
                "recommendations": [
                    {
                        "package_name": "pydantic",
                        "action": "reuse",
                        "capability_need": "typed schema contracts",
                        "justification": "Pydantic is already installed and aligns with schema validation.",
                        "already_installed": True,
                        "install_command": None,
                        "evidence": [
                            {
                                "source": "environment",
                                "locator": "pydantic",
                                "detail": "Installed in the current environment.",
                            }
                        ],
                    }
                ],
                "standard_library_notes": [
                    "The standard library is sufficient for filesystem and JSON handling in the first slice.",
                ],
                "open_questions": [],
            },
            indent=2,
        ),
    )
    return path


def _write_blueprint_plan_fixture(path: Path) -> Path:
    """Persist a deterministic draft blueprint planning fixture."""

    path.write_text(
        json.dumps(
            {
                "planning_summary": "Split the ticket digest into a source parser and a digest sink.",
                "proposed_schemas": [
                    {
                        "schema_name": "RawTicket",
                        "kind": "record",
                        "description": "Normalized support ticket input.",
                        "fields": [
                            {
                                "field_name": "ticket_id",
                                "field_type": "str",
                                "description": "Stable ticket identifier.",
                            },
                            {
                                "field_name": "body",
                                "field_type": "str",
                                "description": "Full issue description for downstream analysis.",
                            }
                        ],
                    }
                ],
                "proposed_components": [
                    {
                        "component_id": "ticket_ingest",
                        "semantic_responsibility": "ingest_ticket",
                        "purpose": "Normalize discovered ticket input into RawTicket records.",
                        "input_ports": [],
                        "output_ports": [
                            {
                                "port_name": "raw_ticket",
                                "schema_name": "RawTicket",
                                "description": "Normalized ticket payload.",
                            }
                        ],
                        "packet_focus": [
                            "normalize incoming ticket fields",
                            "preserve support context that matters downstream",
                        ],
                        "dependency_notes": [
                            "reuse pydantic models for typed schema validation",
                        ],
                    }
                ],
                "proposed_bindings": [],
                "proposed_scenarios": [
                    {
                        "scenario_id": "realistic_batch",
                        "kind": "semantic_acceptance",
                        "description": "Review a realistic batch of support tickets.",
                        "requirement_focus": [
                            "preserve ticket meaning",
                            "keep packets bounded",
                        ],
                    }
                ],
                "packetization_notes": [
                    "Keep the source packet focused on normalization and preserve downstream context needs explicitly.",
                ],
                "dependency_decisions": [
                    "Reuse pydantic for schema contracts in the front-half slice.",
                ],
                "open_questions": [
                    {
                        "question": "Should auth_method be preserved explicitly in RawTicket?",
                        "why_it_matters": "It changes downstream schema shape before freeze.",
                    }
                ],
            },
            indent=2,
        ),
    )
    return path


def _write_refine_blueprint_plan_fixture(path: Path) -> Path:
    """Persist a deterministic refinement fixture for blocked-freeze retries."""

    payload = json.loads(_write_blueprint_plan_fixture(path).read_text())
    payload["refinement_summary"] = "Clarified dependency scope after the blocked freeze."
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return path


def _write_front_half_review_fixture(path: Path) -> Path:
    """Persist a deterministic front-half review fixture."""

    path.write_text(
        json.dumps(
            {
                "overall_verdict": "concern",
                "freeze_verdict": "promising_but_blocked",
                "summary": "The front half preserves the requirements well enough to be promising, but the draft is still blocked by provisional authoring gaps.",
                "strengths": [
                    "Discovery preserved realistic ticket structure and key fields.",
                    "The decomposition stays bounded and uses a truthful source schema.",
                ],
                "concerns": [
                    "The current draft bundle still lacks fixture coverage and concrete invariants.",
                ],
                "requirement_assessments": [
                    {
                        "requirement": "preserve support ticket meaning",
                        "verdict": "satisfied",
                        "rationale": "The discovered fields and draft schema keep the core ticket content intact.",
                    },
                    {
                        "requirement": "keep packets bounded",
                        "verdict": "satisfied",
                        "rationale": "The source-only draft packet stays narrowly scoped.",
                    }
                ],
                "recommended_next_steps": [
                    "Add concrete fixtures and local invariants before retrying freeze.",
                    "Resolve the remaining open schema question explicitly.",
                ],
            },
            indent=2,
        ),
    )
    return path


def _write_freeze_semantic_review_fixture(path: Path) -> Path:
    """Persist a deterministic freeze-semantic review fixture."""

    path.write_text(
        json.dumps(
            {
                "overall_verdict": "concern",
                "freeze_verdict": "promising_but_blocked",
                "summary": "The draft looks strategically plausible, but concrete draft gaps still block freeze.",
                "strengths": [
                    "Discovery preserved realistic ticket structure and downstream-relevant fields.",
                    "The packetization still keeps the first implementation slice narrow.",
                ],
                "concerns": [
                    "Fixture coverage and invariants are still incomplete at freeze time.",
                ],
                "requirement_assessments": [
                    {
                        "requirement": "preserve support ticket meaning",
                        "verdict": "satisfied",
                        "rationale": "The draft schema retains the core ticket content.",
                    },
                    {
                        "requirement": "keep packets bounded",
                        "verdict": "satisfied",
                        "rationale": "The current source packet stays focused on normalization.",
                    },
                ],
                "recommended_next_steps": [
                    "Add concrete fixtures and invariants before retrying freeze.",
                ],
            },
            indent=2,
            sort_keys=True,
        ),
    )
    return path


def test_build_front_half_acceptance_report_runs_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Front-half acceptance should persist the realistic-input pipeline and final review."""

    input_path = tmp_path / "realistic_ticket_batch.json"
    input_path.write_text(
        json.dumps(
            [
                {
                    "ticket_id": "SUP-10421",
                    "body": "SSO login fails after certificate rotation.",
                    "channel": "email",
                },
                {
                    "ticket_id": "SUP-10422",
                    "body": "Bulk user import times out after 300 users.",
                    "channel": "web",
                },
            ],
            indent=2,
        ),
    )
    monkeypatch.setenv(
        "AC14_DEPENDENCY_PLAN_FIXTURE",
        str(_write_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FRONT_HALF_ACCEPTANCE_FIXTURE",
        str(_write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE",
        str(_write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json")),
    )

    artifact = build_front_half_acceptance_report(
        input_path=input_path,
        output_dir=tmp_path / "front_half",
        requirements=["preserve support ticket meaning", "keep packets bounded"],
        project_root=REPO_ROOT,
        requested_packages=["pydantic"],
        max_budget=0.1,
    )

    assert Path(artifact.artifact_paths.discovery_artifact_path).exists()
    assert Path(artifact.artifact_paths.dependency_plan_path).exists()
    assert Path(artifact.artifact_paths.dependency_execution_artifact_path).exists()
    assert Path(artifact.artifact_paths.draft_blueprint_plan_path).exists()
    assert Path(artifact.artifact_paths.freeze_readiness_report_path).exists()
    assert Path(artifact.artifact_paths.freeze_decision_path).exists()
    assert artifact.artifact_paths.freeze_semantic_review_path is not None
    assert Path(artifact.artifact_paths.freeze_semantic_review_path).exists()


def test_build_front_half_acceptance_report_supports_retry_freeze(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Front-half acceptance should optionally persist one bounded retry-chain artifact."""

    input_path = tmp_path / "realistic_ticket_batch.json"
    input_path.write_text(
        json.dumps(
            [
                {
                    "ticket_id": "SUP-10421",
                    "body": "SSO login fails after certificate rotation.",
                    "channel": "email",
                }
            ],
            indent=2,
        ),
    )
    monkeypatch.setenv(
        "AC14_DEPENDENCY_PLAN_FIXTURE",
        str(_write_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_REFINE_BLUEPRINT_PLAN_FIXTURE",
        str(_write_refine_blueprint_plan_fixture(tmp_path / "refine_blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FRONT_HALF_ACCEPTANCE_FIXTURE",
        str(_write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE",
        str(_write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json")),
    )

    artifact = build_front_half_acceptance_report(
        input_path=input_path,
        output_dir=tmp_path / "front_half",
        requirements=["preserve support ticket meaning", "keep packets bounded"],
        project_root=REPO_ROOT,
        requested_packages=["pydantic"],
        retry_blocked_freeze=True,
        max_budget=0.1,
        retry_max_budget=0.1,
    )

    assert artifact.freeze_approved is False
    assert artifact.retry_freeze_attempted is True
    assert artifact.retry_freeze_approved is False
    assert artifact.final_freeze_approved is False
    assert artifact.artifact_paths.retry_freeze_artifact_path is not None
    assert Path(artifact.artifact_paths.retry_freeze_artifact_path).exists()
    assert artifact.freeze_approved is False
    assert "E-B1-COMPONENT-FIXTURE-COVERAGE-MISSING" in artifact.blocking_finding_codes
    assert artifact.review.freeze_verdict == "promising_but_blocked"
    assert artifact.review.overall_verdict == "concern"
    assert (tmp_path / "front_half" / "front_half_acceptance_report.json").exists()


def test_build_front_half_acceptance_suite_report_runs_for_shipped_examples(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Front-half suite artifact should persist one report per shipped example."""

    monkeypatch.setenv(
        "AC14_DEPENDENCY_PLAN_FIXTURE",
        str(_write_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FRONT_HALF_ACCEPTANCE_FIXTURE",
        str(_write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE",
        str(_write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json")),
    )

    artifact = build_front_half_acceptance_suite_report(
        output_dir=tmp_path / "front_half_suite",
        examples_root=REPO_ROOT / "examples",
        max_budget=0.1,
    )

    assert artifact.example_count >= 3
    assert artifact.concern_examples == artifact.example_count
    assert artifact.freeze_blocked_examples == artifact.example_count
    assert artifact.freeze_approved_examples == 0
    assert all(example.report_path is not None for example in artifact.examples)
    assert all(example.freeze_semantic_review_path is not None for example in artifact.examples)
    assert (tmp_path / "front_half_suite" / "front_half_acceptance_suite_report.json").exists()


def test_build_front_half_acceptance_report_supports_messy_input_artifact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Front-half acceptance should stay reviewable on a messier CSV input asset."""

    monkeypatch.setenv(
        "AC14_DEPENDENCY_PLAN_FIXTURE",
        str(_write_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FRONT_HALF_ACCEPTANCE_FIXTURE",
        str(_write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE",
        str(_write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json")),
    )

    artifact = build_front_half_acceptance_report(
        input_path=REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch_messy.csv",
        output_dir=tmp_path / "front_half_csv",
        requirements=["preserve support ticket meaning", "keep packets bounded"],
        project_root=REPO_ROOT,
        requested_packages=["pydantic"],
        max_budget=0.1,
    )

    discovery_payload = json.loads(Path(artifact.artifact_paths.discovery_artifact_path).read_text())
    assert discovery_payload["input_inspection"]["input_format"] == "csv"
    assert artifact.review.freeze_verdict == "promising_but_blocked"
    assert artifact.artifact_paths.freeze_semantic_review_path is not None

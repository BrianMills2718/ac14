"""Tests for realistic-input front-half acceptance artifacts."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from ac14.freeze_decision import FreezeDecisionArtifact
from ac14.freeze_retry import FreezeRetryArtifact
from ac14.front_half_acceptance import (
    FrontHalfReviewResponse,
    abuild_structured_spec_front_half_acceptance_report,
    build_front_half_acceptance_report,
    build_front_half_acceptance_suite_report,
    build_structured_spec_front_half_acceptance_report,
)
from ac14.structured_spec import build_structured_spec_artifact


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


def _write_blocked_blueprint_plan_fixture(path: Path) -> Path:
    """Persist a deterministic draft plan that remains structurally blocked."""

    payload = json.loads(_write_blueprint_plan_fixture(path).read_text())
    payload["proposed_scenarios"] = []
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return path


def _write_blocked_refine_blueprint_plan_fixture(path: Path) -> Path:
    """Persist a deterministic blocked refinement fixture for retry-path tests."""

    payload = json.loads(_write_blocked_blueprint_plan_fixture(path).read_text())
    payload["refinement_summary"] = "The retry did not recover missing scenario coverage yet."
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


def _write_input_directory_bundle(path: Path) -> Path:
    """Persist a bounded directory input bundle for directory-input front-half tests."""

    path.mkdir(parents=True, exist_ok=True)
    (path / "tickets.json").write_text(
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
    (path / "tickets_archive.csv").write_text(
        "ticket_id,body,channel\n"
        "SUP-09999,Archived backlog item,email\n",
    )
    (path / "notes.md").write_text(
        "# Intake notes\n\n"
        "Tickets in this folder represent the latest support batch.\n",
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


def test_build_structured_spec_front_half_acceptance_report_runs_end_to_end(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Structured-spec front-half acceptance should persist the bounded pipeline and review."""

    source_path = tmp_path / "resource_scaling_spec.yaml"
    source_path.write_text(
        "\n".join(
            [
                "system_name: Resource Scaling Contract",
                "purpose: Decide when infrastructure should scale.",
                "requirements:",
                "  - produce a scaling decision for each metrics snapshot",
                "inputs:",
                "  - name: metrics_snapshot",
                "    kind: record",
                "    description: Current utilization metrics.",
                "    fields:",
                "      - field_name: cpu_utilization",
                "        field_type: float",
                "        description: CPU utilization ratio.",
                "        required: true",
                "outputs:",
                "  - name: scaling_decision",
                "    kind: record",
                "    description: Final scaling decision.",
                "    fields:",
                "      - field_name: action",
                "        field_type: str",
                "        description: One scaling action label.",
                "        required: true",
                "workflow_hints:",
                "  - hint_id: evaluate_thresholds",
                "    summary: Evaluate metrics against rules.",
                "    input_names: [metrics_snapshot]",
                "    output_names: [scaling_decision]",
            ],
        ),
    )
    build_structured_spec_artifact(source_path, tmp_path / "structured_spec")
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

    artifact = build_structured_spec_front_half_acceptance_report(
        structured_spec_artifact_path=tmp_path / "structured_spec" / "structured_spec_artifact.json",
        output_dir=tmp_path / "structured_spec_front_half",
        max_budget=0.1,
    )

    assert artifact.planning_input_name == "Resource Scaling Contract"
    assert Path(artifact.artifact_paths.structured_spec_artifact_path).exists()
    assert Path(artifact.artifact_paths.draft_blueprint_plan_path).exists()
    assert Path(artifact.artifact_paths.freeze_readiness_report_path).exists()
    assert Path(artifact.artifact_paths.freeze_decision_path).exists()
    assert artifact.artifact_paths.freeze_semantic_review_path is not None
    assert Path(artifact.artifact_paths.freeze_semantic_review_path).exists()
    assert (tmp_path / "structured_spec_front_half" / "structured_spec_front_half_acceptance_report.json").exists()


def test_async_structured_spec_front_half_acceptance_supports_retry_freeze(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The async structured-spec retry path should not re-enter asyncio.run()."""

    from ac14.freeze_decision import FreezeSemanticReviewResponse

    source_path = tmp_path / "resource_scaling_spec.yaml"
    source_path.write_text(
        "\n".join(
            [
                "system_name: Resource Scaling Contract",
                "purpose: Decide when infrastructure should scale.",
                "requirements:",
                "  - produce a scaling decision for each metrics snapshot",
                "inputs:",
                "  - name: metrics_snapshot",
                "    kind: record",
                "    description: Current utilization metrics.",
                "    fields:",
                "      - field_name: cpu_utilization",
                "        field_type: float",
                "        description: CPU utilization ratio.",
                "        required: true",
                "outputs:",
                "  - name: scaling_decision",
                "    kind: record",
                "    description: Final scaling decision.",
                "    fields:",
                "      - field_name: action",
                "        field_type: str",
                "        description: One scaling action label.",
                "        required: true",
                "workflow_hints:",
                "  - hint_id: evaluate_thresholds",
                "    summary: Evaluate metrics against rules.",
                "    input_names: [metrics_snapshot]",
                "    output_names: [scaling_decision]",
            ],
        ),
    )
    build_structured_spec_artifact(source_path, tmp_path / "structured_spec")
    monkeypatch.setenv(
        "AC14_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blocked_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_REFINE_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blocked_refine_blueprint_plan_fixture(tmp_path / "refine_blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_FRONT_HALF_ACCEPTANCE_FIXTURE",
        str(_write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json")),
    )
    freeze_review = FreezeSemanticReviewResponse(
        overall_verdict="concern",
        freeze_verdict="promising_but_blocked",
        summary="async-safe retry path reached freeze semantic review",
        strengths=["reviewable retry path"],
        concerns=["freeze still blocked on draft fidelity"],
        requirement_assessments=[],
        recommended_next_steps=["repair draft fidelity findings before the next retry"],
    )
    freeze_review_call = AsyncMock(return_value=(freeze_review, object()))
    monkeypatch.setattr("ac14.freeze_decision.acall_llm_structured", freeze_review_call)

    artifact = asyncio.run(
        abuild_structured_spec_front_half_acceptance_report(
            structured_spec_artifact_path=tmp_path / "structured_spec" / "structured_spec_artifact.json",
            output_dir=tmp_path / "structured_spec_front_half_async",
            retry_blocked_freeze=True,
            max_budget=0.1,
            retry_max_budget=0.1,
        )
    )

    assert artifact.freeze_approved is False
    assert artifact.retry_freeze_attempted is True
    assert artifact.artifact_paths.retry_freeze_artifact_path is not None
    assert Path(artifact.artifact_paths.retry_freeze_artifact_path).exists()


def test_build_structured_spec_front_half_acceptance_report_propagates_explicit_models(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Structured-spec front-half acceptance should forward explicit models into freeze paths."""

    source_path = (
        REPO_ROOT
        / "benchmarks"
        / "resource_scaling_structured_spec"
        / "structured_spec_input.yaml"
    )
    build_structured_spec_artifact(source_path, tmp_path / "structured_spec")
    captured: dict[str, object] = {}

    async def _fake_plan_writer(
        structured_spec_artifact_path: Path | str,
        output_dir: Path | str,
        *,
        model: str,
        max_budget: float,
        task: str = "ac14_draft_blueprint_plan_from_structured_spec",
    ) -> None:
        del task
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        payload = json.loads(
            _write_blueprint_plan_fixture(destination / "draft_blueprint_plan_fixture.json").read_text(),
        )
        payload.update(
            {
                "planning_input_kind": "structured_spec",
                "planning_input_name": "Resource Scaling Contract",
                "planning_input_artifact_path": str(structured_spec_artifact_path),
                "structured_spec_artifact_path": str(structured_spec_artifact_path),
                "requirements": ["produce a scaling decision for each metrics snapshot"],
                "planning_input_open_concerns": [],
                "discovery_open_concerns": [],
            },
        )
        (destination / "draft_blueprint_plan.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True),
        )
        captured["plan_model"] = model
        captured["plan_max_budget"] = max_budget

    async def _fake_freeze_decision(
        bundle_dir: Path | str,
        output_dir: Path | str,
        *,
        readiness_report_path: Path | str | None = None,
        semantic_review_model: str,
        semantic_review_max_budget: float,
    ) -> FreezeDecisionArtifact:
        del bundle_dir, readiness_report_path
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        review_path = destination / "freeze_semantic_review.json"
        review_path.write_text(
            _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json").read_text(),
        )
        decision_path = destination / "freeze_decision.json"
        decision = FreezeDecisionArtifact(
            source_bundle_dir=str(tmp_path / "draft_bundle"),
            readiness_report_path=str(tmp_path / "draft_bundle" / "freeze_readiness_report.json"),
            approved=False,
            decision_summary="bundle blocked by freeze-readiness findings",
            findings=[],
            promoted_bundle_dir=None,
            semantic_review_path=str(review_path),
            remediation_plan_path=str(destination / "freeze_remediation_plan.json"),
        )
        decision_path.write_text(json.dumps(decision.model_dump(mode="json"), indent=2, sort_keys=True))
        captured["freeze_model"] = semantic_review_model
        captured["freeze_max_budget"] = semantic_review_max_budget
        return decision

    async def _fake_retry_artifact(
        plan_artifact_path: Path | str,
        freeze_decision_path: Path | str,
        output_dir: Path | str,
        *,
        model: str,
        max_budget: float,
    ) -> FreezeRetryArtifact:
        del plan_artifact_path, freeze_decision_path
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        artifact = FreezeRetryArtifact(
            source_draft_blueprint_plan_path=str(destination / "source_plan.json"),
            source_freeze_decision_path=str(destination / "source_freeze_decision.json"),
            refined_draft_blueprint_plan_path=str(destination / "refined_plan.json"),
            refined_draft_bundle_dir=str(destination / "refined_bundle"),
            refreshed_freeze_readiness_report_path=str(destination / "refreshed_freeze_readiness_report.json"),
            refreshed_freeze_decision_path=str(destination / "refreshed_freeze_decision.json"),
            refreshed_freeze_semantic_review_path=str(destination / "refreshed_freeze_semantic_review.json"),
            refinement_round=1,
            approved=False,
            summary="retry chain kept the refined bundle blocked at freeze",
        )
        (destination / "freeze_retry_artifact.json").write_text(
            json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
        )
        captured["retry_model"] = model
        captured["retry_max_budget"] = max_budget
        return artifact

    async def _fake_review(*args: object, **kwargs: object) -> FrontHalfReviewResponse:
        del args, kwargs
        return FrontHalfReviewResponse.model_validate_json(
            _write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json").read_text(),
        )

    monkeypatch.setattr(
        "ac14.front_half_acceptance.abuild_draft_blueprint_plan_from_structured_spec",
        _fake_plan_writer,
    )
    monkeypatch.setattr(
        "ac14.front_half_acceptance.materialize_draft_blueprint_bundle",
        lambda plan_artifact_path, output_dir: SimpleNamespace(
            draft_bundle_dir=str(Path(output_dir)),
            freeze_readiness_report_path=str(Path(output_dir) / "freeze_readiness_report.json"),
        ),
    )
    monkeypatch.setattr("ac14.front_half_acceptance.abuild_freeze_decision", _fake_freeze_decision)
    monkeypatch.setattr(
        "ac14.front_half_acceptance.abuild_freeze_retry_artifact",
        _fake_retry_artifact,
    )
    monkeypatch.setattr(
        "ac14.front_half_acceptance._review_structured_spec_front_half_acceptance",
        _fake_review,
    )

    artifact = build_structured_spec_front_half_acceptance_report(
        structured_spec_artifact_path=tmp_path / "structured_spec" / "structured_spec_artifact.json",
        output_dir=tmp_path / "structured_spec_front_half",
        model="gpt-5-mini",
        max_budget=1.5,
        retry_blocked_freeze=True,
        retry_model="gpt-5-nano",
        retry_max_budget=0.75,
    )

    assert artifact.freeze_approved is False
    assert artifact.retry_freeze_attempted is True
    assert captured == {
        "plan_model": "gpt-5-mini",
        "plan_max_budget": 1.5,
        "freeze_model": "gpt-5-mini",
        "freeze_max_budget": 1.5,
        "retry_model": "gpt-5-nano",
        "retry_max_budget": 0.75,
    }


def test_build_structured_spec_front_half_acceptance_report_survives_cwd_shift(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Structured-spec front-half paths should stay valid even if cwd changes mid-pipeline."""

    source_path = (
        REPO_ROOT
        / "benchmarks"
        / "resource_scaling_structured_spec"
        / "structured_spec_input.yaml"
    )
    build_structured_spec_artifact(source_path, tmp_path / "structured_spec")
    monkeypatch.chdir(tmp_path)

    async def _fake_plan_writer(
        structured_spec_artifact_path: Path | str,
        output_dir: Path | str,
        *,
        model: str,
        max_budget: float,
        task: str = "ac14_draft_blueprint_plan_from_structured_spec",
    ) -> None:
        del structured_spec_artifact_path, model, max_budget, task
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        payload = json.loads(
            _write_blueprint_plan_fixture(destination / "draft_blueprint_plan_fixture.json").read_text(),
        )
        payload.update(
            {
                "planning_input_kind": "structured_spec",
                "planning_input_name": "Resource Scaling Decision System",
                "planning_input_artifact_path": str(
                    (tmp_path / "structured_spec" / "structured_spec_artifact.json").resolve(),
                ),
                "structured_spec_artifact_path": str(
                    (tmp_path / "structured_spec" / "structured_spec_artifact.json").resolve(),
                ),
                "requirements": [
                    "produce one exact scaling_decision_entry and rolling scaling_decision_store for each event",
                ],
                "planning_input_open_concerns": [],
                "discovery_open_concerns": [],
            },
        )
        (destination / "draft_blueprint_plan.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True),
        )
        monkeypatch.chdir(tmp_path.parent)

    async def _fake_freeze_decision(
        bundle_dir: Path | str,
        output_dir: Path | str,
        *,
        readiness_report_path: Path | str | None = None,
        semantic_review_model: str,
        semantic_review_max_budget: float,
    ) -> FreezeDecisionArtifact:
        del bundle_dir, readiness_report_path, semantic_review_model, semantic_review_max_budget
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        review_path = destination / "freeze_semantic_review.json"
        review_path.write_text(
            _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json").read_text(),
        )
        decision = FreezeDecisionArtifact(
            source_bundle_dir=str((tmp_path / "structured_spec_front_half" / "draft_bundle").resolve()),
            readiness_report_path=str(
                (tmp_path / "structured_spec_front_half" / "draft_bundle" / "freeze_readiness_report.json").resolve(),
            ),
            approved=True,
            decision_summary="bundle approved for freeze",
            findings=[],
            promoted_bundle_dir=str((tmp_path / "structured_spec_front_half" / "draft_bundle").resolve()),
            semantic_review_path=str(review_path),
            remediation_plan_path=str(destination / "freeze_remediation_plan.json"),
        )
        (destination / "freeze_decision.json").write_text(
            json.dumps(decision.model_dump(mode="json"), indent=2, sort_keys=True),
        )
        return decision

    async def _fake_review(*args: object, **kwargs: object) -> FrontHalfReviewResponse:
        draft_plan_path = kwargs["draft_plan_path"]
        assert isinstance(draft_plan_path, Path)
        assert draft_plan_path.is_absolute()
        assert draft_plan_path.exists()
        return FrontHalfReviewResponse.model_validate_json(
            _write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json").read_text(),
        )

    monkeypatch.setattr(
        "ac14.front_half_acceptance.abuild_draft_blueprint_plan_from_structured_spec",
        _fake_plan_writer,
    )
    monkeypatch.setattr(
        "ac14.front_half_acceptance.materialize_draft_blueprint_bundle",
        lambda plan_artifact_path, output_dir: SimpleNamespace(
            draft_bundle_dir=str(Path(output_dir)),
            freeze_readiness_report_path=str(Path(output_dir) / "freeze_readiness_report.json"),
        ),
    )
    monkeypatch.setattr("ac14.front_half_acceptance.abuild_freeze_decision", _fake_freeze_decision)
    monkeypatch.setattr(
        "ac14.front_half_acceptance._review_structured_spec_front_half_acceptance",
        _fake_review,
    )

    artifact = build_structured_spec_front_half_acceptance_report(
        structured_spec_artifact_path=Path("structured_spec") / "structured_spec_artifact.json",
        output_dir=Path("structured_spec_front_half"),
        max_budget=0.1,
    )

    assert artifact.freeze_approved is True
    assert Path(artifact.artifact_paths.draft_blueprint_plan_path).is_absolute()
    assert Path(artifact.artifact_paths.draft_blueprint_plan_path).exists()


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
        str(_write_blocked_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_REFINE_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blocked_refine_blueprint_plan_fixture(tmp_path / "refine_blueprint_plan_fixture.json")),
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
        str(_write_blocked_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")),
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


def test_build_front_half_acceptance_suite_report_supports_retry_freeze(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Front-half suite breadth should optionally aggregate retry-aware results."""

    monkeypatch.setenv(
        "AC14_DEPENDENCY_PLAN_FIXTURE",
        str(_write_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blocked_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_REFINE_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blocked_refine_blueprint_plan_fixture(tmp_path / "refine_blueprint_plan_fixture.json")),
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
        retry_blocked_freeze=True,
        retry_max_budget=0.1,
    )

    assert artifact.example_count >= 3
    assert artifact.retry_attempted_examples == artifact.example_count
    assert artifact.retry_approved_examples == 0
    assert all(example.retry_freeze_attempted for example in artifact.examples)
    assert all(example.retry_freeze_artifact_path is not None for example in artifact.examples)


def test_build_front_half_acceptance_suite_report_supports_realistic_input_profile_selection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Front-half suite breadth should support explicit realistic-input profile selection."""

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
        realistic_input_profile="messy",
        max_budget=0.1,
    )

    assert artifact.realistic_input_profile == "messy"
    assert artifact.example_count >= 3
    assert artifact.missing_profile_examples == artifact.example_count - 1
    assert next(
        example for example in artifact.examples if example.example_id == "support_ticket_digest"
    ).realistic_input_profile == "messy"
    assert {
        example.example_id
        for example in artifact.examples
        if example.overall_verdict == "missing_profile"
    } == {
        "incident_alert_digest",
        "support_ticket_digest_auth_mix",
    }


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


def test_build_front_half_acceptance_report_supports_input_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Front-half acceptance should preserve explicit directory-input discovery evidence."""

    input_dir = _write_input_directory_bundle(tmp_path / "input_bundle")
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
        input_path=input_dir,
        output_dir=tmp_path / "front_half_directory",
        requirements=["preserve support ticket meaning", "keep packets bounded"],
        project_root=REPO_ROOT,
        requested_packages=["pydantic"],
        max_budget=0.1,
    )

    discovery_payload = json.loads(Path(artifact.artifact_paths.discovery_artifact_path).read_text())
    inspection = discovery_payload["input_inspection"]
    assert artifact.input_path == str(input_dir)
    assert inspection["input_path"] == str(input_dir)
    assert inspection["primary_input_path"].endswith("tickets.json")
    assert inspection["structured_candidate_paths"] == [
        str(input_dir / "tickets.json"),
        str(input_dir / "tickets_archive.csv"),
    ]
    assert inspection["supporting_context_paths"] == [str(input_dir / "notes.md")]
    assert artifact.review.freeze_verdict == "promising_but_blocked"
    assert artifact.artifact_paths.freeze_semantic_review_path is not None


def test_build_front_half_acceptance_report_preserves_directory_context_summaries(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Front-half acceptance should preserve directory-context summaries."""

    input_dir = _write_input_directory_bundle(tmp_path / "input_bundle")
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
        input_path=input_dir,
        output_dir=tmp_path / "front_half_directory_summaries",
        requirements=["preserve support ticket meaning", "keep packets bounded"],
        project_root=REPO_ROOT,
        requested_packages=["pydantic"],
        max_budget=0.1,
    )

    discovery_payload = json.loads(Path(artifact.artifact_paths.discovery_artifact_path).read_text())
    inspection = discovery_payload["input_inspection"]
    alternate_summary = inspection["structured_candidate_summaries"][0]
    context_summary = inspection["supporting_context_summaries"][0]
    assert alternate_summary["path"] == str(input_dir / "tickets_archive.csv")
    assert alternate_summary["input_format"] == "csv"
    assert any(field["path"] == "ticket_id" for field in alternate_summary["field_summaries"])
    assert context_summary["path"] == str(input_dir / "notes.md")
    assert context_summary["title"] == "Intake notes"
    assert "latest support batch" in context_summary["preview"].lower()


def test_build_front_half_acceptance_report_supports_retry_freeze_on_messy_input(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Retry-aware front-half acceptance should stay explicit on the messy CSV asset."""

    monkeypatch.setenv(
        "AC14_DEPENDENCY_PLAN_FIXTURE",
        str(_write_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blocked_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")),
    )
    monkeypatch.setenv(
        "AC14_REFINE_BLUEPRINT_PLAN_FIXTURE",
        str(_write_blocked_refine_blueprint_plan_fixture(tmp_path / "refine_blueprint_plan_fixture.json")),
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
        retry_blocked_freeze=True,
        max_budget=0.1,
        retry_max_budget=0.1,
    )

    discovery_payload = json.loads(Path(artifact.artifact_paths.discovery_artifact_path).read_text())
    assert discovery_payload["input_inspection"]["input_format"] == "csv"
    assert artifact.freeze_approved is False
    assert artifact.retry_freeze_attempted is True
    assert artifact.retry_freeze_approved is False
    assert artifact.final_freeze_approved is False
    assert artifact.artifact_paths.retry_freeze_artifact_path is not None
    assert Path(artifact.artifact_paths.retry_freeze_artifact_path).exists()
    assert artifact.review.freeze_verdict == "promising_but_blocked"
    assert artifact.artifact_paths.freeze_semantic_review_path is not None

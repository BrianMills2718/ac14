"""Tests for requirements-aware acceptance artifacts."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from ac14.acceptance import (
    AcceptanceReviewResponse,
    build_acceptance_report,
    build_suite_acceptance_report,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "examples" / "support_ticket_digest" / "blueprint"
INCIDENT_EXAMPLE_DIR = REPO_ROOT / "examples" / "incident_alert_digest" / "blueprint"
EXAMPLES_ROOT = REPO_ROOT / "examples"


def _fake_review() -> tuple[AcceptanceReviewResponse, object]:
    return (
        AcceptanceReviewResponse(
            overall_verdict="accept",
            summary="Outputs satisfy the scenario requirements.",
            concerns=[],
            requirement_assessments=[],
        ),
        object(),
    )


def test_build_acceptance_report_uses_structured_review(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Acceptance report should call llm_client with the expected local contract."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)

    report = build_acceptance_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "acceptance",
        mode="deterministic",
        max_budget=0.1,
    )

    assert len(report.scenario_results) == 1
    result = report.scenario_results[0]
    assert result.scenario_id == "happy_path"
    assert result.review is not None
    assert result.review.overall_verdict == "accept"
    assert fake_call.await_count == 1
    assert fake_call.await_args is not None
    kwargs = fake_call.await_args.kwargs
    assert kwargs["task"] == "ac14_review_acceptance"
    assert kwargs["max_budget"] == 0.1


def test_build_suite_acceptance_report_aggregates_examples(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Suite acceptance should aggregate per-example acceptance results."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)

    report = build_suite_acceptance_report(
        output_dir=tmp_path / "suite_acceptance",
        examples_root=EXAMPLES_ROOT,
        mode="deterministic",
        max_budget=0.1,
    )

    assert report.example_count >= 2
    assert report.accepted_examples == report.example_count
    assert report.concern_examples == 0
    assert report.rejected_examples == 0


def test_build_acceptance_report_supports_realistic_input_artifact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Acceptance report should persist realistic-input context when provided."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    realistic_input_path = REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch.json"

    report = build_acceptance_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "acceptance_realistic",
        mode="reference",
        realistic_input_path=realistic_input_path,
        realistic_input_record_index=0,
        max_budget=0.1,
    )

    assert len(report.scenario_results) == 1
    result = report.scenario_results[0]
    assert result.realistic_input is True
    assert result.realistic_input_path == str(realistic_input_path)
    assert isinstance(result.realistic_input_record, dict)
    assert result.realistic_input_record["ticket_id"] == "SUP-10421"
    assert result.outputs_by_component is not None
    assert result.review is not None
    assert fake_call.await_count == 1


def test_build_acceptance_report_supports_realistic_input_deterministic_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Acceptance report should support realistic inputs in deterministic mode."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    realistic_input_path = REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch.json"

    report = build_acceptance_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "acceptance_realistic_deterministic",
        mode="deterministic",
        realistic_input_path=realistic_input_path,
        realistic_input_record_index=0,
        max_budget=0.1,
    )

    assert len(report.scenario_results) == 1
    result = report.scenario_results[0]
    assert result.realistic_input is True
    assert result.realistic_input_path == str(realistic_input_path)
    assert result.outputs_by_component is not None
    assert result.execution_error is None
    assert result.review is not None
    assert fake_call.await_count == 1


def test_build_acceptance_report_supports_incident_realistic_input(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Acceptance report should support a second shipped realistic-input slice."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    realistic_input_path = REPO_ROOT / "examples" / "incident_alert_digest" / "input" / "realistic_alert_batch.json"

    report = build_acceptance_report(
        blueprint_dir=INCIDENT_EXAMPLE_DIR,
        output_dir=tmp_path / "acceptance_incident_realistic",
        mode="deterministic",
        realistic_input_path=realistic_input_path,
        realistic_input_record_index=0,
        max_budget=0.1,
    )

    assert len(report.scenario_results) == 1
    result = report.scenario_results[0]
    assert result.realistic_input is True
    assert result.realistic_input_path == str(realistic_input_path)
    assert isinstance(result.realistic_input_record, dict)
    assert result.realistic_input_record["alert_id"] == "INC-2041"
    assert result.outputs_by_component is not None
    assert result.execution_error is None
    assert result.review is not None
    assert fake_call.await_count == 1

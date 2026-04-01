"""Tests for requirements-aware acceptance artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from ac14.acceptance import (
    _discover_realistic_input_path,
    AcceptanceReviewResponse,
    build_acceptance_report,
    build_realistic_mode_comparison_report,
    build_realistic_suite_acceptance_report,
    build_suite_acceptance_report,
)
from ac14.examples import discover_shipped_blueprints
from ac14.generated_codegen import emit_generated_package
from ac14.loader import load_blueprint_dir
from ac14.packets import compile_packets


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


def _write_llm_codegen_fixture(tmp_path: Path, blueprint_dir: Path) -> Path:
    """Persist fixture-backed LLM codegen responses using deterministic module code."""

    blueprint = load_blueprint_dir(blueprint_dir)
    packet_bundle = compile_packets(blueprint)
    deterministic_package = emit_generated_package(
        packet_bundle,
        tmp_path / f"{blueprint.metadata.blueprint_id}_deterministic_generated",
        generator_kind="deterministic",
    )
    fixture_payload = {
        component_id: {
            "module_code": Path(module_path).read_text(),
            "implementation_notes": ["fixture-backed llm codegen"],
        }
        for component_id, module_path in deterministic_package.module_paths.items()
    }
    fixture_path = tmp_path / f"{blueprint.metadata.blueprint_id}_llm_codegen_fixture.json"
    fixture_path.write_text(json.dumps(fixture_payload, indent=2, sort_keys=True))
    return fixture_path


def _write_blueprint_aware_llm_codegen_fixture(tmp_path: Path) -> Path:
    """Persist fixture-backed LLM codegen responses keyed by blueprint id and component id."""

    fixture_payload: dict[str, dict[str, dict[str, object]]] = {}
    for example in discover_shipped_blueprints(EXAMPLES_ROOT):
        blueprint = load_blueprint_dir(Path(example.blueprint_dir))
        packet_bundle = compile_packets(blueprint)
        deterministic_package = emit_generated_package(
            packet_bundle,
            tmp_path / f"{blueprint.metadata.blueprint_id}_deterministic_generated",
            generator_kind="deterministic",
        )
        fixture_payload[blueprint.metadata.blueprint_id] = {
            component_id: {
                "module_code": Path(module_path).read_text(),
                "implementation_notes": [f"fixture-backed llm codegen for {blueprint.metadata.blueprint_id}"],
            }
            for component_id, module_path in deterministic_package.module_paths.items()
        }
    fixture_path = tmp_path / "blueprint_aware_llm_codegen_fixture.json"
    fixture_path.write_text(json.dumps(fixture_payload, indent=2, sort_keys=True))
    return fixture_path


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


def test_build_acceptance_report_supports_messy_input_csv_reference_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Acceptance report should support the shipped messy CSV asset in reference mode."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    realistic_input_path = (
        REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch_messy.csv"
    )

    report = build_acceptance_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "acceptance_realistic_messy_reference",
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
    assert result.realistic_input_record["ticket_id"] == "SUP-20421"
    assert result.outputs_by_component is not None
    assert result.review is not None
    assert fake_call.await_count == 1


def test_build_acceptance_report_supports_messy_input_csv_deterministic_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Acceptance report should support the shipped messy CSV asset in deterministic mode."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    realistic_input_path = (
        REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch_messy.csv"
    )

    report = build_acceptance_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "acceptance_realistic_messy_deterministic",
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


def test_build_realistic_suite_acceptance_report_supports_realistic_inputs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Realistic suite acceptance should persist one artifact across shipped examples and modes."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)

    report = build_realistic_suite_acceptance_report(
        output_dir=tmp_path / "realistic_suite_acceptance",
        examples_root=EXAMPLES_ROOT,
        modes=["reference", "deterministic"],
        realistic_input_record_index=0,
        max_budget=0.1,
    )

    assert report.example_count >= 2
    assert set(report.modes) == {"reference", "deterministic"}
    assert set(report.mode_summaries) == {"reference", "deterministic"}
    assert report.mode_summaries["reference"].accepted_examples == report.example_count
    assert report.mode_summaries["deterministic"].accepted_examples == report.example_count
    assert (tmp_path / "realistic_suite_acceptance" / "realistic_suite_acceptance_report.json").exists()


def test_build_acceptance_report_supports_realistic_input_llm_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Acceptance report should support realistic inputs in llm mode with fixture-backed codegen."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    monkeypatch.setenv("AC14_LLM_CODEGEN_FIXTURE", str(_write_llm_codegen_fixture(tmp_path, EXAMPLE_DIR)))
    realistic_input_path = REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch.json"

    report = build_acceptance_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "acceptance_realistic_llm",
        mode="llm",
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


def test_build_acceptance_report_supports_messy_input_csv_llm_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Acceptance report should support the shipped messy CSV asset in bounded llm mode."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    monkeypatch.setenv("AC14_LLM_CODEGEN_FIXTURE", str(_write_llm_codegen_fixture(tmp_path, EXAMPLE_DIR)))
    realistic_input_path = (
        REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch_messy.csv"
    )

    report = build_acceptance_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "acceptance_realistic_messy_llm",
        mode="llm",
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


def test_build_realistic_mode_comparison_report_supports_llm(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Realistic-input comparison should persist verdicts across reference, deterministic, and llm."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    monkeypatch.setenv("AC14_LLM_CODEGEN_FIXTURE", str(_write_llm_codegen_fixture(tmp_path, EXAMPLE_DIR)))
    realistic_input_path = REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch.json"

    report = build_realistic_mode_comparison_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "realistic_mode_compare",
        modes=["reference", "deterministic", "llm"],
        realistic_input_path=realistic_input_path,
        realistic_input_record_index=0,
        max_budget=0.1,
    )

    assert report.modes == ["reference", "deterministic", "llm"]
    assert report.verdicts_by_mode == {
        "reference": "accept",
        "deterministic": "accept",
        "llm": "accept",
    }
    assert (tmp_path / "realistic_mode_compare" / "realistic_mode_comparison_report.json").exists()


def test_build_realistic_mode_comparison_report_supports_messy_input_csv_llm_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Realistic-input comparison should support the messy CSV asset across all bounded modes."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    monkeypatch.setenv("AC14_LLM_CODEGEN_FIXTURE", str(_write_llm_codegen_fixture(tmp_path, EXAMPLE_DIR)))
    realistic_input_path = (
        REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch_messy.csv"
    )

    report = build_realistic_mode_comparison_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "realistic_mode_compare_messy_llm",
        modes=["reference", "deterministic", "llm"],
        realistic_input_path=realistic_input_path,
        realistic_input_record_index=0,
        max_budget=0.1,
    )

    assert report.realistic_input_path == str(realistic_input_path)
    assert report.modes == ["reference", "deterministic", "llm"]
    assert report.verdicts_by_mode == {
        "reference": "accept",
        "deterministic": "accept",
        "llm": "accept",
    }
    assert (tmp_path / "realistic_mode_compare_messy_llm" / "realistic_mode_comparison_report.json").exists()


def test_build_realistic_mode_comparison_report_supports_messy_input_csv_non_llm_modes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Realistic-input comparison should support the messy CSV asset across non-LLM modes."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    realistic_input_path = (
        REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch_messy.csv"
    )

    report = build_realistic_mode_comparison_report(
        blueprint_dir=EXAMPLE_DIR,
        output_dir=tmp_path / "realistic_mode_compare_messy_non_llm",
        modes=["reference", "deterministic"],
        realistic_input_path=realistic_input_path,
        realistic_input_record_index=0,
        max_budget=0.1,
    )

    assert report.realistic_input_path == str(realistic_input_path)
    assert report.modes == ["reference", "deterministic"]
    assert report.verdicts_by_mode == {
        "reference": "accept",
        "deterministic": "accept",
    }
    assert (
        tmp_path / "realistic_mode_compare_messy_non_llm" / "realistic_mode_comparison_report.json"
    ).exists()


def test_build_realistic_suite_acceptance_report_supports_llm_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Realistic suite acceptance should support llm mode across shipped examples."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)
    monkeypatch.setenv("AC14_LLM_CODEGEN_FIXTURE", str(_write_blueprint_aware_llm_codegen_fixture(tmp_path)))

    report = build_realistic_suite_acceptance_report(
        output_dir=tmp_path / "realistic_suite_acceptance_llm",
        examples_root=EXAMPLES_ROOT,
        modes=["llm"],
        realistic_input_record_index=0,
        max_budget=0.1,
    )

    assert report.example_count >= 3
    assert report.mode_summaries["llm"].accepted_examples == report.example_count
    assert (tmp_path / "realistic_suite_acceptance_llm" / "realistic_suite_acceptance_report.json").exists()


def test_build_realistic_suite_acceptance_report_supports_realistic_input_profile_selection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Realistic suite acceptance should record explicit missing-profile states."""

    fake_call = AsyncMock(return_value=_fake_review())
    monkeypatch.setattr("ac14.acceptance.acall_llm_structured", fake_call)

    report = build_realistic_suite_acceptance_report(
        output_dir=tmp_path / "realistic_suite_acceptance_messy",
        examples_root=EXAMPLES_ROOT,
        modes=["reference", "deterministic"],
        realistic_input_profile="messy",
        realistic_input_record_index=0,
        max_budget=0.1,
    )

    assert report.realistic_input_profile == "messy"
    assert report.realistic_input_paths["support_ticket_digest"] is not None
    assert report.realistic_input_paths["incident_alert_digest"] is None
    assert report.realistic_input_paths["support_ticket_digest_auth_mix"] is None
    assert report.mode_summaries["reference"].missing_profile_examples == report.example_count - 1
    assert report.mode_summaries["reference"].example_results["support_ticket_digest"] == "accept"
    assert report.mode_summaries["reference"].example_results["incident_alert_digest"] == "missing_profile"


def test_discover_realistic_input_path_supports_structured_non_json_inputs(tmp_path: Path) -> None:
    """Acceptance should discover a supported structured input even when JSON is absent."""

    example_dir = tmp_path / "csv_only_example"
    blueprint_dir = example_dir / "blueprint"
    input_dir = example_dir / "input"
    blueprint_dir.mkdir(parents=True)
    input_dir.mkdir()
    (input_dir / "realistic_ticket_batch.csv").write_text("ticket_id,status\nSUP-1,open\n")

    discovered = _discover_realistic_input_path(
        {
            "example_id": "csv_only_example",
            "blueprint_dir": str(blueprint_dir),
            "blueprint_id": "csv_only_blueprint",
            "name": "CSV Only Example",
        },
    )

    assert discovered == input_dir / "realistic_ticket_batch.csv"

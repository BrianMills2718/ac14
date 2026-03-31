"""Tests for evidence-backed dependency planning artifacts."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from ac14.dependency_planning import (
    DependencyEvidence,
    DependencyPlanningResponse,
    DependencyQuestion,
    DependencyRecommendation,
    build_dependency_plan,
)
from ac14.discovery import build_discovery_artifact
from ac14.retrieval import (
    RepoRetrievalQuery,
    RetrievedRepoMatch,
    RetrievedWebDocument,
    WebRetrievalQuery,
    build_external_retrieval_artifact,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_build_dependency_plan_persists_artifact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Dependency planning should persist a validated advisory artifact."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"ticket_id": "T-1", "body": "Login is broken"}]')
    build_external_retrieval_artifact(
        output_dir=tmp_path / "retrieval",
        web_queries=[WebRetrievalQuery(query="pydantic docs")],
        repo_queries=[RepoRetrievalQuery(query="packet compiler", repos=["example/ac14"])],
        web_retriever=lambda _query: [
            RetrievedWebDocument(
                query="pydantic docs",
                provider="fixture",
                url="https://docs.pydantic.dev/latest/",
                title="Pydantic",
                publisher="Pydantic",
                snippet="schema docs",
                preview="Pydantic schema docs preview.",
            ),
        ],
        repo_retriever=lambda _query: [
            RetrievedRepoMatch(
                query="packet compiler",
                repository="example/ac14",
                path="ac14/packets.py",
                url="https://github.com/example/ac14/blob/main/ac14/packets.py",
            ),
        ],
    )
    build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
        requested_packages=["pydantic", "ac14-missing-lib"],
        retrieval_artifact_paths=[tmp_path / "retrieval" / "external_retrieval_artifact.json"],
    )
    discovery_artifact_path = tmp_path / "discovery" / "discovery_artifact.json"

    fake_response = DependencyPlanningResponse(
        planning_summary="Reuse pydantic and investigate ac14-missing-lib before adding it.",
        recommendations=[
            DependencyRecommendation(
                package_name="pydantic",
                action="reuse",
                capability_need="Typed schema contracts for packets and blueprint models.",
                justification="Pydantic is already installed and directly matches the structured-schema need.",
                already_installed=True,
                install_command=None,
                evidence=[
                    DependencyEvidence(
                        source="environment",
                        locator="pydantic",
                        detail="The environment inventory shows pydantic installed.",
                    ),
                    DependencyEvidence(
                        source="external_retrieval",
                        locator="https://docs.pydantic.dev/latest/",
                        detail="Retrieved docs support schema-driven validation and typed models.",
                    ),
                ],
            ),
            DependencyRecommendation(
                    package_name="ac14-missing-lib",
                action="investigate",
                capability_need="Human-readable operator output if richer terminal rendering becomes necessary.",
                justification="The package is not installed and the current proof slice does not yet require it.",
                already_installed=False,
                install_command=None,
                evidence=[
                    DependencyEvidence(
                        source="environment",
                        locator="ac14-missing-lib",
                        detail="The environment inventory shows ac14-missing-lib is not installed.",
                    ),
                    DependencyEvidence(
                        source="open_concern",
                        locator="dependency ac14-missing-lib is not installed in the current environment",
                        detail="The concern is already carried forward from discovery.",
                    ),
                ],
            ),
        ],
        standard_library_notes=[
            "Use pathlib, json, and subprocess from the standard library for file and CLI glue.",
        ],
        open_questions=[
            DependencyQuestion(
                question="Does the first draft bundle need any richer operator UI than plain JSON output?",
                why_it_matters="It determines whether a terminal-formatting dependency is justified.",
            ),
        ],
    )
    fake_call = AsyncMock(return_value=(fake_response, object()))
    monkeypatch.setattr("ac14.dependency_planning.acall_llm_structured", fake_call)

    plan = build_dependency_plan(
        discovery_artifact_path=discovery_artifact_path,
        output_dir=tmp_path / "dependency_plan",
        requirements=["preserve typed schema contracts", "avoid unnecessary dependencies"],
        max_budget=0.1,
    )

    assert plan.requirements == [
        "preserve typed schema contracts",
        "avoid unnecessary dependencies",
    ]
    assert plan.recommendations[0].package_name == "pydantic"
    assert (tmp_path / "dependency_plan" / "dependency_plan.json").exists()
    assert fake_call.await_count == 1
    assert fake_call.await_args is not None
    kwargs = fake_call.await_args.kwargs
    assert kwargs["task"] == "ac14_dependency_plan"
    assert kwargs["max_budget"] == 0.1


def test_build_dependency_plan_requires_requirements(tmp_path: Path) -> None:
    """Dependency planning should fail loud when no requirements are provided."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"ticket_id": "T-1"}]')
    build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
    )

    with pytest.raises(ValueError, match="requires at least one requirement"):
        build_dependency_plan(
            discovery_artifact_path=tmp_path / "discovery" / "discovery_artifact.json",
            output_dir=tmp_path / "dependency_plan",
            requirements=[],
        )


def test_build_dependency_plan_fails_on_inconsistent_reuse(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Dependency planning should fail loud when action conflicts with environment state."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"ticket_id": "T-1"}]')
    build_discovery_artifact(
        input_path=input_path,
        output_dir=tmp_path / "discovery",
        project_root=REPO_ROOT,
        requested_packages=["ac14-missing-lib"],
    )
    fake_response = DependencyPlanningResponse(
        planning_summary="Attempt to reuse a missing package.",
        recommendations=[
            DependencyRecommendation(
                package_name="ac14-missing-lib",
                action="reuse",
                capability_need="Pretty terminal output.",
                justification="Incorrectly claims reuse is possible.",
                already_installed=False,
                install_command=None,
                evidence=[
                    DependencyEvidence(
                        source="environment",
                        locator="ac14-missing-lib",
                        detail="ac14-missing-lib is missing from the environment inventory.",
                    ),
                ],
            ),
        ],
        standard_library_notes=[],
        open_questions=[],
    )
    fake_call = AsyncMock(return_value=(fake_response, object()))
    monkeypatch.setattr("ac14.dependency_planning.acall_llm_structured", fake_call)

    with pytest.raises(ValueError, match="cannot reuse a missing package"):
        build_dependency_plan(
            discovery_artifact_path=tmp_path / "discovery" / "discovery_artifact.json",
            output_dir=tmp_path / "dependency_plan",
            requirements=["improve operator output"],
        )

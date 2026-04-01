"""Smoke tests for Makefile proof-surface targets."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from ac14.blueprint_planning import (
    DraftBlueprintPlanArtifact,
    PlannedComponent,
    PlannedPort,
    PlannedScenario,
    PlannedSchema,
    PlannedSchemaField,
    PlanningQuestion,
)
from ac14.dependency_planning import (
    DependencyEvidence,
    DependencyPlanningArtifact,
    DependencyQuestion,
    DependencyRecommendation,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "examples" / "support_ticket_digest" / "blueprint"
EXAMPLES_ROOT = REPO_ROOT / "examples"


def _write_plan_artifact(path: Path) -> Path:
    """Persist a deterministic planning artifact for Make-based authoring tests."""

    artifact = DraftBlueprintPlanArtifact(
        discovery_artifact_path=str(path.parent / "discovery_artifact.json"),
        requirements=["normalize discovered ticket input", "keep packets bounded"],
        discovery_open_concerns=[],
        planning_summary="Use a single source component as the first draft bundle.",
        proposed_schemas=[
            PlannedSchema(
                schema_name="RawTicket",
                kind="record",
                description="Normalized raw ticket input.",
                fields=[
                    PlannedSchemaField(
                        field_name="ticket_id",
                        field_type="str",
                        description="Stable ticket identifier.",
                    ),
                ],
            ),
        ],
        proposed_components=[
            PlannedComponent(
                component_id="ticket_ingest",
                semantic_responsibility="ingest_ticket",
                purpose="Normalize the discovered input into RawTicket.",
                input_ports=[],
                output_ports=[
                    PlannedPort(
                        port_name="raw_ticket",
                        schema_name="RawTicket",
                        description="Normalized ticket payload.",
                    ),
                ],
                packet_focus=["normalize incoming fields", "preserve ticket identity"],
                dependency_notes=["no external libraries required"],
            ),
        ],
        proposed_bindings=[],
        proposed_scenarios=[
            PlannedScenario(
                scenario_id="happy_path",
                kind="semantic_acceptance",
                description="Review one realistic ticket end to end.",
                requirement_focus=["normalize ticket input", "preserve meaning"],
            ),
        ],
        packetization_notes=["Keep the first packet focused on source normalization only."],
        dependency_decisions=["Stay within the current environment for the first draft."],
        open_questions=[
            PlanningQuestion(
                question="Should tags be preserved as a field in RawTicket?",
                why_it_matters="It changes schema shape before freeze.",
            ),
        ],
    )
    path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))
    return path


def _write_dependency_plan_artifact(path: Path) -> Path:
    """Persist a deterministic dependency-planning artifact for Make probe tests."""

    artifact = DependencyPlanningArtifact(
        discovery_artifact_path=str(path.parent / "discovery_artifact.json"),
        requirements=["preserve typed schema contracts"],
        carried_forward_concerns=[],
        planning_summary="Reuse pydantic and block installation by default.",
        recommendations=[
            DependencyRecommendation(
                package_name="pydantic",
                action="reuse",
                capability_need="Typed schema contracts for blueprint models.",
                justification="Already installed and used throughout AC14.",
                already_installed=True,
                install_command=None,
                evidence=[
                    DependencyEvidence(
                        source="environment",
                        locator="pydantic",
                        detail="pydantic is already installed in the current environment.",
                    ),
                ],
            ),
            DependencyRecommendation(
                package_name="ac14-missing-lib",
                action="install",
                capability_need="Demonstrate explicit install probing for a missing package.",
                justification="The package is missing and needs an explicit recommendation.",
                already_installed=False,
                install_command="pip install ac14-missing-lib",
                evidence=[
                    DependencyEvidence(
                        source="environment",
                        locator="ac14-missing-lib",
                        detail="The package is missing from the current environment.",
                    ),
                ],
            ),
        ],
        standard_library_notes=[],
        open_questions=[
            DependencyQuestion(
                question="Should install probes default to review-only mode?",
                why_it_matters="It changes the default environment-mutation policy.",
            ),
        ],
    )
    path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))
    return path


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
    assert "discover-input" in result.stdout
    assert "inspect-environment" in result.stdout
    assert "inspect-project-context" in result.stdout
    assert "retrieve-context" in result.stdout
    assert "plan-dependencies" in result.stdout
    assert "probe-dependencies" in result.stdout
    assert "draft-blueprint-plan" in result.stdout
    assert "materialize-draft-bundle" in result.stdout
    assert "decide-freeze" in result.stdout
    assert "prove-example" in result.stdout
    assert "fresh-runs" in result.stdout
    assert "compare-generators" in result.stdout
    assert "acceptance-review" in result.stdout
    assert "semantic-compare" in result.stdout
    assert "prove-suite" in result.stdout
    assert "compare-suite" in result.stdout
    assert "semantic-compare-suite" in result.stdout
    assert "acceptance-review-suite" in result.stdout
    assert "recommend-default-generator" in result.stdout


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


def test_make_discover_input_runs_end_to_end(tmp_path: Path) -> None:
    """Make discovery target should persist a discovery artifact."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"id": 1, "status": "open"}, {"id": "2", "status": "closed"}]')
    output_dir = tmp_path / "discovery"
    result = subprocess.run(
        [
            "make",
            "discover-input",
            f"INPUT={input_path}",
            f"OUTPUT={output_dir}",
            "PACKAGES=pydantic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "discovery_artifact.json").exists()


def test_make_inspect_environment_runs_end_to_end(tmp_path: Path) -> None:
    """Make environment target should persist an environment inventory artifact."""

    output_dir = tmp_path / "environment"
    result = subprocess.run(
        [
            "make",
            "inspect-environment",
            f"OUTPUT={output_dir}",
            "PACKAGES=pydantic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "environment_inventory.json").exists()


def test_make_probe_dependencies_runs_end_to_end(tmp_path: Path) -> None:
    """Make dependency probe target should persist a reviewable artifact."""

    dependency_plan_path = _write_dependency_plan_artifact(tmp_path / "dependency_plan.json")
    output_dir = tmp_path / "dependency_probe"
    result = subprocess.run(
        [
            "make",
            "probe-dependencies",
            f"DEPENDENCY_PLAN={dependency_plan_path}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "dependency_execution_artifact.json").exists()


def test_make_inspect_project_context_runs_end_to_end(tmp_path: Path) -> None:
    """Make project-context target should persist a local doc inventory artifact."""

    output_dir = tmp_path / "project_context"
    result = subprocess.run(
        [
            "make",
            "inspect-project-context",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "project_context_inventory.json").exists()


def test_make_retrieve_context_runs_with_fixture_env(tmp_path: Path) -> None:
    """Make retrieval target should persist an external retrieval artifact."""

    web_fixture = tmp_path / "web_fixture.json"
    web_fixture.write_text(
        json.dumps(
            {
                "incident response playbook": [
                    {
                        "query": "incident response playbook",
                        "provider": "fixture",
                        "url": "https://example.com/playbook",
                        "title": "Playbook",
                        "publisher": "Example",
                        "snippet": "playbook snippet",
                        "preview": "playbook preview",
                    }
                ]
            }
        )
    )
    repo_fixture = tmp_path / "repo_fixture.json"
    repo_fixture.write_text(
        json.dumps(
            {
                "packet compiler": [
                    {
                        "query": "packet compiler",
                        "repository": "example/ac14",
                        "path": "ac14/packets.py",
                        "url": "https://github.com/example/ac14/blob/main/ac14/packets.py",
                    }
                ]
            }
        )
    )
    output_dir = tmp_path / "retrieval"
    env = os.environ.copy()
    env["AC14_WEB_RETRIEVAL_FIXTURE"] = str(web_fixture)
    env["AC14_REPO_RETRIEVAL_FIXTURE"] = str(repo_fixture)
    result = subprocess.run(
        [
            "make",
            "retrieve-context",
            f"OUTPUT={output_dir}",
            "WEB_QUERY=incident response playbook",
            "REPO_QUERY=packet compiler",
            "REPOS=example/ac14",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "external_retrieval_artifact.json").exists()


def test_make_plan_dependencies_runs_with_fixture_env(tmp_path: Path) -> None:
    """Make dependency-planning target should persist an advisory artifact."""

    discovery_path = tmp_path / "discovery_artifact.json"
    discovery_path.write_text(
        json.dumps(
            {
                "input_inspection": {
                    "input_path": str(tmp_path / "sample.json"),
                    "input_format": "json",
                    "root_kind": "list",
                    "sample_count": 1,
                    "truncated": False,
                    "sample_records": [{"ticket_id": "T-1"}],
                    "field_summaries": [],
                    "concerns": [],
                },
                "environment_inventory": {
                    "project_root": str(REPO_ROOT),
                    "python_version": "3.12.0",
                    "platform": "linux",
                    "dependency_statuses": [
                        {
                            "package_name": "pydantic",
                            "sources": ["requested"],
                            "installed": True,
                            "version": "2.12.0",
                        },
                        {
                            "package_name": "ac14-missing-lib",
                            "sources": ["requested"],
                            "installed": False,
                            "version": None,
                        },
                    ],
                    "concerns": ["dependency ac14-missing-lib is not installed in the current environment"],
                },
                "project_context_inventory": {
                    "project_root": str(REPO_ROOT),
                    "document_count": 1,
                    "truncated": False,
                    "documents": [
                        {
                            "path": str(REPO_ROOT / "README.md"),
                            "category": "readme",
                            "title": "AC14",
                            "preview": "AC14 overview",
                            "line_count": 10,
                        }
                    ],
                    "concerns": [],
                },
                "external_retrieval_summaries": [
                    {
                        "artifact_path": str(tmp_path / "external_retrieval_artifact.json"),
                        "web_document_count": 1,
                        "repo_match_count": 1,
                        "web_urls": ["https://docs.pydantic.dev/latest/"],
                        "repo_paths": ["ac14/packets.py"],
                        "concerns": [],
                    }
                ],
                "open_concerns": ["dependency ac14-missing-lib is not installed in the current environment"],
            }
        )
    )
    fixture_path = tmp_path / "dependency_plan_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "planning_summary": "Reuse pydantic and investigate ac14-missing-lib.",
                "recommendations": [
                    {
                        "package_name": "pydantic",
                        "action": "reuse",
                        "capability_need": "typed schema contracts",
                        "justification": "pydantic is already installed and fits the schema need",
                        "already_installed": True,
                        "install_command": None,
                        "evidence": [
                            {
                                "source": "environment",
                                "locator": "pydantic",
                                "detail": "Installed in the environment inventory",
                            },
                            {
                                "source": "external_retrieval",
                                "locator": "https://docs.pydantic.dev/latest/",
                                "detail": "Retrieved docs confirm schema support",
                            },
                        ],
                    }
                ],
                "standard_library_notes": ["pathlib and json are sufficient for file glue"],
                "open_questions": [],
            }
        )
    )
    output_dir = tmp_path / "dependency_plan"
    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(fixture_path)
    result = subprocess.run(
        [
            "make",
            "plan-dependencies",
            f"DISCOVERY={discovery_path}",
            f"OUTPUT={output_dir}",
            "REQUIREMENTS=preserve typed schema contracts",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "dependency_plan.json").exists()


def test_make_draft_blueprint_plan_runs_with_dependency_plan(tmp_path: Path) -> None:
    """Make draft-planning target should carry dependency-plan provenance."""

    discovery_path = tmp_path / "discovery_artifact.json"
    discovery_path.write_text(
        json.dumps(
            {
                "input_inspection": {
                    "input_path": str(tmp_path / "sample.json"),
                    "input_format": "json",
                    "root_kind": "list",
                    "sample_count": 1,
                    "truncated": False,
                    "sample_records": [{"ticket_id": "T-1"}],
                    "field_summaries": [],
                    "concerns": [],
                },
                "environment_inventory": {
                    "project_root": str(REPO_ROOT),
                    "python_version": "3.12.0",
                    "platform": "linux",
                    "dependency_statuses": [
                        {
                            "package_name": "pydantic",
                            "sources": ["requested"],
                            "installed": True,
                            "version": "2.12.0",
                        }
                    ],
                    "concerns": [],
                },
                "project_context_inventory": {
                    "project_root": str(REPO_ROOT),
                    "document_count": 1,
                    "truncated": False,
                    "documents": [
                        {
                            "path": str(REPO_ROOT / "README.md"),
                            "category": "readme",
                            "title": "AC14",
                            "preview": "AC14 overview",
                            "line_count": 10,
                        }
                    ],
                    "concerns": [],
                },
                "external_retrieval_summaries": [],
                "open_concerns": [],
            }
        )
    )
    dependency_plan_path = tmp_path / "dependency_plan.json"
    dependency_plan_path.write_text(
        json.dumps(
            {
                "discovery_artifact_path": str(discovery_path),
                "requirements": ["reuse installed schema tooling"],
                "carried_forward_concerns": [],
                "planning_summary": "Reuse pydantic for typed schema contracts.",
                "recommendations": [
                    {
                        "package_name": "pydantic",
                        "action": "reuse",
                        "capability_need": "typed schema contracts",
                        "justification": "already installed",
                        "already_installed": True,
                        "install_command": None,
                        "evidence": [
                            {
                                "source": "environment",
                                "locator": "pydantic",
                                "detail": "Installed in the environment inventory",
                            }
                        ],
                    }
                ],
                "standard_library_notes": [],
                "open_questions": [
                    {
                        "question": "Is any additional serialization library needed?",
                        "why_it_matters": "It changes dependency scope before freeze.",
                    }
                ],
            }
        )
    )
    fixture_path = tmp_path / "draft_blueprint_plan_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "planning_summary": "Use a single source component as the first draft bundle.",
                "proposed_schemas": [
                    {
                        "schema_name": "RawTicket",
                        "kind": "record",
                        "description": "Normalized raw ticket input.",
                        "fields": [
                            {
                                "field_name": "ticket_id",
                                "field_type": "str",
                                "description": "Stable ticket identifier.",
                            }
                        ],
                    }
                ],
                "proposed_components": [
                    {
                        "component_id": "ticket_ingest",
                        "semantic_responsibility": "ingest_ticket",
                        "purpose": "Normalize the discovered input into RawTicket.",
                        "input_ports": [],
                        "output_ports": [
                            {
                                "port_name": "raw_ticket",
                                "schema_name": "RawTicket",
                                "description": "Normalized ticket payload.",
                            }
                        ],
                        "packet_focus": ["normalize incoming fields", "preserve ticket identity"],
                        "dependency_notes": ["reuse pydantic for schema models"],
                    }
                ],
                "proposed_bindings": [],
                "proposed_scenarios": [
                    {
                        "scenario_id": "happy_path",
                        "kind": "semantic_acceptance",
                        "description": "Review one realistic ticket end to end.",
                        "requirement_focus": ["normalize ticket input", "preserve meaning"],
                    }
                ],
                "packetization_notes": ["Keep the first packet focused on source normalization only."],
                "dependency_decisions": ["Reuse pydantic for schema contracts."],
                "open_questions": [
                    {
                        "question": "Should tags be preserved as a field in RawTicket?",
                        "why_it_matters": "It changes schema shape before freeze.",
                    }
                ],
            }
        )
    )
    output_dir = tmp_path / "draft_plan"
    env = os.environ.copy()
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(fixture_path)
    result = subprocess.run(
        [
            "make",
            "draft-blueprint-plan",
            f"DISCOVERY={discovery_path}",
            f"DEPENDENCY_PLAN={dependency_plan_path}",
            f"OUTPUT={output_dir}",
            "REQUIREMENTS=normalize discovered ticket input",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "draft_blueprint_plan.json").read_text())
    assert payload["dependency_plan_path"] == str(dependency_plan_path)
    assert payload["dependency_recommendations"] == ["reuse pydantic: typed schema contracts"]


def test_make_materialize_draft_bundle_runs_end_to_end(tmp_path: Path) -> None:
    """Make authoring target should persist the draft bundle and readiness report."""

    plan_path = _write_plan_artifact(tmp_path / "draft_blueprint_plan.json")
    output_dir = tmp_path / "draft_bundle"
    result = subprocess.run(
        [
            "make",
            "materialize-draft-bundle",
            f"PLAN={plan_path}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "freeze_readiness_report.json").exists()


def test_make_decide_freeze_runs_end_to_end(tmp_path: Path) -> None:
    """Make freeze-decision target should persist decision and remediation artifacts."""

    output_dir = tmp_path / "freeze_decision"
    result = subprocess.run(
        [
            "make",
            "decide-freeze",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "freeze_decision.json").exists()
    assert (output_dir / "freeze_remediation_plan.json").exists()
    assert (output_dir / "frozen_bundle" / "metadata.yaml").exists()


def test_make_prove_suite_runs_end_to_end(tmp_path: Path) -> None:
    """Make suite proof target should build aggregate suite artifacts."""

    output_dir = tmp_path / "suite_proof"
    result = subprocess.run(
        [
            "make",
            "prove-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "TRIALS=1",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "suite_proof_report.json").exists()


def test_make_compare_suite_deterministic_only(tmp_path: Path) -> None:
    """Make suite comparison target should build aggregate comparison artifacts."""

    output_dir = tmp_path / "suite_compare"
    result = subprocess.run(
        [
            "make",
            "compare-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "TRIALS=1",
            "GENERATORS=deterministic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "suite_comparison_report.json").exists()


def test_make_semantic_compare_suite_deterministic_only(tmp_path: Path) -> None:
    """Make semantic suite target should build aggregate semantic artifacts."""

    output_dir = tmp_path / "suite_semantic"
    result = subprocess.run(
        [
            "make",
            "semantic-compare-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "MODES=reference deterministic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "suite_semantic_comparison_report.json").exists()


def test_make_recommend_default_generator_deterministic_only(tmp_path: Path) -> None:
    """Make recommendation target should produce the default-generator artifact."""

    output_dir = tmp_path / "recommendation"
    result = subprocess.run(
        [
            "make",
            "recommend-default-generator",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "GENERATORS=deterministic",
            "TRIALS=1",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "default_generator_recommendation.json").exists()

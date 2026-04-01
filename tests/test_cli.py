"""CLI smoke tests for AC14 proof-surface commands."""

from __future__ import annotations

import json
import os
import subprocess
import sys
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
    """Persist a minimal deterministic planning artifact for CLI authoring tests."""

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
    """Persist a deterministic dependency-planning artifact for CLI probe tests."""

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


def test_cli_verify_blueprint() -> None:
    """Blueprint verification command should exit cleanly for the shipped example."""

    result = subprocess.run(
        [sys.executable, "-m", "ac14", "verify-blueprint", str(EXAMPLE_DIR)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["passed"] is True


def test_cli_generate_components(tmp_path: Path) -> None:
    """Generated-components command should emit the package manifest."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "generate-components",
            str(EXAMPLE_DIR),
            "--output-dir",
            str(tmp_path / "generated"),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert "ticket_parser" in payload["module_paths"]


def test_cli_discover_input(tmp_path: Path) -> None:
    """Discovery command should persist a pre-freeze discovery artifact."""

    input_path = tmp_path / "sample.json"
    input_path.write_text('[{"id": 1, "status": "open"}, {"id": "2", "status": "closed"}]')

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "discover-input",
            str(input_path),
            "--output-dir",
            str(tmp_path / "discovery"),
            "--project-root",
            str(REPO_ROOT),
            "--packages",
            "pydantic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["input_inspection"]["input_format"] == "json"
    assert (tmp_path / "discovery" / "discovery_artifact.json").exists()


def test_cli_inspect_environment(tmp_path: Path) -> None:
    """Environment inspection command should persist dependency inventory."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "inspect-environment",
            "--output-dir",
            str(tmp_path / "environment"),
            "--project-root",
            str(REPO_ROOT),
            "--packages",
            "pydantic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    dependency_names = {status["package_name"] for status in payload["dependency_statuses"]}
    assert "pydantic" in dependency_names
    assert (tmp_path / "environment" / "environment_inventory.json").exists()


def test_cli_probe_dependencies(tmp_path: Path) -> None:
    """Dependency execution probe command should persist a reviewable artifact."""

    dependency_plan_path = _write_dependency_plan_artifact(tmp_path / "dependency_plan.json")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "probe-dependencies",
            str(dependency_plan_path),
            "--output-dir",
            str(tmp_path / "dependency_probe"),
            "--project-root",
            str(REPO_ROOT),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["execution_mode"] == "check_only"
    package_names = {entry["package_name"] for entry in payload["results"]}
    assert {"pydantic", "ac14-missing-lib"} <= package_names
    assert (tmp_path / "dependency_probe" / "dependency_execution_artifact.json").exists()


def test_cli_inspect_project_context(tmp_path: Path) -> None:
    """Project-context inspection command should persist local doc inventory."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "inspect-project-context",
            "--output-dir",
            str(tmp_path / "project_context"),
            "--project-root",
            str(REPO_ROOT),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["document_count"] >= 2
    assert (tmp_path / "project_context" / "project_context_inventory.json").exists()


def test_cli_retrieve_context_with_fixture_env(tmp_path: Path) -> None:
    """Retrieval command should persist reviewable artifacts with fixture-backed inputs."""

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

    env = os.environ.copy()
    env["AC14_WEB_RETRIEVAL_FIXTURE"] = str(web_fixture)
    env["AC14_REPO_RETRIEVAL_FIXTURE"] = str(repo_fixture)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "retrieve-context",
            "--output-dir",
            str(tmp_path / "retrieval"),
            "--web-query",
            "incident response playbook",
            "--repo-query",
            "packet compiler",
            "--repo",
            "example/ac14",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload["web_documents"]) == 1
    assert len(payload["repo_matches"]) == 1
    assert (tmp_path / "retrieval" / "external_retrieval_artifact.json").exists()


def test_cli_plan_dependencies_with_fixture_env(tmp_path: Path) -> None:
    """Dependency-planning command should persist an advisory artifact with fixture-backed inputs."""

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
                    },
                    {
                        "package_name": "ac14-missing-lib",
                        "action": "investigate",
                        "capability_need": "optional terminal rendering",
                        "justification": "not installed and not yet necessary",
                        "already_installed": False,
                        "install_command": None,
                        "evidence": [
                            {
                                "source": "environment",
                                "locator": "ac14-missing-lib",
                                "detail": "Missing from the environment inventory",
                            },
                            {
                                "source": "open_concern",
                                "locator": "dependency ac14-missing-lib is not installed in the current environment",
                                "detail": "Carried forward discovery concern",
                            },
                        ],
                    },
                ],
                "standard_library_notes": ["pathlib and json are sufficient for file glue"],
                "open_questions": [
                    {
                        "question": "Do operators need rich terminal rendering in the first proof slice?",
                        "why_it_matters": "It determines whether a new terminal-rendering dependency should be installed.",
                    }
                ],
            }
        )
    )

    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(fixture_path)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "plan-dependencies",
            str(discovery_path),
            "--output-dir",
            str(tmp_path / "dependency_plan"),
            "--requirements",
            "preserve",
            "typed",
            "schema",
            "contracts",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload["recommendations"]) == 2
    assert (tmp_path / "dependency_plan" / "dependency_plan.json").exists()


def test_cli_draft_blueprint_plan_uses_dependency_plan(tmp_path: Path) -> None:
    """Draft planning should persist dependency-plan provenance when supplied."""

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
    dependency_execution_path = tmp_path / "dependency_execution_artifact.json"
    dependency_execution_path.write_text(
        json.dumps(
            {
                "dependency_plan_path": str(dependency_plan_path),
                "execution_mode": "check_only",
                "planning_summary": "Reuse pydantic for typed schema contracts.",
                "carried_forward_questions": [],
                "results": [
                    {
                        "package_name": "pydantic",
                        "action": "reuse",
                        "result": "confirmed",
                        "summary": "reuse probe confirmed the package is already available",
                        "mutation_permitted": False,
                        "mutation_attempted": False,
                        "attempted_command": None,
                        "command_exit_code": None,
                        "before": {
                            "package_name": "pydantic",
                            "installed": True,
                            "version": "2.11.0",
                            "top_level_modules": ["pydantic"],
                            "discoverable_modules": ["pydantic"],
                        },
                        "after": {
                            "package_name": "pydantic",
                            "installed": True,
                            "version": "2.11.0",
                            "top_level_modules": ["pydantic"],
                            "discoverable_modules": ["pydantic"],
                        },
                        "observations": ["checked installed distribution state for pydantic"],
                    }
                ],
                "environment_observations": ["install mutation was disabled for this run"],
            }
        )
    )
    fixture_path = tmp_path / "draft_blueprint_plan_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "planning_summary": "Use a source parser and one sink to keep packets bounded.",
                "proposed_schemas": [
                    {
                        "schema_name": "RawTicket",
                        "kind": "record",
                        "description": "Normalized raw ticket shape.",
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
                        "purpose": "Normalize the discovered ticket input into a source schema.",
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
                "packetization_notes": ["Keep the source component packet focused on normalization only."],
                "dependency_decisions": ["Reuse pydantic for schema contracts."],
                "open_questions": [
                    {
                        "question": "Should ticket tags become an explicit field in RawTicket?",
                        "why_it_matters": "It changes source schema shape before freeze.",
                    }
                ],
            }
        )
    )

    env = os.environ.copy()
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(fixture_path)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "draft-blueprint-plan",
            str(discovery_path),
            "--output-dir",
            str(tmp_path / "draft_plan"),
            "--dependency-plan",
            str(dependency_plan_path),
            "--dependency-execution",
            str(dependency_execution_path),
            "--requirements",
            "normalize",
            "discovered",
            "ticket",
            "input",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["dependency_plan_path"] == str(dependency_plan_path)
    assert payload["dependency_execution_artifact_path"] == str(dependency_execution_path)
    assert payload["dependency_recommendations"] == ["reuse pydantic: typed schema contracts"]
    assert (tmp_path / "draft_plan" / "draft_blueprint_plan.json").exists()


def test_cli_materialize_draft_bundle(tmp_path: Path) -> None:
    """Draft bundle materialization command should write a readiness-backed bundle."""

    plan_path = _write_plan_artifact(tmp_path / "draft_blueprint_plan.json")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "materialize-draft-bundle",
            str(plan_path),
            "--output-dir",
            str(tmp_path / "draft_bundle"),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert Path(payload["freeze_readiness_report_path"]).exists()


def test_cli_decide_freeze_promotes_ready_bundle(tmp_path: Path) -> None:
    """Freeze decision command should emit remediation metadata as well."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "decide-freeze",
            str(EXAMPLE_DIR),
            "--output-dir",
            str(tmp_path / "freeze_decision"),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["approved"] is True
    assert Path(payload["promoted_bundle_dir"]).exists()
    assert Path(payload["remediation_plan_path"]).exists()


def test_cli_prove_example(tmp_path: Path) -> None:
    """Proof command should build a persisted evidence bundle."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "prove-example",
            str(EXAMPLE_DIR),
            "--output-dir",
            str(tmp_path / "proof"),
            "--fresh-run-trials",
            "2",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert Path(payload["packet_test_report_path"]).exists()
    assert Path(payload["fresh_run_summary_path"]).exists()


def test_cli_fresh_runs(tmp_path: Path) -> None:
    """Fresh-runs command should emit a summary with the requested trial count."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "fresh-runs",
            str(EXAMPLE_DIR),
            "--output-dir",
            str(tmp_path / "fresh_runs"),
            "--trials",
            "2",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["trial_count"] == 2


def test_cli_compare_generators_deterministic_only(tmp_path: Path) -> None:
    """Comparison command should write a persisted report."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "compare-generators",
            str(EXAMPLE_DIR),
            "--output-dir",
            str(tmp_path / "comparison"),
            "--fresh-run-trials",
            "2",
            "--generators",
            "deterministic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert len(payload["runs"]) == 1


def test_cli_acceptance_review_help() -> None:
    """Acceptance-review help should expose the command without running live evaluation."""

    result = subprocess.run(
        [sys.executable, "-m", "ac14", "acceptance-review", "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--mode" in result.stdout


def test_cli_discover_input_help() -> None:
    """Discover-input help should expose the discovery command."""

    result = subprocess.run(
        [sys.executable, "-m", "ac14", "discover-input", "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--max-samples" in result.stdout


def test_cli_draft_blueprint_plan_help() -> None:
    """Draft-blueprint-plan help should expose the planning command."""

    result = subprocess.run(
        [sys.executable, "-m", "ac14", "draft-blueprint-plan", "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--requirements" in result.stdout


def test_cli_materialize_draft_bundle_help() -> None:
    """Materialize-draft-bundle help should expose the authoring command."""

    result = subprocess.run(
        [sys.executable, "-m", "ac14", "materialize-draft-bundle", "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--output-dir" in result.stdout


def test_cli_decide_freeze_help() -> None:
    """Decide-freeze help should expose the promotion command."""

    result = subprocess.run(
        [sys.executable, "-m", "ac14", "decide-freeze", "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--readiness-report" in result.stdout


def test_cli_semantic_compare_deterministic_only(tmp_path: Path) -> None:
    """Semantic comparison command should emit a persisted semantic report."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "semantic-compare",
            str(EXAMPLE_DIR),
            "--output-dir",
            str(tmp_path / "semantic"),
            "--modes",
            "reference",
            "deterministic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["runnable_scenario_count"] == 2


def test_cli_list_examples() -> None:
    """List-examples command should return the shipped suite."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "list-examples",
            "--examples-root",
            str(EXAMPLES_ROOT),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert len(payload) >= 2


def test_cli_prove_suite(tmp_path: Path) -> None:
    """Suite proof command should build an aggregate proof artifact."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "prove-suite",
            "--output-dir",
            str(tmp_path / "suite_proof"),
            "--examples-root",
            str(EXAMPLES_ROOT),
            "--fresh-run-trials",
            "1",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["example_count"] >= 2


def test_cli_compare_suite_deterministic_only(tmp_path: Path) -> None:
    """Suite comparison command should build an aggregate comparison artifact."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "compare-suite",
            "--output-dir",
            str(tmp_path / "suite_compare"),
            "--examples-root",
            str(EXAMPLES_ROOT),
            "--fresh-run-trials",
            "1",
            "--generators",
            "deterministic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["example_count"] >= 2


def test_cli_acceptance_review_suite_help() -> None:
    """Acceptance-review-suite help should expose the suite command."""

    result = subprocess.run(
        [sys.executable, "-m", "ac14", "acceptance-review-suite", "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--examples-root" in result.stdout


def test_cli_semantic_compare_suite_deterministic_only(tmp_path: Path) -> None:
    """Suite semantic comparison command should build aggregate semantic artifacts."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "semantic-compare-suite",
            "--output-dir",
            str(tmp_path / "suite_semantic"),
            "--examples-root",
            str(EXAMPLES_ROOT),
            "--modes",
            "reference",
            "deterministic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["example_count"] >= 2


def test_cli_recommend_default_generator_deterministic_only(tmp_path: Path) -> None:
    """Recommendation command should keep deterministic as the default in the local lane."""

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "recommend-default-generator",
            "--output-dir",
            str(tmp_path / "recommendation"),
            "--examples-root",
            str(EXAMPLES_ROOT),
            "--generators",
            "deterministic",
            "--fresh-run-trials",
            "1",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["recommended_default"] == "deterministic"


def test_cli_front_half_acceptance_runs_end_to_end(tmp_path: Path) -> None:
    """Front-half acceptance command should persist the realistic-input artifact chain."""

    dependency_fixture = tmp_path / "dependency_plan_fixture.json"
    dependency_fixture.write_text(
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
                    "The standard library is sufficient for filesystem and JSON handling in the first slice."
                ],
                "open_questions": [],
            },
            indent=2,
        )
    )
    blueprint_fixture = tmp_path / "blueprint_plan_fixture.json"
    blueprint_fixture.write_text(
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
                            "reuse pydantic models for typed schema validation"
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
                    "Keep the source packet focused on normalization and preserve downstream context needs explicitly."
                ],
                "dependency_decisions": [
                    "Reuse pydantic for schema contracts in the front-half slice."
                ],
                "open_questions": [],
            },
            indent=2,
        )
    )
    review_fixture = tmp_path / "front_half_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "concern",
                "freeze_verdict": "promising_but_blocked",
                "summary": "The front half preserves the requirements well enough to be promising, but the draft is still blocked by provisional authoring gaps.",
                "strengths": [
                    "Discovery preserved realistic ticket structure and key fields.",
                    "The decomposition stays bounded and uses a truthful source schema."
                ],
                "concerns": [
                    "The current draft bundle still lacks fixture coverage and concrete invariants."
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
                    "Add concrete fixtures and local invariants before retrying freeze."
                ],
            },
            indent=2,
        )
    )

    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(dependency_fixture)
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(blueprint_fixture)
    env["AC14_FRONT_HALF_ACCEPTANCE_FIXTURE"] = str(review_fixture)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "front-half-acceptance",
            str(REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch.json"),
            "--output-dir",
            str(tmp_path / "front_half"),
            "--requirements",
            "preserve",
            "support",
            "ticket",
            "meaning",
            "keep",
            "packets",
            "bounded",
            "--project-root",
            str(REPO_ROOT),
            "--packages",
            "pydantic",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["freeze_approved"] is False
    assert payload["review"]["freeze_verdict"] == "promising_but_blocked"
    assert (tmp_path / "front_half" / "front_half_acceptance_report.json").exists()


def test_cli_acceptance_review_with_realistic_input_runs_end_to_end(tmp_path: Path) -> None:
    """Acceptance-review command should support realistic-input execution context."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Outputs look consistent with the realistic ticket requirements.",
                "concerns": [],
                "requirement_assessments": [
                    {
                        "requirement": "The system should escalate a billing renewal failure affecting a known enterprise customer.",
                        "verdict": "satisfied",
                        "rationale": "The output preserves the priority, label, and escalation action."
                    }
                ],
            },
            indent=2,
        )
    )

    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "acceptance-review",
            str(EXAMPLE_DIR),
            "--output-dir",
            str(tmp_path / "acceptance_realistic"),
            "--mode",
            "reference",
            "--realistic-input",
            str(REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch.json"),
            "--record-index",
            "0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload["scenario_results"]) == 1
    assert payload["scenario_results"][0]["realistic_input_path"].endswith("realistic_ticket_batch.json")
    assert (tmp_path / "acceptance_realistic" / "acceptance_report.json").exists()


def test_cli_acceptance_review_with_realistic_input_deterministic_mode_runs_end_to_end(
    tmp_path: Path,
) -> None:
    """Acceptance-review command should support deterministic realistic-input execution."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "concern",
                "summary": "Deterministic realistic-input outputs are reviewable and structurally coherent.",
                "concerns": ["Customer context may be absent for unseen IDs."],
                "requirement_assessments": [
                    {
                        "requirement": "The system should escalate a billing renewal failure affecting a known enterprise customer.",
                        "verdict": "partially_satisfied",
                        "rationale": "The digest path executed, but enterprise context was not recovered from the unseen customer ID.",
                    }
                ],
            },
            indent=2,
        )
    )

    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ac14",
            "acceptance-review",
            str(EXAMPLE_DIR),
            "--output-dir",
            str(tmp_path / "acceptance_realistic_deterministic"),
            "--mode",
            "deterministic",
            "--realistic-input",
            str(REPO_ROOT / "examples" / "support_ticket_digest" / "input" / "realistic_ticket_batch.json"),
            "--record-index",
            "0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload["scenario_results"]) == 1
    assert payload["scenario_results"][0]["execution_error"] is None
    assert payload["scenario_results"][0]["review"]["overall_verdict"] == "concern"
    assert (tmp_path / "acceptance_realistic_deterministic" / "acceptance_report.json").exists()

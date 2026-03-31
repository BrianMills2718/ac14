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

"""Smoke tests for Makefile proof-surface targets."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

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
from ac14.examples import discover_shipped_blueprints
from ac14.generated_codegen import emit_generated_package
from ac14.loader import load_blueprint_dir
from ac14.packets import compile_packets


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


def _write_blocked_freeze_inputs(tmp_path: Path, plan_path: Path) -> tuple[Path, Path]:
    """Persist one blocked freeze-decision/remediation pair for Make refinement tests."""

    remediation_plan_path = tmp_path / "freeze_remediation_plan.json"
    remediation_plan_path.write_text(
        json.dumps(
            {
                "blocked": True,
                "summary": "1 remediation task generated for blocked freeze",
                "task_count": 1,
                "upstream_plan_path": str(plan_path),
                "tasks": [
                    {
                        "task_id": "freeze-remediation-01",
                        "blocking": True,
                        "title": "Resolve blocked dependency probes",
                        "summary": "Update dependency evidence before retrying freeze.",
                        "target_files": [str(plan_path)],
                        "source_paths": ["metadata.dependencies"],
                        "finding_codes": ["E-DRAFT-DEPENDENCY-BLOCKED"],
                        "authoring_actions": ["Update dependency decisions and open questions."],
                        "retry_command": "python -m ac14 materialize-draft-bundle",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    freeze_decision_path = tmp_path / "freeze_decision.json"
    freeze_decision_path.write_text(
        json.dumps(
            {
                "approved": False,
                "decision_summary": "bundle blocked by freeze-readiness findings",
                "findings": [
                    {
                        "code": "E-DRAFT-DEPENDENCY-BLOCKED",
                        "message": "Blocked dependency probe remains unresolved.",
                        "path": "metadata.dependencies",
                    }
                ],
                "remediation_plan_path": str(remediation_plan_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return freeze_decision_path, remediation_plan_path


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


def _write_dependency_plan_without_install(path: Path) -> Path:
    """Persist a dependency plan with no install actions for remediation Make tests."""

    artifact = DependencyPlanningArtifact(
        discovery_artifact_path=str(path.parent / "discovery_artifact.json"),
        requirements=["preserve typed schema contracts"],
        carried_forward_concerns=[],
        planning_summary="Reuse pydantic and skip richer formatting for now.",
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
                package_name="rich",
                action="investigate",
                capability_need="Richer terminal formatting later.",
                justification="Not required for this proof slice.",
                already_installed=False,
                install_command=None,
                evidence=[
                    DependencyEvidence(
                        source="requirement",
                        locator="operator output",
                        detail="Formatting is not yet required.",
                    ),
                ],
            ),
        ],
        standard_library_notes=[],
        open_questions=[],
    )
    path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True))
    return path


def _write_llm_codegen_fixture(path: Path, blueprint_dir: Path) -> Path:
    """Persist fixture-backed LLM codegen responses using deterministic module code."""

    blueprint = load_blueprint_dir(blueprint_dir)
    packet_bundle = compile_packets(blueprint)
    deterministic_package = emit_generated_package(
        packet_bundle,
        path.parent / f"{blueprint.metadata.blueprint_id}_deterministic_generated",
        generator_kind="deterministic",
    )
    fixture_payload = {
        component_id: {
            "module_code": Path(module_path).read_text(),
            "implementation_notes": ["fixture-backed llm codegen"],
        }
        for component_id, module_path in deterministic_package.module_paths.items()
    }
    path.write_text(json.dumps(fixture_payload, indent=2, sort_keys=True))
    return path


def _write_blueprint_aware_llm_codegen_fixture(path: Path) -> Path:
    """Persist fixture-backed LLM codegen responses keyed by blueprint id and component id."""

    fixture_payload: dict[str, dict[str, dict[str, object]]] = {}
    for example in discover_shipped_blueprints(EXAMPLES_ROOT):
        blueprint = load_blueprint_dir(Path(example.blueprint_dir))
        packet_bundle = compile_packets(blueprint)
        deterministic_package = emit_generated_package(
            packet_bundle,
            path.parent / f"{blueprint.metadata.blueprint_id}_deterministic_generated",
            generator_kind="deterministic",
        )
        fixture_payload[blueprint.metadata.blueprint_id] = {
            component_id: {
                "module_code": Path(module_path).read_text(),
                "implementation_notes": [f"fixture-backed llm codegen for {blueprint.metadata.blueprint_id}"],
            }
            for component_id, module_path in deterministic_package.module_paths.items()
        }
    path.write_text(json.dumps(fixture_payload, indent=2, sort_keys=True))
    return path


def _write_acceptance_review_fixture(path: Path) -> Path:
    """Persist one deterministic acceptance-review fixture for subprocess tests."""

    path.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Fixture-backed acceptance review approved the outputs.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return path


def _write_front_half_dependency_plan_fixture(path: Path) -> Path:
    """Persist one deterministic dependency-plan fixture for Make front-half tests."""

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
                    "The standard library is sufficient for filesystem and JSON handling in the first slice."
                ],
                "open_questions": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return path


def _write_front_half_blueprint_plan_fixture(path: Path) -> Path:
    """Persist one deterministic draft-blueprint fixture for Make front-half tests."""

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
            sort_keys=True,
        )
    )
    return path


def _write_front_half_review_fixture(path: Path) -> Path:
    """Persist one deterministic front-half review fixture for Make front-half tests."""

    path.write_text(
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
            sort_keys=True,
        )
    )
    return path


def _write_freeze_semantic_review_fixture(path: Path) -> Path:
    """Persist one deterministic freeze-semantic review fixture for Make subprocess tests."""

    path.write_text(
        json.dumps(
            {
                "overall_verdict": "concern",
                "freeze_verdict": "promising_but_blocked",
                "summary": "The draft looks promising, but draft-quality blockers still prevent freeze.",
                "strengths": [
                    "Discovery preserved realistic ticket context.",
                    "The initial decomposition remains bounded.",
                ],
                "concerns": [
                    "Fixture coverage and concrete invariants are still missing.",
                ],
                "requirement_assessments": [
                    {
                        "requirement": "preserve support ticket meaning",
                        "verdict": "satisfied",
                        "rationale": "The draft schema still retains the core ticket content.",
                    },
                    {
                        "requirement": "keep packets bounded",
                        "verdict": "satisfied",
                        "rationale": "The first packet remains narrowly scoped.",
                    },
                ],
                "recommended_next_steps": [
                    "Add concrete fixtures and invariants before retrying freeze.",
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
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
    assert "packet-sufficiency" in result.stdout
    assert "discover-input" in result.stdout
    assert "inspect-environment" in result.stdout
    assert "inspect-project-context" in result.stdout
    assert "retrieve-context" in result.stdout
    assert "plan-dependencies" in result.stdout
    assert "probe-dependencies" in result.stdout
    assert "remediate-dependencies" in result.stdout
    assert "draft-blueprint-plan" in result.stdout
    assert "materialize-draft-bundle" in result.stdout
    assert "decide-freeze" in result.stdout
    assert "front-half-acceptance" in result.stdout
    assert "front-half-acceptance-suite" in result.stdout
    assert "prove-example" in result.stdout
    assert "fresh-runs" in result.stdout
    assert "compare-generators" in result.stdout
    assert "acceptance-review" in result.stdout
    assert "semantic-compare" in result.stdout
    assert "prove-suite" in result.stdout
    assert "compare-suite" in result.stdout
    assert "semantic-compare-suite" in result.stdout
    assert "acceptance-review-suite" in result.stdout
    assert "acceptance-review-realistic-suite" in result.stdout
    assert "acceptance-review-realistic-compare" in result.stdout
    assert "recommend-default-generator" in result.stdout
    assert "live-llm-readiness" in result.stdout
    assert "live-llm-readiness-suite" in result.stdout


def test_make_packet_sufficiency_runs_end_to_end(tmp_path: Path) -> None:
    """Make packet-sufficiency target should persist the structural sufficiency artifact."""

    output_dir = tmp_path / "packet_sufficiency"
    result = subprocess.run(
        [
            "make",
            "packet-sufficiency",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "packet_sufficiency_report.json").read_text())
    assert payload["all_packets_structurally_sufficient"] is True


def test_make_prove_example_runs_end_to_end(tmp_path: Path) -> None:
    """Make proof target should build a persisted bundle without manual Python imports."""

    output_dir = tmp_path / "proof_bundle"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(
        _write_acceptance_review_fixture(tmp_path / "acceptance_review_fixture.json")
    )
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
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "realistic_input_gate.json").exists()


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


def test_make_discover_input_supports_input_directory(tmp_path: Path) -> None:
    """Make discovery target should support directory inputs with explicit primary-candidate persistence."""

    input_dir = tmp_path / "input_bundle"
    input_dir.mkdir()
    (input_dir / "tickets.json").write_text('[{"id": 1, "status": "open"}]')
    (input_dir / "tickets_archive.csv").write_text("id,status\n2,closed\n")
    (input_dir / "notes.md").write_text("# Notes\n\nKeep packet context bounded.\n")
    output_dir = tmp_path / "discovery"
    result = subprocess.run(
        [
            "make",
            "discover-input",
            f"INPUT={input_dir}",
            f"OUTPUT={output_dir}",
            "PACKAGES=pydantic",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "discovery_artifact.json").read_text())
    assert payload["input_inspection"]["input_path"] == str(input_dir)
    assert payload["input_inspection"]["primary_input_path"].endswith("tickets.json")


def test_make_discover_input_persists_directory_context_summaries(tmp_path: Path) -> None:
    """Make discovery should persist bounded summaries for alternate directory context."""

    input_dir = tmp_path / "input_bundle"
    input_dir.mkdir()
    (input_dir / "tickets.json").write_text(
        json.dumps(
            [
                {"ticket_id": "SUP-1", "status": "open"},
                {"ticket_id": "SUP-2", "status": "closed"},
            ],
            indent=2,
        ),
    )
    (input_dir / "tickets_archive.csv").write_text("ticket_id,status\nSUP-3,pending\n")
    (input_dir / "notes.md").write_text("# Notes\n\nKeep the source schema truthful.\n")

    output_dir = tmp_path / "discovery"
    result = subprocess.run(
        [
            "make",
            "discover-input",
            f"INPUT={input_dir}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "discovery_artifact.json").read_text())
    alternate_summary = payload["input_inspection"]["structured_candidate_summaries"][0]
    context_summary = payload["input_inspection"]["supporting_context_summaries"][0]
    assert alternate_summary["path"] == str(input_dir / "tickets_archive.csv")
    assert alternate_summary["input_format"] == "csv"
    assert context_summary["path"] == str(input_dir / "notes.md")
    assert "Keep the source schema truthful." in context_summary["preview"]


def test_make_discover_input_persists_directory_schema_divergence_concerns(tmp_path: Path) -> None:
    """Make discovery should preserve bounded schema-divergence concerns."""

    input_dir = tmp_path / "input_bundle"
    input_dir.mkdir()
    (input_dir / "tickets.json").write_text(
        json.dumps(
            [
                {"ticket_id": "SUP-1", "status": "open"},
                {"ticket_id": "SUP-2", "status": "closed"},
            ],
            indent=2,
        ),
    )
    (input_dir / "tickets_archive.csv").write_text(
        "ticket_id,status,archive_reason\nSUP-3,pending,duplicate\n",
    )

    output_dir = tmp_path / "discovery"
    result = subprocess.run(
        [
            "make",
            "discover-input",
            f"INPUT={input_dir}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "discovery_artifact.json").read_text())
    assert any(
        "tickets_archive.csv exposes fields absent from primary candidate tickets.json: archive_reason"
        in concern
        for concern in payload["input_inspection"]["concerns"]
    )


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


def test_make_remediate_dependencies_runs_end_to_end(tmp_path: Path) -> None:
    """Make remediation target should persist a dependency-remediation artifact."""

    dependency_plan_path = _write_dependency_plan_without_install(tmp_path / "dependency_plan.json")
    probe_output_dir = tmp_path / "dependency_probe"
    probe_result = subprocess.run(
        [
            "make",
            "probe-dependencies",
            f"DEPENDENCY_PLAN={dependency_plan_path}",
            f"OUTPUT={probe_output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert probe_result.returncode == 0, probe_result.stderr

    output_dir = tmp_path / "dependency_remediation"
    result = subprocess.run(
        [
            "make",
            "remediate-dependencies",
            f"INPUT={probe_output_dir / 'dependency_execution_artifact.json'}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "dependency_remediation_artifact.json").read_text())
    assert payload["attempted_packages"] == []


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
    output_dir = tmp_path / "draft_plan"
    env = os.environ.copy()
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(fixture_path)
    result = subprocess.run(
        [
            "make",
            "draft-blueprint-plan",
            f"DISCOVERY={discovery_path}",
            f"DEPENDENCY_PLAN={dependency_plan_path}",
            f"DEPENDENCY_EXECUTION={dependency_execution_path}",
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
    assert payload["dependency_execution_artifact_path"] == str(dependency_execution_path)
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


def test_make_draft_blueprint_plan_accepts_dependency_remediation_artifact(tmp_path: Path) -> None:
    """Make draft planning target should accept remediation artifacts directly."""

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
                    "dependency_statuses": [],
                    "concerns": [],
                },
                "project_context_inventory": {
                    "project_root": str(REPO_ROOT),
                    "document_count": 1,
                    "truncated": False,
                    "documents": [],
                    "concerns": [],
                },
                "external_retrieval_summaries": [],
                "open_concerns": [],
            },
            indent=2,
        )
    )
    dependency_plan_path = _write_dependency_plan_without_install(tmp_path / "dependency_plan.json")
    dependency_execution_path = tmp_path / "dependency_execution_artifact.json"
    dependency_execution_path.write_text(
        json.dumps(
            {
                "dependency_plan_path": str(dependency_plan_path),
                "execution_mode": "allow_install",
                "planning_summary": "Reuse pydantic and skip richer formatting for now.",
                "carried_forward_questions": [],
                "results": [],
                "environment_observations": ["all dependency probes are confirmed after remediation"],
            },
            indent=2,
        )
    )
    remediation_path = tmp_path / "dependency_remediation_artifact.json"
    remediation_path.write_text(
        json.dumps(
            {
                "prior_dependency_execution_artifact_path": str(tmp_path / "prior_dependency_execution_artifact.json"),
                "remediated_dependency_execution_artifact_path": str(dependency_execution_path),
                "attempted_packages": [],
                "newly_confirmed_packages": [],
                "still_blocked_packages": [],
                "summary": "no blocked install probes required remediation",
            },
            indent=2,
        )
    )
    fixture_path = tmp_path / "draft_blueprint_plan_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "planning_summary": "Use a source parser and one sink to keep packets bounded.",
                "proposed_schemas": [],
                "proposed_components": [],
                "proposed_bindings": [],
                "proposed_scenarios": [],
                "packetization_notes": [],
                "dependency_decisions": [],
                "open_questions": [],
            },
            indent=2,
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
            f"DEPENDENCY_REMEDIATION={remediation_path}",
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
    assert payload["dependency_remediation_artifact_path"] == str(remediation_path)
    assert payload["dependency_execution_artifact_path"] == str(dependency_execution_path)


def test_make_refine_draft_blueprint_plan_runs_end_to_end(tmp_path: Path) -> None:
    """Make refinement target should emit a refined planning artifact with provenance."""

    plan_path = _write_plan_artifact(tmp_path / "draft_blueprint_plan.json")
    freeze_decision_path, remediation_plan_path = _write_blocked_freeze_inputs(tmp_path, plan_path)
    fixture_path = tmp_path / "refine_draft_blueprint_plan_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "refinement_summary": "Clarified dependency scope after the blocked freeze.",
                "planning_summary": "Keep the bounded graph and tighten dependency decisions.",
                "proposed_schemas": [],
                "proposed_components": [],
                "proposed_bindings": [],
                "proposed_scenarios": [],
                "packetization_notes": ["Keep the packet boundary unchanged."],
                "dependency_decisions": ["Keep optional formatting dependencies out of the first freeze."],
                "open_questions": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    output_dir = tmp_path / "refined_plan"
    env = os.environ.copy()
    env["AC14_REFINE_BLUEPRINT_PLAN_FIXTURE"] = str(fixture_path)
    result = subprocess.run(
        [
            "make",
            "refine-draft-blueprint-plan",
            f"PLAN={plan_path}",
            f"INPUT={freeze_decision_path}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "draft_blueprint_plan.json").read_text())
    assert payload["source_draft_blueprint_plan_path"] == str(plan_path)
    assert payload["source_freeze_decision_path"] == str(freeze_decision_path)
    assert payload["source_freeze_remediation_plan_path"] == str(remediation_plan_path)
    assert payload["refinement_round"] == 1


def test_make_retry_freeze_runs_end_to_end(tmp_path: Path) -> None:
    """Make retry-freeze target should persist the full retry chain."""

    plan_path = _write_plan_artifact(tmp_path / "draft_blueprint_plan.json")
    freeze_decision_path, remediation_plan_path = _write_blocked_freeze_inputs(tmp_path, plan_path)
    refine_fixture_path = tmp_path / "refine_draft_blueprint_plan_fixture.json"
    refine_fixture_path.write_text(
        json.dumps(
            {
                "refinement_summary": "Clarified dependency scope after the blocked freeze.",
                "planning_summary": "Keep the bounded graph and tighten dependency decisions.",
                "proposed_schemas": [],
                "proposed_components": [],
                "proposed_bindings": [],
                "proposed_scenarios": [],
                "packetization_notes": ["Keep the packet boundary unchanged."],
                "dependency_decisions": ["Keep optional formatting dependencies out of the first freeze."],
                "open_questions": [],
            },
            indent=2,
            sort_keys=True,
        )
    )
    output_dir = tmp_path / "freeze_retry"
    env = os.environ.copy()
    env["AC14_REFINE_BLUEPRINT_PLAN_FIXTURE"] = str(refine_fixture_path)
    env["AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE"] = str(
        _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json"),
    )
    result = subprocess.run(
        [
            "make",
            "retry-freeze",
            f"PLAN={plan_path}",
            f"INPUT={freeze_decision_path}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "freeze_retry_artifact.json").read_text())
    assert payload["source_draft_blueprint_plan_path"] == str(plan_path)
    assert payload["source_freeze_decision_path"] == str(freeze_decision_path)
    assert payload["refined_draft_blueprint_plan_path"].endswith("draft_blueprint_plan.json")
    assert payload["refreshed_freeze_decision_path"].endswith("freeze_decision.json")
    assert payload["refinement_round"] == 1
    assert remediation_plan_path.exists()


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
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(
        _write_acceptance_review_fixture(tmp_path / "acceptance_review_fixture.json")
    )
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
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "suite_proof_report.json").read_text())
    assert payload["realistic_input_gate_included_examples"] == payload["example_count"]


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
    env = os.environ.copy()
    for key in [
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "AC14_ENABLE_LIVE_LLM_READINESS",
    ]:
        env.pop(key, None)
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(
        _write_acceptance_review_fixture(tmp_path / "acceptance_review_fixture.json")
    )
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
        env=env,
    )
    assert result.returncode == 0, result.stderr
    recommendation_path = output_dir / "default_generator_recommendation.json"
    assert recommendation_path.exists()
    payload = json.loads(recommendation_path.read_text())
    assert payload["live_readiness_status"] == "skipped"
    assert payload["live_readiness_suite_status"] == "skipped"
    assert payload["suite_default_gate_missing_examples"] == 0
    assert payload["suite_default_gate_unsupported_examples"] == 0
    assert payload["suite_live_ready_examples"] == 0
    assert payload["suite_live_blocked_examples"] == 0
    assert payload["suite_live_skipped_examples"] >= 2


def test_make_live_llm_readiness_reports_skipped_without_keys(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Make live-readiness target should persist an explicit skipped artifact without keys."""

    for key in [
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "AC14_ENABLE_LIVE_LLM_READINESS",
    ]:
        monkeypatch.delenv(key, raising=False)

    output_dir = tmp_path / "live_readiness"
    result = subprocess.run(
        [
            "make",
            "live-llm-readiness",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "live_llm_readiness.json").read_text())
    assert payload["status"] == "skipped"


def test_make_live_llm_readiness_suite_reports_skipped_without_keys(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Make suite live-readiness target should persist explicit skipped artifacts without keys."""

    for key in [
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "AC14_ENABLE_LIVE_LLM_READINESS",
    ]:
        monkeypatch.delenv(key, raising=False)

    output_dir = tmp_path / "live_readiness_suite"
    result = subprocess.run(
        [
            "make",
            "live-llm-readiness-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "live_llm_readiness_suite.json").read_text())
    assert payload["overall_status"] == "skipped"
    assert payload["example_count"] >= 2


def test_make_front_half_acceptance_runs_end_to_end(tmp_path: Path) -> None:
    """Make front-half acceptance target should persist the realistic-input artifact chain."""

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

    output_dir = tmp_path / "front_half"
    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(dependency_fixture)
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(blueprint_fixture)
    env["AC14_FRONT_HALF_ACCEPTANCE_FIXTURE"] = str(review_fixture)
    env["AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE"] = str(
        _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json"),
    )
    result = subprocess.run(
        [
            "make",
            "front-half-acceptance",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch.json'}",
            f"OUTPUT={output_dir}",
            "REQUIREMENTS=preserve support ticket meaning keep packets bounded",
            "PACKAGES=pydantic",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "front_half_acceptance_report.json").exists()
    payload = json.loads((output_dir / "front_half_acceptance_report.json").read_text())
    assert payload["artifact_paths"]["freeze_semantic_review_path"] is not None
    assert (output_dir / "freeze_decision" / "freeze_semantic_review.json").exists()


def test_make_front_half_acceptance_supports_input_directory(tmp_path: Path) -> None:
    """Make front-half target should preserve directory-input discovery evidence."""

    input_dir = tmp_path / "input_bundle"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "tickets.json").write_text(
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
    (input_dir / "tickets_archive.csv").write_text(
        "ticket_id,body,channel\n"
        "SUP-09999,Archived backlog item,email\n",
    )
    (input_dir / "notes.md").write_text("# Intake notes\n\nLatest support batch.\n")

    dependency_fixture = _write_front_half_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")
    blueprint_fixture = _write_front_half_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")
    review_fixture = _write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json")

    output_dir = tmp_path / "front_half_directory"
    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(dependency_fixture)
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(blueprint_fixture)
    env["AC14_FRONT_HALF_ACCEPTANCE_FIXTURE"] = str(review_fixture)
    env["AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE"] = str(
        _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json"),
    )
    result = subprocess.run(
        [
            "make",
            "front-half-acceptance",
            f"REALISTIC_INPUT={input_dir}",
            f"OUTPUT={output_dir}",
            "REQUIREMENTS=preserve support ticket meaning keep packets bounded",
            "PACKAGES=pydantic",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "front_half_acceptance_report.json").read_text())
    discovery_payload = json.loads((output_dir / "discovery" / "discovery_artifact.json").read_text())
    inspection = discovery_payload["input_inspection"]
    assert payload["input_path"] == str(input_dir)
    assert inspection["input_path"] == str(input_dir)
    assert inspection["primary_input_path"].endswith("tickets.json")
    assert inspection["structured_candidate_paths"] == [
        str(input_dir / "tickets.json"),
        str(input_dir / "tickets_archive.csv"),
    ]
    assert (output_dir / "front_half_acceptance_report.json").exists()


def test_make_front_half_acceptance_preserves_directory_context_summaries(tmp_path: Path) -> None:
    """Make front-half target should preserve directory-context summaries."""

    input_dir = tmp_path / "input_bundle"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "tickets.json").write_text(
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
    (input_dir / "tickets_archive.csv").write_text(
        "ticket_id,body,channel\n"
        "SUP-09999,Archived backlog item,email\n",
    )
    (input_dir / "notes.md").write_text("# Notes\n\nLatest support batch.\n")

    dependency_fixture = _write_front_half_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")
    blueprint_fixture = _write_front_half_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")
    review_fixture = _write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json")

    output_dir = tmp_path / "front_half_directory_summaries"
    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(dependency_fixture)
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(blueprint_fixture)
    env["AC14_FRONT_HALF_ACCEPTANCE_FIXTURE"] = str(review_fixture)
    env["AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE"] = str(
        _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json"),
    )
    result = subprocess.run(
        [
            "make",
            "front-half-acceptance",
            f"REALISTIC_INPUT={input_dir}",
            f"OUTPUT={output_dir}",
            "REQUIREMENTS=preserve support ticket meaning keep packets bounded",
            "PACKAGES=pydantic",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    discovery_payload = json.loads((output_dir / "discovery" / "discovery_artifact.json").read_text())
    inspection = discovery_payload["input_inspection"]
    alternate_summary = inspection["structured_candidate_summaries"][0]
    context_summary = inspection["supporting_context_summaries"][0]
    assert alternate_summary["path"] == str(input_dir / "tickets_archive.csv")
    assert alternate_summary["input_format"] == "csv"
    assert context_summary["path"] == str(input_dir / "notes.md")
    assert "latest support batch" in context_summary["preview"].lower()


def test_make_front_half_acceptance_supports_retry_freeze(tmp_path: Path) -> None:
    """Make front-half target should optionally persist one retry-chain artifact."""

    dependency_fixture = _write_front_half_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")
    blueprint_fixture = _write_front_half_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")
    refine_fixture = tmp_path / "refine_blueprint_plan_fixture.json"
    refine_payload = json.loads(blueprint_fixture.read_text())
    refine_payload["refinement_summary"] = "Clarified dependency scope after the blocked freeze."
    refine_fixture.write_text(json.dumps(refine_payload, indent=2, sort_keys=True))
    review_fixture = _write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json")

    output_dir = tmp_path / "front_half"
    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(dependency_fixture)
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(blueprint_fixture)
    env["AC14_REFINE_BLUEPRINT_PLAN_FIXTURE"] = str(refine_fixture)
    env["AC14_FRONT_HALF_ACCEPTANCE_FIXTURE"] = str(review_fixture)
    env["AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE"] = str(
        _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json"),
    )
    result = subprocess.run(
        [
            "make",
            "front-half-acceptance",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch.json'}",
            f"OUTPUT={output_dir}",
            "REQUIREMENTS=preserve support ticket meaning keep packets bounded",
            "PACKAGES=pydantic",
            "RETRY_BLOCKED_FREEZE=1",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "front_half_acceptance_report.json").read_text())
    assert payload["retry_freeze_attempted"] is True
    assert payload["artifact_paths"]["retry_freeze_artifact_path"] is not None
    assert (output_dir / "freeze_retry" / "freeze_retry_artifact.json").exists()


def test_make_front_half_acceptance_supports_retry_freeze_on_messy_input(tmp_path: Path) -> None:
    """Make front-half target should keep retry-aware messy-input proof explicit."""

    dependency_fixture = _write_front_half_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json")
    blueprint_fixture = _write_front_half_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json")
    refine_fixture = tmp_path / "refine_blueprint_plan_fixture.json"
    refine_payload = json.loads(blueprint_fixture.read_text())
    refine_payload["refinement_summary"] = "Clarified dependency scope after the blocked freeze."
    refine_fixture.write_text(json.dumps(refine_payload, indent=2, sort_keys=True))
    review_fixture = _write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json")

    output_dir = tmp_path / "front_half"
    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(dependency_fixture)
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(blueprint_fixture)
    env["AC14_REFINE_BLUEPRINT_PLAN_FIXTURE"] = str(refine_fixture)
    env["AC14_FRONT_HALF_ACCEPTANCE_FIXTURE"] = str(review_fixture)
    env["AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE"] = str(
        _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json"),
    )
    result = subprocess.run(
        [
            "make",
            "front-half-acceptance",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch_messy.csv'}",
            f"OUTPUT={output_dir}",
            "REQUIREMENTS=preserve support ticket meaning keep packets bounded",
            "PACKAGES=pydantic",
            "RETRY_BLOCKED_FREEZE=1",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "front_half_acceptance_report.json").read_text())
    discovery_payload = json.loads((output_dir / "discovery" / "discovery_artifact.json").read_text())
    assert discovery_payload["input_inspection"]["input_format"] == "csv"
    assert payload["retry_freeze_attempted"] is True
    assert payload["artifact_paths"]["retry_freeze_artifact_path"] is not None
    assert (output_dir / "freeze_retry" / "freeze_retry_artifact.json").exists()


def test_make_front_half_acceptance_suite_runs_end_to_end(tmp_path: Path) -> None:
    """Make front-half suite target should persist the suite breadth artifact."""

    output_dir = tmp_path / "front_half_suite"
    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(
        _write_front_half_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json"),
    )
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(
        _write_front_half_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json"),
    )
    env["AC14_FRONT_HALF_ACCEPTANCE_FIXTURE"] = str(
        _write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json"),
    )
    env["AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE"] = str(
        _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json"),
    )
    result = subprocess.run(
        [
            "make",
            "front-half-acceptance-suite",
            f"OUTPUT={output_dir}",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "front_half_acceptance_suite_report.json").read_text())
    assert payload["example_count"] >= 3
    assert payload["freeze_blocked_examples"] == payload["example_count"]


def test_make_front_half_acceptance_suite_supports_retry_freeze(tmp_path: Path) -> None:
    """Make front-half suite target should optionally persist retry-aware breadth."""

    output_dir = tmp_path / "front_half_suite"
    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(
        _write_front_half_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json"),
    )
    blueprint_fixture = _write_front_half_blueprint_plan_fixture(
        tmp_path / "blueprint_plan_fixture.json",
    )
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(blueprint_fixture)
    refine_fixture = tmp_path / "refine_blueprint_plan_fixture.json"
    refine_payload = json.loads(blueprint_fixture.read_text())
    refine_payload["refinement_summary"] = "Clarified dependency scope after the blocked freeze."
    refine_fixture.write_text(json.dumps(refine_payload, indent=2, sort_keys=True))
    env["AC14_REFINE_BLUEPRINT_PLAN_FIXTURE"] = str(refine_fixture)
    env["AC14_FRONT_HALF_ACCEPTANCE_FIXTURE"] = str(
        _write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json"),
    )
    env["AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE"] = str(
        _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json"),
    )
    result = subprocess.run(
        [
            "make",
            "front-half-acceptance-suite",
            f"OUTPUT={output_dir}",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            "RETRY_BLOCKED_FREEZE=1",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "front_half_acceptance_suite_report.json").read_text())
    assert payload["retry_attempted_examples"] == payload["example_count"]
    assert payload["retry_approved_examples"] == 0


def test_make_front_half_acceptance_suite_supports_realistic_input_profile_selection(tmp_path: Path) -> None:
    """Make front-half suite target should expose explicit realistic-input profile selection."""

    output_dir = tmp_path / "front_half_suite"
    env = os.environ.copy()
    env["AC14_DEPENDENCY_PLAN_FIXTURE"] = str(
        _write_front_half_dependency_plan_fixture(tmp_path / "dependency_plan_fixture.json"),
    )
    env["AC14_BLUEPRINT_PLAN_FIXTURE"] = str(
        _write_front_half_blueprint_plan_fixture(tmp_path / "blueprint_plan_fixture.json"),
    )
    env["AC14_FRONT_HALF_ACCEPTANCE_FIXTURE"] = str(
        _write_front_half_review_fixture(tmp_path / "front_half_review_fixture.json"),
    )
    env["AC14_FREEZE_SEMANTIC_REVIEW_FIXTURE"] = str(
        _write_freeze_semantic_review_fixture(tmp_path / "freeze_semantic_review_fixture.json"),
    )
    result = subprocess.run(
        [
            "make",
            "front-half-acceptance-suite",
            f"OUTPUT={output_dir}",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            "REALISTIC_INPUT_PROFILE=messy",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "front_half_acceptance_suite_report.json").read_text())
    assert payload["realistic_input_profile"] == "messy"
    assert payload["missing_profile_examples"] == payload["example_count"] - 1


def test_make_acceptance_review_with_realistic_input_runs_end_to_end(tmp_path: Path) -> None:
    """Make acceptance-review target should support realistic-input execution context."""

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

    output_dir = tmp_path / "acceptance_realistic"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
            "GENERATOR=reference",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch.json'}",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "acceptance_report.json").exists()


def test_make_acceptance_review_with_realistic_input_deterministic_mode_runs_end_to_end(
    tmp_path: Path,
) -> None:
    """Make acceptance-review target should support deterministic realistic-input execution."""

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

    output_dir = tmp_path / "acceptance_realistic_deterministic"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
            "GENERATOR=deterministic",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch.json'}",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "acceptance_report.json").exists()


def test_make_acceptance_review_with_messy_input_csv_runs_end_to_end(tmp_path: Path) -> None:
    """Make acceptance-review target should support the shipped messy CSV asset in non-LLM modes."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Messy CSV outputs remain reviewable in bounded non-LLM modes.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )

    output_dir = tmp_path / "acceptance_realistic_messy"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
            "GENERATOR=deterministic",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch_messy.csv'}",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "acceptance_report.json").exists()


def test_make_acceptance_review_realistic_suite_runs_end_to_end(tmp_path: Path) -> None:
    """Make realistic suite acceptance target should persist one aggregate artifact."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Outputs remain reasonable across realistic-input slices.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )
    output_dir = tmp_path / "realistic_suite_acceptance"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review-realistic-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "MODES=reference deterministic",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "realistic_suite_acceptance_report.json").exists()


def test_make_acceptance_review_with_realistic_input_llm_mode_runs_end_to_end(
    tmp_path: Path,
) -> None:
    """Make acceptance-review target should support llm realistic-input execution."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Fixture-backed llm outputs remain reviewable on realistic input.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )
    llm_fixture = _write_llm_codegen_fixture(tmp_path / "llm_codegen_fixture.json", EXAMPLE_DIR)

    output_dir = tmp_path / "acceptance_realistic_llm"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    env["AC14_LLM_CODEGEN_FIXTURE"] = str(llm_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
            "GENERATOR=llm",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch.json'}",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "acceptance_report.json").exists()


def test_make_acceptance_review_with_messy_input_csv_llm_mode_runs_end_to_end(
    tmp_path: Path,
) -> None:
    """Make acceptance-review target should support bounded llm execution on the shipped messy CSV asset."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Fixture-backed llm outputs remain reviewable on the messy CSV asset.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )
    llm_fixture = _write_llm_codegen_fixture(tmp_path / "llm_codegen_fixture.json", EXAMPLE_DIR)

    output_dir = tmp_path / "acceptance_realistic_messy_llm"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    env["AC14_LLM_CODEGEN_FIXTURE"] = str(llm_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
            "GENERATOR=llm",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch_messy.csv'}",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "acceptance_report.json").exists()


def test_make_acceptance_review_realistic_compare_runs_end_to_end(tmp_path: Path) -> None:
    """Make realistic-input comparison target should persist one per-blueprint artifact."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "All compared modes remain reviewable on realistic input.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )
    llm_fixture = _write_llm_codegen_fixture(tmp_path / "llm_codegen_fixture.json", EXAMPLE_DIR)

    output_dir = tmp_path / "realistic_compare"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    env["AC14_LLM_CODEGEN_FIXTURE"] = str(llm_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review-realistic-compare",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch.json'}",
            "MODES=reference deterministic llm",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "realistic_mode_comparison_report.json").exists()


def test_make_acceptance_review_realistic_compare_with_messy_input_csv_runs_end_to_end(
    tmp_path: Path,
) -> None:
    """Make realistic-input comparison should support the shipped messy CSV asset in non-LLM modes."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Messy CSV outputs remain comparable across non-LLM modes.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )

    output_dir = tmp_path / "realistic_compare_messy_non_llm"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review-realistic-compare",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
            "MODES=reference deterministic",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch_messy.csv'}",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "realistic_mode_comparison_report.json").exists()


def test_make_acceptance_review_realistic_compare_with_messy_input_csv_llm_mode_runs_end_to_end(
    tmp_path: Path,
) -> None:
    """Make realistic-input comparison should support bounded llm on the shipped messy CSV asset."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Messy CSV outputs remain comparable across all bounded modes.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )
    llm_fixture = _write_llm_codegen_fixture(tmp_path / "llm_codegen_fixture.json", EXAMPLE_DIR)

    output_dir = tmp_path / "realistic_compare_messy_llm"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    env["AC14_LLM_CODEGEN_FIXTURE"] = str(llm_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review-realistic-compare",
            f"INPUT={EXAMPLE_DIR}",
            f"OUTPUT={output_dir}",
            "MODES=reference deterministic llm",
            f"REALISTIC_INPUT={REPO_ROOT / 'examples' / 'support_ticket_digest' / 'input' / 'realistic_ticket_batch_messy.csv'}",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "realistic_mode_comparison_report.json").exists()


def test_make_acceptance_review_realistic_suite_with_llm_runs_end_to_end(tmp_path: Path) -> None:
    """Make realistic suite acceptance target should support fixture-backed llm breadth."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Fixture-backed llm outputs remain reviewable across shipped examples.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )
    llm_fixture = _write_blueprint_aware_llm_codegen_fixture(
        tmp_path / "blueprint_aware_llm_codegen_fixture.json",
    )

    output_dir = tmp_path / "realistic_suite_acceptance_llm"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    env["AC14_LLM_CODEGEN_FIXTURE"] = str(llm_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review-realistic-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "MODES=llm",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "realistic_suite_acceptance_report.json").exists()


def test_make_acceptance_review_realistic_suite_supports_profile_selection(tmp_path: Path) -> None:
    """Make realistic suite acceptance target should expose explicit realistic-input profile selection."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Explicit messy-profile runs remain reviewable where present.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )
    output_dir = tmp_path / "realistic_suite_acceptance_messy"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review-realistic-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "MODES=reference deterministic",
            "REALISTIC_INPUT_PROFILE=messy",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "realistic_suite_acceptance_report.json").read_text())
    assert payload["realistic_input_profile"] == "messy"
    assert payload["mode_summaries"]["reference"]["missing_profile_examples"] == payload["example_count"] - 1


def test_make_acceptance_review_realistic_suite_supports_messy_profile_llm_mode(tmp_path: Path) -> None:
    """Make realistic suite acceptance target should support the explicit messy profile in bounded llm mode."""

    review_fixture = tmp_path / "acceptance_review_fixture.json"
    review_fixture.write_text(
        json.dumps(
            {
                "overall_verdict": "accept",
                "summary": "Explicit messy-profile llm runs remain reviewable where present.",
                "concerns": [],
                "requirement_assessments": [],
            },
            indent=2,
        )
    )
    llm_fixture = _write_blueprint_aware_llm_codegen_fixture(
        tmp_path / "blueprint_aware_llm_codegen_fixture.json",
    )
    output_dir = tmp_path / "realistic_suite_acceptance_messy_llm"
    env = os.environ.copy()
    env["AC14_ACCEPTANCE_REVIEW_FIXTURE"] = str(review_fixture)
    env["AC14_LLM_CODEGEN_FIXTURE"] = str(llm_fixture)
    result = subprocess.run(
        [
            "make",
            "acceptance-review-realistic-suite",
            f"EXAMPLES_ROOT={EXAMPLES_ROOT}",
            f"OUTPUT={output_dir}",
            "MODES=reference deterministic llm",
            "REALISTIC_INPUT_PROFILE=messy",
            "RECORD_INDEX=0",
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads((output_dir / "realistic_suite_acceptance_report.json").read_text())
    assert payload["realistic_input_profile"] == "messy"
    assert payload["mode_summaries"]["llm"]["accepted_examples"] == 1
    assert payload["mode_summaries"]["llm"]["missing_profile_examples"] == payload["example_count"] - 1

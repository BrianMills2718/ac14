"""CLI entrypoints for AC14 proof-surface workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from ac14.acceptance import (
    AcceptanceMode,
    build_acceptance_report,
    build_realistic_mode_comparison_report,
    build_realistic_suite_acceptance_report,
    build_suite_acceptance_report,
)
from ac14.blueprint_planning import (
    DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    DEFAULT_BLUEPRINT_PLAN_MODEL,
    build_draft_blueprint_plan,
    build_refined_draft_blueprint_plan,
)
from ac14.comparison import build_generator_comparison_report
from ac14.dependency_execution import (
    build_dependency_execution_artifact,
    build_dependency_remediation_artifact,
)
from ac14.dependency_planning import (
    DEFAULT_DEPENDENCY_PLAN_MAX_BUDGET,
    DEFAULT_DEPENDENCY_PLAN_MODEL,
    build_dependency_plan,
)
from ac14.discovery import (
    build_discovery_artifact,
    persist_environment_inventory,
    persist_project_context_inventory,
)
from ac14.draft_authoring import materialize_draft_blueprint_bundle
from ac14.evidence_bundle import build_evidence_bundle
from ac14.examples import discover_shipped_blueprints
from ac14.freeze_decision import build_freeze_decision
from ac14.freeze_retry import build_freeze_retry_artifact
from ac14.front_half_acceptance import (
    DEFAULT_FRONT_HALF_ACCEPTANCE_MAX_BUDGET,
    DEFAULT_FRONT_HALF_ACCEPTANCE_MODEL,
    build_front_half_acceptance_report,
    build_front_half_acceptance_suite_report,
)
from ac14.generated_codegen import GeneratorKind, emit_generated_package
from ac14.generated_evidence import run_fresh_generation_trials
from ac14.loader import load_blueprint_dir
from ac14.packets import compile_packets
from ac14.packet_sufficiency import build_packet_sufficiency_report
from ac14.recommendation import (
    build_default_generator_recommendation,
    build_llm_live_readiness_artifact,
    build_llm_live_readiness_suite_artifact,
)
from ac14.semantic_comparison import ComparisonMode, build_semantic_comparison_report
from ac14.semantic_suite import build_suite_semantic_comparison_report
from ac14.suite import build_suite_comparison_report, build_suite_proof_report
from ac14.retrieval import (
    RepoRetrievalQuery,
    WebRetrievalQuery,
    build_external_retrieval_artifact,
)
from ac14.validation import validate_blueprint


def main() -> int:
    """Run the AC14 command-line interface."""

    parser = argparse.ArgumentParser(prog="python -m ac14")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser("verify-blueprint", help="Validate a blueprint bundle.")
    verify_parser.add_argument("blueprint_dir", type=Path)

    packet_sufficiency_parser = subparsers.add_parser(
        "packet-sufficiency",
        help="Build a persisted structural packet-sufficiency artifact for one blueprint.",
    )
    packet_sufficiency_parser.add_argument("blueprint_dir", type=Path)
    packet_sufficiency_parser.add_argument("--output-dir", type=Path, required=True)

    generate_parser = subparsers.add_parser("generate-components", help="Emit generated modules.")
    generate_parser.add_argument("blueprint_dir", type=Path)
    generate_parser.add_argument("--output-dir", type=Path, required=True)
    generate_parser.add_argument("--generator", choices=["deterministic", "llm"], default="deterministic")
    generate_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    generate_parser.add_argument("--max-budget", type=float, default=0.50)

    discover_parser = subparsers.add_parser(
        "discover-input",
        help="Inspect a local input and persist a pre-freeze discovery artifact.",
    )
    discover_parser.add_argument("input_path", type=Path)
    discover_parser.add_argument("--output-dir", type=Path, required=True)
    discover_parser.add_argument("--project-root", type=Path, default=Path.cwd())
    discover_parser.add_argument("--packages", nargs="*", default=[])
    discover_parser.add_argument("--retrieval-artifact", nargs="*", default=[])
    discover_parser.add_argument("--max-samples", type=int, default=5)

    environment_parser = subparsers.add_parser(
        "inspect-environment",
        help="Persist the environment inventory used during discovery planning.",
    )
    environment_parser.add_argument("--output-dir", type=Path, required=True)
    environment_parser.add_argument("--project-root", type=Path, default=Path.cwd())
    environment_parser.add_argument("--packages", nargs="*", default=[])

    project_context_parser = subparsers.add_parser(
        "inspect-project-context",
        help="Persist local project-document context used during discovery planning.",
    )
    project_context_parser.add_argument("--output-dir", type=Path, required=True)
    project_context_parser.add_argument("--project-root", type=Path, default=Path.cwd())
    project_context_parser.add_argument("--max-documents", type=int, default=20)

    retrieval_parser = subparsers.add_parser(
        "retrieve-context",
        help="Persist reviewable external documentation and repository retrieval artifacts.",
    )
    retrieval_parser.add_argument("--output-dir", type=Path, required=True)
    retrieval_parser.add_argument("--web-query", action="append", default=[])
    retrieval_parser.add_argument("--repo-query", action="append", default=[])
    retrieval_parser.add_argument("--repo", action="append", default=[])
    retrieval_parser.add_argument("--web-top-k", type=int, default=3)
    retrieval_parser.add_argument("--repo-limit", type=int, default=5)

    dependency_plan_parser = subparsers.add_parser(
        "plan-dependencies",
        help="Build an evidence-backed dependency and library planning artifact from discovery.",
    )
    dependency_plan_parser.add_argument("discovery_artifact_path", type=Path)
    dependency_plan_parser.add_argument("--output-dir", type=Path, required=True)
    dependency_plan_parser.add_argument("--requirements", nargs="+", required=True)
    dependency_plan_parser.add_argument("--model", default=DEFAULT_DEPENDENCY_PLAN_MODEL)
    dependency_plan_parser.add_argument(
        "--max-budget",
        type=float,
        default=DEFAULT_DEPENDENCY_PLAN_MAX_BUDGET,
    )

    dependency_probe_parser = subparsers.add_parser(
        "probe-dependencies",
        help="Probe dependency recommendations and persist explicit execution results.",
    )
    dependency_probe_parser.add_argument("dependency_plan_path", type=Path)
    dependency_probe_parser.add_argument("--output-dir", type=Path, required=True)
    dependency_probe_parser.add_argument("--allow-install", action="store_true")
    dependency_probe_parser.add_argument("--project-root", type=Path, default=Path.cwd())

    dependency_remediation_parser = subparsers.add_parser(
        "remediate-dependencies",
        help="Rerun blocked install probes and persist a dependency-remediation artifact.",
    )
    dependency_remediation_parser.add_argument("dependency_execution_artifact_path", type=Path)
    dependency_remediation_parser.add_argument("--output-dir", type=Path, required=True)
    dependency_remediation_parser.add_argument("--project-root", type=Path, default=Path.cwd())

    draft_plan_parser = subparsers.add_parser(
        "draft-blueprint-plan",
        help="Build an LLM-backed draft blueprint planning artifact from discovery.",
    )
    draft_plan_parser.add_argument("discovery_artifact_path", type=Path)
    draft_plan_parser.add_argument("--output-dir", type=Path, required=True)
    draft_plan_parser.add_argument("--requirements", nargs="+", required=True)
    draft_plan_parser.add_argument("--dependency-plan", type=Path, default=None)
    draft_plan_parser.add_argument("--dependency-execution", type=Path, default=None)
    draft_plan_parser.add_argument("--dependency-remediation", type=Path, default=None)
    draft_plan_parser.add_argument("--model", default=DEFAULT_BLUEPRINT_PLAN_MODEL)
    draft_plan_parser.add_argument(
        "--max-budget",
        type=float,
        default=DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    )

    refine_draft_plan_parser = subparsers.add_parser(
        "refine-draft-blueprint-plan",
        help="Refine a draft blueprint planning artifact from a blocked freeze decision.",
    )
    refine_draft_plan_parser.add_argument("plan_artifact_path", type=Path)
    refine_draft_plan_parser.add_argument("--freeze-decision", type=Path, required=True)
    refine_draft_plan_parser.add_argument("--output-dir", type=Path, required=True)
    refine_draft_plan_parser.add_argument("--model", default=DEFAULT_BLUEPRINT_PLAN_MODEL)
    refine_draft_plan_parser.add_argument(
        "--max-budget",
        type=float,
        default=DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    )

    retry_freeze_parser = subparsers.add_parser(
        "retry-freeze",
        help="Run one explicit refine -> materialize -> refreeze chain from blocked freeze input.",
    )
    retry_freeze_parser.add_argument("plan_artifact_path", type=Path)
    retry_freeze_parser.add_argument("--freeze-decision", type=Path, required=True)
    retry_freeze_parser.add_argument("--output-dir", type=Path, required=True)
    retry_freeze_parser.add_argument("--model", default=DEFAULT_BLUEPRINT_PLAN_MODEL)
    retry_freeze_parser.add_argument(
        "--max-budget",
        type=float,
        default=DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    )

    author_draft_parser = subparsers.add_parser(
        "materialize-draft-bundle",
        help="Materialize a six-file draft bundle and freeze-readiness report from a planning artifact.",
    )
    author_draft_parser.add_argument("plan_artifact_path", type=Path)
    author_draft_parser.add_argument("--output-dir", type=Path, required=True)

    freeze_parser = subparsers.add_parser(
        "decide-freeze",
        help="Build an explicit approve/block freeze decision and promote only when approved.",
    )
    freeze_parser.add_argument("bundle_dir", type=Path)
    freeze_parser.add_argument("--output-dir", type=Path, required=True)
    freeze_parser.add_argument("--readiness-report", type=Path, default=None)

    front_half_parser = subparsers.add_parser(
        "front-half-acceptance",
        help="Run realistic-input discovery through freeze decision and review the front-half result.",
    )
    front_half_parser.add_argument("input_path", type=Path)
    front_half_parser.add_argument("--output-dir", type=Path, required=True)
    front_half_parser.add_argument("--requirements", nargs="+", required=True)
    front_half_parser.add_argument("--project-root", type=Path, default=Path.cwd())
    front_half_parser.add_argument("--packages", nargs="*", default=[])
    front_half_parser.add_argument("--retrieval-artifact", nargs="*", default=[])
    front_half_parser.add_argument("--allow-install", action="store_true")
    front_half_parser.add_argument("--model", default=DEFAULT_FRONT_HALF_ACCEPTANCE_MODEL)
    front_half_parser.add_argument("--max-budget", type=float, default=DEFAULT_FRONT_HALF_ACCEPTANCE_MAX_BUDGET)
    front_half_parser.add_argument("--max-samples", type=int, default=5)

    front_half_suite_parser = subparsers.add_parser(
        "front-half-acceptance-suite",
        help="Run realistic-input front-half acceptance across shipped examples.",
    )
    front_half_suite_parser.add_argument("--output-dir", type=Path, required=True)
    front_half_suite_parser.add_argument("--examples-root", type=Path, default=None)
    front_half_suite_parser.add_argument("--allow-install", action="store_true")
    front_half_suite_parser.add_argument("--model", default=DEFAULT_FRONT_HALF_ACCEPTANCE_MODEL)
    front_half_suite_parser.add_argument(
        "--max-budget",
        type=float,
        default=DEFAULT_FRONT_HALF_ACCEPTANCE_MAX_BUDGET,
    )
    front_half_suite_parser.add_argument("--max-samples", type=int, default=5)

    prove_parser = subparsers.add_parser("prove-example", help="Build a full proof bundle.")
    prove_parser.add_argument("blueprint_dir", type=Path)
    prove_parser.add_argument("--output-dir", type=Path, required=True)
    prove_parser.add_argument("--fresh-run-trials", type=int, default=3)
    prove_parser.add_argument("--generator", choices=["deterministic", "llm"], default="deterministic")
    prove_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    prove_parser.add_argument("--max-budget", type=float, default=0.50)

    fresh_runs_parser = subparsers.add_parser("fresh-runs", help="Run repeated fresh generation trials.")
    fresh_runs_parser.add_argument("blueprint_dir", type=Path)
    fresh_runs_parser.add_argument("--output-dir", type=Path, required=True)
    fresh_runs_parser.add_argument("--trials", type=int, default=3)
    fresh_runs_parser.add_argument("--generator", choices=["deterministic", "llm"], default="deterministic")
    fresh_runs_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    fresh_runs_parser.add_argument("--max-budget", type=float, default=0.50)

    compare_parser = subparsers.add_parser(
        "compare-generators",
        help="Build a persisted comparison report across generator modes.",
    )
    compare_parser.add_argument("blueprint_dir", type=Path)
    compare_parser.add_argument("--output-dir", type=Path, required=True)
    compare_parser.add_argument(
        "--generators",
        nargs="+",
        choices=["deterministic", "llm"],
        default=["deterministic", "llm"],
    )
    compare_parser.add_argument("--fresh-run-trials", type=int, default=2)
    compare_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    compare_parser.add_argument("--max-budget", type=float, default=0.50)

    acceptance_parser = subparsers.add_parser(
        "acceptance-review",
        help="Build a persisted requirements-aware acceptance report for one blueprint.",
    )
    acceptance_parser.add_argument("blueprint_dir", type=Path)
    acceptance_parser.add_argument("--output-dir", type=Path, required=True)
    acceptance_parser.add_argument("--mode", choices=["reference", "deterministic", "llm"], default="deterministic")
    acceptance_parser.add_argument("--realistic-input", type=Path, default=None)
    acceptance_parser.add_argument("--record-index", type=int, default=0)
    acceptance_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    acceptance_parser.add_argument("--max-budget", type=float, default=0.50)

    semantic_compare_parser = subparsers.add_parser(
        "semantic-compare",
        help="Build a persisted semantic comparison report for one blueprint.",
    )
    semantic_compare_parser.add_argument("blueprint_dir", type=Path)
    semantic_compare_parser.add_argument("--output-dir", type=Path, required=True)
    semantic_compare_parser.add_argument(
        "--modes",
        nargs="+",
        choices=["reference", "deterministic", "llm"],
        default=["reference", "deterministic"],
    )
    semantic_compare_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    semantic_compare_parser.add_argument("--max-budget", type=float, default=0.50)

    list_examples_parser = subparsers.add_parser(
        "list-examples",
        help="List shipped blueprint examples.",
    )
    list_examples_parser.add_argument("--examples-root", type=Path, default=None)

    prove_suite_parser = subparsers.add_parser(
        "prove-suite",
        help="Build persisted proof bundles across shipped examples.",
    )
    prove_suite_parser.add_argument("--output-dir", type=Path, required=True)
    prove_suite_parser.add_argument("--examples-root", type=Path, default=None)
    prove_suite_parser.add_argument("--fresh-run-trials", type=int, default=2)
    prove_suite_parser.add_argument("--generator", choices=["deterministic", "llm"], default="deterministic")
    prove_suite_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    prove_suite_parser.add_argument("--max-budget", type=float, default=0.50)

    compare_suite_parser = subparsers.add_parser(
        "compare-suite",
        help="Build persisted comparison artifacts across shipped examples.",
    )
    compare_suite_parser.add_argument("--output-dir", type=Path, required=True)
    compare_suite_parser.add_argument("--examples-root", type=Path, default=None)
    compare_suite_parser.add_argument(
        "--generators",
        nargs="+",
        choices=["deterministic", "llm"],
        default=["deterministic", "llm"],
    )
    compare_suite_parser.add_argument("--fresh-run-trials", type=int, default=2)
    compare_suite_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    compare_suite_parser.add_argument("--max-budget", type=float, default=0.50)

    semantic_compare_suite_parser = subparsers.add_parser(
        "semantic-compare-suite",
        help="Build persisted semantic comparison artifacts across shipped examples.",
    )
    semantic_compare_suite_parser.add_argument("--output-dir", type=Path, required=True)
    semantic_compare_suite_parser.add_argument("--examples-root", type=Path, default=None)
    semantic_compare_suite_parser.add_argument(
        "--modes",
        nargs="+",
        choices=["reference", "deterministic", "llm"],
        default=["reference", "deterministic"],
    )
    semantic_compare_suite_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    semantic_compare_suite_parser.add_argument("--max-budget", type=float, default=0.50)

    acceptance_suite_parser = subparsers.add_parser(
        "acceptance-review-suite",
        help="Build persisted requirements-aware acceptance reports across shipped examples.",
    )
    acceptance_suite_parser.add_argument("--output-dir", type=Path, required=True)
    acceptance_suite_parser.add_argument("--examples-root", type=Path, default=None)
    acceptance_suite_parser.add_argument("--mode", choices=["reference", "deterministic", "llm"], default="deterministic")
    acceptance_suite_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    acceptance_suite_parser.add_argument("--max-budget", type=float, default=0.50)

    realistic_acceptance_suite_parser = subparsers.add_parser(
        "acceptance-review-realistic-suite",
        help="Build persisted realistic-input acceptance reports across shipped examples and modes.",
    )
    realistic_acceptance_suite_parser.add_argument("--output-dir", type=Path, required=True)
    realistic_acceptance_suite_parser.add_argument("--examples-root", type=Path, default=None)
    realistic_acceptance_suite_parser.add_argument(
        "--modes",
        nargs="+",
        choices=["reference", "deterministic", "llm"],
        default=["reference", "deterministic"],
    )
    realistic_acceptance_suite_parser.add_argument("--record-index", type=int, default=0)
    realistic_acceptance_suite_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    realistic_acceptance_suite_parser.add_argument("--max-budget", type=float, default=0.50)

    realistic_acceptance_compare_parser = subparsers.add_parser(
        "acceptance-review-realistic-compare",
        help="Build persisted realistic-input acceptance comparison for one blueprint across modes.",
    )
    realistic_acceptance_compare_parser.add_argument("blueprint_dir", type=Path)
    realistic_acceptance_compare_parser.add_argument("--output-dir", type=Path, required=True)
    realistic_acceptance_compare_parser.add_argument("--realistic-input", type=Path, required=True)
    realistic_acceptance_compare_parser.add_argument(
        "--modes",
        nargs="+",
        choices=["reference", "deterministic", "llm"],
        default=["reference", "deterministic", "llm"],
    )
    realistic_acceptance_compare_parser.add_argument("--record-index", type=int, default=0)
    realistic_acceptance_compare_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    realistic_acceptance_compare_parser.add_argument("--max-budget", type=float, default=0.50)

    recommend_default_parser = subparsers.add_parser(
        "recommend-default-generator",
        help="Build an evidence-backed default-generator recommendation.",
    )
    recommend_default_parser.add_argument("--output-dir", type=Path, required=True)
    recommend_default_parser.add_argument("--examples-root", type=Path, default=None)
    recommend_default_parser.add_argument(
        "--generators",
        nargs="+",
        choices=["deterministic", "llm"],
        default=["deterministic"],
    )
    recommend_default_parser.add_argument("--fresh-run-trials", type=int, default=2)
    recommend_default_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    recommend_default_parser.add_argument("--max-budget", type=float, default=0.50)

    live_readiness_parser = subparsers.add_parser(
        "live-llm-readiness",
        help="Build one persisted realistic-input live-readiness artifact for the LLM lane.",
    )
    live_readiness_parser.add_argument("--output-dir", type=Path, required=True)
    live_readiness_parser.add_argument("--examples-root", type=Path, default=None)
    live_readiness_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    live_readiness_parser.add_argument("--max-budget", type=float, default=0.50)

    live_readiness_suite_parser = subparsers.add_parser(
        "live-llm-readiness-suite",
        help="Build one persisted realistic-input suite live-readiness artifact for the LLM lane.",
    )
    live_readiness_suite_parser.add_argument("--output-dir", type=Path, required=True)
    live_readiness_suite_parser.add_argument("--examples-root", type=Path, default=None)
    live_readiness_suite_parser.add_argument("--model", default="gemini/gemini-2.5-flash-lite")
    live_readiness_suite_parser.add_argument("--max-budget", type=float, default=0.50)

    args = parser.parse_args()
    if args.command == "verify-blueprint":
        return _verify_blueprint(args.blueprint_dir)
    if args.command == "packet-sufficiency":
        return _packet_sufficiency(args.blueprint_dir, args.output_dir)
    if args.command == "generate-components":
        return _generate_components(
            args.blueprint_dir,
            args.output_dir,
            cast(GeneratorKind, args.generator),
            args.model,
            args.max_budget,
        )
    if args.command == "discover-input":
        return _discover_input(
            args.input_path,
            args.output_dir,
            args.project_root,
            cast(list[str], args.packages),
            [Path(path) for path in cast(list[str], args.retrieval_artifact)],
            args.max_samples,
        )
    if args.command == "inspect-environment":
        return _inspect_environment(
            args.output_dir,
            args.project_root,
            cast(list[str], args.packages),
        )
    if args.command == "inspect-project-context":
        return _inspect_project_context(
            args.output_dir,
            args.project_root,
            args.max_documents,
        )
    if args.command == "retrieve-context":
        return _retrieve_context(
            args.output_dir,
            cast(list[str], args.web_query),
            cast(list[str], args.repo_query),
            cast(list[str], args.repo),
            args.web_top_k,
            args.repo_limit,
        )
    if args.command == "plan-dependencies":
        return _plan_dependencies(
            args.discovery_artifact_path,
            args.output_dir,
            cast(list[str], args.requirements),
            args.model,
            args.max_budget,
        )
    if args.command == "probe-dependencies":
        return _probe_dependencies(
            args.dependency_plan_path,
            args.output_dir,
            args.allow_install,
            args.project_root,
        )
    if args.command == "remediate-dependencies":
        return _remediate_dependencies(
            args.dependency_execution_artifact_path,
            args.output_dir,
            args.project_root,
        )
    if args.command == "draft-blueprint-plan":
        return _draft_blueprint_plan(
            args.discovery_artifact_path,
            args.output_dir,
            cast(list[str], args.requirements),
            args.dependency_plan,
            args.dependency_execution,
            args.dependency_remediation,
            args.model,
            args.max_budget,
        )
    if args.command == "refine-draft-blueprint-plan":
        return _refine_draft_blueprint_plan(
            args.plan_artifact_path,
            args.freeze_decision,
            args.output_dir,
            args.model,
            args.max_budget,
        )
    if args.command == "retry-freeze":
        return _retry_freeze(
            args.plan_artifact_path,
            args.freeze_decision,
            args.output_dir,
            args.model,
            args.max_budget,
        )
    if args.command == "materialize-draft-bundle":
        return _materialize_draft_bundle(
            args.plan_artifact_path,
            args.output_dir,
        )
    if args.command == "decide-freeze":
        return _decide_freeze(
            args.bundle_dir,
            args.output_dir,
            args.readiness_report,
        )
    if args.command == "front-half-acceptance":
        return _front_half_acceptance(
            args.input_path,
            args.output_dir,
            cast(list[str], args.requirements),
            args.project_root,
            cast(list[str], args.packages),
            [Path(path) for path in cast(list[str], args.retrieval_artifact)],
            args.allow_install,
            args.model,
            args.max_budget,
            args.max_samples,
        )
    if args.command == "front-half-acceptance-suite":
        return _front_half_acceptance_suite(
            args.output_dir,
            args.examples_root,
            args.allow_install,
            args.model,
            args.max_budget,
            args.max_samples,
        )
    if args.command == "prove-example":
        return _prove_example(
            args.blueprint_dir,
            args.output_dir,
            args.fresh_run_trials,
            cast(GeneratorKind, args.generator),
            args.model,
            args.max_budget,
        )
    if args.command == "fresh-runs":
        return _fresh_runs(
            args.blueprint_dir,
            args.output_dir,
            args.trials,
            cast(GeneratorKind, args.generator),
            args.model,
            args.max_budget,
        )
    if args.command == "compare-generators":
        return _compare_generators(
            args.blueprint_dir,
            args.output_dir,
            [cast(GeneratorKind, generator) for generator in args.generators],
            args.fresh_run_trials,
            args.model,
            args.max_budget,
        )
    if args.command == "acceptance-review":
        return _acceptance_review(
            args.blueprint_dir,
            args.output_dir,
            cast(AcceptanceMode, args.mode),
            args.realistic_input,
            args.record_index,
            args.model,
            args.max_budget,
        )
    if args.command == "semantic-compare":
        return _semantic_compare(
            args.blueprint_dir,
            args.output_dir,
            [cast(ComparisonMode, mode) for mode in args.modes],
            args.model,
            args.max_budget,
        )
    if args.command == "list-examples":
        return _list_examples(args.examples_root)
    if args.command == "prove-suite":
        return _prove_suite(
            args.output_dir,
            args.examples_root,
            args.fresh_run_trials,
            cast(GeneratorKind, args.generator),
            args.model,
            args.max_budget,
        )
    if args.command == "compare-suite":
        return _compare_suite(
            args.output_dir,
            args.examples_root,
            [cast(GeneratorKind, generator) for generator in args.generators],
            args.fresh_run_trials,
            args.model,
            args.max_budget,
        )
    if args.command == "semantic-compare-suite":
        return _semantic_compare_suite(
            args.output_dir,
            args.examples_root,
            [cast(ComparisonMode, mode) for mode in args.modes],
            args.model,
            args.max_budget,
        )
    if args.command == "acceptance-review-suite":
        return _acceptance_review_suite(
            args.output_dir,
            args.examples_root,
            cast(AcceptanceMode, args.mode),
            args.model,
            args.max_budget,
        )
    if args.command == "acceptance-review-realistic-suite":
        return _acceptance_review_realistic_suite(
            args.output_dir,
            args.examples_root,
            [cast(AcceptanceMode, mode) for mode in args.modes],
            args.record_index,
            args.model,
            args.max_budget,
        )
    if args.command == "acceptance-review-realistic-compare":
        return _acceptance_review_realistic_compare(
            args.blueprint_dir,
            args.output_dir,
            [cast(AcceptanceMode, mode) for mode in args.modes],
            args.realistic_input,
            args.record_index,
            args.model,
            args.max_budget,
        )
    if args.command == "recommend-default-generator":
        return _recommend_default_generator(
            args.output_dir,
            args.examples_root,
            [cast(GeneratorKind, generator) for generator in args.generators],
            args.fresh_run_trials,
            args.model,
            args.max_budget,
        )
    if args.command == "live-llm-readiness":
        return _live_llm_readiness(
            args.output_dir,
            args.examples_root,
            args.model,
            args.max_budget,
        )
    if args.command == "live-llm-readiness-suite":
        return _live_llm_readiness_suite(
            args.output_dir,
            args.examples_root,
            args.model,
            args.max_budget,
        )
    raise ValueError(f"unknown command: {args.command}")


def _verify_blueprint(blueprint_dir: Path) -> int:
    """Validate a blueprint and print a compact summary."""

    blueprint = load_blueprint_dir(blueprint_dir)
    result = validate_blueprint(blueprint)
    print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0 if result.passed else 1


def _packet_sufficiency(blueprint_dir: Path, output_dir: Path) -> int:
    """Build and print a persisted packet-sufficiency report."""

    report = build_packet_sufficiency_report(blueprint_dir=blueprint_dir, output_dir=output_dir)
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _generate_components(
    blueprint_dir: Path,
    output_dir: Path,
    generator: GeneratorKind,
    model: str,
    max_budget: float,
) -> int:
    """Emit generated Python component modules for one blueprint."""

    blueprint = load_blueprint_dir(blueprint_dir)
    packet_bundle = compile_packets(blueprint)
    package = emit_generated_package(
        packet_bundle,
        output_dir,
        generator_kind=generator,
        llm_model=model,
        llm_max_budget=max_budget,
        trace_id_prefix="ac14/cli_generate_components",
    )
    print(json.dumps(package.model_dump(mode="json"), indent=2))
    return 0


def _discover_input(
    input_path: Path,
    output_dir: Path,
    project_root: Path | None,
    packages: list[str],
    retrieval_artifact_paths: list[Path],
    max_samples: int,
) -> int:
    """Build and print a persisted pre-freeze discovery artifact."""

    artifact = build_discovery_artifact(
        input_path=input_path,
        output_dir=output_dir,
        project_root=project_root,
        requested_packages=packages,
        retrieval_artifact_paths=retrieval_artifact_paths,
        max_samples=max_samples,
    )
    print(json.dumps(artifact.model_dump(mode="json"), indent=2))
    return 0


def _inspect_environment(
    output_dir: Path,
    project_root: Path | None,
    packages: list[str],
) -> int:
    """Build and print the persisted discovery environment inventory."""

    inventory = persist_environment_inventory(
        output_dir=output_dir,
        project_root=project_root,
        requested_packages=packages,
    )
    print(json.dumps(inventory.model_dump(mode="json"), indent=2))
    return 0


def _inspect_project_context(
    output_dir: Path,
    project_root: Path | None,
    max_documents: int,
) -> int:
    """Build and print the persisted local project-document inventory."""

    inventory = persist_project_context_inventory(
        output_dir=output_dir,
        project_root=project_root,
        max_documents=max_documents,
    )
    print(json.dumps(inventory.model_dump(mode="json"), indent=2))
    return 0


def _retrieve_context(
    output_dir: Path,
    web_queries: list[str],
    repo_queries: list[str],
    repos: list[str],
    web_top_k: int,
    repo_limit: int,
) -> int:
    """Build and print a persisted external retrieval artifact."""

    artifact = build_external_retrieval_artifact(
        output_dir=output_dir,
        web_queries=[
            WebRetrievalQuery(query=query, top_k=web_top_k)
            for query in web_queries
        ],
        repo_queries=[
            RepoRetrievalQuery(query=query, repos=repos, limit=repo_limit)
            for query in repo_queries
        ],
    )
    print(json.dumps(artifact.model_dump(mode="json"), indent=2))
    return 0


def _plan_dependencies(
    discovery_artifact_path: Path,
    output_dir: Path,
    requirements: list[str],
    model: str,
    max_budget: float,
) -> int:
    """Build and print a persisted dependency and library planning artifact."""

    plan = build_dependency_plan(
        discovery_artifact_path=discovery_artifact_path,
        output_dir=output_dir,
        requirements=requirements,
        model=model,
        max_budget=max_budget,
    )
    print(json.dumps(plan.model_dump(mode="json"), indent=2))
    return 0


def _probe_dependencies(
    dependency_plan_path: Path,
    output_dir: Path,
    allow_install: bool,
    project_root: Path,
) -> int:
    """Build and print a persisted dependency execution-probe artifact."""

    artifact = build_dependency_execution_artifact(
        dependency_plan_path=dependency_plan_path,
        output_dir=output_dir,
        allow_install=allow_install,
        project_root=project_root,
    )
    print(json.dumps(artifact.model_dump(mode="json"), indent=2))
    return 0


def _remediate_dependencies(
    dependency_execution_artifact_path: Path,
    output_dir: Path,
    project_root: Path,
) -> int:
    """Build and print a persisted dependency-remediation artifact."""

    artifact = build_dependency_remediation_artifact(
        dependency_execution_artifact_path=dependency_execution_artifact_path,
        output_dir=output_dir,
        project_root=project_root,
    )
    print(json.dumps(artifact.model_dump(mode="json"), indent=2))
    return 0


def _draft_blueprint_plan(
    discovery_artifact_path: Path,
    output_dir: Path,
    requirements: list[str],
    dependency_plan_path: Path | None,
    dependency_execution_artifact_path: Path | None,
    dependency_remediation_artifact_path: Path | None,
    model: str,
    max_budget: float,
) -> int:
    """Build and print a persisted draft blueprint planning artifact."""

    plan = build_draft_blueprint_plan(
        discovery_artifact_path=discovery_artifact_path,
        output_dir=output_dir,
        requirements=requirements,
        dependency_plan_path=dependency_plan_path,
        dependency_execution_artifact_path=dependency_execution_artifact_path,
        dependency_remediation_artifact_path=dependency_remediation_artifact_path,
        model=model,
        max_budget=max_budget,
    )
    print(json.dumps(plan.model_dump(mode="json"), indent=2))
    return 0


def _refine_draft_blueprint_plan(
    plan_artifact_path: Path,
    freeze_decision_path: Path,
    output_dir: Path,
    model: str,
    max_budget: float,
) -> int:
    """Build and print a remediation-driven refined draft planning artifact."""

    plan = build_refined_draft_blueprint_plan(
        plan_artifact_path=plan_artifact_path,
        freeze_decision_path=freeze_decision_path,
        output_dir=output_dir,
        model=model,
        max_budget=max_budget,
    )
    print(json.dumps(plan.model_dump(mode="json"), indent=2))
    return 0


def _retry_freeze(
    plan_artifact_path: Path,
    freeze_decision_path: Path,
    output_dir: Path,
    model: str,
    max_budget: float,
) -> int:
    """Build and print one explicit freeze-retry artifact."""

    artifact = build_freeze_retry_artifact(
        plan_artifact_path=plan_artifact_path,
        freeze_decision_path=freeze_decision_path,
        output_dir=output_dir,
        model=model,
        max_budget=max_budget,
    )
    print(json.dumps(artifact.model_dump(mode="json"), indent=2))
    return 0


def _materialize_draft_bundle(
    plan_artifact_path: Path,
    output_dir: Path,
) -> int:
    """Build and print a persisted draft bundle plus readiness report."""

    manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=plan_artifact_path,
        output_dir=output_dir,
    )
    print(json.dumps(manifest.model_dump(mode="json"), indent=2))
    return 0


def _decide_freeze(
    bundle_dir: Path,
    output_dir: Path,
    readiness_report: Path | None,
) -> int:
    """Build and print a persisted freeze decision artifact."""

    decision = build_freeze_decision(
        bundle_dir=bundle_dir,
        output_dir=output_dir,
        readiness_report_path=readiness_report,
    )
    print(json.dumps(decision.model_dump(mode="json"), indent=2))
    return 0


def _front_half_acceptance(
    input_path: Path,
    output_dir: Path,
    requirements: list[str],
    project_root: Path | None,
    packages: list[str],
    retrieval_artifact_paths: list[Path],
    allow_install: bool,
    model: str,
    max_budget: float,
    max_samples: int,
) -> int:
    """Build and print a persisted realistic-input front-half acceptance artifact."""

    artifact = build_front_half_acceptance_report(
        input_path=input_path,
        output_dir=output_dir,
        requirements=requirements,
        project_root=project_root,
        requested_packages=packages,
        retrieval_artifact_paths=retrieval_artifact_paths,
        allow_install=allow_install,
        model=model,
        max_budget=max_budget,
        max_samples=max_samples,
    )
    print(json.dumps(artifact.model_dump(mode="json"), indent=2))
    return 0


def _front_half_acceptance_suite(
    output_dir: Path,
    examples_root: Path | None,
    allow_install: bool,
    model: str,
    max_budget: float,
    max_samples: int,
) -> int:
    """Build and print a persisted front-half acceptance suite artifact."""

    artifact = build_front_half_acceptance_suite_report(
        output_dir=output_dir,
        examples_root=examples_root,
        allow_install=allow_install,
        model=model,
        max_budget=max_budget,
        max_samples=max_samples,
    )
    print(json.dumps(artifact.model_dump(mode="json"), indent=2))
    return 0


def _prove_example(
    blueprint_dir: Path,
    output_dir: Path,
    fresh_run_trials: int,
    generator: GeneratorKind,
    model: str,
    max_budget: float,
) -> int:
    """Build the full persisted proof bundle for one blueprint."""

    manifest = build_evidence_bundle(
        blueprint_dir=blueprint_dir,
        output_dir=output_dir,
        fresh_run_trials=fresh_run_trials,
        generator_kind=generator,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(manifest.model_dump(mode="json"), indent=2))
    return 0


def _fresh_runs(
    blueprint_dir: Path,
    output_dir: Path,
    trials: int,
    generator: GeneratorKind,
    model: str,
    max_budget: float,
) -> int:
    """Run repeated fresh generation trials and print the persisted summary."""

    summary = run_fresh_generation_trials(
        blueprint_dir=blueprint_dir,
        output_dir=output_dir,
        trial_count=trials,
        generator_kind=generator,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(summary.model_dump(mode="json"), indent=2))
    return 0


def _compare_generators(
    blueprint_dir: Path,
    output_dir: Path,
    generators: list[GeneratorKind],
    fresh_run_trials: int,
    model: str,
    max_budget: float,
) -> int:
    """Build a persisted comparison report across generator modes."""

    report = build_generator_comparison_report(
        blueprint_dir=blueprint_dir,
        output_dir=output_dir,
        generator_kinds=generators,
        fresh_run_trials=fresh_run_trials,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _acceptance_review(
    blueprint_dir: Path,
    output_dir: Path,
    mode: AcceptanceMode,
    realistic_input: Path | None,
    record_index: int,
    model: str,
    max_budget: float,
) -> int:
    """Build a persisted requirements-aware acceptance report for one blueprint."""

    report = build_acceptance_report(
        blueprint_dir=blueprint_dir,
        output_dir=output_dir,
        mode=mode,
        realistic_input_path=realistic_input,
        realistic_input_record_index=record_index,
        model=model,
        max_budget=max_budget,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _semantic_compare(
    blueprint_dir: Path,
    output_dir: Path,
    modes: list[ComparisonMode],
    model: str,
    max_budget: float,
) -> int:
    """Build a persisted semantic comparison report for one blueprint."""

    report = build_semantic_comparison_report(
        blueprint_dir=blueprint_dir,
        output_dir=output_dir,
        modes=modes,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _acceptance_review_suite(
    output_dir: Path,
    examples_root: Path | None,
    mode: AcceptanceMode,
    model: str,
    max_budget: float,
) -> int:
    """Build persisted requirements-aware acceptance reports across shipped examples."""

    report = build_suite_acceptance_report(
        output_dir=output_dir,
        examples_root=examples_root,
        mode=mode,
        model=model,
        max_budget=max_budget,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _acceptance_review_realistic_suite(
    output_dir: Path,
    examples_root: Path | None,
    modes: list[AcceptanceMode],
    record_index: int,
    model: str,
    max_budget: float,
) -> int:
    """Build realistic-input acceptance reports across shipped examples and modes."""

    report = build_realistic_suite_acceptance_report(
        output_dir=output_dir,
        examples_root=examples_root,
        modes=modes,
        realistic_input_record_index=record_index,
        model=model,
        max_budget=max_budget,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _acceptance_review_realistic_compare(
    blueprint_dir: Path,
    output_dir: Path,
    modes: list[AcceptanceMode],
    realistic_input: Path,
    record_index: int,
    model: str,
    max_budget: float,
) -> int:
    """Build realistic-input acceptance comparison for one blueprint across modes."""

    report = build_realistic_mode_comparison_report(
        blueprint_dir=blueprint_dir,
        output_dir=output_dir,
        modes=modes,
        realistic_input_path=realistic_input,
        realistic_input_record_index=record_index,
        model=model,
        max_budget=max_budget,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _list_examples(examples_root: Path | None) -> int:
    """Print shipped blueprint examples."""

    examples = discover_shipped_blueprints(examples_root)
    print(
        json.dumps(
            [example.model_dump(mode="json") for example in examples],
            indent=2,
        ),
    )
    return 0


def _prove_suite(
    output_dir: Path,
    examples_root: Path | None,
    fresh_run_trials: int,
    generator: GeneratorKind,
    model: str,
    max_budget: float,
) -> int:
    """Build a persisted suite proof report."""

    report = build_suite_proof_report(
        output_dir=output_dir,
        examples_root=examples_root,
        fresh_run_trials=fresh_run_trials,
        generator_kind=generator,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _compare_suite(
    output_dir: Path,
    examples_root: Path | None,
    generators: list[GeneratorKind],
    fresh_run_trials: int,
    model: str,
    max_budget: float,
) -> int:
    """Build a persisted suite comparison report."""

    report = build_suite_comparison_report(
        output_dir=output_dir,
        examples_root=examples_root,
        generator_kinds=generators,
        fresh_run_trials=fresh_run_trials,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _semantic_compare_suite(
    output_dir: Path,
    examples_root: Path | None,
    modes: list[ComparisonMode],
    model: str,
    max_budget: float,
) -> int:
    """Build a persisted suite semantic comparison report."""

    report = build_suite_semantic_comparison_report(
        output_dir=output_dir,
        examples_root=examples_root,
        modes=modes,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2))
    return 0


def _recommend_default_generator(
    output_dir: Path,
    examples_root: Path | None,
    generators: list[GeneratorKind],
    fresh_run_trials: int,
    model: str,
    max_budget: float,
) -> int:
    """Build the evidence-backed default-generator recommendation."""

    recommendation = build_default_generator_recommendation(
        output_dir=output_dir,
        examples_root=examples_root,
        generator_kinds=generators,
        fresh_run_trials=fresh_run_trials,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(recommendation.model_dump(mode="json"), indent=2))
    return 0


def _live_llm_readiness(
    output_dir: Path,
    examples_root: Path | None,
    model: str,
    max_budget: float,
) -> int:
    """Build and print a persisted live-readiness artifact for the LLM lane."""

    artifact = build_llm_live_readiness_artifact(
        output_dir=output_dir,
        examples_root=examples_root,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(artifact.model_dump(mode="json"), indent=2))
    return 0


def _live_llm_readiness_suite(
    output_dir: Path,
    examples_root: Path | None,
    model: str,
    max_budget: float,
) -> int:
    """Build and print a persisted suite-level live-readiness artifact for the LLM lane."""

    artifact = build_llm_live_readiness_suite_artifact(
        output_dir=output_dir,
        examples_root=examples_root,
        llm_model=model,
        llm_max_budget=max_budget,
    )
    print(json.dumps(artifact.model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI entrypoints for AC14 proof-surface workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from ac14.acceptance import (
    AcceptanceMode,
    build_acceptance_report,
    build_suite_acceptance_report,
)
from ac14.blueprint_planning import (
    DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    DEFAULT_BLUEPRINT_PLAN_MODEL,
    build_draft_blueprint_plan,
)
from ac14.comparison import build_generator_comparison_report
from ac14.discovery import (
    build_discovery_artifact,
    persist_environment_inventory,
    persist_project_context_inventory,
)
from ac14.draft_authoring import materialize_draft_blueprint_bundle
from ac14.evidence_bundle import build_evidence_bundle
from ac14.examples import discover_shipped_blueprints
from ac14.freeze_decision import build_freeze_decision
from ac14.generated_codegen import GeneratorKind, emit_generated_package
from ac14.generated_evidence import run_fresh_generation_trials
from ac14.loader import load_blueprint_dir
from ac14.packets import compile_packets
from ac14.recommendation import build_default_generator_recommendation
from ac14.semantic_comparison import ComparisonMode, build_semantic_comparison_report
from ac14.semantic_suite import build_suite_semantic_comparison_report
from ac14.suite import build_suite_comparison_report, build_suite_proof_report
from ac14.validation import validate_blueprint


def main() -> int:
    """Run the AC14 command-line interface."""

    parser = argparse.ArgumentParser(prog="python -m ac14")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser("verify-blueprint", help="Validate a blueprint bundle.")
    verify_parser.add_argument("blueprint_dir", type=Path)

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

    draft_plan_parser = subparsers.add_parser(
        "draft-blueprint-plan",
        help="Build an LLM-backed draft blueprint planning artifact from discovery.",
    )
    draft_plan_parser.add_argument("discovery_artifact_path", type=Path)
    draft_plan_parser.add_argument("--output-dir", type=Path, required=True)
    draft_plan_parser.add_argument("--requirements", nargs="+", required=True)
    draft_plan_parser.add_argument("--model", default=DEFAULT_BLUEPRINT_PLAN_MODEL)
    draft_plan_parser.add_argument(
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

    args = parser.parse_args()
    if args.command == "verify-blueprint":
        return _verify_blueprint(args.blueprint_dir)
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
    if args.command == "draft-blueprint-plan":
        return _draft_blueprint_plan(
            args.discovery_artifact_path,
            args.output_dir,
            cast(list[str], args.requirements),
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
    if args.command == "recommend-default-generator":
        return _recommend_default_generator(
            args.output_dir,
            args.examples_root,
            [cast(GeneratorKind, generator) for generator in args.generators],
            args.fresh_run_trials,
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
    max_samples: int,
) -> int:
    """Build and print a persisted pre-freeze discovery artifact."""

    artifact = build_discovery_artifact(
        input_path=input_path,
        output_dir=output_dir,
        project_root=project_root,
        requested_packages=packages,
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


def _draft_blueprint_plan(
    discovery_artifact_path: Path,
    output_dir: Path,
    requirements: list[str],
    model: str,
    max_budget: float,
) -> int:
    """Build and print a persisted draft blueprint planning artifact."""

    plan = build_draft_blueprint_plan(
        discovery_artifact_path=discovery_artifact_path,
        output_dir=output_dir,
        requirements=requirements,
        model=model,
        max_budget=max_budget,
    )
    print(json.dumps(plan.model_dump(mode="json"), indent=2))
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
    model: str,
    max_budget: float,
) -> int:
    """Build a persisted requirements-aware acceptance report for one blueprint."""

    report = build_acceptance_report(
        blueprint_dir=blueprint_dir,
        output_dir=output_dir,
        mode=mode,
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


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI entrypoints for AC14 proof-surface workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from ac14.comparison import build_generator_comparison_report
from ac14.evidence_bundle import build_evidence_bundle
from ac14.examples import discover_shipped_blueprints
from ac14.generated_codegen import GeneratorKind, emit_generated_package
from ac14.generated_evidence import run_fresh_generation_trials
from ac14.loader import load_blueprint_dir
from ac14.packets import compile_packets
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


if __name__ == "__main__":
    raise SystemExit(main())

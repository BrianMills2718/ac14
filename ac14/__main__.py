"""CLI entrypoints for AC14 proof-surface workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ac14.evidence_bundle import build_evidence_bundle
from ac14.generated_codegen import emit_generated_package
from ac14.generated_evidence import run_fresh_generation_trials
from ac14.loader import load_blueprint_dir
from ac14.packets import compile_packets
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

    prove_parser = subparsers.add_parser("prove-example", help="Build a full proof bundle.")
    prove_parser.add_argument("blueprint_dir", type=Path)
    prove_parser.add_argument("--output-dir", type=Path, required=True)
    prove_parser.add_argument("--fresh-run-trials", type=int, default=3)

    fresh_runs_parser = subparsers.add_parser("fresh-runs", help="Run repeated fresh generation trials.")
    fresh_runs_parser.add_argument("blueprint_dir", type=Path)
    fresh_runs_parser.add_argument("--output-dir", type=Path, required=True)
    fresh_runs_parser.add_argument("--trials", type=int, default=3)

    args = parser.parse_args()
    if args.command == "verify-blueprint":
        return _verify_blueprint(args.blueprint_dir)
    if args.command == "generate-components":
        return _generate_components(args.blueprint_dir, args.output_dir)
    if args.command == "prove-example":
        return _prove_example(args.blueprint_dir, args.output_dir, args.fresh_run_trials)
    if args.command == "fresh-runs":
        return _fresh_runs(args.blueprint_dir, args.output_dir, args.trials)
    raise ValueError(f"unknown command: {args.command}")


def _verify_blueprint(blueprint_dir: Path) -> int:
    """Validate a blueprint and print a compact summary."""

    blueprint = load_blueprint_dir(blueprint_dir)
    result = validate_blueprint(blueprint)
    print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0 if result.passed else 1


def _generate_components(blueprint_dir: Path, output_dir: Path) -> int:
    """Emit generated Python component modules for one blueprint."""

    blueprint = load_blueprint_dir(blueprint_dir)
    packet_bundle = compile_packets(blueprint)
    package = emit_generated_package(packet_bundle, output_dir)
    print(json.dumps(package.model_dump(mode="json"), indent=2))
    return 0


def _prove_example(blueprint_dir: Path, output_dir: Path, fresh_run_trials: int) -> int:
    """Build the full persisted proof bundle for one blueprint."""

    manifest = build_evidence_bundle(
        blueprint_dir=blueprint_dir,
        output_dir=output_dir,
        fresh_run_trials=fresh_run_trials,
    )
    print(json.dumps(manifest.model_dump(mode="json"), indent=2))
    return 0


def _fresh_runs(blueprint_dir: Path, output_dir: Path, trials: int) -> int:
    """Run repeated fresh generation trials and print the persisted summary."""

    summary = run_fresh_generation_trials(
        blueprint_dir=blueprint_dir,
        output_dir=output_dir,
        trial_count=trials,
    )
    print(json.dumps(summary.model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

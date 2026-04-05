"""Single-trial runner with structured diagnosis for AC14 empirical comparisons.

Implements the agentic_scaffolding IterativeRunner protocol for AC14 paired trials.
Run one trial, get a clean DiagnosisArtifact — no batch blind spots.

Usage::

    runner = AC14TrialRunner(
        benchmark_dir="benchmarks/zeta_scale_40/back_half",
        output_dir=".ac14_out/debug_run",
        model="openrouter/openai/gpt-5.4",
    )
    result = runner.run_one("trial_1")
    diag = runner.diagnose("trial_1", result)
    diag.print_summary()

    # Or use the loop harness:
    from agentic_scaffolding.iterative_runner import run_one_loop
    run_one_loop(runner, ["trial_1", "trial_2", ...], output_dir=Path(...))

CLI::

    python -m ac14.trial_runner --benchmark benchmarks/zeta_scale_40/back_half \\
        --output .ac14_out/debug --model openrouter/openai/gpt-5.4 --trial 1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ac14.empirical_comparison import (
    DEFAULT_LLM_MAX_BUDGET,
    DEFAULT_LLM_MODEL,
    DEFAULT_MAX_ATTEMPTS,
    ConditionTrialReport,
    PairedTrialReport,
    load_benchmark_bundle,
    run_ac14_only_trial,
    run_paired_trial,
)

try:
    from agentic_scaffolding.iterative_runner import DiagnosisArtifact
except ImportError:
    # Fallback if agentic_scaffolding not installed — inline minimal version
    import dataclasses

    @dataclasses.dataclass
    class DiagnosisArtifact:  # type: ignore[no-redef]
        unit_id: str
        passed: bool
        one_line: str
        root_cause: str
        suggested_fix: str
        category: str
        structured: dict[str, Any] = dataclasses.field(default_factory=dict)

        def print_summary(self) -> None:
            status = "PASS" if self.passed else "FAIL"
            print(f"[{status}] {self.unit_id}: {self.one_line}")
            if not self.passed:
                print(f"  root cause : {self.root_cause}")
                print(f"  category   : {self.category}")
                print(f"  fix        : {self.suggested_fix}")

        def save(self, path: Path) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(dataclasses.asdict(self), indent=2))


_CATEGORY_FIX_MAP: dict[str, str] = {
    "generation": (
        "LLM generated invalid Python or missing build_component. "
        "Check .context.json and .prompt.json for the failing component. "
        "Run: make diagnose-attempt OUTPUT=<dir> TRIAL=N ATTEMPT=M COMPONENT=<id>"
    ),
    "runtime_outputs": (
        "Generated code ran but produced wrong field names or values, or a required "
        "port was missing. Check recomposition_report.json and runtime case diffs. "
        "Run: make diagnose-attempt OUTPUT=<dir> TRIAL=N ATTEMPT=M"
    ),
    "packet_tests": (
        "Packet-local fixture test failed. Usually a wrong formula or fixture bug. "
        "Check packet_test_report.json for the specific fixture and field mismatch."
    ),
    "success": "No fix needed.",
}


def _summarize_attempt(attempt: dict[str, Any]) -> tuple[str, str, str]:
    """Return (one_line, root_cause, category) for one attempt dict."""
    cat = attempt.get("failure_classification", {}).get("category", "unknown")
    detail = attempt.get("failure_classification", {}).get("detail", "")
    summary_lines = attempt.get("failure_summary", [])

    if cat == "success":
        return "passed", "n/a", "success"

    # Pull the most informative line from the summary
    root_cause = detail[:200] if detail else (summary_lines[0] if summary_lines else "no detail")

    one_line = f"{cat}: {root_cause[:120]}"
    return one_line, root_cause, cat


def diagnose_paired_trial(unit_id: str, report: PairedTrialReport) -> DiagnosisArtifact:
    """Convert a PairedTrialReport into a human+machine readable DiagnosisArtifact."""

    ac14_attempts = report.ac14.attempts
    mono_attempts = report.monolithic.attempts

    ac14_passed = any(a.passed for a in ac14_attempts)
    mono_passed = any(a.passed for a in mono_attempts)
    overall_passed = ac14_passed and mono_passed

    # Characterize AC14
    if ac14_passed:
        ac14_line = f"AC14 PASS (attempt {next(i+1 for i,a in enumerate(ac14_attempts) if a.passed)})"
        ac14_root = "n/a"
        ac14_cat = "success"
    else:
        last = ac14_attempts[-1]
        ac14_line, ac14_root, ac14_cat = _summarize_attempt(last.model_dump())

    # Characterize monolithic
    if mono_passed:
        mono_line = f"Mono PASS (attempt {next(i+1 for i,a in enumerate(mono_attempts) if a.passed)})"
        mono_root = "n/a"
        mono_cat = "success"
    else:
        last = mono_attempts[-1]
        mono_line, mono_root, mono_cat = _summarize_attempt(last.model_dump())

    # Dominant failure is whichever condition failed (AC14 takes priority for diagnosis)
    if not ac14_passed:
        dominant_cat = ac14_cat
        one_line = f"AC14 FAIL — {ac14_line} | Mono: {'PASS' if mono_passed else mono_line}"
        root_cause = f"AC14: {ac14_root}"
        if not mono_passed:
            root_cause += f"\nMono: {mono_root}"
    elif not mono_passed:
        dominant_cat = mono_cat
        one_line = f"AC14 PASS | Mono FAIL — {mono_line}"
        root_cause = f"Mono: {mono_root}"
    else:
        dominant_cat = "success"
        one_line = "both conditions passed"
        root_cause = "n/a"

    suggested_fix = _CATEGORY_FIX_MAP.get(dominant_cat, f"Unknown category '{dominant_cat}'")

    # Per-attempt breakdown for machine reading
    structured: dict[str, Any] = {
        "ac14_passed": ac14_passed,
        "mono_passed": mono_passed,
        "ac14_attempts": [
            {
                "attempt": i + 1,
                "passed": a.passed,
                "category": a.failure_classification.category if a.failure_classification else None,
                "detail": (a.failure_classification.detail[:300] if a.failure_classification else None),
                "packet_tests_passed": a.packet_tests_passed,
                "recomposition_passed": a.recomposition_passed,
                "runtime_cases": [
                    {"case_id": c.case_id, "matched": c.matched_expected, "error": c.error}
                    for c in (a.runtime_cases or [])
                ],
            }
            for i, a in enumerate(ac14_attempts)
        ],
        "mono_attempts": [
            {
                "attempt": i + 1,
                "passed": a.passed,
                "category": a.failure_classification.category if a.failure_classification else None,
                "detail": (a.failure_classification.detail[:300] if a.failure_classification else None),
                "runtime_cases": [
                    {"case_id": c.case_id, "matched": c.matched_expected, "error": c.error}
                    for c in (a.runtime_cases or [])
                ],
            }
            for i, a in enumerate(mono_attempts)
        ],
    }

    return DiagnosisArtifact(
        unit_id=unit_id,
        passed=overall_passed,
        one_line=one_line,
        root_cause=root_cause,
        suggested_fix=suggested_fix,
        category=dominant_cat,
        structured=structured,
    )


class AC14TrialRunner:
    """Run-one-diagnose runner for AC14 paired trials."""

    def __init__(
        self,
        benchmark_dir: str | Path,
        output_dir: str | Path,
        *,
        model: str = DEFAULT_LLM_MODEL,
        max_budget: float = DEFAULT_LLM_MAX_BUDGET,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> None:
        self.benchmark_dir = Path(benchmark_dir)
        self.output_dir = Path(output_dir)
        self.model = model
        self.max_budget = max_budget
        self.max_attempts = max_attempts
        self._bundle = load_benchmark_bundle(benchmark_dir)

    def run_one(self, unit_id: str) -> PairedTrialReport:
        """Run one paired trial. unit_id is used as the trial directory name."""
        trial_dir = self.output_dir / unit_id
        report = run_paired_trial(
            self.benchmark_dir,
            trial_dir,
            trial_id=int(unit_id.split("_")[-1]) if "_" in unit_id else 1,
            model=self.model,
            max_budget=self.max_budget,
            max_attempts=self.max_attempts,
        )
        return report

    def diagnose(self, unit_id: str, result: PairedTrialReport) -> DiagnosisArtifact:
        return diagnose_paired_trial(unit_id, result)


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Run one AC14 trial and print diagnosis.")
    parser.add_argument("--benchmark", required=True, help="Path to back_half benchmark dir")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--model", default=DEFAULT_LLM_MODEL, help="LLM model to use")
    parser.add_argument("--budget", type=float, default=DEFAULT_LLM_MAX_BUDGET)
    parser.add_argument("--trial", type=int, default=1, help="Trial number (for directory naming)")
    parser.add_argument("--attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    parser.add_argument(
        "--condition", choices=["paired", "ac14"], default="paired",
        help="'paired' runs both conditions; 'ac14' skips monolithic (saves credits when mono already passed)",
    )
    parser.add_argument(
        "--generator", choices=["llm", "codex"], default="llm",
        help="Code generator for AC14: 'llm' = single structured call, 'codex' = agentic loop with self-verification",
    )
    parser.add_argument(
        "--workers", type=int, default=1,
        help="Parallel workers for component generation (default 1). Use 5-10 with --generator codex.",
    )
    args = parser.parse_args()

    unit_id = f"trial_{args.trial}"
    trial_id = args.trial

    if args.condition == "ac14":
        print(f"Running {unit_id} (AC14-only, generator={args.generator}, workers={args.workers}) on {args.benchmark}...")
        report = run_ac14_only_trial(
            args.benchmark,
            Path(args.output) / unit_id,
            trial_id=trial_id,
            model=args.model,
            max_budget=args.budget,
            max_attempts=args.attempts,
            generator_kind=args.generator,
            max_workers=args.workers,
        )
        passed = report.passed
        if passed:
            print(f"[PASS] {unit_id}: AC14 PASS (attempt {report.attempts_used})")
        else:
            last = report.attempts[-1]
            cat = last.failure_classification.category if last.failure_classification else "unknown"
            detail = last.failure_classification.detail if last.failure_classification else ""
            print(f"[FAIL] {unit_id}: AC14 FAIL — {cat}: {str(detail)[:120]}")
        sys.exit(0 if passed else 1)

    runner = AC14TrialRunner(
        args.benchmark,
        args.output,
        model=args.model,
        max_budget=args.budget,
        max_attempts=args.attempts,
    )
    print(f"Running {unit_id} on {args.benchmark} with {args.model}...")
    result = runner.run_one(unit_id)
    diag = runner.diagnose(unit_id, result)
    diag.print_summary()
    diag_path = Path(args.output) / f"diagnosis_{unit_id}.json"
    diag.save(diag_path)
    print(f"\nFull diagnosis: {diag_path}")
    sys.exit(0 if diag.passed else 1)


if __name__ == "__main__":
    _cli()

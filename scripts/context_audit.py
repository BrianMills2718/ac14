"""Scan a trial output directory for codegen context gaps.

Reads {component_id}.context.json files written by emit_generated_package() and
flags any context fields that indicate missing or placeholder content — the
primary source of "LLM generated wrong code" failures.

Usage:
    python scripts/context_audit.py .ac14_out/front_half_first_full_gate_4
    python scripts/context_audit.py .ac14_out/front_half_first_full_gate_4 --trial 4 --attempt 1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _check_context(ctx: dict) -> list[str]:
    """Return a list of warning strings for any suspicious context fields."""
    warnings = []

    rules = ctx.get("structured_spec_business_rules", [])
    if len(rules) == 0:
        warnings.append("structured_spec_business_rules: EMPTY — business rules never reached codegen")

    invariants = ctx.get("local_invariants", [])
    todo_invariants = [inv for inv in invariants if "TODO" in str(inv)]
    if todo_invariants:
        warnings.append(
            f"local_invariants: {len(todo_invariants)}/{len(invariants)} are TODO placeholders"
        )

    cases = ctx.get("packet_test_cases", [])
    if len(cases) == 0:
        warnings.append("packet_test_cases: EMPTY — no test cases for grounding")

    grounding = ctx.get("rule_grounding_summaries", [])
    if len(grounding) == 0:
        warnings.append("rule_grounding_summaries: EMPTY")

    return warnings


def audit(output_dir: Path, trial: int | None = None, attempt: int | None = None) -> int:
    """Scan output_dir for context files and report gaps. Returns exit code."""
    if trial is not None and attempt is not None:
        search_root = output_dir / f"trial_{trial}" / "ac14" / f"attempt_{attempt}" / "generated"
    elif trial is not None:
        search_root = output_dir / f"trial_{trial}"
    else:
        search_root = output_dir

    context_files = sorted(search_root.rglob("*.context.json"))

    if not context_files:
        print(f"No .context.json files found under {search_root}")
        print("(Run a gate that has this observability version to generate traces)")
        return 1

    total = 0
    warned = 0
    for ctx_path in context_files:
        total += 1
        ctx = json.loads(ctx_path.read_text())
        rel = ctx_path.relative_to(output_dir)
        warnings = _check_context(ctx)

        rules_count = len(ctx.get("structured_spec_business_rules", []))
        cases_count = len(ctx.get("packet_test_cases", []))
        inv_count = len(ctx.get("local_invariants", []))
        repair_count = len(ctx.get("repair_guidance", []))

        if warnings:
            warned += 1
            print(f"\n[WARN] {rel}")
            print(f"       rules={rules_count} cases={cases_count} invariants={inv_count} repair={repair_count}")
            for w in warnings:
                print(f"  !  {w}")
        else:
            print(f"[OK]   {rel}  (rules={rules_count} cases={cases_count} invariants={inv_count} repair={repair_count})")

    print(f"\n--- {total} contexts scanned, {warned} with warnings ---")
    return 1 if warned > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_dir", type=Path, help="Gate output directory (e.g. .ac14_out/gate_4)")
    parser.add_argument("--trial", type=int, default=None, help="Restrict to trial N")
    parser.add_argument("--attempt", type=int, default=None, help="Restrict to attempt M (requires --trial)")
    args = parser.parse_args()

    sys.exit(audit(args.output_dir, trial=args.trial, attempt=args.attempt))


if __name__ == "__main__":
    main()

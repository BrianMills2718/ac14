"""Show full codegen diagnostics for one attempt.

Displays the codegen context summary for each component, runtime case mismatches,
and the full rendered prompt path so you can see exactly what the LLM received
and why the outputs were wrong.

Usage:
    python scripts/diagnose_attempt.py .ac14_out/front_half_first_full_gate_4 4 1
    python scripts/diagnose_attempt.py .ac14_out/gate_4 4 1 --show-prompt evaluate_thresholds_and_policy
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _show_context_summary(generated_dir: Path) -> None:
    context_files = sorted(generated_dir.glob("*.context.json"))
    if not context_files:
        print("  (no .context.json files found — run with observability-enabled version)")
        return
    for ctx_path in context_files:
        ctx = json.loads(ctx_path.read_text())
        cid = ctx_path.name.replace(".context.json", "")
        rules = ctx.get("structured_spec_business_rules", [])
        cases = ctx.get("packet_test_cases", [])
        invariants = ctx.get("local_invariants", [])
        repair = ctx.get("repair_guidance", [])
        todo_inv = [i for i in invariants if "TODO" in str(i)]
        flag = "  [WARN]" if (len(rules) == 0 or todo_inv) else "  [OK]  "
        print(f"{flag} {cid}")
        print(f"         rules={len(rules)}  cases={len(cases)}  invariants={len(invariants)} (TODO:{len(todo_inv)})  repair={len(repair)}")
        if len(rules) == 0:
            print("         ! structured_spec_business_rules is EMPTY")
        if todo_inv:
            print(f"         ! {len(todo_inv)} TODO invariant(s): {todo_inv[:2]}")
        prompt_path = generated_dir / f"{cid}.prompt.json"
        if prompt_path.exists():
            print(f"         prompt: {prompt_path}")
        else:
            print("         prompt: (not saved — fixture path or pre-observability run)")


def _show_runtime_mismatches(report: dict) -> None:
    cases = report.get("runtime_cases", [])
    if not cases:
        print("  (no runtime_cases in report)")
        return
    any_fail = False
    for case in cases:
        cid = case.get("case_id", "?")
        matched = case.get("matched_expected", True)
        if matched:
            print(f"  [PASS] {cid}")
        else:
            any_fail = True
            print(f"  [FAIL] {cid}")
            actual_sde = (case.get("actual_outputs") or {}).get("scaling_decision_entry", {})
            expected_sde = (case.get("expected_outputs") or {}).get("scaling_decision_entry", {})
            # Show all fields that differ
            all_keys = sorted(set(actual_sde) | set(expected_sde))
            for k in all_keys:
                av = actual_sde.get(k)
                ev = expected_sde.get(k)
                if av != ev:
                    print(f"           {k}: actual={av!r}  expected={ev!r}")
    if not any_fail:
        print("  (all cases matched — failure was not in runtime outputs)")


def _show_prompt(generated_dir: Path, component_id: str) -> None:
    prompt_path = generated_dir / f"{component_id}.prompt.json"
    if not prompt_path.exists():
        print(f"Prompt file not found: {prompt_path}")
        return
    messages = json.loads(prompt_path.read_text())
    for msg in messages:
        role = msg.get("role", "?")
        content = msg.get("content", "")
        print(f"\n--- {role.upper()} ---")
        print(content)


def diagnose(
    output_dir: Path,
    trial: int,
    attempt: int,
    show_prompt: str | None = None,
) -> None:
    attempt_dir = output_dir / f"trial_{trial}" / "ac14" / f"attempt_{attempt}"
    if not attempt_dir.exists():
        print(f"Attempt dir not found: {attempt_dir}")
        sys.exit(1)

    report_path = attempt_dir / "attempt_report.json"
    fc_path = attempt_dir / "failure_classification.json"
    generated_dir = attempt_dir / "generated"

    print(f"=== trial_{trial}/ac14/attempt_{attempt} ===")

    if report_path.exists():
        report = json.loads(report_path.read_text())
        fc = report.get("failure_classification", {})
        print(f"passed: {report.get('passed')}  category: {fc.get('category')}  cost: {report.get('llm_cost', {}).get('cost_usd', '?')}")
        if fc.get("detail"):
            print(f"detail: {fc['detail']}")
        if report.get("generation_error"):
            print(f"generation_error: {report['generation_error']}")
    elif fc_path.exists():
        fc = json.loads(fc_path.read_text())
        print(f"category: {fc.get('category')}  detail: {fc.get('detail', '')}")

    print("\n--- Codegen Context Summary ---")
    _show_context_summary(generated_dir)

    if report_path.exists():
        report = json.loads(report_path.read_text())
        print("\n--- Runtime Case Mismatches ---")
        _show_runtime_mismatches(report)

    if show_prompt:
        print(f"\n--- Full Prompt: {show_prompt} ---")
        _show_prompt(generated_dir, show_prompt)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_dir", type=Path, help="Gate output directory")
    parser.add_argument("trial", type=int, help="Trial number")
    parser.add_argument("attempt", type=int, help="Attempt number")
    parser.add_argument("--show-prompt", metavar="COMPONENT", help="Print full rendered prompt for this component")
    args = parser.parse_args()

    diagnose(args.output_dir, args.trial, args.attempt, show_prompt=args.show_prompt)


if __name__ == "__main__":
    main()

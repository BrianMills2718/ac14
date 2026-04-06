"""
Adapter: maps AC14 attempt artifacts to trace_eval stage_outputs format.

AC14 pipeline stages modelled:
  packet_compilation — context packets compiled per component (*.context.json files)
  codegen            — code generation + recomposition (attempt_report.json)
  runtime_eval       — runtime test case execution (attempt_report.json runtime_cases)

Usage:
    from ac14.trace_eval_adapter import build_stage_outputs
    stage_outputs = build_stage_outputs(attempt_dir)
    # pass to TraceEvaluator.evaluate(case, stage_outputs)

The output dict maps stage names to dicts that trace_eval programmatic
expressions and rubrics evaluate against. Consumer PipelineCase YAMLs
must use only keys present in these dicts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_stage_outputs(attempt_dir: Path | str) -> dict[str, Any]:
    """Build trace_eval stage_outputs dict from an AC14 attempt directory.

    Args:
        attempt_dir: Path to attempt_N/ directory (contains generated/ and attempt_report.json).

    Returns:
        Dict with keys: packet_compilation, codegen, runtime_eval.
        Any missing artifact results in that stage's output containing only
        metadata about what was missing — evaluations will fail appropriately.
    """
    attempt_dir = Path(attempt_dir)
    generated_dir = attempt_dir / "generated"
    report_path = attempt_dir / "attempt_report.json"

    return {
        "packet_compilation": _build_packet_compilation(generated_dir),
        "codegen": _build_codegen(report_path),
        "runtime_eval": _build_runtime_eval(report_path),
    }


def _build_packet_compilation(generated_dir: Path) -> dict[str, Any]:
    """Aggregate all *.context.json files into a single packet_compilation output.

    Programmatic expressions can query:
      total_components     — how many components have context files
      components_with_empty_rules — count with zero structured_spec_business_rules
      total_rules          — sum of rules across all components
      total_test_cases     — sum of packet_test_cases across all components
      components           — list of per-component dicts for deeper inspection
    """
    if not generated_dir.exists():
        return {
            "total_components": 0,
            "components_with_empty_rules": 0,
            "total_rules": 0,
            "total_test_cases": 0,
            "components": [],
            "_missing": "generated/ directory not found",
        }

    context_files = sorted(generated_dir.glob("*.context.json"))
    if not context_files:
        return {
            "total_components": 0,
            "components_with_empty_rules": 0,
            "total_rules": 0,
            "total_test_cases": 0,
            "components": [],
            "_missing": "no *.context.json files found in generated/",
        }

    components = []
    for ctx_path in context_files:
        ctx = json.loads(ctx_path.read_text())
        rules = ctx.get("structured_spec_business_rules") or []
        test_cases = ctx.get("packet_test_cases") or []
        invariants = ctx.get("local_invariants") or []
        todo_invariants = [i for i in invariants if "TODO" in str(i)]
        components.append({
            "id": ctx.get("component_id", ctx_path.stem.replace(".context", "")),
            "rules_count": len(rules),
            "test_cases_count": len(test_cases),
            "invariants_count": len(invariants),
            "todo_invariants_count": len(todo_invariants),
            "rules": rules,
        })

    total_components = len(components)
    components_with_empty_rules = sum(1 for c in components if c["rules_count"] == 0)
    total_rules = sum(c["rules_count"] for c in components)
    total_test_cases = sum(c["test_cases_count"] for c in components)

    return {
        "total_components": total_components,
        "components_with_empty_rules": components_with_empty_rules,
        "total_rules": total_rules,
        "total_test_cases": total_test_cases,
        "components": components,
    }


def _build_codegen(report_path: Path) -> dict[str, Any]:
    """Extract codegen stage output from attempt_report.json.

    Programmatic expressions can query:
      generation_error     — str if generation failed, None if succeeded
      recomposition_passed — bool: all components recomposed into one module
      packet_tests_passed  — bool | None: packet-level unit tests passed
      failure_category     — str | None: failure category (generation, runtime, etc.)
    """
    if not report_path.exists():
        return {
            "generation_error": "attempt_report.json not found",
            "recomposition_passed": False,
            "packet_tests_passed": None,
            "failure_category": "missing_report",
        }

    report = json.loads(report_path.read_text())
    fc = report.get("failure_classification") or {}
    generation_error = report.get("generation_error")

    return {
        "generation_error": generation_error,
        "recomposition_passed": bool(report.get("recomposition_passed")),
        "packet_tests_passed": report.get("packet_tests_passed"),
        "failure_category": fc.get("category"),
    }


def _build_runtime_eval(report_path: Path) -> dict[str, Any]:
    """Extract runtime evaluation output from attempt_report.json.

    Programmatic expressions can query:
      total_cases          — total runtime test cases
      passed_cases         — cases that matched expected outputs
      failed_cases         — cases that did not match
      pass_rate            — float in [0.0, 1.0]
      runtime_outputs_passed — bool: the report's top-level pass flag
      cases                — list of {case_id, matched, mismatches} dicts
    """
    if not report_path.exists():
        return {
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "pass_rate": 0.0,
            "runtime_outputs_passed": False,
            "cases": [],
            "_missing": "attempt_report.json not found",
        }

    report = json.loads(report_path.read_text())
    raw_cases = report.get("runtime_cases") or []

    cases = []
    passed = 0
    for raw in raw_cases:
        matched = bool(raw.get("matched_expected"))
        if matched:
            passed += 1
        actual = raw.get("actual_outputs") or {}
        expected = raw.get("expected_outputs") or {}
        mismatches: dict[str, Any] = {}
        for port in set(actual) | set(expected):
            ap = actual.get(port) or {}
            ep = expected.get(port) or {}
            if ap != ep and isinstance(ap, dict) and isinstance(ep, dict):
                for k in set(ap) | set(ep):
                    if ap.get(k) != ep.get(k):
                        mismatches[f"{port}.{k}"] = {
                            "actual": ap.get(k),
                            "expected": ep.get(k),
                        }
            elif ap != ep:
                mismatches[port] = {"actual": ap, "expected": ep}
        cases.append({
            "case_id": raw.get("case_id", "?"),
            "matched": matched,
            "mismatches": mismatches,
        })

    total = len(cases)
    failed = total - passed
    pass_rate = passed / total if total > 0 else 0.0

    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": failed,
        "pass_rate": pass_rate,
        "runtime_outputs_passed": bool(report.get("runtime_outputs_passed")),
        "cases": cases,
    }

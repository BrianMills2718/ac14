# Plan #47: Syntax-Stable Empirical Benchmark Repair

**Status:** Complete
**Type:** evaluation + implementation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 48

---

## Gap

**Current:** Plan #46 produced a fresh smoke artifact, but the verdict remained
`blocked_on_harness`.

The blocker is now narrow and concrete:

1. the AC14 condition still spends early attempts on syntax-invalid
   `exception_classifier` modules instead of reaching the benchmark harness
2. the monolithic condition is still violating benchmark-local schema fidelity
   by inventing fallback labels and by reading fields that do not exist on the
   local schema surface, especially `shipping_risk['shipment_status']`
3. both conditions therefore remain blocked for benchmark-local reasons rather
   than provider or transport reasons

**Target:** Repair the prompt and benchmark-local repair guidance so the next
smoke rerun tests the actual benchmark logic rather than repeated syntax and
schema-surface mistakes.

**Why:** The five-trial gate is still unjustified. The next honest lane is to
remove the specific blocker that the latest smoke artifact surfaced.

---

## References Reviewed

- `CLAUDE.md` - active empirical execution rules
- `docs/plans/39_monolithic_vs_ac14_comparison_execution.md` - parent empirical lane
- `docs/plans/46_empirical_smoke_gate_refresh.md` - most recent completed smoke gate
- `.ac14_out/empirical_smoke_gate_repair6/smoke_readiness_report.json` - current smoke verdict
- `.ac14_out/empirical_smoke_gate_repair6/trial_1/paired_trial_report.json` - exact paired-trial blocker snapshot
- `.ac14_out/empirical_smoke_gate_repair6/trial_1/ac14/attempt_1/generated/exception_classifier.failed.py` - first AC14 syntax failure
- `.ac14_out/empirical_smoke_gate_repair6/trial_1/ac14/attempt_2/generated/exception_classifier.failed.py` - repeated AC14 syntax failure
- `.ac14_out/empirical_smoke_gate_repair6/trial_1/monolithic/attempt_3/generated/factor_correlator.py` - monolithic schema-surface bug
- `.ac14_out/empirical_smoke_gate_repair6/trial_1/monolithic/attempt_3/generated/exception_classifier.py` - monolithic fallback-label bug
- `benchmarks/order_exception_resolution/requirements.md` - benchmark business rules
- `benchmarks/order_exception_resolution/blueprint/schemas.yaml` - benchmark-local schema surface
- `prompts/generate_component.yaml` - AC14 component prompt
- `prompts/generate_monolithic_system.yaml` - monolithic whole-system prompt
- `ac14/empirical_comparison.py` - empirical repair-guidance wiring
- `ac14/llm_codegen.py` - fail-loud syntax validation path
- `tests/test_empirical_comparison.py` - empirical comparison tests
- `tests/test_llm_codegen.py` - LLM codegen prompt tests

---

## Open Questions

### Q1: Should this plan add a hidden syntax-only repair loop inside one attempt?
**Status:** Resolved
**Why it matters:** A hidden sub-loop would change the fairness story if one
condition receives extra silent repair budget.
**Decision:** No. Keep attempt counting unchanged. Improve prompt discipline and
benchmark-local repair guidance instead.

### Q2: Should the fix become a broad AC14 runtime policy?
**Status:** Resolved
**Why it matters:** The blocker is benchmark-local. Overgeneralizing it would
risk turning one benchmark's needs into accidental global policy.
**Decision:** Keep the strongest business-rule and schema-surface guidance
benchmark-local inside the empirical comparison runner. Only general prompt
hardening should become shared AC14 behavior.

### Q3: What should happen when no benchmark rule maps to a schema-valid label?
**Status:** Resolved
**Why it matters:** The monolithic lane invented `other`, which is outside the
schema and invalidates the benchmark.
**Decision:** The repair guidance should say explicitly: do not invent fallback
labels; raise a loud error rather than synthesizing an out-of-schema category.

---

## Files Affected

- `prompts/generate_component.yaml` (modify)
- `prompts/generate_monolithic_system.yaml` (modify)
- `ac14/empirical_comparison.py` (modify)
- `tests/test_empirical_comparison.py` (modify)
- `tests/test_llm_codegen.py` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Harden the shared prompts so generated code stays direct and syntax-stable:
   no essay-style commentary in branches, no comment-only `else` branches, and
   fail loud instead of inventing schema-invalid fallback categories.
2. Add benchmark-local repair guidance for `order_exception_resolution_v1`
   covering the exact current blocker:
   - the classifier should use the direct benchmark decision rule
   - out-of-schema fallback labels are forbidden
   - `shipping_risk` does not expose `shipment_status`; downstream logic must
     use fields that actually exist on the local schema surface
3. Add focused tests proving the new guidance and prompt constraints exist.
4. Run full local verification and only then hand off to a new smoke rerun plan.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_llm_codegen.py` | `test_component_prompt_forbids_comment_only_branches_and_fallback_labels` | The shared component prompt now hardens the exact syntax/fallback pathology |
| `tests/test_empirical_comparison.py` | `test_benchmark_repair_guidance_marks_missing_schema_fields_and_no_fallback_labels` | Benchmark-local guidance names the current monolithic schema-surface blocker |
| `tests/test_empirical_comparison.py` | `test_component_repair_guidance_targets_classifier_syntax_stability` | AC14 component guidance names the current classifier blocker |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q tests/test_empirical_comparison.py tests/test_llm_codegen.py` | Fast targeted regression for this repair lane |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Keep the empirical lane type-clean |
| `python -m ruff check ac14 tests` | Keep the empirical lane lint-clean |

---

## Acceptance Criteria

- [x] The shared prompts explicitly discourage the current syntax-instability pattern.
- [x] Benchmark-local repair guidance explicitly forbids schema-invalid fallback labels.
- [x] Benchmark-local repair guidance explicitly says `shipping_risk` does not expose `shipment_status`.
- [x] AC14 component guidance for `exception_classifier` explicitly prefers a direct rule implementation and loud failure over speculative fallback logic.
- [x] Targeted and full local verification pass.
- [x] The active control docs point to Plan #48 for the next smoke rerun.

---

## Notes

This plan is intentionally narrow. It exists to clear the specific blocker from
`empirical_smoke_gate_repair6`, not to broaden the benchmark or relax the
fairness contract.

## Implementation Summary (2026-04-02)

- The shared AC14 and monolithic prompts now explicitly forbid comment-only
  branches, long ambiguity commentary inside generated code, and schema-invalid
  fallback labels.
- Benchmark-local repair guidance now names the concrete repair6 schema-surface
  blocker: `shipping_risk` does not expose `shipment_status`.
- Benchmark-local component guidance now names the direct classifier rule and
  the requirement to raise loudly instead of writing speculative fallback logic.
- Verification passed with targeted empirical/codegen tests, full `pytest`,
  `mypy`, and `ruff`.

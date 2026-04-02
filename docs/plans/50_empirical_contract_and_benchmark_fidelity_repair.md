# Plan #50: Empirical Contract And Benchmark Fidelity Repair

**Status:** In Progress
**Type:** evaluation + implementation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 51

---

## Gap

**Current:** Repair7 showed that the old classifier blocker moved, but the
smoke gate is still blocked. The next remaining blocker classes are now known:

1. AC14 still produces generic codegen-contract failures in later attempts:
   - multiline boolean conditions without parentheses
   - `build_component()` signatures or annotations that reference
     `GeneratedComponent` before the class definition exists
2. the benchmark still has specific fidelity misses:
   - ORX-101 shipping-only cases are still not always classified/routed as
     `shipping_delay` / `logistics` / `high`
   - `case_parser.normalized_notes` is drifting from the fixture contract
     because generation is changing punctuation instead of lowercasing only

**Target:** Repair the remaining generator-contract and benchmark-local fidelity
blockers after Plan #49 makes the empirical attempt artifacts fully observable.

**Why:** The next smoke rerun should test the benchmark, not repeated contract
mistakes and silent parser drift.

---

## References Reviewed

- `docs/plans/48_empirical_smoke_gate_refresh_ii.md` - latest smoke result
- `docs/plans/49_empirical_attempt_observability_and_harness_serialization.md` - prerequisite observability lane
- `.ac14_out/empirical_smoke_gate_repair7/trial_1/ac14/attempt_1/generated/factor_correlator.failed.py` - multiline boolean syntax failure
- `.ac14_out/empirical_smoke_gate_repair7/trial_1/ac14/attempt_3/generated/priority_scorer.py` - pre-class `GeneratedComponent` reference pattern
- `.ac14_out/empirical_smoke_gate_repair7/trial_1/ac14/attempt_2/attempt_report.json` - runtime-good but packet/recomposition-failing AC14 attempt
- `.ac14_out/empirical_smoke_gate_repair7/trial_1/monolithic/attempt_3/attempt_report.json` - ORX-101 shipping-only miss
- `benchmarks/order_exception_resolution/requirements.md` - benchmark business rules
- `benchmarks/order_exception_resolution/blueprint/schemas.yaml` - case-parser and routing contracts

---

## Open Questions

### Q1: Should this plan add hidden post-generation rewriting?
**Status:** Resolved
**Why it matters:** Silent code rewriting would blur the fairness contract.
**Decision:** No hidden rewrite layer. Improve prompt discipline, fail-loud validation, and benchmark-local guidance instead.

### Q2: Should parser punctuation behavior become a broad AC14 rule?
**Status:** Resolved
**Why it matters:** The `normalized_notes` exactness issue is benchmark-local unless a broader normalization policy is declared explicitly.
**Decision:** Keep the exact lowercasing-only note in benchmark-local guidance for this benchmark.

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

1. Harden prompts and benchmark-local guidance against the observed AC14 codegen-contract failures.
2. Add benchmark-local guidance for ORX-101 shipping-only handling and exact `normalized_notes` behavior.
3. Add focused tests for the new prompt/guidance constraints.
4. Run full local verification, then hand off to Plan #51.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_llm_codegen.py` | `test_component_prompt_forbids_preclass_generatedcomponent_annotations_and_unparenthesized_multiline_conditions` | Prompt hardening covers the current AC14 contract failures |
| `tests/test_empirical_comparison.py` | `test_benchmark_repair_guidance_targets_shipping_only_orx101_and_case_parser_normalization` | Benchmark-local guidance names the remaining fidelity rules |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q tests/test_empirical_comparison.py tests/test_llm_codegen.py` | Fast regression for the fidelity lane |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [ ] Prompt hardening explicitly covers the current AC14 generator-contract failure patterns.
- [ ] Benchmark-local guidance explicitly covers ORX-101 shipping-only handling.
- [ ] Benchmark-local guidance explicitly says `case_parser.normalized_notes` should lowercase only and not rewrite punctuation.
- [ ] Focused and full local verification pass.
- [ ] The active control docs point to Plan #51 for the next smoke rerun.

---

## Notes

This plan stays benchmark-local where appropriate. The goal is not to broaden
AC14 policy; it is to clear the exact blocker set revealed by repair7.

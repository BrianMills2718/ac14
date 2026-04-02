# Plan #68: Deterministic Exact-Match Semantic Review Policy

**Status:** Complete
**Type:** evaluation + code
**Priority:** Critical
**Blocked By:** 67
**Blocks:** 70

---

## Gap

**Current:** A deterministic categorical benchmark can match expected runtime
outputs exactly and still fail the smoke gate because a loose LLM semantic review
raises a false concern.

**Target:** Make semantic-review behavior configurable per benchmark so exact
output matches remain the primary gate for deterministic categorical benchmarks
while still persisting the LLM review artifact.

**Why:** The smoke gate should not stay blocked because an advisory LLM review
contradicts exact benchmark outputs.

---

## References Reviewed

- `ac14/empirical_comparison.py`
- `ac14/acceptance.py`
- `.ac14_out/full_trials_gate_2_smoke/trial_1/monolithic/attempt_1/attempt_report.json`
- `benchmarks/resource_scaling/benchmark.yaml`
- `benchmarks/order_exception_resolution/benchmark.yaml`

---

## Open Questions

### Q1: Should semantic review be removed?
**Status:** Resolved
**Decision:** No. Persist it, but make its gating role configurable.

### Q2: What policy is needed now?
**Status:** Resolved
**Decision:** Add a benchmark-level semantic-review policy with at least:
- `required`: semantic review must accept for the attempt to pass
- `advisory_on_exact_match`: semantic review is recorded but cannot override an
  exact runtime-output match

---

## Files Affected

- `ac14/empirical_comparison.py`
- `benchmarks/resource_scaling/benchmark.yaml`
- `tests/test_empirical_comparison.py`
- `docs/UNCERTAINTIES.md`

---

## Plan

### Steps

1. Add a benchmark-level semantic-review policy to `BenchmarkConfig`.
2. Make attempt pass/fail classification consume that policy truthfully.
3. Set `resource_scaling_v1` to advisory semantic review because its final
   outputs are categorical and exact-matchable.
4. Add regression tests for both policy modes.

---

## Required Tests

- `python -m pytest -q tests/test_empirical_comparison.py -k 'semantic_review or resource_scaling'`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [ ] Benchmark config exposes an explicit semantic-review policy.
- [ ] An exact-match runtime attempt with policy `advisory_on_exact_match` does
  not fail solely because the semantic review says `concern`.
- [ ] The semantic review artifact is still persisted for later analysis.

---

## Implementation Summary (2026-04-02)

AC14 now supports a benchmark-level `semantic_review_policy` with two modes:

- `required`: semantic review must accept for the attempt to pass
- `advisory_on_exact_match`: semantic review is still persisted, but it cannot
  override an exact runtime-output match

`resource_scaling_v1` now opts into `advisory_on_exact_match` because its final
outputs are fully categorical and already have exact expected outputs. This
fixes the concrete smoke blocker where `monolithic/attempt_1` matched every
runtime case exactly but still failed because the semantic review hallucinated a
false inequality for `RSC-103`.

# Plan #42: Empirical Benchmark Fidelity Repair

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 39

---

## Gap

**Current:** After Plans #40 and #41:

1. the empirical gate is explicitly `blocked_on_harness`, not blocked on infrastructure
2. AC14 no longer dies at import-time validation in the bounded smoke lane
3. both conditions now fail later at packet/runtime fidelity

The dominant remaining blockers are benchmark-specific:

1. dynamic or incorrect `generated_at` behavior
2. required-field omissions inside parsed intermediate payloads
3. business-rule mismatches against the benchmark's expected escalation logic

**Target:** AC14 should tighten benchmark-fidelity repair guidance so both
conditions are trying to satisfy the same explicit benchmark contract rather
than free-running on loosely similar semantics.

**Why:** The next honest repair lane is no longer basic observability. It is
benchmark-contract fidelity.

---

## References Reviewed

- `docs/plans/39_monolithic_vs_ac14_comparison_execution.md` - parent empirical gate
- `docs/plans/40_empirical_smoke_stabilization.md` - smoke verdict lane
- `docs/plans/41_empirical_harness_repair.md` - first harness-repair lane
- `.ac14_out/empirical_smoke_gate_repair1/smoke_readiness_report.json` - latest bounded smoke verdict
- `.ac14_out/empirical_smoke_gate_repair1/trial_1/paired_trial_report.json` - current packet/runtime mismatch details
- `benchmarks/order_exception_resolution/requirements.md` - benchmark business rules
- `benchmarks/order_exception_resolution/input/expected_runtime_outputs.json` - exact benchmark outputs

---

## Open Questions

### Q1: Should benchmark exactness be relaxed for `generated_at`?
**Status:** Resolved
**Why it matters:** Repeated failures now show wall-clock timestamp drift, but
that does not justify weakening the harness globally.
**Decision:** Keep the benchmark explicit and deterministic. Repair guidance
should steer both conditions away from wall-clock timestamps for this benchmark
rather than teaching AC14 to ignore output exactness broadly.

### Q2: Where should the next repair guidance live?
**Status:** Resolved
**Why it matters:** These are benchmark-specific expectations, not general AC14
truths.
**Decision:** Keep the next repair surface benchmark-local: prompt/guidance
changes tied to the empirical comparison lane, not new global runtime
abstractions.

### Q3: What ends this plan?
**Status:** Resolved
**Why it matters:** The lane should not sprawl into general generator research.
**Decision:** This plan ends when one bounded smoke rerun either produces a
hard-harness success or isolates a smaller, more specific benchmark-fidelity
blocker than the current mixed packet/runtime failures.

---

## Files Affected

- `ac14/empirical_comparison.py` (modify)
- `prompts/generate_monolithic_system.yaml` (modify)
- `prompts/generate_component.yaml` (modify)
- `tests/test_empirical_comparison.py` (modify)
- `docs/plans/42_empirical_benchmark_fidelity_repair.md` (create)
- `docs/plans/CLAUDE.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/TODO.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Turn the current packet/runtime failure patterns into benchmark-local repair
   guidance that both conditions can consume.
2. Tighten prompt/guidance language around deterministic benchmark outputs,
   required parsed fields, and exact business-rule fidelity.
3. Rerun one bounded smoke gate and record whether one condition now reaches a
   hard-harness success.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_empirical_comparison.py` | `test_benchmark_repair_guidance_mentions_deterministic_generated_at` | Benchmark-local guidance includes deterministic timestamp expectations |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Keep the benchmark-fidelity lane type-clean |
| `python -m ruff check ac14 tests` | Keep the benchmark-fidelity lane lint-clean |

---

## Acceptance Criteria

- [ ] Benchmark-local repair guidance names deterministic `generated_at` expectations.
- [ ] Benchmark-local repair guidance names missing required parsed fields and key business-rule mismatches.
- [ ] One bounded smoke rerun happens under the tighter benchmark-fidelity guidance.
- [ ] The next blocker is narrower than the current mixed packet/runtime bundle, or one condition achieves a hard-harness success.
- [ ] Full local verification passes and the repo stays clean.

---

## Notes

This plan is deliberately benchmark-local. The point is to repair the empirical
gate honestly before broadening the lesson into general AC14 behavior.

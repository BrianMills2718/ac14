# Plan #40: Empirical Smoke Stabilization

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 41

---

## Gap

**Current:** Plan #39 now has a real benchmark bundle, paired-trial runner,
decision artifact, and bounded live smoke findings. But no bounded smoke paired
trial has yet produced a hard-harness success, and provider instability is
still mixed into the empirical gate.

**Target:** AC14 should separate infrastructure/provider failures from
benchmark/harness failures, persist one explicit smoke-readiness artifact, and
rerun bounded smoke trials until the project has either:

1. one smoke verdict that justifies spending the five-trial budget, or
2. one stable documented blocker that explains why the five-trial budget should
   not be spent yet

**Why:** Without this stabilization lane, the active control surface still
suggests that the next action is the full five-trial experiment even though the
repo already knows that would mix thesis evidence with unresolved smoke noise.

---

## References Reviewed

- `CLAUDE.md` - active continuation and thesis-gate rules
- `docs/AC14_NEXT_24_HOURS.md` - current tactical lane and smoke blocker
- `docs/TODO.md` - current active checklist
- `docs/UNCERTAINTIES.md` - empirical smoke uncertainties
- `docs/AC14_ROADMAP.md` - empirical gate priority
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current empirical-gate framing
- `docs/plans/39_monolithic_vs_ac14_comparison_execution.md` - parent experiment lane
- `investigations/ac14/2026-04-01-empirical-comparison-smoke-findings.md` - latest smoke findings
- `ac14/empirical_comparison.py` - current runner and failure surface
- `tests/test_empirical_comparison.py` - current comparison coverage

---

## Open Questions

### Q1: How should infrastructure/provider failures be represented?
**Status:** Resolved
**Why it matters:** The five-trial gate should not confuse provider disconnects,
DNS failures, or `503` demand errors with benchmark or generation failures.
**Decision:** Persist explicit attempt-level failure classification that
distinguishes infrastructure/provider failures from generation, packet,
recomposition, runtime, and semantic-review failures.

### Q2: What is the stop/go artifact for smoke readiness?
**Status:** Resolved
**Why it matters:** The smoke decision should be reviewable and explicit, not a
chat-only judgment.
**Decision:** Persist a dedicated smoke-readiness artifact that summarizes one
bounded paired smoke run and returns only:

- `ready_for_full_trials`
- `blocked_on_infrastructure`
- `blocked_on_harness`

### Q3: When is this plan complete?
**Status:** Resolved
**Why it matters:** The lane should not turn into another indefinite sequence
of micro-fixes.
**Decision:** This plan completes when AC14 has:

1. explicit attempt-level failure classification,
2. a persisted smoke-readiness artifact,
3. one bounded smoke verdict that either unblocks Plan #39 or documents a
   stable blocker clearly enough to keep Plan #39 blocked.

---

## Files Affected

- `ac14/empirical_comparison.py` (modify)
- `tests/test_empirical_comparison.py` (modify)
- `docs/plans/39_monolithic_vs_ac14_comparison_execution.md` (modify)
- `docs/plans/40_empirical_smoke_stabilization.md` (create)
- `docs/plans/CLAUDE.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/TODO.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `README.md` (modify)
- `CLAUDE.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Extend the empirical runner so each attempt records explicit failure
   classification instead of only free-text `generation_error` and bounded
   repair guidance.
2. Persist one smoke-readiness artifact for a bounded paired smoke run that
   explains whether AC14 should proceed to the full five-trial gate.
3. Rerun one bounded smoke paired trial under the new artifact surface.
4. Update the active control docs so Plan #39 is clearly blocked or unblocked
   based on the smoke artifact rather than on chat judgment.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_empirical_comparison.py` | `test_classify_infrastructure_failure_from_provider_error` | Provider failures are classified explicitly |
| `tests/test_empirical_comparison.py` | `test_build_smoke_readiness_artifact_detects_infrastructure_blocker` | Smoke-readiness artifact returns the correct blocker verdict |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Keep the stabilization lane type-clean |
| `python -m ruff check ac14 tests` | Keep the stabilization lane lint-clean |

---

## Acceptance Criteria

- [x] Condition attempts persist explicit failure classification instead of only untyped error text.
- [x] AC14 persists one smoke-readiness artifact with `ready_for_full_trials`, `blocked_on_infrastructure`, or `blocked_on_harness`.
- [x] One bounded smoke paired trial is rerun under the new artifact surface.
- [x] The active control docs say clearly whether Plan #39 is unblocked or remains blocked.
- [x] Full local verification passes and the repo stays clean.

---

## Notes

This plan does not replace Plan #39. It is the blocker-clearing lane required
to continue Plan #39 honestly.

The current empirical gate remains valuable, but it is still only the first
back-half comparison gate over a fixed decomposition. It should not be
described as the final end-to-end proof of the full AC14 thesis.

Completion note:

- the smoke verdict is now explicit and reviewable
- the latest bounded smoke run returned `blocked_on_harness`
- no infrastructure/provider contamination was detected in that bounded rerun
- the next queued lane is benchmark-fidelity repair, not immediate five-trial execution

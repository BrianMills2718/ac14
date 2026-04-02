# Plan #43: Full Trial Gate

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 44

---

## Gap

**Current:** Plan #60 cleared the smoke gate with `ready_for_full_trials`. The project had
never yet run a full five-trial paired experiment.

**Target:** Run five paired monolithic-vs-AC14 trials on the frozen benchmark,
persist per-trial artifacts, and produce one experiment-decision artifact with
a `ac14_wins`, `monolithic_wins`, or `inconclusive` verdict.

**Why:** Until the five-trial gate completes, the main thesis claim has no
empirical measurement.

---

## Open Questions

### Q1: What if the latest smoke rerun returns `blocked_on_harness`?
**Status:** Resolved
**Decision:** Full trials require a `ready_for_full_trials` smoke verdict. Plan #60 satisfied that prerequisite.

### Q2: Should the five trials run sequentially or in parallel?
**Status:** Resolved
**Decision:** Sequentially. Each trial writes to a separate directory. No
parallelism needed for five trials.

### Q3: What if a trial hits infrastructure/provider failures mid-run?
**Status:** Resolved
**Decision:** Persist the failure classification and count the trial as failed
for that condition. Do not retry with a new trial ID. Infrastructure failures
are evidence too.

---

## Files Affected

- `.ac14_out/full_trials_gate_1/` (created via CLI)
- `docs/plans/43_full_trial_gate.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Confirm the smoke verdict from Plan #60 is `ready_for_full_trials`.
2. Run five paired trials into `.ac14_out/full_trials_gate_1/` via `python -m ac14 empirical-compare benchmarks/order_exception_resolution --output-dir .ac14_out/full_trials_gate_1 --trials 5 --max-attempts 3`.
3. Read the persisted `experiment_decision.json` artifact directly.
4. Lock the docs with the verdict.

---

## Required Tests

No new unit tests. The full trials are the acceptance criterion.

---

## Acceptance Criteria

- [x] Five paired trials completed and persisted reviewable per-trial artifacts.
- [x] One experiment-decision artifact exists with a verdict of
  `ac14_wins`, `monolithic_wins`, or `inconclusive`.
- [x] The verdict is based on the Plan #38 decision rule without modification.
- [x] The active control docs reflect the verdict.

---

## Implementation Summary (2026-04-02)

The full five-trial gate completed under `.ac14_out/full_trials_gate_1/` and
produced `experiment_decision.json` with verdict `inconclusive`.

Observed result:

- `ac14`: 2/5 successful trials
- `monolithic`: 2/5 successful trials
- both conditions averaged `1.6` repair loops
- both conditions averaged semantic score `2.0`
- `monolithic` was faster and cheaper on this benchmark

The decision artifact rationale is explicit:

- `The conditions tied on success and the secondary metrics did not separate them cleanly.`

This completes the first honest monolithic-vs-AC14 benchmark gate, but it does
not validate the stronger AC14 thesis. The next honest step is diagnosis and a
sharper next comparison contract, not another local benchmark repair loop.

---

## Notes

This plan did what it needed to do: it produced a real empirical result. The
important outcome is not that AC14 “won” or “lost”; it is that the project now
has a bounded, reviewable baseline result instead of relying only on internal
proof machinery.

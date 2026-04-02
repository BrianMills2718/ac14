# Plan #43: Full Trial Gate

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 44

---

## Gap

**Current:** Plan #60 cleared the smoke gate with `ready_for_full_trials`. The project has
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
**Decision:** Full trials require a `ready_for_full_trials` smoke verdict. Plan #60 now satisfied that prerequisite, so this plan is unblocked.

### Q2: Should the five trials run sequentially or in parallel?
**Status:** Resolved
**Decision:** Sequentially. Each trial writes to a separate directory. No
parallelism needed for five trials.

### Q3: What if a trial hits infrastructure/provider failures mid-run?
**Status:** Resolved
**Decision:** Persist the failure classification and count the trial as failed
for that condition. Do not retry with a new trial ID — infrastructure failures
are evidence too.

---

## Files Affected

- `.ac14_out/full_trials_gate_1/` (create via CLI)
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

- [ ] Five paired trials complete and persist reviewable per-trial artifacts.
- [ ] One experiment-decision artifact exists with a verdict of
  `ac14_wins`, `monolithic_wins`, or `inconclusive`.
- [ ] The verdict is based on the Plan #38 decision rule without modification.
- [ ] The active control docs reflect the verdict.

---

## Notes

This plan does not reopen the decision rule. The rule was frozen in Plan #38.
Whatever the verdict says, it says.

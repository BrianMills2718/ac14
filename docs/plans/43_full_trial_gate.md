# Plan #43: Full Trial Gate

**Status:** Planned
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 48
**Blocks:** 44

---

## Gap

**Current:** The smoke gate is still blocked behind Plan #48. The project has
never yet run a full five-trial paired experiment.

**Target:** Run five paired monolithic-vs-AC14 trials on the frozen benchmark,
persist per-trial artifacts, and produce one experiment-decision artifact with
a `ac14_wins`, `monolithic_wins`, or `inconclusive` verdict.

**Why:** Until the five-trial gate completes, the main thesis claim has no
empirical measurement.

---

## Open Questions

### Q1: What if the smoke rerun from Plan #48 still returns `blocked_on_harness`?
**Status:** Resolved
**Decision:** If smoke is still blocked after Plan #48, define the next narrower
blocker-clearing plan rather than proceeding to full trials. Full trials require
a `ready_for_full_trials` smoke verdict.

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

- `.ac14_out/full_trials/` (create via CLI)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Confirm the smoke verdict from Plan #48 is `ready_for_full_trials`.
2. Run five paired trials via `make run-full-trial-gate` (or equivalent CLI
   command) — each trial persists its own directory and paired report.
3. After all five trials complete, run `make build-experiment-decision` to
   produce the final decision artifact.
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

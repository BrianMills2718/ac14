# Plan #46: Empirical Smoke Gate Refresh

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 45
**Blocks:** 43

---

## Gap

**Current:** The empirical lane has new targeted repair work planned, but there
is no fresh smoke artifact showing whether the gate is now ready for full
trials.

**Target:** Run one bounded smoke paired trial after Plan #45, persist the new
artifact, and make one explicit decision:

1. `ready_for_full_trials` -> unblock Plan #43
2. `blocked_on_harness` -> freeze a narrower blocker-clearing plan
3. `blocked_on_infrastructure` -> keep the empirical gate paused for provider
   reasons rather than thesis reasons

**Why:** The five-trial budget should only be spent when the smoke artifact
actually earns it.

---

## References Reviewed

- `docs/plans/38_empirical_comparison_gate.md` - frozen experiment contract
- `docs/plans/39_monolithic_vs_ac14_comparison_execution.md` - parent lane
- `docs/plans/45_schema_aware_empirical_repair.md` - immediate prerequisite
- `.ac14_out/empirical_smoke_v2/smoke_readiness_report.json` - current smoke baseline
- `.ac14_out/empirical_smoke_v2/trial_1/paired_trial_report.json` - current paired baseline

---

## Open Questions

### Q1: What if the smoke verdict is still `blocked_on_harness`?
**Status:** Resolved
**Why it matters:** The project should not drift straight into full trials or vague continuation.
**Decision:** Define the next narrower blocker-clearing plan immediately and keep Plan #43 blocked.

### Q2: What if the smoke verdict is `ready_for_full_trials`?
**Status:** Resolved
**Why it matters:** The project should move to the five-trial gate without inventing another propagation lane.
**Decision:** Unblock and execute Plan #43 next.

---

## Files Affected

- `.ac14_out/empirical_smoke_*` (create via CLI)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Run one bounded smoke gate on the benchmark after Plan #45 lands.
2. Read the resulting smoke artifact and paired-trial artifact directly.
3. Update the active control docs to match the verdict.
4. Either unblock Plan #43 or define the next narrower blocker-clearing plan.

---

## Required Tests

No new unit tests. The smoke artifact itself is the acceptance surface for this plan.

---

## Acceptance Criteria

- [ ] One fresh bounded smoke artifact exists after Plan #45 lands.
- [ ] The verdict is one of `ready_for_full_trials`, `blocked_on_harness`, or `blocked_on_infrastructure`.
- [ ] The active control docs reflect that verdict exactly.
- [ ] Plan #43 is only unblocked if the smoke artifact says `ready_for_full_trials`.

---

## Notes

This plan exists to force an explicit go/no-go gate before the five-trial budget.

# Plan #48: Empirical Smoke Gate Refresh II

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 47
**Blocks:** 43

---

## Gap

**Current:** Plan #47 is the new targeted blocker-clearing lane, but there is
no fresh smoke artifact showing whether those repairs are enough to justify the
five-trial gate.

**Target:** Run one bounded smoke paired trial after Plan #47, persist the new
artifact, and make one explicit decision:

1. `ready_for_full_trials` -> unblock Plan #43
2. `blocked_on_harness` -> define the next narrower blocker-clearing plan
3. `blocked_on_infrastructure` -> keep the empirical gate paused for provider
   reasons rather than thesis reasons

**Why:** The project should not spend the five-trial budget until the repaired
lane earns it.

---

## References Reviewed

- `docs/plans/39_monolithic_vs_ac14_comparison_execution.md` - parent lane
- `docs/plans/46_empirical_smoke_gate_refresh.md` - previous smoke rerun
- `docs/plans/47_syntax_stable_empirical_benchmark_repair.md` - prerequisite repair lane
- `.ac14_out/empirical_smoke_gate_repair6/smoke_readiness_report.json` - current smoke baseline
- `.ac14_out/empirical_smoke_gate_repair6/trial_1/paired_trial_report.json` - current paired-trial blocker snapshot

---

## Open Questions

### Q1: What if AC14 clears syntax failures but packet tests still fail?
**Status:** Resolved
**Why it matters:** The next lane should be narrower than "benchmark repair" in
general.
**Decision:** Freeze the next blocker-clearing plan against the specific packet,
recomposition, or runtime mismatch shown by the new smoke artifact.

### Q2: What if monolithic clears the schema bug but still loses on benchmark logic?
**Status:** Resolved
**Why it matters:** That would still be harness evidence rather than an excuse
to spend the five-trial budget prematurely.
**Decision:** Keep Plan #43 blocked unless the smoke verdict itself says
`ready_for_full_trials`.

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

1. Run one bounded smoke gate after Plan #47 lands.
2. Read the resulting smoke artifact and paired-trial artifact directly.
3. Update the active control docs to match the verdict.
4. Either unblock Plan #43 or define the next narrower blocker-clearing plan.

---

## Required Tests

No new unit tests. The smoke artifact itself is the acceptance surface for this plan.

---

## Acceptance Criteria

- [ ] One fresh bounded smoke artifact exists after Plan #47 lands.
- [ ] The verdict is one of `ready_for_full_trials`, `blocked_on_harness`, or `blocked_on_infrastructure`.
- [ ] The active control docs reflect that verdict exactly.
- [ ] Plan #43 is only unblocked if the smoke artifact says `ready_for_full_trials`.

---

## Notes

This plan exists to force a strict go/no-go gate before the five-trial budget.

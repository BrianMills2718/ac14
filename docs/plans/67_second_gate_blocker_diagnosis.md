# Plan #67: Second-Gate Blocker Diagnosis

**Status:** Planned
**Type:** evaluation + planning
**Priority:** Critical
**Blocked By:** 65 (`blocked_on_harness` or `blocked_on_infrastructure`)
**Blocks:** 37

---

## Gap

**Current:** The second empirical smoke run may block before the five-trial
budget is spendable.

**Target:** Diagnose the blocker from the smoke artifacts, freeze the next
repair plan, and keep unrelated propagation lanes blocked.

**Why:** A blocked smoke run is useful only if it produces a bounded next move
instead of another vague repair loop.

---

## References Reviewed

- `docs/plans/65_second_gate_smoke.md`
- `ac14/empirical_comparison.py`
- `.ac14_out/full_trials_gate_2_smoke/`
- `docs/UNCERTAINTIES.md`

---

## Open Questions

### Q1: What should this plan output?
**Status:** Resolved
**Decision:** A diagnosis doc plus one explicit next numbered repair plan.

---

## Files Affected

- `docs/plans/67_second_gate_blocker_diagnosis.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/plans/NN_<repair>.md` (create)

---

## Plan

### Steps

1. Read the smoke readiness artifact and paired trial report.
2. Separate harness, provider, and benchmark-local blockers.
3. Freeze exactly one blocker-clearing next plan.
4. Keep blocked propagation lanes blocked.

---

## Required Tests

No new code tests are required unless the diagnosis lane lands code changes.
The acceptance surface is the persisted smoke artifact plus truthful plan/docs.

---

## Acceptance Criteria

- [ ] The smoke blocker is named concretely from persisted artifacts.
- [ ] One explicit next repair plan exists.
- [ ] The active docs point to that plan rather than drifting sideways.

---

## Notes

This plan only activates if the second-gate smoke run is blocked.

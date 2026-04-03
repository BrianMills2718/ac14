# Plan #89: Front-Half-First Blocker Diagnosis

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 87
**Blocks:** None

---

## Gap

**Current:** The new front-half-first smoke gate may still block before the full
trial budget is worth spending.

**Target:** If Plan #87 produces a blocked verdict, classify the blocker
directly from the persisted smoke artifacts and freeze the next bounded repair
lane.

**Why:** The project should diagnose the actual blocker instead of drifting
back into generic local tuning.

---

## Acceptance Criteria

- [ ] One blocker diagnosis artifact exists and cites the smoke artifact
      directly.
- [ ] The next bounded repair or contract lane is explicit.
- [ ] The full-trial budget remains closed unless the diagnosis says otherwise.

---

## Notes

This plan is conditional. It only activates if Plan #87 produces one of:
`blocked_on_front_half`, `blocked_on_harness`, or `blocked_on_infrastructure`.

# Plan #91: Front-Half-First Smoke Rerun

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 90
**Blocks:** 88, 92

---

## Gap

**Current:** The first front-half-first smoke gate is blocked and the repaired
contract surfaces are not yet re-tested.

**Target:** Rerun one bounded front-half-first smoke trial after Plan #90.

**Why:** The project needs a fresh persisted verdict after the repaired
structured-spec and monolithic contracts, not chat-level optimism.

---

## Acceptance Criteria

- [ ] One fresh smoke artifact exists after the Plan #90 repairs.
- [ ] The verdict is explicit and persisted.
- [ ] The next branch is explicit:
      - Plan #88 if `ready_for_full_trials`
      - Plan #92 if still `blocked_*`

---

## Notes

This plan only executes after Plan #90 is fully verified.

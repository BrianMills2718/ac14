# Plan #94: Front-Half-First Smoke Rerun II

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 88, 95

---

## Gap

**Current:** The second smoke artifact is blocked on the repaired front half,
but the next repair lane has not yet been tested.

**Target:** Rerun one bounded front-half-first smoke trial after Plan #93.

**Why:** The repo needs one fresh persisted verdict after the async-safe
front-half repair, not reasoning by analogy from smoke2.

---

## Acceptance Criteria

- [ ] One fresh smoke artifact exists after Plan #93.
- [ ] The verdict is explicit and persisted.
- [ ] The next branch is explicit:
      - Plan #88 if `ready_for_full_trials`
      - Plan #95 if still `blocked_*`

---

## Notes

This plan only executes after Plan #93 is fully verified.

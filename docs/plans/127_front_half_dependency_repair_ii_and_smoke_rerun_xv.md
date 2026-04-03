# Plan #127: Front-Half Dependency Repair II And Smoke Rerun XV

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 126
**Blocks:** None

---

## Gap

**Current:** If smoke_14 still says `blocked_on_front_half`, the repaired
repo-local dependency contract is no longer enough and one narrower front-half
repair lane must land before another rerun is spent.

**Target:** Repair the exact blocker frozen by Plan #126, verify it cleanly,
then spend one fresh bounded smoke rerun immediately.

**Why:** The active 24-hour chain must keep narrowing the actual front-half
blocker rather than looping on solved dependency issues.

---

## Acceptance Criteria

- [ ] The blocker frozen by Plan #126 is repaired on the truthful code or
      environment surface.
- [ ] Verification proves the repair before another rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

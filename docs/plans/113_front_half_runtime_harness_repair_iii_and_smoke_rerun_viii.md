# Plan #113: Front-Half Runtime-Harness Repair III And Smoke Rerun VIII

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 112
**Blocks:** None

---

## Gap

**Current:** If smoke_9 still says `blocked_on_harness`, the next dominant
runtime or harness blocker will need one more bounded repair lane rather than a
generic continuation loop.

**Target:** Repair the dominant runtime or harness blocker named by Plan #112,
then spend one fresh bounded smoke rerun immediately.

**Why:** The active 24-hour chain must stay executable without new human
direction at each blocker boundary.

---

## Acceptance Criteria

- [ ] The dominant runtime or harness blocker from Plan #112 is repaired explicitly.
- [ ] Targeted tests prove the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant blocker named by Plan #112
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. update the control docs from the fresh verdict before stopping

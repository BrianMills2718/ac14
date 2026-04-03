# Plan #117: Front-Half Runtime-Harness Repair V And Smoke Rerun X

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 116
**Blocks:** None

---

## Gap

**Current:** If smoke_11 still says `blocked_on_harness`, the next dominant
runtime or harness blocker will need one more bounded repair lane rather than a
generic continuation loop.

**Target:** Repair the dominant runtime or harness blocker named by Plan #116,
then spend one fresh bounded smoke rerun immediately.

**Why:** The active 24-hour chain must stay executable without new human
direction at each blocker boundary.

---

## Acceptance Criteria

- [ ] The dominant runtime or harness blocker from Plan #116 is repaired explicitly.
- [ ] Targeted tests prove the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant blocker named by Plan #116
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. if the rerun still returns `blocked_on_harness`, freeze the next blocker boundary
   immediately rather than broadening scope

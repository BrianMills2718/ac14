# Plan #111: Front-Half Runtime-Harness Repair II And Smoke Rerun VII

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 110
**Blocks:** None

---

## Gap

**Current:** If smoke_8 still says `blocked_on_harness`, the next dominant
runtime or harness blocker will need one bounded repair lane rather than
another generic diagnosis cycle.

**Target:** Repair the dominant runtime or harness blocker named by Plan #110,
then spend one fresh bounded smoke rerun immediately.

**Why:** The current 24-hour chain must stay executable without depending on
chat memory or a new human decision at each smoke boundary.

---

## Acceptance Criteria

- [ ] The dominant runtime or harness blocker from Plan #110 is repaired explicitly.
- [ ] Targeted tests prove the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant blocker named by Plan #110
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. update the control docs from the fresh verdict before stopping

# Plan #105: Front-Half Runtime-Harness Repair And Smoke Rerun IV

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 98
**Blocks:** None

---

## Gap

**Current:** If Plan #96 reaches front-half approval but still fails the runtime
hard harness, AC14 will need one bounded repair-and-rerun lane instead of a
stop at blocker diagnosis.

**Target:** Repair the dominant runtime or harness blocker from Plan #98 and
then spend one fresh bounded smoke rerun immediately.

**Why:** The active empirical chain should keep moving from blocker boundary to
one measured retry without requiring new chat direction.

---

## Acceptance Criteria

- [ ] The dominant runtime or harness blocker from Plan #98 is repaired explicitly.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant runtime or harness blocker named by Plan #98
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. update the control docs from the fresh verdict before stopping


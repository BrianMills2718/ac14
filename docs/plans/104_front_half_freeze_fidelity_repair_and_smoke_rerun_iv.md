# Plan #104: Front-Half Freeze-Fidelity Repair And Smoke Rerun IV

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 97
**Blocks:** None

---

## Gap

**Current:** If Plan #96 still blocks on the front half, AC14 will have a new
artifact identifying a concrete freeze-fidelity failure surface, but the next
24-hour chain would still be incomplete without one explicit repair-and-rerun
plan.

**Target:** Repair the dominant front-half freeze-fidelity blocker from Plan
#97 and then spend one fresh bounded smoke rerun immediately.

**Why:** The active lane should not stop at blocker naming; it should convert
the boundary into one bounded empirical retry inside the same 24-hour chain.

---

## Acceptance Criteria

- [ ] The dominant front-half blocker from Plan #97 is repaired explicitly.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next boundary or full-trial branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant front-half blocker named by Plan #97
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. update the control docs from the fresh verdict before stopping


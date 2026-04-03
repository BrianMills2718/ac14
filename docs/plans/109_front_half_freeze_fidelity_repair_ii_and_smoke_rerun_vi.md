# Plan #109: Front-Half Freeze-Fidelity Repair II And Smoke Rerun VI

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 108
**Blocks:** None

---

## Gap

**Current:** If smoke_7 still blocks on the front half, AC14 needs one explicit
second repair lane rather than drifting back into generic front-half retries.

**Target:** Repair the dominant remaining freeze-fidelity blocker from Plan #108
and immediately spend one fresh bounded smoke rerun.

**Why:** The active front-half-first branch should remain empirical and bounded:
repair one blocker class, rerun once, branch again from the artifact.

---

## Acceptance Criteria

- [ ] The dominant blocker from Plan #108 is repaired explicitly.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from that artifact.

---

## Execution Contract

1. repair only the dominant blocker frozen by Plan #108
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. update the control docs from the new verdict before stopping

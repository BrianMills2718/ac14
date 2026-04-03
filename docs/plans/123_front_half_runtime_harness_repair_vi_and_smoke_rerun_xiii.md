# Plan #123: Front-Half Runtime-Harness Repair VI And Smoke Rerun XIII

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 122
**Blocks:** None

---

## Gap

**Current:** If smoke_13 still says `blocked_on_harness`, at least one narrower
harness defect remains after the pre-runtime contract repair lane.

**Target:** Repair that remaining harness defect, verify it, and spend one fresh
bounded smoke rerun immediately.

**Why:** The smoke budget should only be spent on real end-to-end evaluation, not
repeatable avoidable harness failures.

---

## Acceptance Criteria

- [ ] The remaining harness blocker from Plan #122 is repaired explicitly.
- [ ] Targeted tests prove the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

1. repair only the remaining harness blocker named by Plan #122
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately
4. branch from the persisted rerun verdict without pause

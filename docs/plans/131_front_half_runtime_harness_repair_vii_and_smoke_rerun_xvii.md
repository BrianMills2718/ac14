# Plan #131: Front-Half Runtime-Harness Repair VII And Smoke Rerun XVII

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 130
**Blocks:** None

---

## Gap

**Current:** If smoke_15 still says `blocked_on_harness`, then the leaf-output
preference repair in Plan #123 was not sufficient and one narrower harness
repair lane remains.

**Target:** Repair the exact blocker frozen by Plan #130, verify it, and spend
one fresh bounded smoke rerun immediately.

**Why:** The active 24-hour chain must keep narrowing the real harness blocker
instead of drifting back into resolved dependency or broad runtime-output work.

---

## Acceptance Criteria

- [ ] The blocker frozen by Plan #130 is repaired explicitly.
- [ ] Targeted tests prove the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

1. repair only the remaining harness blocker named by Plan #130
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately
4. branch from the persisted rerun verdict without pause

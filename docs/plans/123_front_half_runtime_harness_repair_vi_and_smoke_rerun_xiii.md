# Plan #123: Front-Half Runtime-Harness Repair VI And Smoke Rerun XIII

**Status:** In Progress
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 122
**Blocks:** None

---

## Gap

**Current:** Smoke_14 still says `blocked_on_harness` after the structured
dependency repair. Attempts 1 and 3 fail before evaluation because
runtime-contract inference sees two non-source candidates for
`scaling_decision_entry`: an intermediate compliance component output and a
downstream recorder output that is the true leaf system output.

**Target:** Repair that remaining harness defect by preferring the unique
unbound leaf output over the intermediate pass-through output, verify it, and
spend one fresh bounded smoke rerun immediately.

**Why:** The smoke budget should only be spent on real end-to-end evaluation, not
repeatable avoidable harness failures.

---

## Acceptance Criteria

- [ ] Runtime-contract inference selects the recorder leaf output for
      `scaling_decision_entry` when the only competing candidate is an
      intermediate upstream emitter of the same schema.
- [ ] Targeted tests prove the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair at
      `.ac14_out/front_half_first_smoke_15/`.
- [ ] The next branch is explicit from the new artifact as Plan #88 + #100,
      Plan #120 + #121, Plan #130 + #131, Plan #126 + #127, or
      Plan #128 + #129.

---

## Execution Contract

1. repair only the remaining harness blocker named by Plan #122
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately
4. branch from the persisted rerun verdict without pause

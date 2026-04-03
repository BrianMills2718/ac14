# Plan #110: Front-Half Runtime-Harness Boundary II

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 105
**Blocks:** 111

---

## Gap

**Current:** If smoke_8 still says `blocked_on_harness`, AC14 will have moved
past the root-port inference bug but still failed the runtime hard harness.

**Target:** Freeze the next runtime/harness blocker boundary from the fresh
smoke_8 artifact instead of letting the chain fall back into vague repair work.

**Why:** The front-half-first chain only stays honest if each bounded smoke
verdict unlocks one explicit next blocker class.

---

## Acceptance Criteria

- [ ] One explicit blocker-boundary artifact exists if smoke_8 still returns
      `blocked_on_harness`.
- [ ] The dominant remaining blocker class is named precisely enough for one
      bounded repair lane.
- [ ] The next move is explicit as Plan #111, not an open-ended repair loop.

---

## Continuation Contract

If this boundary plan activates, the next required move is
[Plan #111: Front-Half Runtime-Harness Repair II And Smoke Rerun VII](111_front_half_runtime_harness_repair_ii_and_smoke_rerun_vii.md).

# Plan #114: Front-Half Runtime-Harness Boundary IV

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 113
**Blocks:** 115

---

## Gap

**Current:** If smoke_10 still says `blocked_on_harness`, the structured-spec
benchmark fidelity repair will have landed but the front-half-first runtime
contract will still be failing on a narrower blocker.

**Target:** Freeze the next runtime or harness blocker from the fresh smoke_10
artifact instead of letting the chain dissolve into generic continuation work.

**Why:** The front-half-first lane only stays empirically honest if each smoke
artifact names one explicit blocker class and one bounded next repair.

---

## Acceptance Criteria

- [ ] One explicit blocker-boundary artifact exists if smoke_10 still returns
      `blocked_on_harness`.
- [ ] The dominant remaining blocker class is named precisely enough for one
      bounded repair lane.
- [ ] The next move is explicit as Plan #115.

---

## Continuation Contract

If this boundary plan activates, the next required move is
[Plan #115: Front-Half Runtime-Harness Repair IV And Smoke Rerun IX](115_front_half_runtime_harness_repair_iv_and_smoke_rerun_ix.md).

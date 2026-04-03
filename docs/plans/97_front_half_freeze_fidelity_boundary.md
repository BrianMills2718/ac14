# Plan #97: Front-Half Freeze Fidelity Boundary

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 96
**Blocks:** None

---

## Gap

**Current:** After the explicit-model rerun, the smoke gate may still block
because the structured-spec-derived draft bundle is not freeze-correct enough to
earn approval.

**Target:** If Plan #96 returns `blocked_on_front_half`, freeze the next blocker
boundary around front-half freeze fidelity instead of reopening generic
micro-repairs.

**Why:** The front-half-first empirical chain should stay falsifiable and
bounded to the dominant blocker.

---

## Acceptance Criteria

- [ ] One explicit blocker-boundary artifact exists if the rerun blocks on
      front-half fidelity.
- [ ] The next move is explicit and bounded to the dominant front-half blocker
      class.
- [ ] The full-trial budget remains closed unless the rerun says otherwise.

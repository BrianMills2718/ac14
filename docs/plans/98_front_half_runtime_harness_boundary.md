# Plan #98: Front-Half Runtime-Harness Boundary

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 96
**Blocks:** None

---

## Gap

**Current:** After the explicit-model rerun, AC14 may earn front-half approval
yet still fail to produce an end-to-end runtime hard-harness success.

**Target:** If Plan #96 returns `blocked_on_harness`, freeze the next blocker
boundary around runtime/harness fidelity.

**Why:** The front-half-first chain should make the remaining blocker class
explicit instead of collapsing back into mixed repair work.

---

## Acceptance Criteria

- [ ] One explicit blocker-boundary artifact exists if the rerun blocks on
      runtime/harness fidelity.
- [ ] The next move is explicit and bounded to the dominant runtime blocker
      class.
- [ ] The full-trial budget remains closed unless the rerun says otherwise.

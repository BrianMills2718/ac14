# Plan #107: Front-Half External Provider Boundary II

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 106
**Blocks:** None

---

## Gap

**Current:** If Plan #106 reruns the smoke gate after explicit model propagation
and the result is still `blocked_on_infrastructure`, then the hidden-default
explanation is no longer sufficient.

**Target:** Freeze the next infrastructure boundary from the repaired rerun
without pretending it is a front-half or runtime thesis signal.

**Why:** The repo should not spend more benchmark or repair budget until it can
distinguish external provider availability from AC14-specific plumbing faults.

---

## Acceptance Criteria

- [ ] One explicit infrastructure boundary artifact exists for the repaired rerun.
- [ ] The next move is explicit and bounded to truly external provider
      availability or routing policy.
- [ ] The full-trial budget remains closed unless the rerun says otherwise.

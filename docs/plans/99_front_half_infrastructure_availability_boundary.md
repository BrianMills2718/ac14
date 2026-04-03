# Plan #99: Front-Half Infrastructure Availability Boundary

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 96
**Blocks:** None

---

## Gap

**Current:** Even with an explicit non-default model, the rerun may still block
on provider availability or quota.

**Target:** If Plan #96 returns `blocked_on_infrastructure`, freeze the next
boundary around model/provider availability instead of claiming the rerun
measured front-half fidelity.

**Why:** External availability limits must not be misreported as thesis evidence.

---

## Acceptance Criteria

- [ ] One explicit infrastructure-availability boundary artifact exists if the
      rerun still blocks on provider noise.
- [ ] The next move is explicit and bounded to model/provider availability.
- [ ] The full-trial budget remains closed unless the rerun says otherwise.

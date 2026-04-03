# Plan #128: Front-Half External Provider Boundary III

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 125
**Blocks:** 129

---

## Gap

**Current:** If smoke_14 returns `blocked_on_infrastructure`, the repo-local
structured dependency repair is not the dominant blocker and the rerun has
re-entered provider or routing failure territory.

**Target:** Freeze the exact infrastructure blocker from the repaired rerun
without pretending it is a front-half or runtime thesis signal.

**Why:** The repo should not spend more benchmark budget until the provider
surface is separated cleanly from AC14-specific behavior.

---

## Acceptance Criteria

- [ ] One explicit infrastructure boundary artifact exists for the repaired rerun.
- [ ] The next move is explicit and bounded to provider or routing recovery.
- [ ] The full-trial budget remains closed unless the rerun says otherwise.

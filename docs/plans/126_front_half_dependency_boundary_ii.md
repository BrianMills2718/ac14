# Plan #126: Front-Half Dependency Boundary II

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 125
**Blocks:** 127

---

## Gap

**Current:** If smoke_14 still says `blocked_on_front_half` after the explicit
structured-dependency repair, then the dependency explanation from smoke_13 is
no longer sufficient.

**Target:** Freeze the next narrower front-half blocker from the repaired rerun
without collapsing it back into generic dependency drift.

**Why:** The chain should spend the next repair lane on the actual persisted
front-half blocker, not on repeated environment guessing.

---

## Acceptance Criteria

- [ ] One explicit front-half blocker artifact exists for the repaired rerun.
- [ ] The dominant next blocker is narrowed to one truthful surface.
- [ ] The next move is explicit as Plan #127.

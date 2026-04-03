# Plan #92: Front-Half-First Second Blocker Boundary

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 91
**Blocks:** None

---

## Gap

**Current:** A repaired smoke rerun may still block even after the first
contract-and-observability repair lane.

**Target:** If Plan #91 still returns `blocked_*`, freeze a second blocker
boundary instead of reopening unbounded micro-repairs.

**Why:** The front-half-first empirical chain should remain explicit and
falsifiable.

---

## Acceptance Criteria

- [ ] One explicit blocker-boundary artifact exists if the rerun still blocks.
- [ ] The next move is explicit and claim-bounded.
- [ ] The full-trial budget remains closed unless the rerun says otherwise.

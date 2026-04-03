# Plan #108: Front-Half Freeze Fidelity Boundary II

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 104
**Blocks:** 109

---

## Gap

**Current:** If smoke_7 still returns `blocked_on_front_half` after Plan #104,
the original freeze-fidelity blocker class has narrowed again and the next move
must be frozen from the new artifact instead of guessed in chat.

**Target:** Persist one second freeze-fidelity boundary from smoke_7 and keep
the next repair lane bounded to the dominant remaining blocker.

**Why:** The front-half-first chain should keep converting fresh artifacts into
one explicit next repair, not into an indefinite draft-quality tweak loop.

---

## Acceptance Criteria

- [ ] One explicit blocker-boundary artifact exists if smoke_7 still says
      `blocked_on_front_half`.
- [ ] The dominant remaining blocker class is separated from secondary noise.
- [ ] The next required move is frozen as Plan #109.

---

## Continuation Contract

If this boundary plan activates, the next required move is
[Plan #109: Front-Half Freeze-Fidelity Repair II And Smoke Rerun VI](109_front_half_freeze_fidelity_repair_ii_and_smoke_rerun_vi.md).

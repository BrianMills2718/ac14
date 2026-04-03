# Plan #124: Front-Half Structured Dependency Boundary

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 119
**Blocks:** 125

---

## Gap

**Current:** Smoke_13 unexpectedly returned `blocked_on_front_half`, but the
artifact does not show a new front-half logic failure. All six bounded attempts
(AC14 and monolithic) failed immediately with `No module named 'instructor'`
when the smoke gate ran in the repo-local `.venv`.

**Target:** Freeze the exact blocker as a repo-local structured dependency
contract gap:

1. AC14 declares plain `llm_client`, but the front-half-first structured
   generation path actually requires the `llm_client[structured]` extra
2. the repo-local smoke lane must not depend on hidden system-site packages
3. the next rerun branch matrix must account for this dependency lane before
   another bounded smoke artifact is spent

**Why:** The next rerun should measure AC14's front-half/runtime behavior again,
not waste budget on a missing local package contract.

---

## Acceptance Criteria

- [x] The smoke_13 dependency blocker is frozen from persisted artifacts.
- [x] The dominant next lane is explicit as repo-local structured dependency
      repair, not algorithmic front-half tuning.
- [x] The next move is explicit as Plan #125.

---

## Continuation Contract

The next required move is
[Plan #125: Front-Half Structured-Dependency Repair And Smoke Rerun XIV](125_front_half_structured_dependency_repair_and_smoke_rerun_xiv.md).

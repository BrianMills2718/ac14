# Plan #121: Front-Half Runtime-Output Repair II And Smoke Rerun XII

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 120
**Blocks:** None

---

## Gap

**Current:** If smoke_13 says `blocked_on_runtime_outputs`, pre-runtime contract
quality is no longer the dominant issue and the benchmark is failing on actual
runtime-output mismatches.

**Target:** Repair one bounded runtime-output blocker from Plan #120, verify it,
and spend one fresh smoke rerun immediately.

**Why:** Once the smoke gate reaches real runtime evaluation consistently, the
next highest-value work is narrowing benchmark-output mismatch, not reopening
contract plumbing.

---

## Acceptance Criteria

- [ ] The dominant runtime-output blocker from Plan #120 is repaired explicitly.
- [ ] Targeted tests prove the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

1. repair only the dominant runtime-output blocker named by Plan #120
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately
4. if the rerun still says `blocked_on_runtime_outputs`, freeze the next
   narrower runtime-output boundary immediately rather than broadening scope

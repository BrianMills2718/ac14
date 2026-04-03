# Plan #92: Front-Half-First Second Blocker Boundary

**Status:** Complete
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

- [x] One explicit blocker-boundary artifact exists if the rerun still blocks.
- [x] The next move is explicit and claim-bounded.
- [x] The full-trial budget remains closed unless the rerun says otherwise.

---

## Implementation Summary

Plan #91 produced a fresh smoke artifact at:

- `.ac14_out/front_half_first_smoke_2/smoke_readiness_report.json`

The verdict is still:

- `blocked_on_front_half`

The blocker chain is now more precise than smoke1:

- monolithic no longer fails on the old raw-record contract mistake; it now
  reaches real runtime-output mismatches
- AC14 no longer fails first on invalid structured-spec bindings; it now
  materializes a draft plan, draft bundle, and freeze remediation artifacts
- every AC14 attempt still fails before returning a front-half artifact because
  the retry-enabled structured-spec front-half path hits
  `asyncio.run() cannot be called from a running event loop`
- the draft bundle also remains structurally blocked at freeze on truthful
  schema/fidelity findings, so the next repair must first eliminate the async
  wrapper crash before the remaining freeze blocker can be judged honestly

The next explicit chain is:

1. [Plan #93: Async-Safe Freeze Review Repair](93_async_safe_freeze_review_repair.md)
2. [Plan #94: Front-Half-First Smoke Rerun II](94_front_half_first_smoke_rerun_ii.md)
3. [Plan #88: Front-Half-First Full Trial Gate](88_front_half_first_full_trial_gate.md) only if the rerun says `ready_for_full_trials`
4. [Plan #95: Front-Half Infrastructure Boundary](95_front_half_infrastructure_boundary.md) otherwise

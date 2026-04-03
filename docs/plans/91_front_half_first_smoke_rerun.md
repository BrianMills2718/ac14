# Plan #91: Front-Half-First Smoke Rerun

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 90
**Blocks:** 88, 92

---

## Gap

**Current:** The first front-half-first smoke gate is blocked and the repaired
contract surfaces are not yet re-tested.

**Target:** Rerun one bounded front-half-first smoke trial after Plan #90.

**Why:** The project needs a fresh persisted verdict after the repaired
structured-spec and monolithic contracts, not chat-level optimism.

---

## Acceptance Criteria

- [x] One fresh smoke artifact exists after the Plan #90 repairs.
- [x] The verdict is explicit and persisted.
- [x] The next branch is explicit:
      - Plan #88 if `ready_for_full_trials`
      - Plan #92 if still `blocked_*`

---

## Notes

This plan only executes after Plan #90 is fully verified.

## Implementation Summary

Plan #91 produced a fresh smoke artifact at:

- `.ac14_out/front_half_first_smoke_2/smoke_readiness_report.json`

The verdict is:

- `blocked_on_front_half`

The rerun moved the blocker chain:

- monolithic no longer fails on the old raw-record contract mistake
- AC14 no longer fails first on invalid structured-spec bindings
- AC14 now reaches draft planning, draft authoring, and freeze-remediation
  artifacts before failing on nested `asyncio.run()` reentry in the retry path

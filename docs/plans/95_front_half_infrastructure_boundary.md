# Plan #95: Front-Half Infrastructure Boundary

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 94
**Blocks:** 96

---

## Gap

**Current:** Plan #94 reran the front-half-first smoke gate after the async-safe
repair, but every bounded attempt failed on Gemini `429 RESOURCE_EXHAUSTED`
before the front half could be empirically judged.

**Target:** Freeze the blocker boundary around infrastructure availability
instead of pretending the rerun measured front-half freeze fidelity.

**Why:** The empirical chain must distinguish provider quota noise from thesis
evidence.

---

## Acceptance Criteria

- [x] One explicit blocker-boundary artifact exists.
- [x] The next move is explicit and bounded to the dominant blocker class.
- [x] The full-trial budget remains closed unless a later rerun says otherwise.

---

## Implementation Summary

The blocker-boundary artifact is:

- `.ac14_out/front_half_first_smoke_4/smoke_readiness_report.json`

It shows:

- verdict `blocked_on_infrastructure`
- `infrastructure_failure_detected = true`
- all six bounded attempts classified `infrastructure_provider`
- no AC14 front-half artifact was empirically judged because quota exhaustion
  stopped both conditions before real execution

Decision:

- the dominant blocker is `infrastructure_quota_exhausted`, not freeze fidelity
- Plan #93's async-safe fix remains untested empirically
- the next honest move is Plan #96: rerun the smoke gate with an explicit
  non-Gemini model instead of waiting on the Makefile default

---

## Notes

The Makefile default `MODEL` remains `gemini/gemini-2.5-flash-lite`, so the
front-half-first smoke target must override `MODEL` explicitly until the quota
block is no longer active.

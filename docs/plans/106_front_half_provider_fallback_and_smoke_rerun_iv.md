# Plan #106: Front-Half Model Propagation Repair And Smoke Rerun IV

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 99
**Blocks:** 97

---

## Gap

**Current:** Plan #99 showed that smoke_5 was blocked by hidden Gemini-default
subcalls inside the AC14 front-half path, not by the top-level smoke runner.

**Target:** Propagate the explicit smoke model and budget through the AC14
front-half subcalls that still defaulted to Gemini, then rerun one bounded
smoke trial.

**Why:** Until the front-half subcalls honor the operator-selected model, the
smoke artifact still mixes thesis evidence with hidden infrastructure defaults.

---

## Acceptance Criteria

- [x] Explicit model propagation is implemented and verified across the active
      front-half path.
- [x] One fresh smoke artifact exists after the propagation repair.
- [x] The next branch is explicit from the new artifact.

---

## Implementation Summary (Complete — 2026-04-02)

Repair target completed:

- propagate explicit model/budget through:
  - structured-spec front-half acceptance
  - discovery front-half acceptance
  - freeze semantic review
  - refreshed freeze inside retry paths

Verified repair state before rerun:

- committed in `24627ff` (`[Plan #106] Propagate freeze review model overrides`)
- targeted verification passed before the rerun

Smoke_6 result:

- artifact: `.ac14_out/front_half_first_smoke_6/smoke_readiness_report.json`
- verdict: `blocked_on_front_half`
- infrastructure contamination: `false`
- monolithic failure categories: `runtime_outputs`
- AC14 failure categories: `front_half`

Branch unlocked from smoke_6:

- Plan #97 froze the clean front-half blocker boundary
- Plan #104 is the required repair-and-rerun lane

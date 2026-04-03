# Plan #110: Front-Half Runtime-Harness Boundary II

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 105
**Blocks:** 111

---

## Gap

**Current:** If smoke_8 still says `blocked_on_harness`, AC14 will have moved
past the root-port inference bug but still failed the runtime hard harness.

**Target:** Freeze the next runtime/harness blocker boundary from the fresh
smoke_8 artifact instead of letting the chain fall back into vague repair work.

**Why:** The front-half-first chain only stays honest if each bounded smoke
verdict unlocks one explicit next blocker class.

---

## Acceptance Criteria

- [x] One explicit blocker-boundary artifact exists from the smoke_8
      `blocked_on_harness` verdict.
- [x] The dominant remaining blocker class is named precisely enough for one
      bounded repair lane.
- [x] The next move is explicit as Plan #111, not an open-ended repair loop.

---

## Continuation Contract

If this boundary plan activates, the next required move is
[Plan #111: Front-Half Runtime-Harness Repair II And Smoke Rerun VII](111_front_half_runtime_harness_repair_ii_and_smoke_rerun_vii.md).

---

## References Reviewed

- `.ac14_out/front_half_first_smoke_8/smoke_readiness_report.json`
- `.ac14_out/front_half_first_smoke_8/trial_1/paired_trial_report.json`
- `.ac14_out/front_half_first_smoke_8/trial_1/ac14/attempt_1/attempt_report.json`
- `.ac14_out/front_half_first_smoke_8/trial_1/ac14/attempt_1/front_half/draft_bundle/components.yaml`
- `ac14/front_half_first_empirical.py`

## Open Questions

- None for the boundary itself. The blocker is concrete enough for a bounded
  repair in Plan #111.

## Files Affected

- `docs/AC14_NEXT_24_HOURS.md`
- `docs/TODO.md`
- `docs/plans/CLAUDE.md`
- `docs/plans/110_front_half_runtime_harness_boundary_ii.md`
- `docs/plans/111_front_half_runtime_harness_repair_ii_and_smoke_rerun_vii.md`

## Required Tests

- No code verification required. This boundary is grounded in the persisted
  smoke_8 artifact.

## Boundary Summary (Complete — 2026-04-02)

Smoke_8 result:

- artifact: `.ac14_out/front_half_first_smoke_8/smoke_readiness_report.json`
- verdict: `blocked_on_harness`
- infrastructure contamination: `false`
- AC14 front-half success: `true`

Dominant blocker from the saved AC14 attempts:

- the source-input inference bug is fixed
- all three AC14 attempts now fail on final-output inference:
  `unable to infer one unique final component from structured spec outputs ['scaling_decision_entry', 'scaling_decision_store']: []`
- the generated draft bundle truthfully splits those final outputs across two
  components, so the runner's single-final-component assumption is now the
  blocker

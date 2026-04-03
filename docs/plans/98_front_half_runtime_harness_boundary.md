# Plan #98: Front-Half Runtime-Harness Boundary

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 96
**Blocks:** 105

---

## Gap

**Current:** Smoke_7 moved the active lane out of front-half approval failure.
AC14 now earns approved structured-spec front-half artifacts, but all three
bounded AC14 attempts still fail before packet/recomposition/runtime because the
front-half-first runner cannot infer one unique runtime source contract from the
generated draft bundle.

**Target:** Freeze the next blocker boundary around runtime/harness fidelity
from the persisted smoke_7 artifact, naming the dominant blocker precisely
enough that Plan #105 can repair it without another generic diagnosis loop.

**Why:** The front-half-first chain should make the remaining blocker class
explicit instead of collapsing back into mixed repair work.

---

## Acceptance Criteria

- [x] One explicit blocker-boundary artifact exists from the smoke_7
      `blocked_on_harness` verdict.
- [x] The next move is explicit and bounded to the dominant runtime blocker
      class.
- [x] The full-trial budget remains closed unless a later rerun says otherwise.

---

## Continuation Contract

If this boundary plan activates, the next required move is
[Plan #105: Front-Half Runtime-Harness Repair And Smoke Rerun IV](105_front_half_runtime_harness_repair_and_smoke_rerun_iv.md).

---

## References Reviewed

- `.ac14_out/front_half_first_smoke_7/smoke_readiness_report.json`
- `.ac14_out/front_half_first_smoke_7/trial_1/paired_trial_report.json`
- `.ac14_out/front_half_first_smoke_7/trial_1/ac14/attempt_1/attempt_report.json`
- `.ac14_out/front_half_first_smoke_7/trial_1/ac14/attempt_1/front_half/draft_bundle/components.yaml`
- `.ac14_out/front_half_first_smoke_7/trial_1/ac14/attempt_1/front_half/draft_bundle/schemas.yaml`
- `ac14/front_half_first_empirical.py`

## Open Questions

- None for the boundary itself. The dominant blocker is concrete enough to
  repair directly in Plan #105.

## Files Affected

- `docs/AC14_NEXT_24_HOURS.md`
- `docs/TODO.md`
- `docs/plans/CLAUDE.md`
- `docs/plans/98_front_half_runtime_harness_boundary.md`
- `docs/plans/105_front_half_runtime_harness_repair_and_smoke_rerun_iv.md`

## Required Tests

- No code verification required. This boundary is grounded in the persisted
  smoke_7 artifact.

## Boundary Summary (Complete — 2026-04-02)

Smoke_7 result:

- artifact: `.ac14_out/front_half_first_smoke_7/smoke_readiness_report.json`
- verdict: `blocked_on_harness`
- infrastructure contamination: `false`
- AC14 front-half success: `true`
- runtime hard-harness success: `false`

Dominant blocker from the saved AC14 attempts:

- all three AC14 attempts failed with the same generation-time error:
  `unable to infer one unique source component from structured spec input 'metrics_snapshot': []`
- the generated front-half bundle uses one unbound root input port named
  `metrics_snapshot_in` on `MetricsNormalizer`
- the runtime-contract inference path currently assumes the structured-spec
  input name must exactly match the generated component input-port name

Required next lane:

- Plan #105 must repair this runtime-contract inference mismatch, improve
  attempt-level observability where useful, verify with targeted tests, and
  spend one fresh bounded smoke rerun immediately.

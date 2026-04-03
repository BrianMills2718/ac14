# Plan #116: Front-Half Runtime-Harness Boundary V

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 115
**Blocks:** 117

---

## Gap

**Current:** Smoke_11 still says `blocked_on_harness`, but the final-output
binding repair landed and front-half approval is now stable. The smoke label is
too coarse for the new state.

**Target:** Freeze the exact next blocker from the fresh smoke_11 artifact:
both conditions now fail in `runtime_outputs`, so the old harness bug is no
longer the dominant blocker. The next repair should sharpen the smoke verdict
and observability rather than pretend the old harness defect still exists.

**Why:** The front-half-first lane only stays empirically honest if each smoke
artifact names one explicit blocker class and one bounded next repair.

---

## Acceptance Criteria

- [x] One explicit blocker-boundary artifact exists because smoke_11 returned
      `blocked_on_harness`.
- [x] The dominant remaining blocker class is named precisely enough for one
      bounded repair lane.
- [x] The next move is explicit as Plan #117.

---

## Continuation Contract

If this boundary plan activates, the next required move is
[Plan #117: Front-Half Runtime-Harness Repair V And Smoke Rerun X](117_front_half_runtime_harness_repair_v_and_smoke_rerun_x.md).

---

## Frozen Smoke_11 Boundary

- Canonical artifact:
  - `.ac14_out/front_half_first_smoke_11/smoke_readiness_report.json`
- Verdict: `blocked_on_harness`
- AC14 front half: `true`
- Infrastructure failure detected: `false`
- AC14 failure categories: `runtime_outputs`, `runtime_outputs`, `runtime_outputs`
- Monolithic failure categories: `runtime_outputs`, `runtime_outputs`, `runtime_outputs`
- Interpretation:
  - the old final-output binding blocker is cleared
  - the smoke gate is now classifying true runtime-output benchmark misses under
    the same label as harness defects
  - packet/recomposition failures remain visible in AC14 attempt summaries, but
    the next repair should first make the smoke verdict truthful about the
    dominant failure surface

# Plan #117: Front-Half Runtime-Harness Repair V And Smoke Rerun X

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 116
**Blocks:** None

---

## Gap

**Current:** Smoke_11 still says `blocked_on_harness`, but both conditions now
fail in `runtime_outputs`. The current smoke verdict no longer distinguishes
real runtime-output benchmark misses from genuine harness defects.

**Target:** Repair smoke verdict taxonomy and observability so the front-half-first
gate can emit an explicit `blocked_on_runtime_outputs` state when the benchmark
executes end to end without infrastructure noise but no condition matches the
runtime outputs, then spend one fresh bounded smoke rerun immediately.

**Why:** The active 24-hour chain must stay executable without new human
direction at each blocker boundary.

---

## Acceptance Criteria

- [ ] The smoke verdict distinguishes runtime-output benchmark failures from true
      harness failures.
- [ ] The smoke artifact preserves enough summary detail that the next branch can
      see whether packet/recomposition noise coexists with runtime-output misses.
- [ ] Targeted tests prove the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant smoke-taxonomy blocker named by Plan #116
2. do not weaken the success gate; only make the failure classification truthful
3. verify the repair with targeted tests first
4. rerun one bounded smoke trial immediately after the repair
5. if the rerun returns `blocked_on_runtime_outputs`, freeze the next runtime-output
   boundary immediately as Plan #118
6. if the rerun still returns `blocked_on_harness`, freeze the next narrower
   harness-only boundary immediately rather than broadening scope

---

## Result

Smoke_12 exists at `.ac14_out/front_half_first_smoke_12/` and still returns
`blocked_on_harness`, but the blocker is no longer the old taxonomy issue. The
fresh artifact shows three concrete pre-runtime contract failures:

1. one generation path still treats a bound source output as the final
   `scaling_decision_store` output
2. one AC14 attempt reaches runtime with an extra required unbound state input
   (`StoreUpdater.previous_store`)
3. one front-half draft still persists a generic unknown port schema alias
   (`record`)

That means the runtime-output verdict split landed, and the next bounded lane is
pre-runtime contract hardening rather than benchmark-local semantic tuning.

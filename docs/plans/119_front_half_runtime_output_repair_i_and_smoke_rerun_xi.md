# Plan #119: Front-Half Runtime-Output Repair I And Smoke Rerun XI

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 118
**Blocks:** None

---

## Gap

**Current:** Smoke_12 is still `blocked_on_harness`, but the remaining failures
are all pre-runtime contract quality problems:

1. final-output inference can still pick a bound source output instead of the
   true final emitted store output
2. front-half-first AC14 retries still waste attempts on extra required unbound
   inputs like `StoreUpdater.previous_store`
3. draft-plan validation still allows generic unknown port schema aliases like
   `record`

**Target:** Repair those pre-runtime contract failures, then spend one fresh
bounded smoke rerun immediately.

**Why:** The active 24-hour chain must stay executable without new human
direction at each blocker boundary.

---

## Acceptance Criteria

- [x] Final-output inference excludes non-final bound outputs when choosing
      structured-spec final outputs.
- [x] Front-half-first AC14 attempts fail before runtime when a generated
      blueprint leaves extra required inputs unbound.
- [x] Draft-plan validation rejects generic unknown port schema aliases like
      `record` and `dict`.
- [x] Targeted tests prove the repair before the rerun.
- [x] One fresh smoke artifact exists after the repair at
      `.ac14_out/front_half_first_smoke_13/`.
- [x] The next branch is explicit from the new artifact as Plan #88 + #100,
      Plan #120 + #121, Plan #122 + #123, Plan #124 + #125, or
      Plan #128 + #129.

---

## Execution Contract

This plan must stay bounded:

1. repair only the smoke_12 pre-runtime contract blockers named by Plan #118
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. if the rerun returns `ready_for_full_trials`, immediately continue into
   Plan #88 then Plan #100
5. if the rerun returns `blocked_on_runtime_outputs`, immediately continue into
   Plan #120 then Plan #121
6. if the rerun still returns `blocked_on_harness`, immediately continue into
   Plan #122 then Plan #123

## Result

The code repair landed and verified cleanly, but smoke_13 did not reach the
expected runtime-output or harness boundary. The rerun artifact at
`.ac14_out/front_half_first_smoke_13/` returned `blocked_on_front_half`
because both AC14 and monolithic generation failed immediately in the
repo-local environment with `No module named 'instructor'`. That artifact
closed Plan #119's pre-runtime contract lane and opened the new dependency
boundary in Plan #124.

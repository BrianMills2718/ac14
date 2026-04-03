# Plan #118: Front-Half Runtime-Output Boundary I

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 117
**Blocks:** 119

---

## Gap

**Current:** Smoke_12 still says `blocked_on_harness`, but the blocker is now a
mixed pre-runtime contract failure set rather than a runtime-output taxonomy
problem.

**Target:** Freeze the exact smoke_12 blocker mix into one bounded next repair
lane:

1. final-output inference must not treat bound source outputs as final system
   outputs
2. front-half-first AC14 attempts must fail earlier on extra required unbound
   inputs like `StoreUpdater.previous_store`
3. draft-plan validation must fail generic unknown port schema aliases like
   `record` before runtime

**Why:** The next smoke run should spend its budget on real end-to-end runtime
evaluation rather than avoidable contract-quality failures.

---

## Acceptance Criteria

- [x] The smoke_12 blocker mix is frozen from persisted artifacts.
- [x] The dominant next repair lane is narrowed to pre-runtime contract quality,
      not generic runtime-output tuning.
- [x] The next move is explicit as Plan #119.

---

## Continuation Contract

The next required move is
[Plan #119: Front-Half Runtime-Output Repair I And Smoke Rerun XI](119_front_half_runtime_output_repair_i_and_smoke_rerun_xi.md).

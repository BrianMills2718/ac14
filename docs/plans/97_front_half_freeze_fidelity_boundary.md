# Plan #97: Front-Half Freeze Fidelity Boundary

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 106
**Blocks:** 104

---

## Gap

**Current:** Smoke rerun IV at `.ac14_out/front_half_first_smoke_6/` completed
without infrastructure contamination and returned `blocked_on_front_half`.
AC14 now persists full front-half artifacts through freeze decision and retry,
so the blocker is no longer hidden default-model plumbing.

**Target:** Freeze the next blocker boundary around front-half freeze fidelity
instead of reopening generic micro-repairs.

**Why:** The front-half-first empirical chain should stay falsifiable and
bounded to the dominant blocker class from the clean smoke artifact.

---

## Acceptance Criteria

- [x] One explicit blocker-boundary artifact exists from the clean smoke_6
      verdict.
- [x] The next move is explicit and bounded to the dominant front-half blocker
      class.
- [x] The full-trial budget remains closed unless a later rerun says otherwise.

---

## Boundary Result

The repeated blocker cluster from smoke_6 is:

1. `E-B1-SCHEMA-FIELD-REF-MISSING` dominates attempts 1-3 because
   draft-authored schemas still use compact structured-spec type aliases such as
   `str`, `int`, `float`, `bool`, and `list[record]` where the frozen blueprint
   validator expects blueprint field types.
2. `E-B1-COMPONENT-FIXTURE-COVERAGE-MISSING` and
   `E-B1-END-TO-END-SCENARIO-COVERAGE-MISSING` remain because the draft-authoring
   path still emits an empty `fixtures.yaml`.
3. The readiness rule is stricter than the code taxonomy: warnings qualify the
   draft but still make `ready=false`, which makes approved freeze impossible
   even when only `W-*` findings remain.

Secondary noise from attempt 3:

- `E-B1-BINDING-SCHEMA-MISMATCH`
- `E-B1-GRAPH-CYCLE`

These remain secondary until the shared freeze-fidelity blocker class above is
repaired.

---

## Continuation Contract

The next required move is
[Plan #104: Front-Half Freeze-Fidelity Repair And Smoke Rerun V](104_front_half_freeze_fidelity_repair_and_smoke_rerun_iv.md).

# Plan #104: Front-Half Freeze-Fidelity Repair And Smoke Rerun V

**Status:** In Progress
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 97
**Blocks:** 88, 98, 107, 108

---

## Gap

**Current:** Smoke_6 proved the active lane is no longer blocked by hidden
Gemini-default subcalls. The gate is now blocked by front-half freeze fidelity:
invalid draft schema field types, empty fixture coverage, and a readiness rule
that treats warnings like blockers.

**Target:** Repair that shared freeze-fidelity blocker class, then spend one
fresh bounded smoke rerun immediately.

**Why:** The active lane should not stop at blocker naming; it should convert
the boundary into one bounded empirical retry inside the same 24-hour chain.

---

## Acceptance Criteria

- [ ] Draft authoring normalizes structured-spec aliases into valid blueprint
      field types and no longer emits `E-B1-SCHEMA-FIELD-REF-MISSING` for
      `str/int/float/bool/list[record]`.
- [ ] Draft authoring emits scenario-linked component fixtures so freeze
      approval is no longer impossible by construction.
- [ ] Readiness blocks only on `E-*` findings; `W-*` findings remain persisted
      and reviewable.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next boundary or full-trial branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant front-half blocker class named by Plan #97
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. update the control docs from the fresh verdict before stopping

---

## Implementation Scope

Bounded repair contents:

1. normalize compact structured-spec field types during draft authoring
2. tolerate those aliases at validation boundaries to avoid false blocker
   classification on saved draft artifacts
3. synthesize minimal typed fixture coverage and connect scenario fixture IDs
   during draft authoring
4. make freeze readiness block only on `E-*` findings so warnings qualify the
   draft instead of making approval impossible

Fresh smoke rerun target:

```bash
make front-half-first-smoke-gate \
  OUTPUT=.ac14_out/front_half_first_smoke_7 \
  BENCHMARK=benchmarks/resource_scaling_structured_spec \
  MAX_ATTEMPTS=3 \
  MODEL=gpt-5-mini
```

---

## Branch Contract After Smoke_7

- if `ready_for_full_trials`: execute Plan #88, then Plan #100
- if `blocked_on_harness`: execute Plan #98, then Plan #105
- if `blocked_on_infrastructure`: execute Plan #107
- if `blocked_on_front_half`: execute Plan #108, then Plan #109

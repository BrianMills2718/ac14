# Plan #106: Front-Half Model Propagation Repair And Smoke Rerun IV

**Status:** In Progress
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 99
**Blocks:** 88, 97, 98, 107

---

## Gap

**Current:** Plan #99 showed that smoke_5 is blocked by hidden Gemini-default
subcalls inside the AC14 front-half path, not by the top-level smoke runner.

**Target:** Propagate the explicit smoke model and budget through the AC14
front-half subcalls that still default to Gemini, then rerun one bounded smoke
trial immediately.

**Why:** Until the front-half subcalls honor the operator-selected model, the
smoke artifact is still mixing thesis evidence with hidden infrastructure
defaults.

---

## Acceptance Criteria

- [ ] Explicit model propagation is implemented and verified across the active
      front-half path.
- [ ] One fresh smoke artifact exists after the propagation repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the hidden default-model plumbing isolated by Plan #99
2. verify the propagation with targeted tests before spending the rerun
3. rerun one bounded smoke trial immediately
4. update the control docs from the fresh verdict before stopping

---

## Implementation Summary (In Progress — 2026-04-02)

Repair target:

- propagate explicit model/budget through:
  - structured-spec front-half acceptance
  - discovery front-half acceptance
  - freeze semantic review
  - refreshed freeze inside retry paths

Verification target before rerun:

- targeted unit tests prove explicit model propagation
- `mypy` and `ruff` stay green

Smoke rerun target:

```bash
make front-half-first-smoke-gate \
  OUTPUT=.ac14_out/front_half_first_smoke_6 \
  BENCHMARK=benchmarks/resource_scaling_structured_spec \
  MAX_ATTEMPTS=3 \
  MODEL=gpt-5-mini
```

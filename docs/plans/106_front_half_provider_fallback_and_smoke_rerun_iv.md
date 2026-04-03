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

- [x] Explicit model propagation is implemented and verified across the active
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

Verified repair state before rerun:

- committed in `24627ff` (`[Plan #106] Propagate freeze review model overrides`)
- targeted verification passed:
  - `python -m pytest -q tests/test_freeze_decision.py tests/test_freeze_retry.py tests/test_front_half_acceptance.py`
  - `python -m pytest -q tests/test_cli.py tests/test_make_targets.py -k 'decide_freeze or retry_freeze or structured_spec_front_half_acceptance or front_half_acceptance_help'`
  - `python -m ruff check ac14 tests`

Live rerun state at the current uncertainty boundary:

- monolithic attempt 1: persisted, `runtime_outputs`
- monolithic attempt 2: persisted, `runtime_outputs`
- monolithic attempt 3: persisted, `runtime_outputs`
- AC14 attempt 1 has progressed past the old hidden-default boundary far enough
  to persist `trial_1/ac14/attempt_1/structured_spec/structured_spec_artifact.json`
- the rerun has **not** yet produced `smoke_readiness_report.json`, so Plan #106
  remains in progress and no branch verdict is honest yet

# Plan #113: Front-Half Runtime-Harness Repair III And Smoke Rerun VIII

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 112
**Blocks:** None

---

## Gap

**Current:** Smoke_9 still says `blocked_on_harness`, and the dominant blocker
is now concrete: the structured-spec benchmark bundle still under-specifies the
runtime contract reused from `resource_scaling`, and one retry emitted a true
zero-input `source` component that the current runtime contract cannot inject.

**Target:** Repair the structured-spec/runtime contract boundary named by
Plan #112, then spend one fresh bounded smoke rerun immediately.

**Why:** The active 24-hour chain must stay executable without new human
direction at each blocker boundary.

---

## Acceptance Criteria

- [x] The structured-spec benchmark/runtime contract is made truthful enough
      that both conditions consume the same bounded input surface.
- [x] The runtime contract can execute a generated graph even when the draft
      emits a zero-input `source` component for the top-level structured input.
- [x] Targeted tests prove the repair before the rerun.
- [x] One fresh smoke artifact exists after the repair.
- [x] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant blocker named by Plan #112
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. update the control docs from the fresh verdict before stopping

---

## References Reviewed

- `.ac14_out/front_half_first_smoke_9/smoke_readiness_report.json`
- `.ac14_out/front_half_first_smoke_9/trial_1/paired_trial_report.json`
- `.ac14_out/front_half_first_smoke_9/trial_1/ac14/attempt_1/attempt_report.json`
- `.ac14_out/front_half_first_smoke_9/trial_1/ac14/attempt_2/attempt_report.json`
- `.ac14_out/front_half_first_smoke_9/trial_1/ac14/attempt_3/attempt_report.json`
- `benchmarks/resource_scaling_structured_spec/structured_spec_input.yaml`
- `benchmarks/resource_scaling/input/runtime_cases.json`
- `ac14/front_half_first_empirical.py`
- `ac14/structured_spec_benchmark.py`
- `tests/test_front_half_first_empirical.py`
- `tests/test_structured_spec_benchmark.py`

## Open Questions

- Should the benchmark repair adapt the legacy runtime records into the
  structured-spec shape, or should the structured spec itself be tightened to
  match the reused runtime assets? This plan must make that decision explicitly
  instead of leaving both half-supported.

## Files Affected

- `benchmarks/resource_scaling_structured_spec/benchmark.yaml`
- `benchmarks/resource_scaling_structured_spec/structured_spec_input.yaml`
- `benchmarks/resource_scaling_structured_spec/requirements.md`
- `ac14/structured_spec_benchmark.py`
- `ac14/front_half_first_empirical.py`
- `tests/test_structured_spec_benchmark.py`
- `tests/test_front_half_first_empirical.py`
- `docs/AC14_NEXT_24_HOURS.md`
- `docs/TODO.md`
- `docs/plans/CLAUDE.md`
- `docs/plans/113_front_half_runtime_harness_repair_iii_and_smoke_rerun_viii.md`

## Required Tests

- `python -m pytest -q tests/test_structured_spec_benchmark.py tests/test_front_half_first_empirical.py`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

## Implementation Scope

Bounded repair contents:

1. make the `resource_scaling_structured_spec` bundle truthful about the
   runtime contract it reuses
2. ensure the front-half-first runner feeds both conditions the same bounded
   structured-spec input surface rather than one side seeing legacy raw fields
3. support one generated top-level `source` component contract when it is the
   unique structured-spec entry point
4. rerun the smoke gate immediately after the repair

Fresh smoke rerun target:

```bash
make front-half-first-smoke-gate \
  OUTPUT=.ac14_out/front_half_first_smoke_10 \
  BENCHMARK=benchmarks/resource_scaling_structured_spec \
  MAX_ATTEMPTS=3 \
  MODEL=gpt-5-mini
```

## Branch Contract After Smoke_10

- if `ready_for_full_trials`: execute Plan #88, then Plan #100
- if `blocked_on_harness`: execute Plan #114, then Plan #115
- if `blocked_on_infrastructure`: execute Plan #107
- if `blocked_on_front_half`: execute Plan #108, then Plan #109

## Progress Notes

- Repair landed and was committed as `[Plan #113] Repair structured-spec runtime contract and source entry`.
- Fresh smoke artifact: `.ac14_out/front_half_first_smoke_10/smoke_readiness_report.json`
- Smoke_10 still returned `blocked_on_harness`, but the old input/source-entry
  mismatch cleared. The next blocker is final-output binding fidelity: generated
  drafts emit the correct final schemas under renamed output ports, and runtime
  inference still expects literal ports named `scaling_decision_entry`.

- 2026-04-03: Activated from Plan #112 after smoke_9 kept the top-level verdict
  at `blocked_on_harness` but moved the blocker to the structured-spec/runtime
  contract boundary itself.

# Plan #111: Front-Half Runtime-Harness Repair II And Smoke Rerun VII

**Status:** In Progress
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 110
**Blocks:** None

---

## Gap

**Current:** Smoke_8 still says `blocked_on_harness`, but the blocker is now
specific: the front-half-first runner assumes all structured-spec final outputs
must come from one component, while the generated AC14 graph now splits
`scaling_decision_entry` and `scaling_decision_store` across two components.

**Target:** Repair the dominant runtime/harness blocker named by Plan #110 by
making final-output inference and runtime execution truthful for split-output
graphs, then spend one fresh bounded smoke rerun immediately.

**Why:** The current 24-hour chain must stay executable without depending on
chat memory or a new human decision at each smoke boundary.

---

## Acceptance Criteria

- [ ] Runtime-contract inference succeeds when structured-spec final outputs are
      emitted by multiple components in one generated graph.
- [ ] Runtime execution can collect final outputs from the inferred component
      map without faking a single final component.
- [ ] Targeted tests prove the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant blocker named by Plan #110
2. verify the repair with targeted tests first
3. rerun one bounded smoke trial immediately after the repair
4. update the control docs from the fresh verdict before stopping

---

## References Reviewed

- `.ac14_out/front_half_first_smoke_8/smoke_readiness_report.json`
- `.ac14_out/front_half_first_smoke_8/trial_1/paired_trial_report.json`
- `.ac14_out/front_half_first_smoke_8/trial_1/ac14/attempt_1/attempt_report.json`
- `.ac14_out/front_half_first_smoke_8/trial_1/ac14/attempt_1/front_half/draft_bundle/components.yaml`
- `ac14/front_half_first_empirical.py`
- `tests/test_front_half_first_empirical.py`

## Open Questions

- If smoke_9 still says `blocked_on_harness`, is the next blocker packet/runtime
  evaluation itself rather than contract inference? Plan #112 is predeclared
  for that verdict.

## Files Affected

- `ac14/front_half_first_empirical.py`
- `tests/test_front_half_first_empirical.py`
- `docs/AC14_NEXT_24_HOURS.md`
- `docs/TODO.md`
- `docs/plans/CLAUDE.md`
- `docs/plans/111_front_half_runtime_harness_repair_ii_and_smoke_rerun_vii.md`

## Required Tests

- `python -m pytest -q tests/test_front_half_first_empirical.py`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

## Implementation Scope

Bounded repair contents:

1. replace the single-final-component assumption in
   `infer_runtime_contract_from_structured_spec()` with truthful per-output
   component inference
2. update runtime execution to gather each final output from its inferred
   component instead of indexing one final component
3. add direct tests for split-output graphs

Fresh smoke rerun target:

```bash
make front-half-first-smoke-gate \
  OUTPUT=.ac14_out/front_half_first_smoke_9 \
  BENCHMARK=benchmarks/resource_scaling_structured_spec \
  MAX_ATTEMPTS=3 \
  MODEL=gpt-5-mini
```

## Branch Contract After Smoke_9

- if `ready_for_full_trials`: execute Plan #88, then Plan #100
- if `blocked_on_harness`: execute Plan #112, then Plan #113
- if `blocked_on_infrastructure`: execute Plan #107
- if `blocked_on_front_half`: execute Plan #108, then Plan #109

## Progress Notes

- 2026-04-02: Activated from Plan #110 after smoke_8 kept the same top-level
  verdict but moved the blocker to split final-output inference.

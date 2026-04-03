# Plan #105: Front-Half Runtime-Harness Repair And Smoke Rerun IV

**Status:** In Progress
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 98
**Blocks:** None

---

## Gap

**Current:** Smoke_7 proved that AC14 now reaches approved front-half artifacts,
but the active runner still fails before runtime because runtime-contract
inference assumes the structured-spec input name must exactly equal the
generated root input-port name.

**Target:** Repair the dominant runtime/harness blocker from Plan #98 by making
runtime-contract inference robust to generated root-port renaming, then spend
one fresh bounded smoke rerun immediately.

**Why:** The active empirical chain should keep moving from blocker boundary to
one measured retry without requiring new chat direction.

---

## Acceptance Criteria

- [ ] Runtime-contract inference succeeds when the generated blueprint preserves
      one unique unbound root input but renames the port away from the original
      structured-spec input name.
- [ ] Attempt artifacts persist enough observability to distinguish future
      contract-inference failures from later packet/runtime failures without a
      manual reproduction pass.
- [ ] Targeted tests cover the repaired runtime-contract inference path.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant runtime or harness blocker named by Plan #98
2. keep the repair at the runner/runtime-contract layer; do not reopen
   front-half authoring or benchmark semantics in this lane
3. verify the repair with targeted tests first
4. rerun one bounded smoke trial immediately after the repair
5. update the control docs from the fresh verdict before stopping

---

## References Reviewed

- `.ac14_out/front_half_first_smoke_7/smoke_readiness_report.json`
- `.ac14_out/front_half_first_smoke_7/trial_1/paired_trial_report.json`
- `.ac14_out/front_half_first_smoke_7/trial_1/ac14/attempt_1/attempt_report.json`
- `.ac14_out/front_half_first_smoke_7/trial_1/ac14/attempt_1/front_half/draft_bundle/components.yaml`
- `.ac14_out/front_half_first_smoke_7/trial_1/ac14/attempt_1/front_half/draft_bundle/schemas.yaml`
- `ac14/front_half_first_empirical.py`
- `tests/test_front_half_first_empirical.py`

## Open Questions

- If smoke_8 still says `blocked_on_harness` after the runtime-contract repair,
  is the next blocker packet/recomposition/runtime mismatch or another runner
  inference failure? Plan #110 is predeclared for that verdict.

## Files Affected

- `ac14/front_half_first_empirical.py`
- `tests/test_front_half_first_empirical.py`
- `docs/AC14_NEXT_24_HOURS.md`
- `docs/TODO.md`
- `docs/plans/CLAUDE.md`
- `docs/plans/105_front_half_runtime_harness_repair_and_smoke_rerun_iv.md`

## Required Tests

- `python -m pytest -q tests/test_front_half_first_empirical.py`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

## Implementation Scope

Bounded repair contents:

1. repair `infer_runtime_contract_from_structured_spec()` so it can:
   - prefer one exact unbound input-port name match
   - otherwise accept one unique unbound root input whose schema shape matches
     the single structured-spec top-level input
   - fail loud with explicit candidate details when the source contract is still
     ambiguous
2. persist per-attempt failure classification as a first-class artifact if that
   improves direct smoke diagnosis without broadening scope
3. add a direct test for the `metrics_snapshot -> metrics_snapshot_in` case

Fresh smoke rerun target:

```bash
make front-half-first-smoke-gate \
  OUTPUT=.ac14_out/front_half_first_smoke_8 \
  BENCHMARK=benchmarks/resource_scaling_structured_spec \
  MAX_ATTEMPTS=3 \
  MODEL=gpt-5-mini
```

## Branch Contract After Smoke_8

- if `ready_for_full_trials`: execute Plan #88, then Plan #100
- if `blocked_on_harness`: execute Plan #110, then Plan #111
- if `blocked_on_infrastructure`: execute Plan #107
- if `blocked_on_front_half`: execute Plan #108, then Plan #109

## Progress Notes

- 2026-04-02: Activated from Plan #98 after smoke_7 showed `blocked_on_harness`
  with `ac14_front_half_success = true`.

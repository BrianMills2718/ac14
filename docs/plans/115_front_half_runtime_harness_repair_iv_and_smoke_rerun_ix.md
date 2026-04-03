# Plan #115: Front-Half Runtime-Harness Repair IV And Smoke Rerun IX

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 114
**Blocks:** None

---

## Gap

**Current:** Smoke_10 still says `blocked_on_harness`, and the dominant blocker
is now specific: runtime contract inference still expects each structured-spec
output name to appear as the literal emitted port name, even when the generated
draft emits the correct final schema under a renamed port such as
`final_decision` or `decision_out`.

**Target:** Repair final-output binding fidelity so the runtime contract can bind
one structured-spec output to one generated component output by exact port name,
schema-id/name fidelity, or bounded schema-shape fidelity, then spend one fresh
bounded smoke rerun immediately.

**Why:** The active 24-hour chain must stay executable without new human
direction at each blocker boundary.

---

## Acceptance Criteria

- [x] Final-output binding inference supports renamed emitted ports without relaxing
      ambiguity handling.
- [x] Runtime execution can read generated outputs through the inferred emitted-port
      mapping while still reporting the structured-spec output names externally.
- [x] Targeted tests prove the repair before the rerun.
- [x] One fresh smoke artifact exists after the repair.
- [x] The next branch is explicit from the new artifact.

---

## Execution Contract

This plan must stay bounded:

1. repair only the dominant final-output binding blocker named by Plan #114
2. keep ambiguity loud: multiple matching outputs must still fail with explicit candidates
3. verify the repair with targeted tests first
4. rerun one bounded smoke trial immediately after the repair
5. update the control docs from the fresh verdict before stopping

---

## Implementation Summary

- Runtime contract inference now binds final structured-spec outputs by emitted
  port name, schema-id/name fidelity, or schema-shape fidelity instead of exact
  port spelling only.
- Runtime execution now extracts outputs through the inferred emitted-port
  mapping while preserving the structured-spec output names externally.
- Verification passed before the rerun:
  - `python -m pytest -q tests/test_front_half_first_empirical.py tests/test_structured_spec_benchmark.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- Fresh smoke artifact:
  - `.ac14_out/front_half_first_smoke_11/smoke_readiness_report.json`
- Smoke_11 still returned `blocked_on_harness`, but the old output-binding bug is
  cleared. The next blocker is that the smoke verdict now conflates real
  runtime-output benchmark failures with remaining harness noise.

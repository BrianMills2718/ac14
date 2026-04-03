# Plan #75: Resource Scaling Prompt-Schema Grounding Repair

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 74
**Blocks:** 76

---

## Gap

**Current:** The packet-context diagnosis says the failing `resource_scaling`
component packets are structurally sufficient, but rule salience is uneven.
`trend_evaluator` and `deploy_risk_evaluator` rely heavily on examples and weak
schema descriptions instead of explicit local benchmark guidance.

**Target:** Strengthen prompt/schema grounding for the failing component cluster
without changing packet projection itself, then run one bounded smoke trial to
see whether the repair materially improves AC14's hard-harness performance.

**Why:** The diagnosis points to generation-grounding weakness, not packet
insufficiency. The next honest code lane is to make the local rules more salient
before redesigning packets.

---

## References Reviewed

- `investigations/ac14/2026-04-02-resource-scaling-second-gate-diagnosis.md`
- `investigations/ac14/2026-04-02-resource-scaling-packet-context-diagnosis.md`
- `.ac14_out/full_trials_gate_2/trial_*/paired_trial_report.json`
- `ac14/empirical_comparison.py`
- `benchmarks/resource_scaling/blueprint/components.yaml`
- `benchmarks/resource_scaling/blueprint/schemas.yaml`

---

## Open Questions

### Q1: Which local surfaces should carry the missing benchmark rules?
**Status:** Open
**Why it matters:** The repair should improve salience without smearing
benchmark-local rules into unrelated global machinery.

### Q2: Is one bounded smoke rerun enough to justify or reject the grounding repair?
**Status:** Open
**Why it matters:** The next gate should stay cheap until the repair earns
another full-trial budget.

---

## Files Affected

- `ac14/empirical_comparison.py` (modify)
- `benchmarks/resource_scaling/blueprint/components.yaml` (modify)
- `benchmarks/resource_scaling/blueprint/schemas.yaml` (modify)
- `tests/test_empirical_comparison.py` (modify)
- `docs/plans/75_resource_scaling_prompt_schema_grounding_repair.md` (create)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)

---

## Plan

### Steps

1. Add explicit benchmark-local guidance for the under-specified failing components.
2. Strengthen the relevant local schema descriptions and/or component constraints.
3. Add regression tests for the new benchmark-local guidance and schema wording.
4. Run one bounded smoke trial on `resource_scaling_v1` and inspect whether AC14 gains a hard-harness success.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_empirical_comparison.py` | `test_resource_scaling_component_guidance_targets_trend_and_deploy_risk_rules` | The new local rules are present in the empirical guidance surface |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q tests/test_empirical_comparison.py` | Targeted regression coverage for the empirical lane |
| `python -m mypy ac14 tests` | Type safety remains clean |
| `python -m ruff check ac14 tests` | Lint/import hygiene remains clean |

---

## Acceptance Criteria

- [x] The failing component cluster has stronger local rule salience without packet redesign.
- [x] Targeted regression tests cover the new benchmark-local guidance surface.
- [x] One bounded smoke artifact shows whether the grounding repair earned another full-trial budget.

---

## Notes

This plan should stay benchmark-local and grounding-local. It is not permission
to add more broad empirical machinery.

## Implementation Summary (2026-04-02)

What landed:

- explicit benchmark-local guidance for `trend_evaluator`
- explicit benchmark-local guidance for `deploy_risk_evaluator`
- stronger local component constraints and schema descriptions for the same rule surfaces
- targeted empirical regression coverage for those guidance/schema additions

Fresh smoke artifact:

- `.ac14_out/full_trials_gate_2_smoke_grounding1/smoke_readiness_report.json`
- verdict: `ready_for_full_trials`
- infrastructure contamination: `false`

Important nuance:

- AC14 still achieved `0` hard-harness successes in the smoke trial
- the dominant AC14 failures shifted away from the original trend/deploy-risk
  cluster and narrowed to `recommendation_generator`, `alert_planner`, and a
  `decision_recorder` runtime/code path issue

So the grounding repair changed the failure surface, but it did not yet earn an
AC14 smoke success.

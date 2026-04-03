# Plan #79: Post-Grounding Smoke Rerun

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 78
**Blocks:** 80, 81

---

## Gap

**Current:** Plan #78 should strengthen rule grounding in a reusable way, but
the project still needs a bounded empirical test to decide whether that repair
is meaningful enough to reopen the harder benchmark gate.

**Target:** Run one fresh bounded smoke trial on `resource_scaling_v1` after the
reusable grounding repair and freeze the next branch from the persisted smoke
artifact.

**Why:** The project should spend another full gate only if the reusable repair
earns at least one AC14 hard-harness success without infrastructure
contamination.

---

## References Reviewed

- `docs/plans/77_cross_benchmark_failure_taxonomy.md`
- `docs/plans/78_reusable_packet_rule_grounding.md`
- `.ac14_out/full_trials_gate_2_smoke_grounding1/smoke_readiness_report.json`
- `.ac14_out/full_trials_gate_2_smoke_grounding1/trial_1/paired_trial_report.json`

---

## Open Questions

### Q1: Did the reusable grounding repair earn an AC14 hard-harness smoke success?
**Status:** Resolved
**Why it matters:** Without that, another full five-trial rerun is not justified.
**Resolution:** No. The fresh smoke artifact remained `ready_for_full_trials`
only because monolithic passed. AC14 still failed all three bounded attempts.

### Q2: Does the fresh smoke artifact point to a full rerun or a strategic pivot?
**Status:** Resolved
**Why it matters:** The next branch should be explicit and artifact-driven.
**Resolution:** It points to a strategic pivot. The stricter branch rule for
this plan was AC14 success, not merely any-condition smoke success.

---

## Files Affected

- `.ac14_out/...` empirical smoke artifacts (generated)
- `docs/plans/79_post_grounding_smoke_rerun.md` (create/update)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)

---

## Plan

### Steps

1. Run one bounded smoke trial after Plan #78.
2. Record whether AC14 achieved a hard-harness success and whether
   infrastructure contamination appeared.
3. Freeze the next branch explicitly:
   - Plan #80 if AC14 earns a clean hard-harness smoke success
   - Plan #81 otherwise

---

## Required Tests

| Command | Why |
|---------|-----|
| `python -m ac14 empirical-smoke-gate ...` | The smoke artifact is the acceptance surface for this plan |

---

## Acceptance Criteria

- [x] A fresh post-grounding smoke artifact exists.
- [x] The repo states clearly whether AC14 earned a hard-harness success.
- [x] The next branch is explicit from the smoke artifact.

---

## Notes

This plan should not silently reopen the full gate. The smoke artifact decides.

## Implementation Summary (2026-04-02)

Fresh artifact:

- `.ac14_out/full_trials_gate_2_smoke_reusable_grounding1/smoke_readiness_report.json`
- `.ac14_out/full_trials_gate_2_smoke_reusable_grounding1/trial_1/paired_trial_report.json`

Result:

- smoke verdict: `ready_for_full_trials`
- infrastructure contamination: `false`
- monolithic: passed in 1 attempt
- AC14: failed in 3 attempts

Important branch rule:

- this plan required an **AC14** hard-harness smoke success to reopen the full
  second gate
- that did not happen
- therefore the next branch is [Plan #81: Post-Grounding Strategic Pivot](/home/brian/projects/ac14/docs/plans/81_post_grounding_strategic_pivot.md), not Plan #80

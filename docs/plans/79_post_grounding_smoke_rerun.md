# Plan #79: Post-Grounding Smoke Rerun

**Status:** In Progress
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
**Status:** Open
**Why it matters:** Without that, another full five-trial rerun is not justified.

### Q2: Does the fresh smoke artifact point to a full rerun or a strategic pivot?
**Status:** Open
**Why it matters:** The next branch should be explicit and artifact-driven.

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

- [ ] A fresh post-grounding smoke artifact exists.
- [ ] The repo states clearly whether AC14 earned a hard-harness success.
- [ ] The next branch is explicit from the smoke artifact.

---

## Notes

This plan should not silently reopen the full gate. The smoke artifact decides.

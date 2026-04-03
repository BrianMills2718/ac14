# Plan #81: Post-Grounding Strategic Pivot

**Status:** Complete
**Type:** evaluation + planning
**Priority:** Critical
**Blocked By:** 79
**Blocks:** None

---

## Gap

**Current:** If the reusable grounding repair still fails to earn an AC14
hard-harness smoke success, the harder benchmark should not be reopened by
habit.

**Target:** Freeze the post-grounding strategic response explicitly: claim
boundary adjustment, front-half-first pivot, or different empirical design.

**Why:** The project should pivot from evidence, not continue local tuning
without a new basis.

---

## References Reviewed

- `docs/plans/77_cross_benchmark_failure_taxonomy.md`
- `docs/plans/78_reusable_packet_rule_grounding.md`
- `docs/plans/79_post_grounding_smoke_rerun.md`
- `.ac14_out/full_trials_gate_2/experiment_decision.json`
- `.ac14_out/full_trials_gate_2_smoke_reusable_grounding1/smoke_readiness_report.json`
- `.ac14_out/full_trials_gate_2_smoke_reusable_grounding1/trial_1/paired_trial_report.json`

---

## Open Questions

### Q1: Should the harder second gate be reopened anyway because the smoke verdict says `ready_for_full_trials`?
**Status:** Resolved
**Why it matters:** Reopening the gate on the wrong criterion would undo the
purpose of Plan #79.
**Resolution:** No. Plan #79 required AC14 success, not merely monolithic
success, so the harder second gate stays closed.

### Q2: What should the project do next instead of another back-half rerun?
**Status:** Resolved
**Why it matters:** The next lane should strengthen the thesis where AC14 is
supposed to have real advantage.
**Resolution:** Pivot to a front-half-first empirical contract and keep further
back-half benchmark-local tuning frozen.

---

## Files Affected

- `docs/plans/81_post_grounding_strategic_pivot.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)

---

## Plan

### Steps

1. Read the post-grounding smoke artifact against the stricter branch rule.
2. State explicitly why the second gate stays closed.
3. Freeze the next strategic move toward a front-half-first empirical contract.

---

## Acceptance Criteria

- [x] The repo states clearly why the harder gate stays closed.
- [x] The next strategic move is explicit and does not default to more local repair.

---

## Notes

This plan becomes active only if Plan #79 fails to earn a clean AC14 smoke
success.

## Implementation Summary (2026-04-02)

Decision:

- the harder second gate remains closed
- further `resource_scaling_v1` tuning remains frozen
- the current back-half empirical story is now:
  - gate 1: `inconclusive`
  - gate 2: `monolithic_wins`
  - reusable grounding rerun: still `0/3` AC14 smoke successes

Strategic response:

- stop spending more budget on back-half local repairs
- move the next empirical horizon to a front-half-first comparison where AC14's
  discovery / draft / freeze machinery is actually part of the thesis test
- freeze that response explicitly as [Plan #82: Front-Half-First Empirical Contract](/home/brian/projects/ac14/docs/plans/82_front_half_first_empirical_contract.md)

# Plan #76: Second-Gate Repair Boundary

**Status:** Planned
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 75
**Blocks:** None

---

## Gap

**Current:** Plan #75 improved local rule salience and produced a fresh smoke
artifact, but AC14 still achieved `0` hard-harness successes while monolithic
continued to pass.

**Target:** Decide explicitly whether another benchmark-local repair is
justified, or whether the project should stop tuning `resource_scaling_v1` and
move to a broader strategic response.

**Why:** The project should not drift back into an endless micro-repair chain
after already observing one decisive full-trial loss and one failed
post-diagnosis grounding repair.

---

## References Reviewed

- `.ac14_out/full_trials_gate_2/experiment_decision.json`
- `.ac14_out/full_trials_gate_2_smoke_grounding1/smoke_readiness_report.json`
- `.ac14_out/full_trials_gate_2_smoke_grounding1/trial_1/paired_trial_report.json`
- `docs/plans/75_resource_scaling_prompt_schema_grounding_repair.md`
- `investigations/ac14/2026-04-02-resource-scaling-second-gate-diagnosis.md`
- `investigations/ac14/2026-04-02-resource-scaling-packet-context-diagnosis.md`

---

## Open Questions

### Q1: Did the grounding repair materially improve AC14 enough to justify another benchmark-local repair?
**Status:** Open
**Why it matters:** If not, more narrow tuning is likely to be low-value drift.

### Q2: Should the next lane target a structural generation issue, a different empirical surface, or a strategic pivot in claims?
**Status:** Open
**Why it matters:** The next lane should respond to evidence, not habit.

---

## Files Affected

- `docs/plans/76_second_gate_repair_boundary.md` (create)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)

---

## Plan

### Steps

1. Compare the full-trial loss and the grounding-repaired smoke artifact.
2. Decide whether another benchmark-local repair is evidence-justified.
3. Freeze the next strategic or implementation lane explicitly.

---

## Required Tests

This is an evaluation/strategy lane. No new code should land unless the
boundary decision itself points to one narrow justified repair.

---

## Acceptance Criteria

- [ ] The repo states explicitly whether further `resource_scaling_v1` micro-repairs are justified.
- [ ] The next lane is frozen explicitly from that decision.

---

## Notes

This plan exists to preserve project-management discipline after a decisive
empirical loss and a non-winning post-loss smoke repair.

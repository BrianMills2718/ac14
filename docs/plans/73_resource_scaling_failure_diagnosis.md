# Plan #73: Resource Scaling Failure Diagnosis

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 72
**Blocks:** 74

---

## Gap

**Current:** The second empirical gate finished decisively with
`monolithic_wins`, but the repo does not yet have one compact diagnosis of
where AC14 failed on `resource_scaling_v1`.

**Target:** Produce one bounded diagnosis artifact that distinguishes
benchmark-local semantic misses, packet/context sufficiency issues, and
generation-stability issues across the five-trial result.

**Why:** Without this diagnosis, the project risks sliding back into
benchmark-local micro-repairs or broad strategic claims without knowing which
failure class actually dominated the loss.

---

## References Reviewed

- `.ac14_out/full_trials_gate_2/experiment_decision.json`
- `.ac14_out/full_trials_gate_2/trial_*/paired_trial_report.json`
- `docs/plans/72_second_gate_verdict_interpretation.md`
- `docs/AC14_IMPLEMENTATION_STATUS.md`
- `docs/AC14_ROADMAP.md`

---

## Open Questions

### Q1: Is the loss dominated by syntax/generation instability or by benchmark semantics?
**Status:** Open
**Why it matters:** The next code lane depends on whether AC14 is mostly losing
before runtime or mostly losing on wrong business logic after generation.

### Q2: Are the dominant misses benchmark-local or structural to packetized generation?
**Status:** Open
**Why it matters:** Benchmark-local misses call for one kind of follow-up;
structural packet-context insufficiency calls for another.

---

## Files Affected

- `investigations/ac14/2026-04-02-resource-scaling-second-gate-diagnosis.md` (create)
- `docs/plans/73_resource_scaling_failure_diagnosis.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)

---

## Plan

### Steps

1. Summarize aggregate verdict and per-trial outcomes.
2. Count the dominant AC14 failure categories and repeated mismatch surfaces.
3. Decide whether the next response should be benchmark-local repair,
   packet-context diagnosis, or broader strategic pivot.

---

## Required Tests

This is an investigation lane. No new code is required unless the diagnosis
itself reveals a bounded implementation fix that should be landed separately.

---

## Acceptance Criteria

- [x] One persisted diagnosis artifact exists for the second-gate loss.
- [x] The active control docs reflect the next recommended lane based on the diagnosis.

---

## Notes

The goal is not to tune the benchmark yet. The goal is to understand the loss
well enough that the next plan is strategic rather than reflexive.

## Implementation Summary (2026-04-02)

The diagnosis artifact now exists at:

- `investigations/ac14/2026-04-02-resource-scaling-second-gate-diagnosis.md`

It concludes that AC14's loss is dominated by repeated semantic/runtime misses
in a small coupled component cluster, not by infrastructure noise. The next
explicit question is whether those misses reflect insufficient packet context or
poor use of sufficient local context, which is now frozen as Plan #74.

# Plan #67: Second-Gate Blocker Diagnosis

**Status:** Complete
**Type:** evaluation + planning
**Priority:** Critical
**Blocked By:** 65 (`blocked_on_harness` or `blocked_on_infrastructure`)
**Blocks:** 37, 68, 69, 70

---

## Gap

**Current:** The second empirical smoke run blocked before the five-trial
budget was spendable.

**Target:** Diagnose the blocker from the smoke artifacts, freeze the next
repair chain, and keep unrelated propagation lanes blocked.

**Why:** A blocked smoke run is useful only if it produces a bounded next move
instead of another vague repair loop.

---

## References Reviewed

- `docs/plans/65_second_gate_smoke.md`
- `ac14/empirical_comparison.py`
- `.ac14_out/full_trials_gate_2_smoke/smoke_readiness_report.json`
- `.ac14_out/full_trials_gate_2_smoke/trial_1/paired_trial_report.json`
- `.ac14_out/full_trials_gate_2_smoke/trial_1/monolithic/attempt_1/attempt_report.json`
- `.ac14_out/full_trials_gate_2_smoke/trial_1/monolithic/attempt_3/generated/decision_recorder.py`
- `.ac14_out/full_trials_gate_2_smoke/trial_1/ac14/attempt_3/attempt_report.json`
- `docs/UNCERTAINTIES.md`

---

## Open Questions

### Q1: What should this plan output?
**Status:** Resolved
**Decision:** A diagnosis summary plus one explicit next repair chain.

### Q2: What is the narrowest blocker-clearing chain?
**Status:** Resolved
**Decision:** Fix harness correctness first, not AC14 benchmark tuning first.
The smoke gate only needs one hard-harness success. The narrowest honest chain
is: (1) stop exact-match categorical runs from failing on loose semantic review,
(2) catch invalid monolithic input-port references before runtime, then (3)
rerun the smoke gate.

---

## Files Affected

- `docs/plans/67_second_gate_blocker_diagnosis.md`
- `docs/plans/68_deterministic_exact_match_semantic_review_policy.md`
- `docs/plans/69_monolithic_input_port_contract_validation.md`
- `docs/plans/70_second_gate_smoke_rerun.md`
- `docs/plans/CLAUDE.md`
- `docs/TODO.md`
- `docs/AC14_NEXT_24_HOURS.md`
- `docs/UNCERTAINTIES.md`
- `CLAUDE.md`

---

## Plan

### Steps

1. Read the clean post-fix smoke artifact and paired-trial report.
2. Separate harness, provider, and benchmark-local blockers.
3. Freeze the narrowest blocker-clearing next chain.
4. Keep blocked propagation lanes blocked.

---

## Required Tests

No new code tests were required for the diagnosis itself. The acceptance surface
is the persisted smoke artifact plus truthful plan/docs.

---

## Acceptance Criteria

- [x] The smoke blocker is named concretely from persisted artifacts.
- [x] One explicit next repair chain exists.
- [x] The active docs point to that chain rather than drifting sideways.

---

## Implementation Summary (2026-04-02)

The clean smoke run in `.ac14_out/full_trials_gate_2_smoke/` finished with
verdict `blocked_on_harness`, not `blocked_on_infrastructure`. The persisted
smoke artifact reports no hard-harness success and no infrastructure-only
explanation.

Concrete blockers from the artifact set:

1. `monolithic/attempt_1` matched expected runtime outputs for all four runtime
   cases but still failed on semantic review. The review raised a false concern
   claiming `RSC-103 request_rate_rps = 60` was `< 20`, so deterministic exact
   outputs were vetoed by a loose LLM review.
2. `monolithic/attempt_3` reached runtime with modules that referenced the
   nonexistent input port `on_compliance`, producing four `KeyError` runtime
   failures that the pre-emit contract validator did not catch.
3. The AC14 attempts still show real benchmark-local logic misses around
   `trend_evaluator`, `deploy_risk_evaluator`, and `recommendation_generator`,
   but those are not the narrowest gate-opening blocker because the smoke gate
   only needs one hard-harness success.

So the next chain is deliberately narrow:

- Plan #68: make deterministic exact-match benchmarks configurable so semantic
  review becomes advisory when exact outputs already match.
- Plan #69: add pre-emit validation for literal `inputs[...]` port references in
  monolithic generated modules.
- Plan #70: rerun the second-gate smoke trial.

---

## Notes

This plan completed by freezing the next repair chain from persisted artifacts.

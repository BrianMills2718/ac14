# Plan #60: Empirical Smoke Gate Refresh VI

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 58, 59
**Blocks:** 43

---

## Gap

**Current:** Repair10 stayed `blocked_on_harness` without an infrastructure-only explanation. The remaining blocker set is now concrete: one shared shipping-only semantic mismatch plus one recurring generation-stability/observability gap.

**Target:** Run one fresh bounded smoke paired trial against the post-58/post-59 lane and make one explicit gate decision:

1. `ready_for_full_trials` -> unblock Plan #43
2. `blocked_on_harness` -> freeze the next narrower blocker-clearing plan immediately
3. `blocked_on_infrastructure` -> keep the five-trial gate paused for infra reasons

**Why:** Plans #58 and #59 are only successful if the empirical smoke artifact changes honestly.

---

## References Reviewed

- `docs/plans/57_empirical_smoke_gate_refresh_v.md`
- `docs/plans/58_shipping_only_priority_and_correlator_repair.md`
- `docs/plans/59_generation_stability_and_pre_emit_validation_repair.md`
- `.ac14_out/empirical_smoke_gate_repair10/smoke_readiness_report.json`
- `.ac14_out/empirical_smoke_gate_repair10/trial_1/paired_trial_report.json`

---

## Files Affected

- `.ac14_out/empirical_smoke_gate_repair11/` (create)
- `docs/plans/CLAUDE.md`
- `docs/TODO.md`
- `docs/AC14_NEXT_24_HOURS.md`
- `docs/UNCERTAINTIES.md`
- `docs/AC14_IMPLEMENTATION_STATUS.md`
- `KNOWLEDGE.md`

---

## Plan

### Steps

1. Run one bounded smoke gate against the post-58/post-59 lane.
2. Read the smoke verdict and paired-trial artifacts directly.
3. Update the active control docs to match that verdict.
4. Only unblock Plan #43 if the fresh smoke verdict says `ready_for_full_trials`.

---

## Required Tests

- the smoke artifact itself is the primary acceptance surface for this plan
- after the smoke run, rerun `python -m pytest -q`, `python -m mypy ac14 tests`, and `python -m ruff check ac14 tests` only if code/doc changes are needed before commit

---

## Acceptance Criteria

- [x] A fresh bounded smoke artifact exists under `.ac14_out/empirical_smoke_gate_repair11/`.
- [x] The verdict is one of `ready_for_full_trials`, `blocked_on_harness`, or `blocked_on_infrastructure`.
- [x] The active control docs reflect that verdict exactly.
- [x] Plan #43 is unblocked because the fresh smoke artifact says `ready_for_full_trials`.

---

## Implementation Summary (2026-04-02)

Repair11 finally cleared the bounded smoke gate. The new smoke artifact under `.ac14_out/empirical_smoke_gate_repair11/` reported `verdict = ready_for_full_trials`, `hard_harness_success = true`, and `infrastructure_failure_detected = false`. AC14 passed the full benchmark harness on attempt 1, including packet tests, recomposition, runtime outputs, and final semantic review. The monolithic condition still failed all three bounded attempts for reviewable reasons: packet mismatches around optional manual override handling and negative-case factor correlation, then one persisted syntax-invalid `factor_correlator` module. That means the five-trial gate is now worth spending.

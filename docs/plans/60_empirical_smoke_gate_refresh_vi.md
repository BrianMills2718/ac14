# Plan #60: Empirical Smoke Gate Refresh VI

**Status:** In Progress
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

- [ ] A fresh bounded smoke artifact exists under `.ac14_out/empirical_smoke_gate_repair11/`.
- [ ] The verdict is one of `ready_for_full_trials`, `blocked_on_harness`, or `blocked_on_infrastructure`.
- [ ] The active control docs reflect that verdict exactly.
- [ ] Plan #43 is only unblocked if the fresh smoke artifact says `ready_for_full_trials`.

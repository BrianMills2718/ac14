# Plan #54: Empirical Smoke Gate Refresh IV

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 52, 53
**Blocks:** 43

---

## Gap

**Current:** Repair8 proved the empirical gate was still `blocked_on_harness`, but it also gave us a precise blocker set. Plans #52 and #53 landed the observability and benchmark-local contract repairs implied by that artifact.

**Target:** Run one fresh bounded smoke paired trial against the post-52/post-53 lane and make one explicit gate decision:

1. `ready_for_full_trials` -> unblock Plan #43
2. `blocked_on_harness` -> freeze the next narrower blocker-clearing plan immediately
3. `blocked_on_infrastructure` -> keep the five-trial gate paused for infra reasons

**Why:** The repair lanes are only complete if the empirical gate artifact changes honestly.

---

## References Reviewed

- `docs/plans/51_empirical_smoke_gate_refresh_iii.md`
- `docs/plans/52_structured_empirical_harness_diffs.md`
- `docs/plans/53_benchmark_local_contract_hardening_iv.md`
- `.ac14_out/empirical_smoke_gate_repair8/smoke_readiness_report.json`
- `.ac14_out/empirical_smoke_gate_repair8/trial_1/paired_trial_report.json`

---

## Files Affected

- `.ac14_out/empirical_smoke_gate_repair9/` (create)
- `docs/plans/CLAUDE.md`
- `docs/TODO.md`
- `docs/AC14_NEXT_24_HOURS.md`
- `docs/UNCERTAINTIES.md`
- `docs/AC14_IMPLEMENTATION_STATUS.md`
- `KNOWLEDGE.md`

---

## Plan

### Steps

1. Run one bounded smoke gate against the post-52/post-53 lane.
2. Read the smoke verdict and paired-trial artifacts directly.
3. Update the active control docs to match that verdict.
4. Only unblock Plan #43 if the fresh smoke verdict says `ready_for_full_trials`.

---

## Required Tests

- the smoke artifact itself is the primary acceptance surface for this plan
- after the smoke run, rerun `python -m pytest -q`, `python -m mypy ac14 tests`, and `python -m ruff check ac14 tests` only if code/doc changes are needed before commit

---

## Acceptance Criteria

- [ ] A fresh bounded smoke artifact exists under `.ac14_out/empirical_smoke_gate_repair9/`.
- [ ] The verdict is one of `ready_for_full_trials`, `blocked_on_harness`, or `blocked_on_infrastructure`.
- [ ] The active control docs reflect that verdict exactly.
- [ ] Plan #43 is only unblocked if the fresh smoke artifact says `ready_for_full_trials`.

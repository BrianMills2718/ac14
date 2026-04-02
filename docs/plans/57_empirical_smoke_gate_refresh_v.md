# Plan #57: Empirical Smoke Gate Refresh V

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 55, 56
**Blocks:** 43

---

## Gap

**Current:** Repair9 stayed `blocked_on_harness`, but it also reduced the blocker set to a narrower shared benchmark-semantics problem plus one monolithic syntax-observability gap.

**Target:** Run one fresh bounded smoke paired trial against the post-55/post-56 lane and make one explicit gate decision:

1. `ready_for_full_trials` -> unblock Plan #43
2. `blocked_on_harness` -> freeze the next narrower blocker-clearing plan immediately
3. `blocked_on_infrastructure` -> keep the five-trial gate paused for infra reasons

**Why:** Plans #55 and #56 are only successful if the empirical gate artifact changes honestly.

---

## References Reviewed

- `docs/plans/54_empirical_smoke_gate_refresh_iv.md`
- `docs/plans/55_shared_benchmark_shipping_and_escalation_semantics_repair.md`
- `docs/plans/56_monolithic_syntax_and_failure_artifact_repair.md`
- `.ac14_out/empirical_smoke_gate_repair9/smoke_readiness_report.json`
- `.ac14_out/empirical_smoke_gate_repair9/trial_1/paired_trial_report.json`

---

## Files Affected

- `.ac14_out/empirical_smoke_gate_repair10/` (create)
- `docs/plans/CLAUDE.md`
- `docs/TODO.md`
- `docs/AC14_NEXT_24_HOURS.md`
- `docs/UNCERTAINTIES.md`
- `docs/AC14_IMPLEMENTATION_STATUS.md`
- `KNOWLEDGE.md`

---

## Plan

### Steps

1. Run one bounded smoke gate against the post-55/post-56 lane.
2. Read the smoke verdict and paired-trial artifacts directly.
3. Update the active control docs to match that verdict.
4. Only unblock Plan #43 if the fresh smoke verdict says `ready_for_full_trials`.

---

## Required Tests

- the smoke artifact itself is the primary acceptance surface for this plan
- after the smoke run, rerun `python -m pytest -q`, `python -m mypy ac14 tests`, and `python -m ruff check ac14 tests` only if code/doc changes are needed before commit

---

## Acceptance Criteria

- [x] A fresh bounded smoke artifact exists under `.ac14_out/empirical_smoke_gate_repair10/`.
- [x] The verdict is one of `ready_for_full_trials`, `blocked_on_harness`, or `blocked_on_infrastructure`.
- [x] The active control docs must be updated to reflect that verdict exactly.
- [x] Plan #43 remains blocked because the fresh smoke artifact says `blocked_on_harness`.

---

## Implementation Summary (2026-04-02)

Repair10 produced a real fresh smoke artifact and kept the empirical lane honest: the verdict remained `blocked_on_harness`, and `infrastructure_failure_detected` stayed `false`. The remaining blocker set narrowed again. Both conditions still disagreed with the benchmark on the shipping-only standard-customer path, where `factor_correlator` kept forcing `escalation_required=true`, and the monolithic lane still coupled shipping-only `high` priority to escalation. The smoke also exposed one remaining observability/stability gap: the AC14 lane still lost bounded attempts to `resolution_assembler` generation failures, and one monolithic invalid-module path still failed before full failed-source persistence. That is why Plans #58 and #59 are now the active repair chain before another bounded smoke rerun.

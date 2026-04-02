# Plan #70: Second-Gate Smoke Rerun

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 68, 69
**Blocks:** 66, 71

---

## Gap

**Current:** The clean second-gate smoke run is blocked on harness correctness.

**Target:** Rerun one bounded smoke trial after Plans #68 and #69 and let the
persisted verdict determine the next branch.

**Why:** The five-trial budget is only worth spending after the repaired harness
produces one honest smoke verdict.

---

## References Reviewed

- `docs/plans/68_deterministic_exact_match_semantic_review_policy.md`
- `docs/plans/69_monolithic_input_port_contract_validation.md`
- `.ac14_out/full_trials_gate_2_smoke/`

---

## Open Questions

### Q1: What branches are allowed after this rerun?
**Status:** Resolved
**Decision:**
- `ready_for_full_trials` -> Plan #66 immediately
- `blocked_on_harness` or `blocked_on_infrastructure` -> freeze a new diagnosis
  plan (`#71`) immediately

---

## Files Affected

- `.ac14_out/full_trials_gate_2_smoke_rerun/` (create)
- `docs/plans/70_second_gate_smoke_rerun.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)

---

## Plan

### Steps

1. Run one bounded paired smoke trial after Plans #68 and #69 land.
2. Read the readiness artifact and classify the result honestly.
3. If ready, activate Plan #66 immediately.
4. If blocked, freeze Plan #71 immediately and keep propagation lanes blocked.

---

## Required Tests

- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [ ] `.ac14_out/full_trials_gate_2_smoke_rerun/smoke_readiness_report.json` exists.
- [ ] The verdict is one of `ready_for_full_trials`, `blocked_on_harness`, or
  `blocked_on_infrastructure`.
- [ ] The active docs point to Plan #66 if ready, otherwise Plan #71.

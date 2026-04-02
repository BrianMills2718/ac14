# Plan #65: Second-Gate Smoke Run

**Status:** Planned
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 64
**Blocks:** 66, 67

---

## Gap

**Current:** The second empirical gate has no bounded smoke verdict on the new
benchmark.

**Target:** Run one bounded paired smoke trial on the new benchmark under the
runtime-first contract and persist an explicit readiness artifact.

**Why:** The five-trial budget should only be spent when the smoke artifact says
`ready_for_full_trials`.

---

## References Reviewed

- `docs/plans/63_runtime_first_comparison_contract.md`
- `docs/plans/64_second_gate_benchmark_bundle.md`
- `docs/plans/40_empirical_smoke_stabilization.md`
- `ac14/empirical_comparison.py`
- `.ac14_out/full_trials_gate_1/experiment_decision.json`

---

## Open Questions

### Q1: What counts as a completed smoke plan?
**Status:** Resolved
**Decision:** Any explicit persisted smoke verdict counts as plan completion.
The branch after this plan depends on the verdict:
- `ready_for_full_trials` -> Plan #66
- `blocked_on_harness` or `blocked_on_infrastructure` -> Plan #67

---

## Files Affected

- `.ac14_out/full_trials_gate_2_smoke/` (create)
- `docs/plans/65_second_gate_smoke.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)

---

## Plan

### Steps

1. Run the bounded smoke trial on the new benchmark.
2. Read the readiness artifact and classify the result honestly.
3. Update the active docs so the next numbered plan is explicit.
4. Commit the smoke artifact interpretation.

---

## Required Tests

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Keep the repo green before and after the smoke run |

---

## Acceptance Criteria

- [ ] `.ac14_out/full_trials_gate_2_smoke/smoke_readiness_report.json` exists.
- [ ] The smoke verdict is one of `ready_for_full_trials`, `blocked_on_harness`, or `blocked_on_infrastructure`.
- [ ] The active docs point to Plan #66 if ready, otherwise Plan #67.
- [ ] The verdict is described without hand-waving.

---

## Notes

This plan is about readiness, not victory. A blocked smoke result is still a
completed plan if it yields a truthful branch decision.

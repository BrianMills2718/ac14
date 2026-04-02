# Plan #55: Shared Benchmark Shipping And Escalation Semantics Repair

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 54
**Blocks:** 57

---

## Gap

**Current:** Repair9 stayed `blocked_on_harness`, but the fresh artifact narrowed the shared semantic failures across both conditions. The recurring blockers are no longer generic packet or recomposition failures; they are benchmark-local disagreements about shipping-delay materiality, correlator escalation semantics, and the compound inventory-risk band/reason mapping.

**Target:** State those benchmark-local rules explicitly enough that both the AC14 and monolithic conditions stop rediscovering them from sparse examples.

**Why:** The next smoke rerun should test the decomposition thesis, not whether the benchmark still leaves narrow business rules implicit.

---

## References Reviewed

- `docs/plans/54_empirical_smoke_gate_refresh_iv.md`
- `.ac14_out/empirical_smoke_gate_repair9/smoke_readiness_report.json`
- `.ac14_out/empirical_smoke_gate_repair9/trial_1/paired_trial_report.json`
- `.ac14_out/empirical_smoke_gate_repair9/trial_1/ac14/attempt_3/packet_test_report.json`
- `.ac14_out/empirical_smoke_gate_repair9/trial_1/ac14/attempt_3/recomposition_report.json`
- `.ac14_out/empirical_smoke_gate_repair9/trial_1/monolithic/attempt_3/packet_test_report.json`
- `benchmarks/order_exception_resolution/requirements.md`
- `benchmarks/order_exception_resolution/blueprint/components.yaml`
- `benchmarks/order_exception_resolution/blueprint/schemas.yaml`
- `benchmarks/order_exception_resolution/blueprint/fixtures.yaml`

---

## Files Affected

- `benchmarks/order_exception_resolution/requirements.md`
- `benchmarks/order_exception_resolution/blueprint/components.yaml`
- `benchmarks/order_exception_resolution/blueprint/schemas.yaml`
- `ac14/empirical_comparison.py`
- `tests/test_empirical_comparison.py`

---

## Plan

### Steps

1. State the shipping benchmark semantics explicitly:
   - shipping delay is a `shipping_delay` exception at `24+` hours
   - shipping risk is `high` at `24+` hours and severe at `48+` hours or `shipment_status == 'exception'`
   - a manual override does not change a low shipping-risk reason into an override-based reason
2. State correlator semantics explicitly:
   - shipping-only standard-customer cases route to `logistics` without forcing `escalation_required=True`
   - override presence changes blocker source and team ownership, but does not rewrite upstream shipping-risk rationale
3. State compound inventory semantics explicitly:
   - the compound case may still keep the inventory reason in the “partial fulfillment or back-order” family even when the band is `high`
4. Harden benchmark-local repair guidance and prompt-facing rules around those exact semantics.
5. Verify with targeted tests before the next smoke rerun.

---

## Required Tests

- `python -m pytest -q tests/test_empirical_comparison.py`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [x] The benchmark contract states the shared shipping/correlator/inventory semantics explicitly.
- [x] Empirical repair guidance names those semantics directly instead of relying on sparse fixture interpretation.
- [x] Targeted tests prove the new guidance/contract text exists.
- [x] Full `pytest`, `mypy`, and `ruff` pass.

---

## Implementation Summary (2026-04-02)

This lane hardened the benchmark contract where repair9 showed the remaining shared ambiguity. The requirements, schemas, and component constraints now state that shipping risk is already `high` at 24+ hours, that logistics routing does not automatically imply `escalation_required=true`, and that a moderate shortage with delayed replenishment may still be `high` risk while keeping the reason in the partial-fulfillment/back-order family. The empirical repair guidance now repeats those rules directly so both the AC14 and monolithic conditions receive the same sharper benchmark semantics.

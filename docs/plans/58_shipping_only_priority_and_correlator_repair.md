# Plan #58: Shipping-Only Priority And Correlator Repair

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 57
**Blocks:** 60

---

## Gap

**Current:** Repair10 proved that one shared shipping-only rule is still underspecified in a way that affects both conditions. ORX-101 should route to `logistics`, keep `escalation_required=false`, and still remain `priority_band='high'`.

**Target:** State that rule explicitly enough that both `factor_correlator` and `priority_scorer` stop coupling shipping-only priority to the escalation flag.

**Why:** The next smoke rerun should not keep burning attempts on the same shared shipping-only interpretation gap.

---

## References Reviewed

- `docs/plans/57_empirical_smoke_gate_refresh_v.md`
- `.ac14_out/empirical_smoke_gate_repair10/smoke_readiness_report.json`
- `.ac14_out/empirical_smoke_gate_repair10/trial_1/paired_trial_report.json`
- `.ac14_out/empirical_smoke_gate_repair10/trial_1/ac14/attempt_1/generated/factor_correlator.py`
- `.ac14_out/empirical_smoke_gate_repair10/trial_1/monolithic/attempt_1/generated/priority_scorer.py`
- `benchmarks/order_exception_resolution/requirements.md`
- `benchmarks/order_exception_resolution/blueprint/components.yaml`
- `benchmarks/order_exception_resolution/blueprint/schemas.yaml`

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

1. State explicitly that shipping-only standard-customer cases may route to logistics, keep `escalation_required=false`, and still score as `high` priority.
2. Tighten factor-correlator guidance so high shipping risk at 24+ does not silently force escalation.
3. Tighten priority-scorer guidance so shipping-delay `high` priority is not gated on `escalation_required=true`.
4. Verify the benchmark contract and guidance through targeted tests.

---

## Required Tests

- `python -m pytest -q tests/test_empirical_comparison.py`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [x] The benchmark contract states that shipping-only standard cases remain `high` priority even with `escalation_required=false`.
- [x] Empirical repair guidance names that rule directly for both correlator and priority scoring.
- [x] Targeted tests prove the new contract/guidance text exists.
- [x] Full `pytest`, `mypy`, and `ruff` pass.

---

## Implementation Summary (2026-04-02)

This lane made the remaining shipping-only rule explicit across every benchmark-facing surface that matters. The requirements now say directly that shipping-only standard-customer cases stay `priority_band='high'` even when `escalation_required=false`. The blueprint contract now repeats that rule in `priority_scorer` constraints and the `ResolutionPriority`/`ResolutionDigestEntry` schema descriptions. The empirical repair guidance now names the same rule at both the whole-condition and component-local levels, so both AC14 and monolithic generation stop coupling shipping-delay priority to escalation.

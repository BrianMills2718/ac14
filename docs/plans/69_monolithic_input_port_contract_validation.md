# Plan #69: Monolithic Input-Port Contract Validation

**Status:** Complete
**Type:** evaluation + code
**Priority:** Critical
**Blocked By:** 67
**Blocks:** 70

---

## Gap

**Current:** Monolithic generated modules can pass syntax/import validation and
still fail at runtime by reading nonexistent `inputs[...]` ports.

**Target:** Fail loud before runtime when a generated monolithic module uses a
literal input-port name that is not declared by that component.

**Why:** Invalid port names such as `on_compliance` should become precise
contract failures with persisted failed source, not noisy runtime surprises.

---

## References Reviewed

- `ac14/empirical_comparison.py`
- `.ac14_out/full_trials_gate_2_smoke/trial_1/monolithic/attempt_3/generated/decision_recorder.py`
- `.ac14_out/full_trials_gate_2_smoke/trial_1/monolithic/attempt_3/generated/execution_gate.py`
- `.ac14_out/full_trials_gate_2_smoke/trial_1/monolithic/attempt_3/generated/scaling_plan_builder.py`
- `benchmarks/resource_scaling/blueprint/components.yaml`

---

## Open Questions

### Q1: How much static validation is enough?
**Status:** Resolved
**Decision:** Catch literal `inputs['port']` and `inputs.get('port')` accesses
inside generated modules. Do not try to solve arbitrary dynamic aliasing in this
plan.

---

## Files Affected

- `ac14/empirical_comparison.py`
- `tests/test_empirical_comparison.py`
- `docs/UNCERTAINTIES.md`

---

## Plan

### Steps

1. Thread allowed input-port names into monolithic module validation.
2. Add AST-based detection for literal `inputs[...]` port references.
3. Fail loud with a clear contract error that names the unknown port and allowed
   ports.
4. Add a regression test that persists failed source and surfaces the contract
   error.

---

## Required Tests

- `python -m pytest -q tests/test_empirical_comparison.py -k 'port or monolithic'`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [ ] A monolithic module that reads an undeclared input port fails before
  runtime evaluation.
- [ ] The validation error names the unknown port and the affected component.
- [ ] Failed source is still persisted for direct review.

---

## Implementation Summary (2026-04-02)

Monolithic module validation now accepts the allowed input-port set for each
component and performs a bounded AST check for literal `inputs[...]` and
`inputs.get(...)` port references before import-time execution.

That means modules like the smoke-run `decision_recorder.py` that referenced the
nonexistent input port `on_compliance` now fail as precise contract errors
before runtime, while still persisting failed source and validation metadata for
direct review.

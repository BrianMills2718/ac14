# Plan #56: Monolithic Syntax And Failure Artifact Repair

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 54
**Blocks:** 57

---

## Gap

**Current:** Repair9 still lost one monolithic attempt to syntax-invalid Python, and the failure artifact did not preserve the invalid module source. The same condition also regressed on the shipping-only classifier path.

**Target:** Make the monolithic lane more observable and less lossy:

1. persist failed monolithic module source whenever validation rejects it
2. tighten monolithic guidance for shipping-only classifier logic and short direct decision-tree syntax
3. ensure future monolithic failures point to persisted source rather than only an exception string

**Why:** The empirical gate cannot be debugged honestly when one condition loses attempts to invisible invalid code.

---

## References Reviewed

- `.ac14_out/empirical_smoke_gate_repair9/trial_1/paired_trial_report.json`
- `.ac14_out/empirical_smoke_gate_repair9/trial_1/monolithic/attempt_2/attempt_report.json`
- `.ac14_out/empirical_smoke_gate_repair9/trial_1/monolithic/attempt_3/generated/exception_classifier.py`
- `prompts/generate_monolithic_system.yaml`
- `ac14/empirical_comparison.py`

---

## Files Affected

- `prompts/generate_monolithic_system.yaml`
- `ac14/empirical_comparison.py`
- `tests/test_empirical_comparison.py`

---

## Plan

### Steps

1. Persist raw monolithic module code when validation fails before the normal generated package is written.
2. Thread the failed-source path into the attempt artifact or failure summary.
3. Harden monolithic guidance around:
   - shipping-only `shipping_delay` classification at `24+` hours
   - short direct decision trees for categorical benchmark logic
   - no multiline or half-open expression patterns that waste attempts on syntax
4. Verify the new observability and prompt contract with targeted tests.

---

## Required Tests

- `python -m pytest -q tests/test_empirical_comparison.py tests/test_llm_codegen.py`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [x] Monolithic validation failures persist failed module source to disk.
- [x] Attempt artifacts or failure summaries point to that failed source.
- [x] Monolithic prompt/guidance explicitly names the shipping-only classifier rule and syntax-hardening rule.
- [x] Full `pytest`, `mypy`, and `ruff` pass.

---

## Implementation Summary (2026-04-02)

This lane moved monolithic invalid-Python failures out of the black box. `emit_monolithic_package_with_llm(...)` now persists `monolithic_response.json` before per-module validation, writes `<component>.failed.py` plus validation metadata when a module is invalid, and raises an error that points directly to the failed-source path. The monolithic prompt was also hardened to prefer one short explicit decision tree per categorical benchmark module, and tests now prove both the failed-source persistence and the prompt contract.

# Plan #53: Benchmark-Local Contract Hardening IV

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 51
**Blocks:** 54

---

## Gap

**Current:** The repair8 artifact proved that some benchmark-local expectations were still implicit instead of stated directly in prompts and benchmark contract text. The remaining misses were not broad system failures; they were local contract ambiguities.

**Target:** Harden the benchmark-local contract around:

1. `case_parser` note normalization and absent override-field omission
2. `inventory_risk_evaluator` high-risk rationale for the ORX-100 benchmark case
3. `priority_scorer` override-vs-compound branch separation and benchmark-local rationale values
4. ASCII-only code emission so the lane does not waste attempts on non-Python identifiers

**Why:** The empirical gate should not spend retries rediscovering benchmark-local rules that the benchmark can state explicitly.

---

## References Reviewed

- `.ac14_out/empirical_smoke_gate_repair8/trial_1/ac14/attempt_1/generated/resolution_assembler.failed.py`
- `.ac14_out/empirical_smoke_gate_repair8/trial_1/ac14/attempt_2/generated/case_parser.py`
- `.ac14_out/empirical_smoke_gate_repair8/trial_1/ac14/attempt_2/generated/inventory_risk_evaluator.py`
- `.ac14_out/empirical_smoke_gate_repair8/trial_1/ac14/attempt_2/generated/priority_scorer.py`
- `benchmarks/order_exception_resolution/blueprint/fixtures.yaml`
- `benchmarks/order_exception_resolution/requirements.md`

---

## Files Affected

- `prompts/generate_component.yaml`
- `prompts/generate_monolithic_system.yaml`
- `benchmarks/order_exception_resolution/blueprint/schemas.yaml`
- `benchmarks/order_exception_resolution/blueprint/components.yaml`
- `ac14/empirical_comparison.py`
- `tests/test_llm_codegen.py`
- `tests/test_empirical_comparison.py`

---

## Plan

### Steps

1. Make the prompt contract ban non-ASCII identifiers.
2. State the benchmark-local parser normalization and optional-field omission rules directly in the blueprint contract.
3. State the benchmark-local inventory and priority rationale rules directly in repair guidance.
4. Verify those rules through prompt/guidance tests before rerunning smoke.

---

## Required Tests

- `python -m pytest -q tests/test_empirical_comparison.py tests/test_llm_codegen.py`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [x] Component and monolithic prompts forbid non-ASCII identifiers.
- [x] Benchmark blueprint contract states the parser normalization and absent-override-field rules explicitly.
- [x] Benchmark-local repair guidance states the ORX-100 and priority-branch rules explicitly.
- [x] Targeted tests plus full `pytest`, `mypy`, and `ruff` pass.

---

## Implementation Summary (2026-04-02)

The prompts now require ASCII-only Python source. The benchmark blueprint now states that `normalized_notes` should be lowercased with at most one trailing sentence period removed, and that absent override fields should be omitted rather than synthesized. The benchmark-local repair guidance now explicitly names the ORX-100 inventory-risk rationale and the distinction between override and compound priority branches.

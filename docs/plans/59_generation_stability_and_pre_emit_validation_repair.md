# Plan #59: Generation Stability And Pre-Emit Validation Repair

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 57
**Blocks:** 60

---

## Gap

**Current:** Repair10 exposed two generation-stability gaps:

1. the monolithic lane still has one validation path that can fail before invalid source is persisted
2. the AC14 lane still loses attempts to `resolution_assembler` generation failures such as missing `build_component()` and non-ASCII corruption

**Target:** Make both failure sites more observable and less likely.

**Why:** The empirical gate cannot stabilize if bounded attempts are still wasted on invisible or recurring generation-contract failures.

---

## References Reviewed

- `docs/plans/57_empirical_smoke_gate_refresh_v.md`
- `.ac14_out/empirical_smoke_gate_repair10/trial_1/paired_trial_report.json`
- `.ac14_out/empirical_smoke_gate_repair10/trial_1/monolithic/attempt_3/attempt_report.json`
- `.ac14_out/empirical_smoke_gate_repair10/trial_1/ac14/attempt_2/generated/resolution_assembler.failed.py`
- `.ac14_out/empirical_smoke_gate_repair10/trial_1/ac14/attempt_3/generated/resolution_assembler.failed.py`
- `ac14/empirical_comparison.py`
- `prompts/generate_component.yaml`
- `prompts/generate_monolithic_system.yaml`

---

## Files Affected

- `ac14/empirical_comparison.py`
- `prompts/generate_component.yaml`
- `tests/test_empirical_comparison.py`
- `tests/test_llm_codegen.py`

---

## Plan

### Steps

1. Move monolithic module validation responsibility fully into the emission path so every invalid module can be persisted before failure.
2. Ensure the attempt artifact or failure summary points to the persisted failed-source path for that remaining failure site too.
3. Harden `resolution_assembler` guidance/prompt rules around:
   - always ending with `build_component()`
   - no unfinished trailing comments or prose
   - ASCII-only list-update logic using ordinary Python operations
4. Verify the new observability and prompt contract with targeted tests.

---

## Required Tests

- `python -m pytest -q tests/test_empirical_comparison.py tests/test_llm_codegen.py`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [x] Monolithic invalid-source persistence covers the pre-emit validation path too.
- [x] Attempt artifacts or failure summaries point to the persisted source for that path.
- [x] `resolution_assembler` guidance/prompt explicitly names the current generation-stability failures.
- [x] Full `pytest`, `mypy`, and `ruff` pass.

---

## Implementation Summary (2026-04-02)

This lane moved the remaining monolithic invalid-module rejection out of the pre-emit black box and tightened the AC14 component contract around the real `resolution_assembler` failures from repair10. `agenerate_monolithic_system_with_llm(...)` now returns structured module responses without pre-validating module source, so `emit_monolithic_package_with_llm(...)` is the single place that validates and persists failed monolithic modules. The shared component prompt and empirical component guidance now say directly that generated modules must end with a real `build_component()` function, must not stop at trailing prose or half-finished code, and must use ordinary ASCII Python operations for digest-store updates. Both the empirical validator and the shared LLM codegen validator now fail loud on non-ASCII source with a direct contract error.

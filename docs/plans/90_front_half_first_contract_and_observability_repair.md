# Plan #90: Front-Half-First Contract And Observability Repair

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 89
**Blocks:** 91

---

## Gap

**Current:** The first front-half-first smoke artifact is real, but it is
blocked for two concrete reasons:

1. AC14 structured-spec planning emits invalid bindings before front-half
   acceptance can complete.
2. The monolithic runtime prompt still allows a nested source-port input
   contract that disagrees with the benchmark runner.

**Target:** Repair both contract surfaces and persist better failed-front-half
diagnostics before the next smoke rerun.

**Why:** The next smoke rerun should test the repaired front-half-first contract,
not repeat the same planning and raw-input mistakes with low observability.

---

## Acceptance Criteria

- [x] Invalid structured-spec draft-plan responses persist reviewable failed-plan
      diagnostics before the attempt exits.
- [x] Structured-spec planning gets one bounded validation-repair loop for
      binding errors instead of failing immediately on the first invalid plan.
- [x] The monolithic runtime contract makes `run_case(record)` consume the raw
      benchmark record directly and rejects the nested source-port mistake.
- [x] Targeted tests cover the new diagnostics and contract repair surfaces.

---

## Files Affected

- `ac14/blueprint_planning.py`
- `ac14/front_half_acceptance.py`
- `ac14/front_half_first_empirical.py`
- `prompts/draft_blueprint_plan_from_structured_spec.yaml`
- `prompts/generate_monolithic_runtime_system_from_structured_spec.yaml`
- `tests/test_blueprint_planning.py`
- `tests/test_front_half_first_empirical.py`
- `tests/test_cli.py`
- `tests/test_make_targets.py`
- `docs/TODO.md`
- `docs/AC14_NEXT_24_HOURS.md`
- `docs/plans/CLAUDE.md`

---

## Plan

### Steps

1. Persist invalid structured-spec draft-plan responses and validation errors
   when `_validate_draft_blueprint_plan()` rejects them.
2. Add one bounded repair retry for structured-spec planning driven by the
   binding-validation error.
3. Harden the monolithic front-half-first prompt/contract so `run_case(record)`
   uses the benchmark record directly and repair guidance reinforces that.
4. Add a direct guardrail so the monolithic condition fails with a clearer
   contract error before repeated empty-output runtime attempts.
5. Verify the repaired lane before rerunning the smoke gate.

---

## Required Tests

| Command | Why |
|---------|-----|
| `python -m pytest -q tests/test_blueprint_planning.py tests/test_front_half_first_empirical.py tests/test_cli.py tests/test_make_targets.py` | Proves the repaired contract and diagnostics surfaces |
| `python -m mypy ac14 tests` | Keeps the new diagnostics typed |
| `python -m ruff check ac14 tests` | Keeps the lane lint-clean |

---

## Notes

This plan does not spend the smoke budget again. It repairs the exact blocker
surfaces identified by Plan #89 so Plan #91 can rerun the smoke gate honestly.

## Implementation Summary

- Structured-spec planning now persists one invalid plan payload plus one
  validation-diagnostics artifact for each rejected attempt.
- Structured-spec planning now gets one bounded retry only when the first
  validator failure is a retryable binding-reference error.
- The structured-spec planning prompt now states binding-validity rules
  explicitly and receives the previous invalid plan plus validator error on the
  bounded retry.
- Monolithic front-half-first generation now persists failed runtime-module
  source and validation metadata when the raw-record contract is violated.
- The monolithic prompt now states the raw-record contract explicitly and sees a
  sample runtime record plus the top-level source port name.
- Verification landed on:
  - `python -m pytest -q tests/test_blueprint_planning.py tests/test_front_half_first_empirical.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m pytest -q`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`

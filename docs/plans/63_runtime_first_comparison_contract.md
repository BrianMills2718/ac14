# Plan #63: Runtime-First Comparison Contract

**Status:** Complete
**Type:** evaluation + benchmark design
**Priority:** Critical
**Blocked By:** None
**Blocks:** 64, 37

---

## Gap

**Current:** The first monolithic-vs-AC14 benchmark completed and returned
`inconclusive`. Plan #62 showed that packet-level failures dominated the
verdict even when final runtime outputs were often correct.

**Target:** Freeze the next empirical contract so final runtime output
correctness is the primary success gate, while packet-level tests remain
explicit secondary diagnostic evidence, and split the next 24-hour execution
chain into explicit numbered plans.

**Why:** The project needs the next empirical gate to measure the thesis more
cleanly: does decomposition produce systems with more correct final outputs,
not merely fewer intermediate packet mismatches.

---

## Open Questions

### Q1: Should packet tests remain part of the comparison?
**Status:** Resolved
**Decision:** Yes, but as explicit diagnostic evidence rather than the primary
trial-success gate.

### Q2: Should the first benchmark be discarded?
**Status:** Resolved
**Decision:** No. Keep `order_exception_resolution` as the first completed data
point. The next gate should use a harder benchmark alongside the cleaner
runtime-primary criterion.

### Q3: Should the next lane remain one overloaded plan?
**Status:** Resolved
**Decision:** No. The next 24-hour chain should be explicit as:

1. Plan #64: harder benchmark bundle
2. Plan #65: bounded smoke gate on that bundle
3. Plan #66: full five-trial gate if smoke is `ready_for_full_trials`
4. Plan #67: blocker diagnosis and next repair plan if smoke is blocked

---

## Files Affected

- `ac14/empirical_comparison.py` (modify — runtime-primary success criterion)
- `tests/test_empirical_comparison.py` (modify)
- `docs/plans/63_runtime_first_comparison_contract.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `CLAUDE.md` (modify)

---

## Plan

### Steps

1. Redefine the empirical success criterion around final runtime output correctness.
2. Preserve packet/recomposition reports as explicit diagnostic artifacts.
3. Freeze the next 24-hour empirical chain as separate numbered plans.
4. Lock the active docs so another agent can continue without chat history.

---

## Required Tests

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q tests/test_empirical_comparison.py` | Runtime-first contract tests pass |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type safety |
| `python -m ruff check ac14 tests` | Lint and import hygiene |

---

## Acceptance Criteria

- [x] The trial success criterion uses runtime output correctness as the
  primary gate.
- [x] Packet test results are logged but do not determine trial pass/fail.
- [x] Full local verification passes (`244 passed`, mypy, ruff all clean).
- [x] The next execution chain is explicit as separate numbered plans rather
  than one overloaded plan.
- [x] The active docs are updated to point at the new chain.

---

## Implementation Summary (2026-04-02)

What landed:

- `ac14/empirical_comparison.py` now treats packet tests and recomposition as
  diagnostic artifacts rather than primary trial-success gates
- `tests/test_empirical_comparison.py` now proves that runtime-correct attempts
  can pass even when packet tests fail, while still persisting packet reports
- the next empirical lane is now split cleanly into Plans #64–#67 instead of
  remaining implicit inside one oversized plan

Verification:

- `python -m pytest -q tests/test_empirical_comparison.py`
- `python -m pytest -q` -> `244 passed`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Notes

This plan freezes the measurement contract. It does not itself build the harder
benchmark or spend the next smoke/full-trial budget.

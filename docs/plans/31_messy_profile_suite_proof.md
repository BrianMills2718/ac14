# Plan #31: Messy-Profile Suite Proof

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** 30
**Blocks:** 32

---

## Gap

**Current:** AC14 can prove one bounded messy-input lane per example, and after
Plan #30 it can make profile selection explicit across surfaces, but the suite
story still does not explicitly prove how an alternate messy profile behaves
without redefining the clean default proof path.

**Target:** AC14 should prove one explicit suite-level messy-profile lane across
front-half and realistic-input acceptance surfaces, preserving the clean
default profile as the default proof path while making missing-profile states
reviewable.

**Why:** The next honest generality step is not to silently switch the default
input asset. It is to show that alternate realistic-input profiles can be
requested explicitly, executed explicitly where available, and reported
explicitly where absent.

---

## References Reviewed

- `CLAUDE.md` - active proof-expansion and continuation rules
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current messy-input scope and remaining gap
- `docs/plans/30_profile_aware_realistic_input_parity.md` - profile-aware suite prerequisite
- `ac14/front_half_acceptance.py` - front-half suite reporting
- `ac14/acceptance.py` - realistic-input suite reporting

---

## Open Questions

### Q1: Should the first messy-profile suite proof include `llm` mode?
**Status:** Resolved
**Why it matters:** The plan should strengthen the non-deterministic proof story honestly without broadening into live readiness.
**Decision:** Yes, but keep it bounded and fixture-backed, mirroring the single-example messy-input `llm` lane.

### Q2: What should count as success when only one example currently ships a messy profile?
**Status:** Resolved
**Why it matters:** The suite artifact must stay truthful about coverage.
**Decision:** Success is explicit `included`/`missing_profile` accounting, not pretending broad messy-profile coverage exists today.

---

## Files Affected

- `tests/test_front_half_acceptance.py` (modify)
- `tests/test_acceptance.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Prove one explicit front-half suite run on the `messy` realistic-input profile and persist included-vs-missing-profile counts.
2. Prove one explicit realistic-input suite run on the same `messy` profile across `reference`, `deterministic`, and bounded fixture-backed `llm`.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_suite_report_supports_messy_profile` | Front-half suite can run the explicit `messy` profile and records missing-profile states |
| `tests/test_acceptance.py` | `test_build_realistic_suite_acceptance_report_supports_messy_profile` | Realistic-input suite can run the explicit `messy` profile across bounded modes and records missing-profile states |
| `tests/test_cli.py` | `test_cli_acceptance_review_realistic_suite_supports_messy_profile` | CLI realistic suite supports the explicit `messy` profile |
| `tests/test_make_targets.py` | `test_make_acceptance_review_realistic_suite_supports_messy_profile` | Make realistic suite supports the explicit `messy` profile |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] AC14 can run one explicit suite-level `messy` profile lane on the front-half surface.
- [x] AC14 can run one explicit suite-level `messy` profile lane on the realistic-input final-gate surface across bounded modes.
- [x] The suite artifacts record `included` versus `missing_profile` explicitly and preserve the clean default path as the default proof story.
- [x] Full local verification passes and the docs match the lane.

## Verification

- Targeted messy-profile suite verification passed:
  - `python -m pytest -q tests/test_acceptance.py::test_build_realistic_suite_acceptance_report_supports_messy_profile_llm_mode tests/test_cli.py::test_cli_acceptance_review_realistic_suite_supports_messy_profile_llm_mode tests/test_make_targets.py::test_make_acceptance_review_realistic_suite_supports_messy_profile_llm_mode`
  - `python -m mypy tests/test_acceptance.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m ruff check tests/test_acceptance.py tests/test_cli.py tests/test_make_targets.py`

## Outcome

AC14 now has an explicit suite-level `messy` profile proof that keeps the clean
default path unchanged, records `missing_profile` explicitly for the examples
that do not ship that profile, and extends the realistic-input suite proof
across `reference`, `deterministic`, and bounded fixture-backed `llm`.

---

## Notes

This plan is about explicit alternate-profile proof, not about claiming broad
messy-profile coverage across the whole shipped suite.

# Plan #30: Profile-Aware Realistic-Input Parity

**Status:** Planned
**Type:** implementation
**Priority:** High
**Blocked By:** 29
**Blocks:** 31

---

## Gap

**Current:** AC14 can define explicit realistic-input policy after Plan #29,
but front-half acceptance, final-gate acceptance, and suite/default surfaces do
not yet all consume the same profile-aware resolver.

**Target:** AC14 should make front-half acceptance, final-gate acceptance, and
their suite/default discovery surfaces consume the same profile-aware
realistic-input resolver, with explicit profile fields persisted on the
artifacts.

**Why:** The proof story stays coherent only if every realistic-input surface
uses the same explicit selection policy and records which profile was actually
executed.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and explicit realistic-input policy chain
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current cross-surface parity gap
- `docs/plans/29_explicit_realistic_input_policy.md` - shared manifest and resolver prerequisite
- `ac14/acceptance.py` - final-gate realistic-input execution and suite reporting
- `ac14/front_half_acceptance.py` - front-half realistic-input execution and suite reporting
- `ac14/__main__.py` - CLI surface for realistic-input commands
- `Makefile` - operator-facing realistic-input targets

---

## Open Questions

### Q1: Should profile selection be optional or required on CLI/Make surfaces?
**Status:** Resolved
**Why it matters:** The default proof path should stay easy to run, but explicit alternate profiles must remain available.
**Decision:** Keep profile selection optional with `default` as the explicit fallback from the manifest.

### Q2: What should suite artifacts do when a requested profile is absent for one example?
**Status:** Resolved
**Why it matters:** Suite breadth should not silently skip examples or silently switch profiles.
**Decision:** Persist explicit per-example `missing_profile` states and aggregate counts instead of skipping or falling back.

---

## Files Affected

- `ac14/acceptance.py` (modify)
- `ac14/front_half_acceptance.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_acceptance.py` (modify)
- `tests/test_front_half_acceptance.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)

---

## Plan

### Steps

1. Thread an optional realistic-input profile through front-half and final-gate per-example execution.
2. Thread the same profile through suite/default discovery and persist explicit per-example profile or missing-profile state.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_suite_report_supports_realistic_input_profile_selection` | Front-half suite uses the shared profile-aware resolver and records missing-profile states explicitly |
| `tests/test_acceptance.py` | `test_build_realistic_suite_acceptance_report_supports_realistic_input_profile_selection` | Final-gate realistic suite uses the same shared profile-aware resolver and records missing-profile states explicitly |
| `tests/test_cli.py` | `test_cli_front_half_acceptance_suite_supports_realistic_input_profile_selection` | CLI front-half suite supports profile selection |
| `tests/test_cli.py` | `test_cli_acceptance_review_realistic_suite_supports_profile_selection` | CLI realistic suite supports profile selection |
| `tests/test_make_targets.py` | `test_make_front_half_acceptance_suite_supports_realistic_input_profile_selection` | Make front-half suite supports profile selection |
| `tests/test_make_targets.py` | `test_make_acceptance_review_realistic_suite_supports_profile_selection` | Make realistic suite supports profile selection |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [ ] Front-half and final-gate realistic-input surfaces consume the same shared profile-aware resolver.
- [ ] Suite/default artifacts persist explicit selected-profile or missing-profile state.
- [ ] CLI and Make surfaces expose profile selection without changing the clean default path.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

This plan is about cross-surface parity and explicit artifact state, not yet
about broader alternate-profile proof claims.

# Plan #24: Front-Half Retry Suite Breadth

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** Single-example front-half acceptance can now include one explicit
retry chain, but the suite-level front-half breadth artifact still only reports
the initial freeze result per example.

**Target:** AC14 should let the suite-level front-half artifact optionally run
retry-aware front-half acceptance across shipped realistic-input examples and
aggregate retry outcomes explicitly.

**Why:** Once the single-example retry contract is stable, the next honest
breadth step is to expose retry-aware front-half evidence across the shipped
suite.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and current proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 front-half strengthening direction
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current front-half retry breadth status
- `docs/plans/23_front_half_retry_integration.md` - just-completed single-example retry lane
- `ac14/front_half_acceptance.py` - current suite-level front-half breadth artifact

---

## Open Questions

### Q1: Should suite retry breadth be opt-in?
**Status:** Resolved
**Why it matters:** The first breadth lane should remain explicit and conservative.
**Decision:** Yes. Keep retry breadth behind an explicit flag.

### Q2: What retry data should the suite aggregate?
**Status:** Resolved
**Why it matters:** Breadth should summarize retry outcomes without hiding
per-example paths.
**Decision:** Aggregate retry-attempted and retry-approved counts while
preserving per-example retry artifact paths.

---

## Files Affected

- `ac14/front_half_acceptance.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_front_half_acceptance.py` (modify)
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

1. Pre-make retry breadth as an explicit optional extension to suite-level front-half acceptance.
2. Thread retry-aware front-half acceptance through the suite runner and aggregate retry counts.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_suite_report_supports_retry_freeze` | Suite-level front-half breadth can aggregate retry-aware results |
| `tests/test_cli.py` | `test_cli_front_half_acceptance_suite_supports_retry_freeze` | CLI suite front-half acceptance supports retry breadth |
| `tests/test_make_targets.py` | `test_make_front_half_acceptance_suite_supports_retry_freeze` | Make suite front-half acceptance supports retry breadth |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] AC14 can optionally run retry-aware front-half acceptance across the shipped suite.
- [x] The suite artifact aggregates retry counts and preserves per-example retry artifact paths.
- [x] The lane stays explicit and opt-in.
- [x] Full local verification passes and the docs match the lane.

## Verification

- Targeted retry-aware suite verification passed:
  - `python -m pytest -q tests/test_front_half_acceptance.py::test_build_front_half_acceptance_suite_report_supports_retry_freeze tests/test_cli.py::test_cli_front_half_acceptance_suite_supports_retry_freeze tests/test_make_targets.py::test_make_front_half_acceptance_suite_supports_retry_freeze`
  - `python -m mypy ac14/front_half_acceptance.py ac14/__main__.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m ruff check ac14/front_half_acceptance.py ac14/__main__.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py`

## Outcome

AC14 can now opt into retry-aware front-half breadth across the shipped suite,
aggregate retry-attempted and retry-approved counts, and preserve per-example
retry artifact paths instead of collapsing retry evidence into a single claim.

---

## Notes

This lane is about explicit retry breadth across the shipped suite, not broad automatic healing.

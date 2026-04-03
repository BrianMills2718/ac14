# Plan #84: Structured-Spec Front-Half Acceptance

**Status:** In Progress
**Type:** implementation
**Priority:** Critical
**Blocked By:** 83
**Blocks:** 85

---

## Gap

**Current:** AC14 can now prepare a bounded structured-spec artifact and build a
draft blueprint plan from it, but that contract still stops before draft bundle
authoring, freeze decision, and front-half semantic review.

**Target:** Add one persisted front-half acceptance artifact for
structured-spec-driven drafting through freeze decision and review.

**Why:** The new front-half-first empirical direction needs more than a planning
artifact. It needs one truthful end-to-end front-half lane from structured-spec
input through freeze.

---

## References Reviewed

- `docs/plans/83_structured_spec_input_contract.md`
- `ac14/front_half_acceptance.py`
- `ac14/blueprint_planning.py`
- `ac14/draft_authoring.py`
- `ac14/freeze_decision.py`
- `prompts/review_front_half_acceptance.yaml`

---

## Open Questions

### Q1: Should this lane reuse the existing realistic-input front-half artifact shape?
**Status:** Resolved
**Why it matters:** Reuse keeps the story surface comparable across front-half input types.
**Resolution:** Yes, but add a parallel structured-spec artifact path and
source-kind fields instead of pretending discovery ran.

### Q2: Should dependency planning/probing be forced into the first structured-spec front-half lane?
**Status:** Resolved
**Why it matters:** Forcing more moving parts into the first lane would expand scope faster than evidence.
**Resolution:** No. The first structured-spec front-half lane should stay
bounded: structured spec -> draft plan -> draft bundle -> freeze -> review.

---

## Files Affected

- `docs/plans/84_structured_spec_front_half_acceptance.md` (create)
- `ac14/front_half_acceptance.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `prompts/review_structured_spec_front_half_acceptance.yaml` (create or modify prompt surface)
- `tests/test_front_half_acceptance.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/plans/CLAUDE.md` (modify)

---

## Plan

### Steps

1. Add a structured-spec front-half acceptance path that starts from the new
   artifact instead of discovery.
2. Reuse the existing draft authoring and freeze surfaces.
3. Persist a structured semantic review of the front-half result.
4. Verify with targeted tests, then type/lint checks.

---

## Required Tests

| Command | Why |
|---------|-----|
| `python -m pytest -q tests/test_front_half_acceptance.py::test_build_structured_spec_front_half_acceptance_report_runs_end_to_end tests/test_cli.py::test_cli_structured_spec_front_half_acceptance tests/test_make_targets.py::test_make_structured_spec_front_half_acceptance_runs_end_to_end` | Proves the new front-half lane end to end |
| `python -m mypy ac14 tests` | Keep the new lane type-clean |
| `python -m ruff check ac14 tests` | Keep the new lane lint-clean |

---

## Acceptance Criteria

- [ ] AC14 persists one structured-spec front-half acceptance artifact.
- [ ] The artifact proves structured spec -> draft plan -> draft bundle ->
      freeze decision -> semantic review.
- [ ] The lane stays bounded and does not claim broad NL-to-blueprint support.

---

## Notes

This lane is the first real consumer of Plan #83.

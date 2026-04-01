# Plan #33: Directory Front-Half Acceptance Proof

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** 32
**Blocks:** None

---

## Gap

**Current:** AC14 can now inspect a bounded input directory, inventory
structured candidates, and persist one explicit primary structured candidate.
But the front-half acceptance lane has only been proven on single-file inputs.

**Target:** AC14 should prove one full front-half acceptance lane on a
directory input bundle, preserving the directory input path plus the chosen
primary structured candidate all the way through discovery, draft planning, and
freeze review artifacts.

**Why:** Directory discovery is only thesis-preserving if the next planning
surface can consume it without collapsing back into hidden single-file
assumptions.

---

## References Reviewed

- `CLAUDE.md` - continuation rule and active proof-expansion rule
- `docs/AC14_NEXT_24_HOURS.md` - active tactical lane
- `docs/plans/32_multi_artifact_discovery_inputs.md` - completed predecessor
- `ac14/front_half_acceptance.py` - current front-half artifact chain
- `ac14/discovery.py` - directory-input discovery contract
- `tests/test_front_half_acceptance.py` - current front-half proof coverage

---

## Open Questions

### Q1: Should directory front-half acceptance plan across every structured file in the directory?
**Status:** Resolved
**Why it matters:** Hidden multi-file planning would overclaim what Plan #32 actually implemented.
**Decision:** No. Preserve the directory as the reviewed input surface, but keep one explicit primary structured candidate as the planning input inside the discovery artifact.

### Q2: Does the front-half acceptance artifact itself need new top-level fields for directory proof?
**Status:** Resolved
**Why it matters:** Redundant fields would create another drift surface if the discovery artifact already carries the truth.
**Decision:** No. Keep the top-level front-half artifact stable and prove directory support by asserting the persisted discovery artifact now carries `input_path`, `primary_input_path`, `structured_candidate_paths`, and `supporting_context_paths` truthfully.

---

## Files Affected

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

1. Add one direct front-half acceptance test for a bounded directory input with
   multiple structured candidates plus supporting local context.
2. Add CLI and Make parity tests for the same directory-input front-half lane.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_report_supports_input_directory` | Front-half acceptance can start from a directory input and preserve explicit primary-candidate discovery evidence |
| `tests/test_cli.py` | `test_cli_front_half_acceptance_supports_input_directory` | CLI front-half acceptance supports a directory input without hiding which structured candidate became primary |
| `tests/test_make_targets.py` | `test_make_front_half_acceptance_supports_input_directory` | Make front-half acceptance preserves the same reviewable directory-input story |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] Front-half acceptance supports a directory input as the reviewed input surface.
- [x] The persisted discovery artifact keeps the directory input path plus explicit primary and alternate structured candidates.
- [x] CLI and Make front-half surfaces preserve the same directory-input story.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

This plan proves that bounded directory discovery is not just a raw inspection
feature. It becomes part of the same discovery-through-freeze front-half chain
without introducing hidden multi-file orchestration.

## Outcome

Implemented and verified:

1. front-half acceptance now has one direct proof lane starting from a bounded
   directory input bundle
2. the persisted discovery artifact inside that lane keeps the directory input
   path plus explicit primary and alternate structured candidates
3. CLI and Make front-half surfaces preserve the same reviewable story

## Verification

- `python -m pytest -q tests/test_front_half_acceptance.py::test_build_front_half_acceptance_report_supports_input_directory tests/test_cli.py::test_cli_front_half_acceptance_supports_input_directory tests/test_make_targets.py::test_make_front_half_acceptance_supports_input_directory`
  passed with `3 passed`
- `python -m mypy tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py`
  passed
- `python -m ruff check tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py`
  passed
- `python -m pytest -q` passed with `203 passed`
- `python -m mypy ac14 tests` passed on `65` source files
- `python -m ruff check ac14 tests` passed

# Plan #32: Multi-Artifact Discovery Inputs

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** 31
**Blocks:** None

---

## Gap

**Current:** AC14 discovery is still centered on one input path at a time,
even though real projects often require looking across a directory of related
structured files and local context artifacts before planning a blueprint.

**Target:** AC14 should accept one input directory as a reviewable discovery
surface, inventory supported structured candidates and local context files,
select a primary structured candidate explicitly, and persist that decision in
the discovery artifact.

**Why:** The next honest front-half strengthening step is broader discovery
context, not another proof-side artifact. Real blueprint derivation often
needs more than one file.

---

## References Reviewed

- `CLAUDE.md` - current continuation rules and front-half focus
- `docs/AC14_IMPLEMENTATION_STATUS.md` - discovery remains narrower than the thesis
- `docs/AC14_ROADMAP.md` - Horizon 2 front-half strengthening direction
- `ac14/discovery.py` - current single-input discovery contract
- `ac14/structured_inputs.py` - current supported structured-input formats

---

## Open Questions

### Q1: Should the first multi-artifact lane plan across every file in a directory?
**Status:** Resolved
**Why it matters:** Broad directory ingestion can become hidden orchestration or accidental overreach.
**Decision:** No. Inventory supported candidates, pick one primary structured candidate explicitly, and persist the rest as supporting context.

### Q2: How should the primary candidate be chosen?
**Status:** Resolved
**Why it matters:** Hidden heuristics would recreate the same ambiguity AC14 just removed in realistic-input selection.
**Decision:** Use deterministic ranking plus explicit persistence of the chosen primary candidate and the alternative candidates.

---

## Files Affected

- `ac14/discovery.py` (modify)
- `ac14/structured_inputs.py` (modify)
- `tests/test_discovery.py` (modify)
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

1. Extend discovery so an input directory can be inventoried as one reviewable unit with structured candidates and supporting local context files.
2. Persist the chosen primary structured candidate plus the alternative candidates explicitly in the discovery artifact.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_discovery.py` | `test_build_discovery_artifact_supports_input_directory_with_primary_candidate` | Discovery can inventory a directory, choose one primary structured candidate, and persist alternatives explicitly |
| `tests/test_cli.py` | `test_cli_discover_input_supports_input_directory` | CLI discovery supports a directory input without hiding which file became primary |
| `tests/test_make_targets.py` | `test_make_discover_input_supports_input_directory` | Make discovery supports a directory input and persists the same explicit primary/alternate story |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] AC14 discovery accepts a directory input and inventories supported structured candidates explicitly.
- [x] The discovery artifact persists one explicit primary structured candidate plus explicit alternatives.
- [x] CLI and Make discovery surfaces preserve the same reviewable story.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

This plan strengthens the front half by broadening discovery context in a
bounded, reviewable way. It is not broad automatic multi-file planning yet.

## Outcome

Implemented and verified:

1. discovery now accepts a directory input as one bounded reviewable unit
2. discovery inventories supported structured candidates and supporting local
   context files explicitly
3. discovery chooses one primary structured candidate deterministically and
   persists both the chosen primary candidate and the alternatives
4. CLI and Make discovery surfaces preserve the same explicit story

## Verification

- `python -m pytest -q tests/test_discovery.py::test_build_discovery_artifact_supports_input_directory_with_primary_candidate tests/test_cli.py::test_cli_discover_input_supports_input_directory tests/test_make_targets.py::test_make_discover_input_supports_input_directory`
  passed with `3 passed`
- `python -m mypy ac14/discovery.py tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py`
  passed
- `python -m ruff check ac14/discovery.py tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py`
  passed
- `python -m pytest -q` passed with `200 passed`
- `python -m mypy ac14 tests` passed on `65` source files
- `python -m ruff check ac14 tests` passed

# Plan #34: Directory Context Summaries

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** 33
**Blocks:** None

---

## Gap

**Current:** AC14 can now inspect a directory input, inventory structured
candidates and supporting local context files, and carry that explicit story
through front-half acceptance. But follow-on planning still gets only file
paths for the alternate structured candidates and supporting context files.

**Target:** AC14 should persist bounded summaries for alternate structured
candidates and supporting local context files in the discovery artifact, while
keeping one explicit primary structured planning input.

**Why:** Directory discovery is stronger when planners can review a compact,
bounded content summary of the surrounding input set instead of only filenames.

---

## References Reviewed

- `CLAUDE.md` - continuation rule and bounded-context thesis
- `docs/AC14_IMPLEMENTATION_STATUS.md` - discovery remains weak on messy multi-artifact synthesis
- `docs/plans/32_multi_artifact_discovery_inputs.md` - explicit directory inventory predecessor
- `docs/plans/33_directory_front_half_acceptance_proof.md` - end-to-end directory front-half proof
- `ac14/discovery.py` - current directory-input artifact shape
- `ac14/structured_inputs.py` - current structured-input formats and summaries

---

## Open Questions

### Q1: Should AC14 fully inspect every alternate structured candidate?
**Status:** Resolved
**Why it matters:** Full multi-file inspection could become hidden orchestration or large prompt payloads.
**Decision:** No. Persist bounded summaries only for alternate candidates and supporting context files, while preserving one explicit primary structured planning input.

### Q2: What level of detail should supporting context summaries carry?
**Status:** Resolved
**Why it matters:** Too little detail is useless; too much detail recreates the context-bloat problem AC14 is trying to solve.
**Decision:** Persist compact previews and basic metadata only, with explicit truncation when needed.

---

## Files Affected

- `ac14/discovery.py` (modify)
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

1. Extend directory discovery so alternate structured candidates carry bounded
   compact summaries instead of only file paths.
2. Extend directory discovery so supporting local context files carry compact
   preview metadata instead of only file paths.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_discovery.py` | `test_build_discovery_artifact_persists_directory_context_summaries` | Directory discovery persists bounded summaries for alternate structured candidates and supporting local context files |
| `tests/test_cli.py` | `test_cli_discover_input_persists_directory_context_summaries` | CLI directory discovery preserves the same compact summary story |
| `tests/test_make_targets.py` | `test_make_discover_input_persists_directory_context_summaries` | Make directory discovery preserves the same compact summary story |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] Directory discovery persists bounded summaries for alternate structured candidates.
- [x] Directory discovery persists bounded summaries for supporting local context files.
- [x] CLI and Make discovery surfaces preserve the same explicit compact-summary story.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

This plan strengthens the front half without changing the core single-primary
planning rule. One structured candidate remains primary; the rest become
bounded context, not hidden orchestration.

## Outcome

Implemented and verified:

1. directory discovery now persists bounded summaries for alternate structured
   candidates
2. directory discovery now persists bounded summaries for supporting local
   context files
3. CLI and Make discovery surfaces preserve the same compact-summary story

## Verification

- `python -m pytest -q tests/test_discovery.py::test_build_discovery_artifact_persists_directory_context_summaries tests/test_cli.py::test_cli_discover_input_persists_directory_context_summaries tests/test_make_targets.py::test_make_discover_input_persists_directory_context_summaries`
  passed with `3 passed`
- `python -m mypy ac14/discovery.py tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py`
  passed
- `python -m ruff check ac14/discovery.py tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py`
  passed
- `python -m pytest -q` passed with `206 passed`
- `python -m mypy ac14 tests` passed on `65` source files
- `python -m ruff check ac14 tests` passed

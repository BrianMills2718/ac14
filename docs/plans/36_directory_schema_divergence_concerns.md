# Plan #36: Directory Schema Divergence Concerns

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** 35
**Blocks:** None

---

## Gap

**Current:** AC14 can now inventory a directory input, persist bounded
summaries for alternate structured candidates and supporting context, and prove
that those summaries survive the front-half chain. But it still treats the
primary and alternate structured candidates as separate summaries only; it does
not compare them and surface explicit schema-divergence concerns.

**Target:** AC14 should compare the primary structured candidate against
alternate structured candidates and persist bounded schema-divergence concerns
when their inferred field shapes differ materially.

**Why:** Real blueprint derivation often depends on spotting mismatched fields
or shape drift across related input artifacts before freezing a plan.

---

## References Reviewed

- `CLAUDE.md` - front-half strengthening and continuation rules
- `docs/AC14_IMPLEMENTATION_STATUS.md` - discovery remains weak on deeper schema inference
- `docs/plans/34_directory_context_summaries.md` - discovery summary enrichment predecessor
- `docs/plans/35_directory_summary_front_half_proof.md` - front-half propagation predecessor
- `ac14/discovery.py` - current field-summary and concern surfaces

---

## Open Questions

### Q1: Should AC14 attempt full multi-file schema merging in this lane?
**Status:** Resolved
**Why it matters:** Full schema merging would broaden the lane from bounded concerns into implicit synthesis.
**Decision:** No. Persist compact divergence concerns only; do not merge candidates into one synthetic schema.

### Q2: What counts as a material divergence?
**Status:** Resolved
**Why it matters:** Overly sensitive drift detection would flood discovery with low-value noise.
**Decision:** Start with bounded, explicit cases: fields present in alternate candidates but absent from the primary candidate, and fields present in the primary candidate but absent from alternates.

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

1. Compare primary and alternate structured-candidate field summaries inside
   directory discovery.
2. Persist bounded schema-divergence concerns when fields differ materially.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_discovery.py` | `test_build_discovery_artifact_persists_directory_schema_divergence_concerns` | Directory discovery raises explicit divergence concerns when alternate structured candidates expose different fields |
| `tests/test_cli.py` | `test_cli_discover_input_persists_directory_schema_divergence_concerns` | CLI discovery preserves the same divergence concerns |
| `tests/test_make_targets.py` | `test_make_discover_input_persists_directory_schema_divergence_concerns` | Make discovery preserves the same divergence concerns |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] Directory discovery persists explicit schema-divergence concerns between the primary and alternate structured candidates.
- [x] Divergence detection stays bounded and reviewable rather than merging files into one hidden synthetic schema.
- [x] CLI and Make discovery surfaces preserve the same divergence concerns.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

This lane strengthens schema inference without changing the one-primary-input
rule. It adds reviewable divergence evidence, not hidden schema synthesis.

## Outcome

Implemented and verified:

1. directory discovery now compares the primary structured candidate against
   alternate structured candidates
2. directory discovery now persists bounded schema-divergence concerns when the
   alternate candidates expose different fields
3. CLI and Make discovery surfaces preserve the same divergence concerns

## Verification

- `python -m pytest -q tests/test_discovery.py::test_build_discovery_artifact_persists_directory_schema_divergence_concerns tests/test_cli.py::test_cli_discover_input_persists_directory_schema_divergence_concerns tests/test_make_targets.py::test_make_discover_input_persists_directory_schema_divergence_concerns`
  passed with `3 passed`
- `python -m mypy ac14/discovery.py tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py`
  passed
- `python -m ruff check ac14/discovery.py tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py`
  passed
- `python -m pytest -q` passed with `212 passed`
- `python -m mypy ac14 tests` passed on `65` source files
- `python -m ruff check ac14 tests` passed

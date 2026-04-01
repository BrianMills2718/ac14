# Plan #35: Directory Summary Front-Half Proof

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** 34
**Blocks:** None

---

## Gap

**Current:** AC14 now persists bounded summaries for alternate structured
candidates and supporting local context files when discovery starts from a
directory input. But the front-half acceptance proof has not yet shown that
those summaries survive the discovery-through-freeze chain.

**Target:** AC14 should prove one front-half acceptance lane on a directory
input bundle where the persisted discovery artifact includes the new alternate
candidate summaries and supporting-context summaries.

**Why:** The new directory-summary surface should not remain only a raw
discovery feature. It should be proven inside the same front-half chain that
AC14 uses to claim pre-freeze reasoning strength.

---

## References Reviewed

- `CLAUDE.md` - continuation rule and active proof-expansion rule
- `docs/plans/33_directory_front_half_acceptance_proof.md` - predecessor proof
- `docs/plans/34_directory_context_summaries.md` - predecessor discovery enrichment
- `ac14/front_half_acceptance.py` - current front-half artifact chain
- `ac14/discovery.py` - current directory summary contract
- `tests/test_front_half_acceptance.py` - current directory front-half proof surface

---

## Open Questions

### Q1: Does the front-half acceptance artifact itself need new top-level summary fields?
**Status:** Resolved
**Why it matters:** Duplicating the discovery truth would create another drift surface.
**Decision:** No. Prove the new summaries by asserting against the persisted discovery artifact inside the existing front-half chain.

### Q2: Should this lane broaden into retry-aware directory proof immediately?
**Status:** Resolved
**Why it matters:** The next honest gap is summary propagation, not more retry breadth.
**Decision:** No. Keep this lane focused on proving the new summary fields survive the standard front-half path first.

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

1. Add one direct front-half acceptance proof asserting the new alternate
   structured-candidate summaries and supporting-context summaries survive the
   directory-input artifact chain.
2. Add CLI and Make parity proofs for the same directory-summary front-half
   lane.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_report_preserves_directory_context_summaries` | Front-half acceptance preserves the new alternate-candidate and supporting-context summaries on a directory input |
| `tests/test_cli.py` | `test_cli_front_half_acceptance_preserves_directory_context_summaries` | CLI front-half acceptance preserves the same directory-summary story |
| `tests/test_make_targets.py` | `test_make_front_half_acceptance_preserves_directory_context_summaries` | Make front-half acceptance preserves the same directory-summary story |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] Front-half acceptance preserves alternate structured-candidate summaries on a directory input.
- [x] Front-half acceptance preserves supporting-context summaries on a directory input.
- [x] CLI and Make front-half surfaces preserve the same directory-summary story.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

This lane proves propagation, not new discovery logic. The artifact of record
remains the persisted discovery artifact inside the existing front-half chain.

## Outcome

Implemented and verified:

1. front-half acceptance now proves that alternate structured-candidate
   summaries survive the directory-input artifact chain
2. front-half acceptance now proves that supporting-context summaries survive
   the same chain
3. CLI and Make front-half surfaces preserve the same propagated summary story
4. AC14 now declares `open-web-retrieval` explicitly in `pyproject.toml`, and
   the shared package was repointed from a stale editable worktree to the
   canonical shared repo so the repo-standard mypy surface is green again

## Verification

- `python -m pytest -q tests/test_front_half_acceptance.py::test_build_front_half_acceptance_report_preserves_directory_context_summaries tests/test_cli.py::test_cli_front_half_acceptance_preserves_directory_context_summaries tests/test_make_targets.py::test_make_front_half_acceptance_preserves_directory_context_summaries`
  passed with `3 passed`
- `python -m mypy ac14 tests` passed on `65` source files
- `python -m ruff check tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py`
  passed
- `python -m pytest -q` passed with `209 passed`
- `python -m ruff check ac14 tests` passed

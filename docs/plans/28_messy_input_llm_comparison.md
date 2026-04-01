# Plan #28: Messy-Input LLM Comparison

**Status:** Planned
**Type:** implementation
**Priority:** High
**Blocked By:** 27
**Blocks:** None

---

## Gap

**Current:** AC14 may support messy structured input at the final gate after
Plan #27, but the bounded `llm` realistic-input lane and mode-comparison
surface will still only be proven on the cleaner JSON slice.

**Target:** AC14 should prove one bounded messy-input `llm` realistic-input
acceptance lane on the support-ticket CSV asset and extend the per-blueprint
mode-comparison artifact to include `llm` on that same messy input.

**Why:** AC14’s validation philosophy is not deterministic-only. Once the
non-LLM messy-input final gate is explicit, the next honest step is one bounded
messy-input `llm` comparison lane.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and current proof-expansion chain
- `docs/AC14_ROADMAP.md` - Horizon 1 realistic-input proof and operator-gated live readiness
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current bounded `llm` realistic-input status
- `docs/plans/27_messy_input_full_system_acceptance.md` - non-LLM messy-input prerequisite
- `ac14/acceptance.py` - realistic-input `llm` acceptance and comparison surface
- `ac14/llm_codegen.py` - bounded fixture-backed `llm` generation path

---

## Open Questions

### Q1: Should the first messy-input `llm` lane be live or fixture-backed?
**Status:** Resolved
**Why it matters:** The lane should strengthen semantic breadth without smuggling live-readiness claims into the default proof story.
**Decision:** Keep it fixture-backed and bounded. Live readiness remains a separate artifact.

### Q2: What should the comparison surface cover?
**Status:** Resolved
**Why it matters:** The messy-input `llm` lane should line up with the existing per-blueprint realistic comparison story.
**Decision:** Compare `reference`, `deterministic`, and `llm` on the same messy CSV asset.

---

## Files Affected

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

1. Reuse the shipped messy CSV asset plus fixture-backed LLM codegen to prove one bounded `llm` realistic-input acceptance lane.
2. Extend the per-blueprint realistic mode-comparison artifact to include `llm` on the same messy CSV asset.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_acceptance.py` | `test_build_acceptance_report_supports_messy_input_csv_llm_mode` | Full-system realistic-input acceptance supports the messy CSV asset in bounded `llm` mode |
| `tests/test_acceptance.py` | `test_build_realistic_mode_comparison_report_supports_messy_input_csv_llm_mode` | Messy-input realistic comparison works across `reference`, `deterministic`, and `llm` |
| `tests/test_cli.py` | `test_cli_acceptance_review_with_messy_input_csv_llm_mode_runs_end_to_end` | CLI bounded `llm` realistic-input acceptance works on the messy CSV asset |
| `tests/test_cli.py` | `test_cli_acceptance_review_realistic_compare_with_messy_input_csv_llm_mode_runs_end_to_end` | CLI messy-input realistic comparison supports bounded `llm` mode |
| `tests/test_make_targets.py` | `test_make_acceptance_review_with_messy_input_csv_llm_mode_runs_end_to_end` | Make bounded `llm` realistic-input acceptance works on the messy CSV asset |
| `tests/test_make_targets.py` | `test_make_acceptance_review_realistic_compare_with_messy_input_csv_llm_mode_runs_end_to_end` | Make messy-input realistic comparison supports bounded `llm` mode |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [ ] AC14 can run bounded `llm` realistic-input acceptance on the shipped messy CSV asset.
- [ ] The realistic mode-comparison artifact supports `reference`, `deterministic`, and `llm` on the same messy CSV asset.
- [ ] CLI and Make surfaces preserve the same bounded messy-input `llm` story without implying live readiness.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

This lane should strengthen bounded messy-input semantic breadth while keeping
fixture-backed `llm` evidence clearly separate from operator-gated live
readiness.

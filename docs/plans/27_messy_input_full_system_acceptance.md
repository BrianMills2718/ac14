# Plan #27: Messy-Input Full-System Acceptance

**Status:** Planned
**Type:** implementation
**Priority:** High
**Blocked By:** 26
**Blocks:** 28

---

## Gap

**Current:** AC14 has messy-input proof only on the front half. Final
requirements-aware acceptance still has no explicit proof on the messy CSV
slice, even though the support-ticket example already ships a messy realistic
input artifact.

**Target:** AC14 should prove full-system realistic-input acceptance on the
messy CSV asset in `reference` and `deterministic` modes, including CLI and
Make surfaces.

**Why:** The thesis needs one honest messy-input final gate before broader
claims about end-to-end semantic acceptance on realistic inputs.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and current proof-expansion chain
- `docs/AC14_ROADMAP.md` - Horizon 1 realistic-input acceptance and Horizon 2 messy-input strengthening
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current back-half vs messy-input gap
- `docs/plans/26_structured_realistic_input_loading.md` - loading prerequisite for non-JSON structured inputs
- `ac14/acceptance.py` - realistic-input acceptance and mode comparison surfaces
- `examples/support_ticket_digest/input/realistic_ticket_batch_messy.csv` - target messy input asset

---

## Open Questions

### Q1: Which non-LLM modes should the first messy-input full-system proof cover?
**Status:** Resolved
**Why it matters:** The lane should strengthen the final gate without mixing in live-readiness questions too early.
**Decision:** Cover `reference` and `deterministic` first.

### Q2: Should this lane include the realistic mode-comparison surface?
**Status:** Resolved
**Why it matters:** Comparison is already part of the reviewable proof surface and should stay aligned with the single-mode artifacts.
**Decision:** Yes. Prove the per-blueprint realistic comparison artifact on the messy CSV slice for `reference` and `deterministic`.

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

1. Reuse the shipped messy CSV asset with the existing support-ticket blueprint and prove `reference`-mode realistic-input acceptance on it.
2. Prove the same messy CSV lane in `deterministic` mode and through the realistic mode-comparison surface.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_acceptance.py` | `test_build_acceptance_report_supports_messy_input_csv_reference_mode` | Full-system realistic-input acceptance supports the messy CSV asset in `reference` mode |
| `tests/test_acceptance.py` | `test_build_acceptance_report_supports_messy_input_csv_deterministic_mode` | Full-system realistic-input acceptance supports the messy CSV asset in `deterministic` mode |
| `tests/test_acceptance.py` | `test_build_realistic_mode_comparison_report_supports_messy_input_csv_non_llm_modes` | Messy-input comparison works across `reference` and `deterministic` modes |
| `tests/test_cli.py` | `test_cli_acceptance_review_with_messy_input_csv_runs_end_to_end` | CLI realistic-input acceptance works on the messy CSV asset |
| `tests/test_cli.py` | `test_cli_acceptance_review_realistic_compare_with_messy_input_csv_runs_end_to_end` | CLI realistic comparison works on the messy CSV asset |
| `tests/test_make_targets.py` | `test_make_acceptance_review_with_messy_input_csv_runs_end_to_end` | Make realistic-input acceptance works on the messy CSV asset |
| `tests/test_make_targets.py` | `test_make_acceptance_review_realistic_compare_with_messy_input_csv_runs_end_to_end` | Make realistic comparison works on the messy CSV asset |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [ ] AC14 can run full-system realistic-input acceptance on the shipped messy CSV asset in `reference` and `deterministic` modes.
- [ ] The realistic mode-comparison artifact supports the same messy CSV asset across the non-LLM modes.
- [ ] CLI and Make surfaces preserve the same messy-input final-gate story.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

This lane is about carrying messy-input realism into the existing final gate,
not about broadening the blueprint model or live-readiness story.

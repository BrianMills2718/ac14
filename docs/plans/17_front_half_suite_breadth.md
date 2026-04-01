# Plan #17: Front-Half Suite Breadth

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 can persist one realistic-input front-half acceptance artifact
per example, and that artifact now includes a directly attached freeze-semantic
review path.

**Target:** AC14 should persist one suite-level front-half acceptance artifact
across the shipped realistic-input examples, with explicit per-example report
paths, review verdict counts, freeze-approval counts, and no silent skipping
when realistic inputs are missing.

**Why:** The front half now has real semantic review, but breadth is still more
of a back-half story than a front-half story. A suite artifact keeps
discovery-through-freeze breadth explicit and thesis-aligned.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 emphasis on stronger front-half evidence
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current breadth and front-half gaps
- `docs/AC14_ANTI_DRIFT_DOCTRINE.md` - hierarchy of truth
- `docs/plans/16_freeze_semantic_review_gate.md` - just-completed prerequisite lane
- `ac14/front_half_acceptance.py` - current per-example front-half artifact
- `ac14/acceptance.py` - suite artifact patterns for realistic-input acceptance
- `ac14/examples.py` - shipped-example discovery

---

## Open Questions

### Q1: Where should suite requirements come from for front-half breadth?
**Status:** Resolved
**Why it matters:** Front-half acceptance needs explicit requirements, and the
suite lane should stay deterministic and reviewable instead of hiding them in
code.
**Resolution:** The suite now derives requirements from each blueprint's
realistic-input `semantic_acceptance` scenarios and fails loud when those
requirements are missing.

### Q2: Should the suite aggregate count review verdicts only, or also freeze approval?
**Status:** Resolved
**Why it matters:** The suite needs a compact truth surface that reflects both
semantic quality and structural freeze readiness without conflating them.
**Resolution:** The suite artifact now counts semantic verdicts and freeze
approval separately while preserving per-example report paths and directly
attached freeze-semantic review paths.

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
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Define the suite-level front-half artifact shape and pre-make requirement sourcing and aggregate semantics.
2. Implement the suite builder plus CLI/Make surfaces and explicit missing-input handling.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_suite_report_runs_for_shipped_examples` | Suite artifact persists per-example front-half reports and aggregate counts |
| `tests/test_cli.py` | `test_cli_front_half_acceptance_suite_runs_end_to_end` | CLI suite surface persists the suite artifact |
| `tests/test_make_targets.py` | `test_make_front_half_acceptance_suite_runs_end_to_end` | Make suite surface persists the suite artifact |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] AC14 persists one suite-level front-half acceptance artifact across shipped realistic-input examples.
- [x] The suite artifact makes missing realistic-input coverage explicit instead of silently skipping it.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

This lane should strengthen front-half breadth only. It should not redefine the
front-half artifact, remove per-example reports, or dilute the directly attached
freeze-semantic review that Plan #16 just added.

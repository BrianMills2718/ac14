# Plan #16: Freeze Semantic Review Gate

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 has strong structural freeze readiness plus front-half
acceptance artifacts, but draft/freeze phases still lack a first-class
requirements-aware semantic review artifact attached directly to the freeze
decision surface.

**Target:** AC14 should persist one semantic review artifact for draft bundle
and freeze decision quality, covering business logic, requirement fit, and
obvious strategic concerns before final system execution.

**Why:** The front half is still weaker than the back half. A freeze-semantic
gate would make business-logic review visible earlier instead of waiting until
final realistic-input acceptance.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 emphasis on stronger front-half semantic review
- `docs/AC14_IMPLEMENTATION_STATUS.md` - remaining front-half semantic gap
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/15_recommendation_live_suite_awareness.md` - just-completed readiness lane
- `ac14/draft_authoring.py` - draft bundle materialization and freeze readiness
- `ac14/freeze_decision.py` - freeze approve/block logic
- `ac14/front_half_acceptance.py` - current front-half acceptance artifact

---

## Open Questions

### Q1: Should the freeze semantic review be part of `decide-freeze` or a separate artifact consumed by it?
**Status:** Resolved
**Why it matters:** The lane should strengthen freeze decisions without turning
freeze into a monolith.
**Resolution:** The semantic review is persisted as its own
`freeze_semantic_review.json` artifact, but `decide-freeze` owns building it and
publishes its path directly on the freeze decision artifact.

### Q2: Should the semantic gate run by default or remain operator-configurable at first?
**Status:** Resolved
**Why it matters:** The lane needs a clean balance between stronger front-half
review and proof-slice cost/control.
**Resolution:** The semantic review now runs by default whenever `decide-freeze`
is evaluating a draft bundle with a readiness report. Already-frozen shipped
bundles still skip it.

---

## Files Affected

- `prompts/review_freeze_semantic.yaml` (create)
- `ac14/freeze_decision.py` (modify)
- `ac14/front_half_acceptance.py` (modify)
- `tests/test_freeze_decision.py` (modify)
- `tests/test_front_half_acceptance.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `CLAUDE.md` (modify)
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

1. Define the freeze-semantic review artifact and where it attaches to the current front-half chain.
2. Implement the artifact with explicit persisted verdicts and concerns.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_freeze_decision.py` | `test_build_freeze_decision_blocks_draft_bundle` | Draft freeze now persists the attached semantic review artifact |
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_report_runs_pipeline` | Front-half artifact now carries the freeze-semantic artifact path |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q tests/test_freeze_decision.py tests/test_front_half_acceptance.py tests/test_cli.py::test_cli_front_half_acceptance_runs_end_to_end tests/test_make_targets.py::test_make_front_half_acceptance_runs_end_to_end` | Targeted freeze-semantic integration checks |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |
| `python -m pytest -q` | Full regression verification |

---

## Acceptance Criteria

- [x] AC14 persists one explicit freeze-semantic review artifact.
- [x] The artifact is connected to the freeze decision surface rather than floating as a side review.
- [x] Full local verification passes and the docs match the lane.

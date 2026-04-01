# Plan #20: Remediation Hand-Off Automation

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 now has an explicit dependency-remediation artifact that
points to a fresh dependency execution artifact.

**Target:** AC14 should let front-half and draft-planning surfaces consume that
remediation artifact directly instead of requiring operators to manually extract
the remediated dependency execution path.

**Why:** The remediation lane only fully helps if the hand-off back into the
front-half chain is just as explicit and reviewable as the remediation artifact
itself.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 environment/tool execution direction
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current dependency-remediation status
- `docs/AC14_ANTI_DRIFT_DOCTRINE.md` - hierarchy of truth
- `docs/plans/19_controlled_dependency_remediation.md` - just-completed remediation lane
- `ac14/dependency_execution.py` - remediation artifact shape
- `ac14/front_half_acceptance.py` - current front-half artifact chain
- `ac14/blueprint_planning.py` - current dependency execution artifact consumption

---

## Open Questions

### Q1: Which surfaces should accept remediation artifacts first?
**Status:** Resolved
**Why it matters:** The first automation step should reduce friction without
spreading a half-finished contract everywhere.
**Decision:** Draft blueprint planning is the first consumer. It already sits
at the boundary where dependency-plan provenance and dependency execution
evidence are explicit, so it can accept remediation artifacts without creating
hidden state.

### Q2: Should remediation hand-off stay explicit in the persisted artifacts?
**Status:** Resolved
**Why it matters:** Automation should not hide which dependency execution
artifact actually drove the later phases.
**Decision:** Yes. The persisted draft planning artifact now records both the
selected dependency execution artifact path and the remediation artifact path
when remediation drove the selection.

---

## Files Affected

- `ac14/blueprint_planning.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_blueprint_planning.py` (modify)
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

1. Pre-make draft planning as the first remediation-artifact consumer and keep
   provenance explicit.
2. Implement remediation-artifact consumption in draft planning, CLI, and Make.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_blueprint_planning.py` | `test_build_draft_blueprint_plan_accepts_dependency_remediation_artifact` | Draft planning can consume a remediation artifact without losing explicit provenance |
| `tests/test_cli.py` | `test_cli_draft_blueprint_plan_accepts_dependency_remediation_artifact` | CLI draft planning can consume a remediation artifact directly |
| `tests/test_make_targets.py` | `test_make_draft_blueprint_plan_accepts_dependency_remediation_artifact` | Make-driven draft planning can consume a remediation artifact directly |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] AC14 lets draft planning consume remediation artifacts directly.
- [x] The persisted artifacts still make the chosen dependency execution path explicit.
- [x] Full local verification passes and the docs match the lane.

## Verification

- Targeted remediation-hand-off verification passed:
  - `python -m pytest -q tests/test_blueprint_planning.py::test_build_draft_blueprint_plan_accepts_dependency_remediation_artifact tests/test_cli.py::test_cli_draft_blueprint_plan_accepts_dependency_remediation_artifact tests/test_make_targets.py::test_make_draft_blueprint_plan_accepts_dependency_remediation_artifact`
  - `python -m mypy ac14/blueprint_planning.py ac14/__main__.py tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m ruff check ac14/blueprint_planning.py ac14/__main__.py tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py`

## Outcome

Draft planning now accepts a remediation artifact directly, preserves the
original remediation artifact path, preserves the final dependency execution
artifact path, and fails loud if those two sources disagree.

---

## Notes

This lane is about reducing hand-off friction, not about hiding remediation or
making dependency execution implicit.

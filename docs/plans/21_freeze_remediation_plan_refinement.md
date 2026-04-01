# Plan #21: Freeze Remediation Plan Refinement

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 can produce a blocked freeze decision plus a grouped
remediation plan, but the main retry path is still manual bundle editing.

**Target:** AC14 should produce a refined draft planning artifact directly from
the original draft plan plus the freeze remediation plan.

**Why:** The next thesis-preserving iteration step is not another side artifact.
It is a reviewable loop that turns blocked freeze findings back into explicit
plan changes before bundle materialization and freeze retry.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and current proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 front-half strengthening direction
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current remediation/manual-loop status
- `docs/plans/19_controlled_dependency_remediation.md` - remediation artifact contract
- `docs/plans/20_remediation_handoff_automation.md` - just-completed hand-off lane
- `ac14/freeze_decision.py` - freeze remediation task/plan model
- `ac14/blueprint_planning.py` - current draft planning artifact contract
- `ac14/draft_authoring.py` - bundle materialization and freeze-readiness flow

---

## Open Questions

### Q1: What is the first refinement target?
**Status:** Resolved
**Why it matters:** The first loop should stay explicit and bounded instead of
jumping straight to automatic bundle mutation.
**Decision:** Refine the draft planning artifact, not the materialized bundle.

### Q2: How should refinement provenance stay explicit?
**Status:** Resolved
**Why it matters:** A refinement loop should not hide which blocked findings
drove the new plan.
**Decision:** Persist the source draft plan path, source freeze decision path,
source remediation plan path, refinement summary, and refinement round on the
refined planning artifact.

---

## Files Affected

- `ac14/blueprint_planning.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `prompts/refine_draft_blueprint_plan.yaml` (add)
- `tests/test_blueprint_planning.py` (modify)
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

1. Pre-make the first refinement loop around the draft planning artifact.
2. Add a refinement entrypoint that consumes the original draft plan plus a
   freeze remediation plan/decision and emits a refined draft planning artifact.
3. Persist explicit refinement provenance and fail loud on incompatible inputs.
4. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_blueprint_planning.py` | `test_refine_draft_blueprint_plan_from_freeze_remediation_preserves_provenance` | Refinement emits a new plan artifact with explicit links back to the blocked freeze/remediation inputs |
| `tests/test_cli.py` | `test_cli_refine_draft_blueprint_plan_runs_end_to_end` | CLI refinement works end to end |
| `tests/test_make_targets.py` | `test_make_refine_draft_blueprint_plan_runs_end_to_end` | Make refinement works end to end |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] AC14 can refine a blocked draft planning artifact from freeze remediation input.
- [x] The refined planning artifact records explicit provenance back to the blocked freeze/remediation source.
- [x] The lane stays plan-first and does not mutate the draft bundle in place.
- [x] Full local verification passes and the docs match the lane.

## Verification

- Targeted refinement verification passed:
  - `python -m pytest -q tests/test_blueprint_planning.py::test_refine_draft_blueprint_plan_from_freeze_remediation_preserves_provenance tests/test_cli.py::test_cli_refine_draft_blueprint_plan_runs_end_to_end tests/test_make_targets.py::test_make_refine_draft_blueprint_plan_runs_end_to_end`
  - `python -m mypy ac14/blueprint_planning.py ac14/__main__.py tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m ruff check ac14/blueprint_planning.py ac14/__main__.py tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py`
- Full verification passed:
  - `python -m pytest -q`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`

## Outcome

AC14 now exposes a remediation-driven draft-plan refinement lane that consumes
the original draft plan plus a blocked freeze decision, preserves explicit
retry provenance, increments a refinement round, and emits a fresh planning
artifact instead of mutating the bundle in place.

---

## Notes

This lane is about replacing the first manual retry step with a reviewable
planning artifact, not about broad autonomous bundle editing.

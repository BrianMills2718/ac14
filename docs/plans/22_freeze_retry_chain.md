# Plan #22: Freeze Retry Chain

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 can refine a blocked draft planning artifact from a freeze
decision, but operators still have to manually chain refinement, bundle
materialization, and freeze retry.

**Target:** AC14 should provide one explicit retry-chain artifact that runs the
refined planning step, rematerializes the draft bundle, reruns freeze, and
persists the resulting path summary.

**Why:** The next honest reduction in front-half friction is explicit chain
automation, not hidden in-place mutation or silent retries.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and current proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 front-half strengthening direction
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current manual retry-chain status
- `docs/plans/21_freeze_remediation_plan_refinement.md` - just-completed refinement lane
- `ac14/blueprint_planning.py` - refined draft planning artifact contract
- `ac14/draft_authoring.py` - bundle materialization contract
- `ac14/freeze_decision.py` - freeze retry contract

---

## Open Questions

### Q1: What should the retry chain own?
**Status:** Resolved
**Why it matters:** The first chain should reduce orchestration friction without
hiding intermediate artifacts.
**Decision:** Own refinement, rematerialization, and refreeze only. Keep all
three intermediate artifacts persisted and exposed.

### Q2: How should retry outcomes stay reviewable?
**Status:** Resolved
**Why it matters:** A chained retry should not become a black box.
**Decision:** Persist one retry artifact with the paths to the refined plan,
refined bundle, refreshed readiness report, refreshed freeze decision, and a
compact final summary.

---

## Files Affected

- `ac14/freeze_retry.py` (add)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_freeze_retry.py` (add)
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

1. Pre-make the retry chain around persisted intermediate artifacts.
2. Implement one retry-chain command/artifact that runs refine → materialize → freeze.
3. Keep all intermediate artifact paths explicit in the persisted retry artifact.
4. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_freeze_retry.py` | `test_build_freeze_retry_artifact_runs_refine_materialize_and_refreeze` | The retry chain persists all intermediate artifact paths and the refreshed freeze result |
| `tests/test_cli.py` | `test_cli_retry_freeze_runs_end_to_end` | CLI retry chain works end to end |
| `tests/test_make_targets.py` | `test_make_retry_freeze_runs_end_to_end` | Make retry chain works end to end |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] AC14 can run an explicit retry chain from blocked freeze input.
- [x] The retry artifact exposes every intermediate path instead of hiding the chain.
- [x] The lane stays artifact-backed and does not mutate bundles silently.
- [x] Full local verification passes and the docs match the lane.

## Verification

- Targeted retry-chain verification passed:
  - `python -m pytest -q tests/test_freeze_retry.py::test_build_freeze_retry_artifact_runs_refine_materialize_and_refreeze tests/test_cli.py::test_cli_retry_freeze_runs_end_to_end tests/test_make_targets.py::test_make_retry_freeze_runs_end_to_end`
  - `python -m mypy ac14/freeze_retry.py ac14/__main__.py tests/test_freeze_retry.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m ruff check ac14/freeze_retry.py ac14/__main__.py tests/test_freeze_retry.py tests/test_cli.py tests/test_make_targets.py`

## Outcome

AC14 now provides one explicit retry-chain artifact that runs refine ->
materialize -> refreeze, preserves every intermediate path, and keeps the
refreshed freeze result reviewable instead of leaving that chain as manual
operator orchestration.

---

## Notes

This lane is about explicit chained retries, not about broad autonomous healing.

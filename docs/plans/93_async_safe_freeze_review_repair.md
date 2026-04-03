# Plan #93: Async-Safe Freeze Review Repair

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 92
**Blocks:** 94

---

## Gap

**Current:** The second front-half-first smoke rerun moved past the original
structured-spec binding failures, but every AC14 attempt now dies with
`asyncio.run() cannot be called from a running event loop` before the
structured-spec front-half artifact can return.

**Target:** Make freeze decision and freeze semantic review safe to call from
the async front-half and retry paths without nested `asyncio.run()` reentry.

**Why:** The next smoke rerun should measure whether the repaired front half can
earn approval and reach runtime, not whether a sync wrapper crashes inside an
async lane.

---

## Acceptance Criteria

- [x] Retry-enabled structured-spec front-half acceptance no longer fails on
      nested `asyncio.run()` reentry.
- [x] Freeze decision and freeze semantic review remain callable from both sync
      and async paths.
- [x] Targeted tests cover the async-safe retry-enabled front-half path.

---

## Files Affected

- `ac14/freeze_decision.py`
- `ac14/freeze_retry.py`
- `ac14/front_half_acceptance.py`
- `tests/test_front_half_acceptance.py`
- `tests/test_front_half_first_empirical.py`
- `tests/test_cli.py`
- `tests/test_make_targets.py`

---

## Plan

### Steps

1. Split freeze semantic review and freeze decision into async-native entry
   points plus sync wrappers.
2. Update async front-half and retry-chain callers to await the async-native
   freeze path instead of calling sync wrappers from inside active event loops.
3. Add retry-enabled structured-spec front-half coverage so the original smoke2
   blocker is reproduced in tests and then eliminated.
4. Re-verify before the next smoke rerun.

---

## Required Tests

| Command | Why |
|---------|-----|
| `python -m pytest -q tests/test_front_half_acceptance.py tests/test_front_half_first_empirical.py tests/test_cli.py tests/test_make_targets.py` | Proves the async-safe front-half retry path and operator surfaces |
| `python -m mypy ac14 tests` | Keeps the async/sync surface typed |
| `python -m ruff check ac14 tests` | Keeps the repair lint-clean |

---

## Notes

This plan is deliberately narrow. It repairs the new smoke2 blocker without yet
claiming that the front half is semantically correct enough to reopen the full
trial gate.

## Implementation Summary

Plan #93 made the freeze path async-safe instead of relying on sync wrappers
inside already-running event loops.

What changed:

- `freeze_decision.py` now exposes async-native entry points for freeze
  decision, freeze semantic review, and the semantic-quality LLM call, while
  keeping sync wrappers for CLI and other synchronous callers.
- `front_half_acceptance.py` and `freeze_retry.py` now await the async-native
  freeze path directly in retry-enabled front-half flows.
- `blueprint_planning.py` now preserves structured-spec planning provenance
  during refined-plan retries so the async-safe retry path does not regress into
  discovery-shaped artifacts.
- `tests/test_front_half_acceptance.py` now proves the original smoke2 blocker
  directly with an async retry-enabled structured-spec front-half run.

Verified with:

- `python -m pytest -q tests/test_front_half_acceptance.py tests/test_front_half_first_empirical.py -k 'async_structured_spec_front_half_acceptance_supports_retry_freeze or generate_monolithic_runtime_system_persists_failed_source_for_nested_input_contract'`
- `python -m pytest -q tests/test_cli.py tests/test_make_targets.py -k 'structured_spec_front_half_acceptance or front_half_first_smoke_gate'`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

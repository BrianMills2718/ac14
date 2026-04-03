# Plan #87: Front-Half-First Smoke Execution

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 86
**Blocks:** 88, 89

---

## Gap

**Current:** The repo can have a truthful front-half-first smoke runner, but it
still needs one persisted smoke verdict from the structured-spec benchmark
bundle.

**Target:** Spend one bounded front-half-first smoke trial and persist the
verdict artifact.

**Why:** The next branch should be decided by evidence, not by intuition or by
reopening the older back-half gate.

---

## Acceptance Criteria

- [x] One bounded front-half-first smoke artifact exists.
- [x] The verdict is one of:
      `ready_for_full_trials`, `blocked_on_front_half`,
      `blocked_on_harness`, or `blocked_on_infrastructure`.
- [x] The next branch is explicit from the artifact with no chat-only
      interpretation.

---

## Plan

### Steps

1. Run the new front-half-first smoke runner on the structured-spec benchmark bundle.
2. Inspect the persisted verdict and attempt reports.
3. Freeze the next branch immediately:
   - Plan #88 if the verdict is `ready_for_full_trials`
   - Plan #89 otherwise

---

## Required Tests

| Command | Why |
|---------|-----|
| `python -m pytest -q tests/test_front_half_first_empirical.py` | Keeps the runner behavior stable while the smoke artifact is interpreted |
| `python -m mypy ac14 tests` | Keeps the empirical artifacts typed |
| `python -m ruff check ac14 tests` | Keeps the lane clean before spending the smoke budget |

---

## Notes

This plan spends the smoke budget only once. It should not quietly expand into
repair work; that belongs to Plan #89 if the verdict is blocked.

## Implementation Summary

Persisted artifact:

- `.ac14_out/front_half_first_smoke_1/smoke_readiness_report.json`

Verdict:

- `blocked_on_front_half`

Key facts:

1. no provider/infrastructure contamination was detected
2. AC14 failed all three bounded attempts in `generation` before any approved
   front-half artifact existed
3. monolithic failed all three bounded attempts in `runtime_outputs` because it
   expected a nested `metrics_snapshot` key instead of consuming the raw record

Next branch:

- [Plan #89: Front-Half-First Blocker Diagnosis](89_front_half_first_blocker_diagnosis.md)

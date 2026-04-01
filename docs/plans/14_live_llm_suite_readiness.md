# Plan #14: Live LLM Suite Readiness

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 has one explicit operator-gated live-readiness artifact for
realistic-input `llm` acceptance, but it only probes one shipped example.

**Target:** AC14 should persist one suite-level live-readiness artifact that
records per-example `ready`, `blocked`, or `skipped` states for realistic-input
`llm` acceptance across the shipped suite, while keeping live execution
operator-explicit.

**Why:** The current live/default readiness story is still narrow. A
suite-level live-readiness artifact would broaden evidence without conflating
fixture-backed breadth with live capability.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and live-readiness boundary
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis on broader live/default readiness evidence
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current readiness gap after recommendation awareness
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/13_recommendation_default_gate_awareness.md` - just-completed recommendation lane
- `ac14/recommendation.py` - current single-example live-readiness artifact
- `ac14/acceptance.py` - realistic-input acceptance artifact builder
- `tests/test_recommendation.py` - recommendation/live readiness regression coverage
- `tests/test_cli.py` - CLI readiness smoke coverage
- `tests/test_make_targets.py` - Make-based readiness smoke coverage

---

## Open Questions

### Q1: Should suite live readiness run all shipped examples or stop at the first failure?
**Status:** Resolved
**Why it matters:** The artifact should stay reviewable and avoid hiding partial coverage.
**Resolution:** It should record one per-example result across the shipped suite
and aggregate them, even when some examples are blocked.

### Q2: Should suite live readiness change the default-generator recommendation immediately?
**Status:** Resolved
**Why it matters:** The current lane should broaden evidence first without
quietly changing promotion policy.
**Resolution:** Not yet. Persist the suite live-readiness artifact first; later
lanes can decide how recommendation should consume it.

---

## Files Affected

- `CLAUDE.md` (modify)
- `ac14/recommendation.py` (modify)
- `ac14/__main__.py` (modify if needed)
- `Makefile` (modify if needed)
- `tests/test_recommendation.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `README.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Add a suite-level live-readiness artifact with explicit per-example and aggregate statuses.
2. Keep live execution explicitly gated and separate from fixture-backed breadth.
3. Run targeted readiness verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_recommendation.py` | `test_build_llm_live_readiness_suite_artifact_skips_without_live_keys` | Suite live readiness persists explicit skipped results without keys |
| `tests/test_cli.py` | `test_cli_live_llm_readiness_suite_reports_skipped_without_keys` | CLI suite live readiness persists reviewable skipped artifacts |
| `tests/test_make_targets.py` | `test_make_live_llm_readiness_suite_reports_skipped_without_keys` | Make suite live readiness persists reviewable skipped artifacts |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [ ] AC14 persists one suite-level live-readiness artifact with explicit per-example and aggregate statuses.
- [ ] Live suite readiness remains operator-explicit and separate from fixture-backed breadth.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

- Keep this lane additive: broaden live-readiness evidence without silently
  changing recommendation policy or default-generator promotion rules.

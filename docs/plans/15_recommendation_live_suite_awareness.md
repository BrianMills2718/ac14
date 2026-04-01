# Plan #15: Recommendation Live Suite Awareness

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 now has a suite-level live-readiness artifact, but the
default-generator recommendation still consumes only the single-example
live-readiness artifact.

**Target:** Recommendation should consume both the bounded one-example
live-readiness artifact and the broader suite-level live-readiness artifact,
and it should fail loud when the suite artifact is not ready.

**Why:** The default-generator story should reflect the broader explicit
live-readiness evidence that AC14 now persists, not just the earlier one-example
probe.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis on broader live/default readiness evidence
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current readiness gap after suite live-readiness landed
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/14_live_llm_suite_readiness.md` - just-completed suite live-readiness lane
- `ac14/recommendation.py` - current recommendation logic
- `tests/test_recommendation.py` - recommendation regression coverage
- `tests/test_cli.py` - CLI recommendation smoke coverage
- `tests/test_make_targets.py` - Make recommendation smoke coverage

---

## Open Questions

### Q1: Should recommendation keep the one-example live-readiness artifact after adding the suite artifact?
**Status:** Resolved
**Why it matters:** The smaller bounded probe is still useful as a narrow live
signal even after suite breadth exists.
**Resolution:** Yes. Keep both artifacts and make the recommendation report both.

### Q2: Should suite live readiness block LLM promotion when it is not ready?
**Status:** Resolved
**Why it matters:** Recommendation should stay conservative until broader live
evidence is explicit.
**Resolution:** Yes. Missing or non-ready suite live-readiness should block LLM
promotion and appear in the reasons.

---

## Files Affected

- `CLAUDE.md` (modify)
- `ac14/recommendation.py` (modify)
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

1. Feed the suite live-readiness artifact into recommendation.
2. Make recommendation reasons fail loud when suite live readiness is not ready.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_recommendation.py` | `test_build_default_generator_recommendation_persists_suite_live_readiness` | Recommendation now persists suite live-readiness evidence |
| `tests/test_cli.py` | `test_cli_recommend_default_generator_deterministic_only` | CLI recommendation output includes suite live-readiness evidence |
| `tests/test_make_targets.py` | `test_make_recommend_default_generator_deterministic_only` | Make recommendation output includes suite live-readiness evidence |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [ ] Recommendation artifacts persist suite-level live-readiness evidence explicitly.
- [ ] Recommendation reasons mention suite live-readiness status when it is not ready.
- [ ] Full local verification passes and the docs match the lane.

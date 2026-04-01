# Plan #13: Recommendation Default-Gate Awareness

**Status:** In Progress
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 now carries realistic-input final-gate acceptance into the
default suite proof/evidence story, but the default-generator recommendation
still reasons from suite comparison, suite semantic comparison, and live
readiness without consuming the suite-level realistic-input gate evidence.

**Target:** The recommendation artifact should consume suite-level realistic-input
default-gate coverage explicitly, persist that evidence reviewably, and fail
loud when default-gate coverage is missing or unsupported.

**Why:** Recommendation/default-generator policy should reflect the same default
proof story that AC14 now claims at the suite level.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis after suite-level default-gate integration
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current readiness/recommendation gaps
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/12_realistic_input_suite_default_gate.md` - just-completed suite default-gate lane
- `ac14/suite.py` - suite-level proof aggregation
- `ac14/recommendation.py` - current default-generator recommendation logic
- `tests/test_recommendation.py` - recommendation artifact regression coverage
- `tests/test_cli.py` - CLI recommendation smoke coverage
- `tests/test_make_targets.py` - Make-based recommendation smoke coverage

---

## Open Questions

### Q1: Should recommendation rebuild the suite proof report or read an already-built artifact?
**Status:** Resolved
**Why it matters:** The lane should reuse the existing suite proof surface rather
than re-deriving gate coverage heuristically.
**Resolution:** Recommendation should call the existing suite proof builder and
consume the persisted suite proof report explicitly.

### Q2: Should missing default-gate coverage block only LLM promotion or also deterministic recommendation?
**Status:** Resolved
**Why it matters:** The recommendation artifact should stay honest without
silently weakening deterministic control-lane claims.
**Resolution:** Missing or unsupported default-gate coverage should block LLM
promotion and appear explicitly in reasons; deterministic can remain the
conservative default but the artifact must say why evidence is incomplete.

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

1. Feed suite-level realistic-input default-gate evidence into the recommendation artifact.
2. Make recommendation reasons fail loud when default-gate coverage is missing or unsupported.
3. Run targeted recommendation verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_recommendation.py` | `test_build_default_generator_recommendation_persists_suite_default_gate_coverage` | Recommendation now persists suite-level realistic-input default-gate evidence |
| `tests/test_cli.py` | `test_cli_recommend_default_generator_deterministic_only` | CLI recommendation output includes default-gate evidence |
| `tests/test_make_targets.py` | `test_make_recommend_default_generator_deterministic_only` | Make recommendation output includes default-gate evidence |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [ ] Recommendation artifacts persist suite-level realistic-input default-gate coverage explicitly.
- [ ] Recommendation reasons mention missing or unsupported default-gate coverage instead of silently ignoring it.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

- Keep this lane additive: recommendation should consume the existing suite
  proof artifact chain, not invent a parallel proof surface.

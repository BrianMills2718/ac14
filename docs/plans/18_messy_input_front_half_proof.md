# Plan #18: Messy-Input Front-Half Proof

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 now has suite-level front-half breadth across the shipped
realistic-input JSON examples, but those inputs are still relatively clean and
schema-friendly.

**Target:** AC14 should prove one explicit front-half lane on a messier input
artifact, with discovery, dependency planning, draft planning, freeze review,
and front-half semantic review all remaining reviewable and explicit.

**Why:** The core thesis is not just that AC14 works on clean examples; it is
that decomposition and context management help when inputs are messy enough that
monolithic coding agents start to lose the thread.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 emphasis on stronger pre-freeze evidence
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current remaining messy-input gap
- `docs/AC14_ANTI_DRIFT_DOCTRINE.md` - hierarchy of truth
- `docs/plans/17_front_half_suite_breadth.md` - just-completed breadth prerequisite
- `ac14/discovery.py` - current input inspection capabilities
- `ac14/front_half_acceptance.py` - current front-half artifact chain

---

## Open Questions

### Q1: What input format is the smallest honest messy-input step?
**Status:** Resolved
**Why it matters:** The lane should increase realism without exploding scope.
**Resolution:** The first honest messy-input step is a reviewable CSV artifact
for the support-ticket slice, because it is messier than the current JSON suite
without requiring a broader blueprint/runtime expansion.

### Q2: Should the first messy-input lane become a shipped example asset or remain a proof fixture?
**Status:** Resolved
**Why it matters:** The result should improve the proof slice without confusing
the product boundary or overclaiming generality.
**Resolution:** The first lane uses a shipped repo asset under the existing
support-ticket example so the proof remains reviewable and easy to inspect
without pretending it is a new blueprint family.

---

## Files Affected

- `examples/...` (modify or create)
- `ac14/front_half_acceptance.py` (modify if needed)
- `ac14/discovery.py` (modify only if the current inspection path is insufficient)
- `tests/test_front_half_acceptance.py` (modify)
- `tests/test_cli.py` (modify if operator surface changes)
- `tests/test_make_targets.py` (modify if Make surface changes)
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

1. Pre-make the messy-input format choice and whether it is a shipped asset or proof fixture.
2. Add the messy-input artifact and run one explicit front-half acceptance lane on it.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_report_supports_messy_input_artifact` | Discovery-through-freeze remains reviewable on one messier input artifact |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] AC14 proves one explicit front-half lane on a messier input artifact.
- [x] The lane stays reviewable and fail-loud instead of hiding ambiguity inside prompts.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

This lane should not yet broaden the blueprint model. It should prove stronger
front-half realism on top of the existing artifact chain.

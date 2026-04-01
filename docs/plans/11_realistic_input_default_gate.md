# Plan #11: Realistic-Input Default Gate

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 has realistic-input acceptance artifacts, but they still sit
beside the main proof/evidence paths rather than acting as the default final
gate for shipped examples.

**Target:** AC14 should carry realistic-input full-system acceptance into the
default proof/evidence path for shipped examples whenever a realistic-input
artifact exists.

**Why:** The system thesis is not fully proven by structural and deterministic
artifacts alone. The final gate should include actual realistic-input execution
plus LLM semantic review by default, not only as an optional side command.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and current proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis after packet sufficiency evidence
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current missing default-gate integration
- `docs/UNCERTAINTIES.md` - current uncertainty state after packet sufficiency
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/10_packet_sufficiency_evidence.md` - just-completed packet-sufficiency lane
- `ac14/acceptance.py` - realistic-input acceptance artifacts
- `ac14/evidence_bundle.py` - current persisted proof bundle builder
- `ac14/suite.py` - current suite-level proof aggregation

---

## Open Questions

### Q1: Should realistic-input acceptance replace existing proof artifacts?
**Status:** Resolved
**Why it matters:** The lane should strengthen the proof slice without deleting
useful structural evidence.
**Resolution:** No. Realistic-input acceptance should become an additional
default final gate, not a replacement for structural, packet, or recomposition
proof.

### Q2: What should happen when a shipped blueprint has no realistic-input artifact?
**Status:** Resolved
**Why it matters:** The default gate should stay explicit rather than silently
shrinking.
**Resolution:** For shipped examples, missing realistic-input artifacts should
stay explicit in the evidence output instead of being silently ignored.

### Q3: Should the first lane cover one blueprint or the shipped suite?
**Status:** Resolved
**Why it matters:** The lane should land quickly without hiding the broader
goal.
**Resolution:** Start by wiring the default gate into one-example proof/evidence
bundles and keep the artifact shape reusable for suite expansion.

---

## Files Affected

- `CLAUDE.md` (modify)
- `ac14/evidence_bundle.py` (modify)
- `ac14/__main__.py` (modify if new operator surface is needed)
- `Makefile` (modify if new operator surface is needed)
- `tests/test_generated_evidence.py` or `tests/test_cli.py` (modify)
- `README.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Carry realistic-input full-system acceptance into the default single-example
   proof/evidence path when a realistic-input artifact exists.
2. Make any missing realistic-input artifact explicit in the persisted evidence
   instead of silently skipping it.
3. Run full verification and lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_generated_evidence.py` or `tests/test_cli.py` | `test_prove_example_includes_realistic_input_acceptance_when_available` | Default proof/evidence path now carries realistic-input acceptance |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [x] AC14 default proof/evidence path includes realistic-input acceptance when a shipped realistic-input artifact exists.
- [x] Missing realistic-input artifacts remain explicit instead of being silently skipped.
- [x] The proof story now treats realistic-input full-system acceptance as part of the default final gate, not only as an optional side artifact.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

- Keep this lane thesis-centered: the goal is to strengthen the final proof
  gate, not to add another disconnected artifact.

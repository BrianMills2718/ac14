# Plan #12: Realistic-Input Suite Default Gate

**Status:** In Progress
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 now carries realistic-input full-system acceptance into the
default single-example proof/evidence path, but the suite-level proof surface
still treats realistic-input acceptance as a separate side artifact.

**Target:** AC14 should carry realistic-input acceptance into the default suite
proof/evidence story for shipped examples that provide realistic-input
artifacts, while keeping missing artifacts explicit.

**Why:** The next honest step after single-example default-gate integration is
to make the suite proof story reflect the same final-gate discipline.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis after single-example default-gate integration
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current missing suite-level default-gate integration
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/11_realistic_input_default_gate.md` - just-completed single-example default-gate lane
- `ac14/evidence_bundle.py` - current single-example proof bundle
- `ac14/suite.py` - current suite-level proof aggregation
- `ac14/acceptance.py` - realistic-input acceptance artifacts

---

## Open Questions

### Q1: Should the suite gate reuse the existing realistic-input suite acceptance artifact?
**Status:** Resolved
**Why it matters:** The lane should prefer explicit reuse over parallel artifacts.
**Resolution:** Yes. Reuse the existing realistic-input acceptance artifact
shape where possible and connect it to the suite proof story instead of
inventing a parallel evaluator.

### Q2: What happens when a shipped example has no realistic-input artifact?
**Status:** Resolved
**Why it matters:** The suite story should remain honest.
**Resolution:** Missing realistic-input artifacts must remain explicit in the
persisted suite evidence instead of being silently ignored.

---

## Files Affected

- `CLAUDE.md` (modify)
- `ac14/suite.py` (modify)
- `ac14/__main__.py` (modify if needed)
- `Makefile` (modify if needed)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `tests/test_acceptance.py` or `tests/test_evidence_bundle.py` (modify)
- `README.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Carry realistic-input acceptance into the default suite proof/evidence story.
2. Keep missing realistic-input artifacts explicit in suite evidence.
3. Run full verification and lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_cli.py` or `tests/test_acceptance.py` | `test_suite_default_proof_includes_realistic_input_acceptance_when_available` | Suite proof/evidence now carries realistic-input acceptance by default |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [ ] AC14 suite proof/evidence story includes realistic-input acceptance when shipped realistic-input artifacts exist.
- [ ] Missing realistic-input artifacts remain explicit in suite evidence.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

- Keep this lane additive: strengthen the suite proof story without deleting the
  structural and recomposition evidence that already exists.

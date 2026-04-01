# Plan #37: Directory Divergence Front-Half Proof

**Status:** In Progress
**Type:** implementation
**Priority:** High
**Blocked By:** 36
**Blocks:** None

---

## Gap

**Current:** AC14 now persists explicit schema-divergence concerns between the
primary structured candidate and alternate structured candidates at raw
discovery time. But the front-half acceptance proof has not yet shown that
those divergence concerns survive the discovery-through-freeze chain.

**Target:** AC14 should prove one directory-input front-half lane where the
persisted discovery artifact includes the new schema-divergence concerns.

**Why:** Schema-divergence detection remains weaker than the thesis if it is
only proven at `discover-input` and not in the broader front-half artifact
chain that AC14 uses to judge pre-freeze reasoning quality.

---

## References Reviewed

- `CLAUDE.md` - continuation rules and active proof-expansion rule
- `docs/plans/36_directory_schema_divergence_concerns.md` - predecessor raw-discovery lane
- `ac14/front_half_acceptance.py` - current front-half artifact chain
- `ac14/discovery.py` - current divergence-concern contract
- `tests/test_front_half_acceptance.py` - current directory-input proof surface

---

## Open Questions

### Q1: Does this lane need new top-level fields on the front-half artifact?
**Status:** Resolved
**Why it matters:** Duplicating the discovery truth would create another drift surface.
**Decision:** No. Assert against the persisted discovery artifact inside the front-half chain.

### Q2: Should this lane expand into retry-aware proof immediately?
**Status:** Resolved
**Why it matters:** The next honest gap is divergence propagation, not retry breadth.
**Decision:** No. Keep the lane focused on the standard front-half path.

---

## Files Affected

- `tests/test_front_half_acceptance.py` (modify)
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

1. Add one direct front-half acceptance proof asserting that the new
   schema-divergence concerns survive a directory-input front-half lane.
2. Add CLI and Make parity proofs for the same directory-divergence front-half
   story.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_report_preserves_directory_schema_divergence_concerns` | Front-half acceptance preserves the new directory schema-divergence concerns |
| `tests/test_cli.py` | `test_cli_front_half_acceptance_preserves_directory_schema_divergence_concerns` | CLI front-half acceptance preserves the same divergence concerns |
| `tests/test_make_targets.py` | `test_make_front_half_acceptance_preserves_directory_schema_divergence_concerns` | Make front-half acceptance preserves the same divergence concerns |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [ ] Front-half acceptance preserves directory schema-divergence concerns on a directory input.
- [ ] CLI and Make front-half surfaces preserve the same divergence concerns.
- [ ] The lane stays reviewable and does not add a second schema-truth surface.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

This lane is about propagation, not new discovery logic. The persisted
discovery artifact remains the artifact of record for divergence concerns.

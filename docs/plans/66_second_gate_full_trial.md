# Plan #66: Second-Gate Full Trial

**Status:** Planned
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 71 (resume-safe full-trial rerun)
**Blocks:** None

---

## Gap

**Current:** The second empirical gate has no full five-trial result on the
new benchmark.

**Target:** Run the runtime-first five-trial gate on the new benchmark,
persist the decision artifact, and lock the verdict docs.

**Why:** The project needs a second real comparison artifact before claiming
that the first gate was merely noisy or benchmark-local.

---

## References Reviewed

- `docs/plans/38_empirical_comparison_gate.md`
- `docs/plans/63_runtime_first_comparison_contract.md`
- `docs/plans/65_second_gate_smoke.md`
- `ac14/empirical_comparison.py`

---

## Open Questions

### Q1: What if the second gate is also inconclusive?
**Status:** Resolved
**Decision:** Record it honestly and update the roadmap/docs before any further
scope broadening.

---

## Files Affected

- `.ac14_out/full_trials_gate_2/` (create)
- `docs/plans/66_second_gate_full_trial.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Run the full five-trial gate under the new benchmark and runtime-first contract.
2. Persist the decision artifact.
3. Interpret the verdict honestly in the active docs.
4. Commit the result and updated control surface.

---

## Required Tests

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Keep the repo green around the evaluation run |
| `python -m mypy ac14 tests` | Keep type safety green |
| `python -m ruff check ac14 tests` | Keep lint/import hygiene green |

---

## Acceptance Criteria

- [ ] `.ac14_out/full_trials_gate_2/experiment_decision.json` exists.
- [ ] The verdict is recorded plainly in the active docs.
- [ ] The repo remains green after the verdict lock.

---

## Notes

This plan should only run after the smoke gate is `ready_for_full_trials` and
any interrupted full-trial output has been repaired into a restart-safe state.

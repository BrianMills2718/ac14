# Plan #71: Empirical Full-Trial Resume Integrity

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 66, 72

---

## Gap

**Current:** The second-gate full trial was interrupted mid-run and left partial,
zero-byte artifacts under `.ac14_out/full_trials_gate_2/`. The empirical runner
does not currently resume from valid completed trials or preserve incomplete
trial evidence before rerunning.

**Target:** Full-trial execution should reuse valid completed paired-trial
reports, archive incomplete trial directories for observability, and write
attempt/trial/decision artifacts atomically so interruption cannot silently
corrupt the empirical gate.

**Why:** The thesis gate is only credible if the empirical harness itself is
restart-safe and reviewable. Blind reruns discard evidence and zero-byte
artifacts collapse observability right where AC14 is supposed to be strongest.

---

## References Reviewed

- `CLAUDE.md`
- `docs/AC14_NEXT_24_HOURS.md`
- `docs/TODO.md`
- `docs/plans/66_second_gate_full_trial.md`
- `ac14/empirical_comparison.py`
- `ac14/generated_codegen.py`
- `.ac14_out/full_trials_gate_2/trial_1/paired_trial_report.json`
- `.ac14_out/full_trials_gate_2/trial_2/paired_trial_report.json`
- `.ac14_out/full_trials_gate_2/trial_3/paired_trial_report.json`
- `.ac14_out/full_trials_gate_2/trial_4/`

---

## Open Questions

### Q1: Should incomplete trial directories be deleted or preserved?
**Status:** Resolved
**Why it matters:** Deletion simplifies reruns but destroys the exact evidence
of interruption and partial writes.
**Decision:** Preserve them under `_interrupted_trials/` and rerun the clean
trial directory.

### Q2: Should the runner resume only whole trials or individual attempts?
**Status:** Resolved
**Why it matters:** Attempt-level resume is more complex and risks mixing
partial condition state.
**Decision:** Resume at the paired-trial level only. Reuse valid
`paired_trial_report.json`; archive anything less complete.

---

## Files Affected

- `ac14/atomic_io.py` (create)
- `ac14/generated_codegen.py` (modify)
- `ac14/empirical_comparison.py` (modify)
- `tests/test_empirical_comparison.py` (modify)
- `docs/plans/71_empirical_full_trial_resume_integrity.md` (create)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `CLAUDE.md` (modify)

---

## Plan

### Steps

1. Add atomic text/JSON artifact writes for empirical attempt, trial, and
   generated-module outputs that matter to the second gate.
2. Add full-trial resume behavior that:
   - reuses valid completed `paired_trial_report.json` files
   - archives incomplete trial directories under `_interrupted_trials/`
   - reruns incomplete trials cleanly
3. Add targeted regression tests for reuse and archive behavior.
4. Resume Plan #66 with the repaired runner and only then lock this plan.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_empirical_comparison.py` | `test_run_empirical_comparison_reuses_completed_trial_reports` | Valid completed trial reports are reused |
| `tests/test_empirical_comparison.py` | `test_run_empirical_comparison_archives_incomplete_trial_before_rerun` | Incomplete trial dirs are preserved and rerun cleanly |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q tests/test_empirical_comparison.py` | Targeted empirical runner regression coverage |
| `python -m mypy ac14 tests` | Type safety on the new resume/atomic helpers |
| `python -m ruff check ac14 tests` | Lint/import hygiene |

---

## Acceptance Criteria

- [x] Empirical full-trial execution reuses valid completed paired-trial reports.
- [x] Incomplete full-trial directories are preserved before rerun instead of overwritten in place.
- [x] The repaired runner is used to continue Plan #66 toward a final decision artifact.

---

## Notes

This plan is intentionally narrow. It does not change the benchmark semantics
or decision rule; it only makes the active thesis gate restart-safe and
observable enough to trust.

## Implementation Summary (2026-04-02)

The empirical runner now:

- writes attempt, packet, recomposition, paired-trial, and decision artifacts atomically
- reuses valid existing `paired_trial_report.json` artifacts instead of rerunning completed trials
- archives incomplete trial directories under `_interrupted_trials/` before rerunning them cleanly

The repaired runner was used directly against the interrupted
`.ac14_out/full_trials_gate_2/` directory:

- trials 1 and 2 were reused
- the broken partial `trial_3/` state was archived and rebuilt
- the broken partial `trial_4/` state was rebuilt cleanly
- the run completed through `trial_5/` and emitted
  `.ac14_out/full_trials_gate_2/experiment_decision.json`

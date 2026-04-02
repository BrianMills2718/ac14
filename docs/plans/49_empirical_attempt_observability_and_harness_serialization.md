# Plan #49: Empirical Attempt Observability And Harness Serialization

**Status:** Complete
**Type:** evaluation + implementation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 50

---

## Gap

**Current:** Plan #48 stayed `blocked_on_harness`, but the saved empirical
attempt artifacts were still too lossy. I had to rerun packet and recomposition
checks manually against the saved attempt-2 package to see the real causes.

The new concrete findings are:

1. empirical attempts are not persisting `packet_test_report.json` and
   `recomposition_report.json`, so the main artifacts under-report the actual
   harness failures
2. packet and recomposition semantic-eval paths are crashing on fixture values
   that include `datetime` objects, producing `Object of type datetime is not
   JSON serializable`
3. because of those two problems, the active empirical lane is weaker on
   observability than it should be at exactly the point where the thesis gate
   depends on precise blocker diagnosis

**Target:** Persist the detailed harness artifacts for every empirical attempt
and make semantic-eval prompt inputs JSON-safe so the harness tells the truth
about actual packet and recomposition mismatches.

**Why:** The next repair lane should be driven by first-class empirical attempt
artifacts, not by manual after-the-fact reproduction.

---

## References Reviewed

- `CLAUDE.md` - active empirical execution rules and observability emphasis
- `docs/plans/48_empirical_smoke_gate_refresh_ii.md` - latest smoke gate result
- `.ac14_out/empirical_smoke_gate_repair7/smoke_readiness_report.json` - current smoke verdict
- `.ac14_out/empirical_smoke_gate_repair7/trial_1/paired_trial_report.json` - current paired-trial snapshot
- `.ac14_out/empirical_smoke_gate_repair7/trial_1/ac14/attempt_2/attempt_report.json` - under-specified attempt artifact
- `ac14/empirical_comparison.py` - empirical attempt runner
- `ac14/generated_evidence.py` - packet-test semantic-eval path
- `ac14/recomposition.py` - recomposition semantic-eval path
- `tests/test_empirical_comparison.py` - empirical lane tests

---

## Open Questions

### Q1: Should this plan change the fairness contract?
**Status:** Resolved
**Why it matters:** The empirical gate should not silently get more repair budget while improving diagnostics.
**Decision:** No. This plan improves observability and harness truthfulness only. Attempt counting and smoke semantics stay unchanged.

### Q2: Should datetime normalization happen only in the empirical lane?
**Status:** Resolved
**Why it matters:** The packet-test and recomposition helpers are shared proof surfaces, and the serialization bug exists there regardless of the empirical lane.
**Decision:** Fix datetime-safe semantic-eval prompt inputs in the shared helper paths, not just in one empirical wrapper.

---

## Files Affected

- `ac14/empirical_comparison.py` (modify)
- `ac14/generated_evidence.py` (modify)
- `ac14/recomposition.py` (modify)
- `tests/test_empirical_comparison.py` (modify)
- `tests/test_generated_evidence.py` (modify)
- `tests/test_recomposition.py` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Persist `packet_test_report.json` and `recomposition_report.json` for every empirical attempt.
2. Include bounded report-path visibility in the attempt artifact or adjacent files so follow-on lanes can diagnose failures without rerunning them manually.
3. Make packet-test and recomposition semantic-eval prompt inputs JSON-safe for `datetime`-bearing fixture data.
4. Add focused tests that prove the new observability and serialization behavior.
5. Run full local verification, then hand off to Plan #50.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_empirical_comparison.py` | `test_empirical_attempt_persists_packet_and_recomposition_reports` | Empirical attempts now persist detailed harness reports |
| `tests/test_generated_evidence.py` | `test_packet_case_semantic_eval_handles_datetime_fixture_values` | Packet semantic-eval prompt inputs are JSON-safe |
| `tests/test_recomposition.py` | `test_recomposition_semantic_eval_handles_datetime_fixture_values` | Recomposition semantic-eval prompt inputs are JSON-safe |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q tests/test_empirical_comparison.py tests/test_generated_evidence.py tests/test_recomposition.py` | Fast regression for the observability lane |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] Every empirical attempt persists packet and recomposition reports directly.
- [x] Packet semantic-eval prompt building no longer fails on `datetime` fixture values.
- [x] Recomposition semantic-eval prompt building no longer fails on `datetime` fixture values.
- [x] Focused and full local verification pass.
- [x] The active control docs point to Plan #50 as the next repair lane.

---

## Notes

This plan exists because maximum observability is now part of the testing
protocol. The thesis gate is too important to run on generic attempt summaries.

## Implementation Summary (2026-04-02)

- Empirical attempts now always persist `packet_test_report.json` and
  `recomposition_report.json`, even when generation fails before the harness can
  run normally.
- Attempt reports now point directly to those persisted harness artifacts so the
  next repair lane does not need a manual rerun just to diagnose packet or
  recomposition failures.
- Packet and recomposition semantic-evaluation prompt inputs are now normalized
  into JSON-safe values before Jinja `tojson` renders them, which fixes the
  `datetime is not JSON serializable` crash on benchmark fixtures.
- Verification passed with targeted Plan #49 tests, full `pytest`, `mypy`, and
  `ruff`.

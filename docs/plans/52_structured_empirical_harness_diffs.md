# Plan #52: Structured Empirical Harness Diffs

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 51
**Blocks:** 54

---

## Gap

**Current:** Empirical attempts persist packet and recomposition reports, but the retry lane still compresses those failures into generic summaries like `packet-local tests failed`.

**Target:** Persist bounded field-level mismatch details in the harness reports and feed those details back into empirical repair guidance. Also run the empirical lane inside a real `llm_client` experiment context instead of relying on warning-only guardrails.

**Why:** Observability is only useful if the retry loop actually consumes it. Generic failure labels waste attempts.

---

## References Reviewed

- `docs/plans/49_empirical_attempt_observability_and_harness_serialization.md`
- `docs/plans/51_empirical_smoke_gate_refresh_iii.md`
- `.ac14_out/empirical_smoke_gate_repair8/trial_1/ac14/attempt_2/packet_test_report.json`
- `.ac14_out/empirical_smoke_gate_repair8/trial_1/ac14/attempt_2/recomposition_report.json`
- `.ac14_out/empirical_smoke_gate_repair8/trial_1/paired_trial_report.json`

---

## Files Affected

- `ac14/output_diff.py`
- `ac14/generated_evidence.py`
- `ac14/recomposition.py`
- `ac14/empirical_comparison.py`
- `tests/test_generated_evidence.py`
- `tests/test_recomposition.py`
- `tests/test_empirical_comparison.py`

---

## Plan

### Steps

1. Add reusable bounded diff helpers for mapping/list outputs.
2. Persist bounded mismatch details in packet and recomposition reports.
3. Feed those details into empirical failure summaries.
4. Wrap empirical attempts in `llm_client` experiment and feature-profile context.

---

## Required Tests

- `python -m pytest -q tests/test_generated_evidence.py tests/test_recomposition.py tests/test_empirical_comparison.py tests/test_llm_codegen.py`
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [x] Packet-test results persist bounded field-level mismatch details.
- [x] Recomposition results persist bounded component-local mismatch details.
- [x] Empirical failure summaries include packet/recomposition diff details instead of generic-only summaries.
- [x] Empirical attempts activate a real `llm_client` experiment context and feature profile.
- [x] Targeted tests plus full `pytest`, `mypy`, and `ruff` pass.

---

## Implementation Summary (2026-04-02)

Landed a reusable diff helper in `ac14/output_diff.py`, added `mismatch_details` to `PacketCaseResult`, added `mismatch_component_id` and `mismatch_details` to `RecompositionScenarioResult`, and threaded both report types into empirical failure-summary generation. The retry loop can now name exact field-level blockers such as `parsed_case.normalized_notes` instead of only saying `packet-local tests failed`. The empirical attempt runner now enters `llm_client` `experiment_run(...)` plus `activate_feature_profile(...)`, which removes the ambiguity between benchmark/eval calls and ordinary generation calls.

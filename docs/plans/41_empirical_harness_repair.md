# Plan #41: Empirical Harness Repair

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 40
**Blocks:** 42

---

## Gap

**Current:** Plan #40 now gives AC14 an explicit smoke verdict. The latest
bounded smoke run returned `blocked_on_harness` with:

1. `monolithic` failing packet/runtime expectations
2. `ac14` failing earlier during import-time validation for `case_parser`

**Target:** AC14 should make both blocker classes directly repairable by:

1. persisting failed LLM module source even when validation aborts the write,
2. persisting richer runtime mismatch guidance for monolithic repair loops,
3. rerunning the smoke gate after those repair-surface improvements

**Why:** The next honest step is not a vague "try again." It is to make the
two current harness blockers inspectable and repairable enough that one bounded
smoke rerun can either succeed or fail for a sharper reason.

---

## References Reviewed

- `docs/plans/40_empirical_smoke_stabilization.md` - smoke verdict contract
- `.ac14_out/empirical_smoke_gate/smoke_readiness_report.json` - latest smoke verdict
- `.ac14_out/empirical_smoke_gate/trial_1/paired_trial_report.json` - current failure categories
- `ac14/empirical_comparison.py` - paired runner and repair guidance surface
- `ac14/generated_codegen.py` - emitted package write path
- `ac14/llm_codegen.py` - LLM module validation path
- `tests/test_empirical_comparison.py` - current comparison coverage

---

## Open Questions

### Q1: How should AC14 preserve failed generated module source?
**Status:** Resolved
**Why it matters:** The current AC14 failure says only `No module named 'max'`.
That is not enough to repair confidently without the raw module source.
**Decision:** Persist failed LLM module source plus its validation error under
the generated output tree even when validation aborts normal module emission.

### Q2: How should monolithic runtime mismatches feed the next repair loop?
**Status:** Resolved
**Why it matters:** "outputs did not match" is too weak when the benchmark
already knows the exact expected and actual final outputs.
**Decision:** Add bounded structured mismatch guidance that names the runtime
case and the specific output-port diffs instead of only a generic mismatch line.

### Q3: What ends this plan?
**Status:** Resolved
**Why it matters:** This should not become another open-ended artifact lane.
**Decision:** The plan completes after:

1. failed module source is persisted on validation failure,
2. runtime mismatch guidance is sharper,
3. one bounded smoke rerun happens under the improved repair surface.

---

## Files Affected

- `ac14/generated_codegen.py` (modify)
- `ac14/llm_codegen.py` (modify)
- `ac14/empirical_comparison.py` (modify)
- `tests/test_empirical_comparison.py` (modify)
- `tests/test_generated_codegen.py` (modify)
- `docs/plans/41_empirical_harness_repair.md` (create)
- `docs/plans/CLAUDE.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/TODO.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Persist failed LLM-generated module source and validation metadata so AC14
   condition failures remain inspectable even when import-time validation aborts
   normal package emission.
2. Replace coarse runtime mismatch repair guidance with bounded per-case,
   per-port mismatch summaries.
3. Rerun one bounded smoke gate and record whether the blocker categories
   sharpen or whether one condition now achieves a hard-harness success.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_generated_codegen.py` | `test_failed_llm_module_source_is_persisted_for_diagnosis` | Failed AC14 module source stays inspectable |
| `tests/test_empirical_comparison.py` | `test_failure_summary_includes_runtime_port_diffs` | Monolithic repair guidance becomes more specific |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Keep the harness-repair lane type-clean |
| `python -m ruff check ac14 tests` | Keep the harness-repair lane lint-clean |

---

## Acceptance Criteria

- [x] Failed AC14 LLM module source is persisted when validation aborts normal emission.
- [x] Runtime mismatch guidance is more specific than generic output mismatch lines.
- [x] One bounded smoke rerun is recorded under the improved repair surface.
- [x] The next blocker categories are clearer or at least one condition now achieves a hard-harness success.
- [x] Full local verification passes and the repo stays clean.

---

## Notes

This plan is only worthwhile because Plan #40 already proved the blocker is not
currently infrastructure/provider contamination. It is a harness-repair lane,
not another propagation proof.

Completion note:

- the bounded repair slice moved AC14 from import-time module failure to later packet-level failure
- the latest smoke rerun remains `blocked_on_harness`
- the next blocker is now benchmark-fidelity repair rather than missing diagnostics

# Plan #147: Codegen Observability — Trace Persistence And Diagnostic Make Targets

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** When generated code fails at runtime, the only artifacts are the
generated `.py` file, `attempt_report.json`, and `failure_classification.json`.
There is no record of what context the LLM actually received. Diagnosing "did
the LLM have the business rules?" requires a full analysis plan (Plan #142 was
exactly this).

The recurring failure mode: LLM generates bad code → we blame harness or
infrastructure → eventually discover it was a context wiring bug (rules not
passed, invariants were TODO placeholders). This happened in gate_2 where
`structured_spec_business_rules` was 0 for all 5 trials and we didn't know
until Plan #142.

**Target:** Persist the `CodegenContext` and rendered LLM prompt alongside each
generated component. Add `make context-audit` and `make diagnose-attempt`
targets so the next failure is diagnosable without a full plan.

---

## Acceptance Criteria

- [x] `{component_id}.context.json` written to `generated/` dir alongside each `.py`
- [x] `{component_id}.prompt.json` written to `generated/` dir alongside each `.py` (LLM path only)
- [x] `scripts/context_audit.py` scans output dir, flags zero/TODO context fields
- [x] `scripts/diagnose_attempt.py` shows context summary + runtime mismatches for one attempt
- [x] `make context-audit OUTPUT=...` target
- [x] `make diagnose-attempt OUTPUT=... TRIAL=N ATTEMPT=M` target
- [x] All existing tests pass

---

## Design

### Files Written Per Component (in `generated/`)

| File | Content | Key Use |
|------|---------|---------|
| `{component_id}.py` | Generated Python module | Already existed |
| `{component_id}.context.json` | Full `CodegenContext` as JSON | Flags missing rules, TODO invariants |
| `{component_id}.prompt.json` | Rendered prompt messages (LLM path only) | See exact text sent to LLM |

### What `context_audit` Flags

- `structured_spec_business_rules: 0` → RED (would have caught Plan #142 bug immediately)
- `local_invariants` contains "TODO" strings → WARN
- `packet_test_cases: 0` → WARN

### Files Changed

- `ac14/generated_codegen.py` — persist context JSON after `build_codegen_context()`; thread `trace_dir` into render functions
- `ac14/llm_codegen.py` — add `trace_dir: Path | None = None` parameter; write prompt JSON after `render_prompt()`
- `scripts/context_audit.py` — new script
- `scripts/diagnose_attempt.py` — new script
- `Makefile` — two new targets

---

## Files Affected

- `ac14/generated_codegen.py`
- `ac14/llm_codegen.py`
- `scripts/context_audit.py` (new)
- `scripts/diagnose_attempt.py` (new)
- `Makefile`

# Plan #78: Reusable Packet Rule Grounding

**Status:** Complete
**Type:** implementation
**Priority:** Critical
**Blocked By:** 77
**Blocks:** 79

---

## Gap

**Current:** The empirical taxonomy says the strongest reusable weakness is not
packet size, but weak first-class rule grounding for semantically coupled
business logic inside bounded packets. Today AC14 mostly relies on raw packet
fixtures, local constraints, schema descriptions, and benchmark-local repair
guidance.

**Target:** Add one reusable, benchmark-agnostic rule-grounding surface to the
packet/codegen context so component generation gets a concise decision-oriented
summary of local packet cases in addition to the raw fixtures.

**Why:** The current empirical story says AC14 needs stronger local rule
salience without abandoning bounded packets or returning to benchmark-local
prompt tuning as the default.

---

## References Reviewed

- `docs/plans/77_cross_benchmark_failure_taxonomy.md`
- `ac14/codegen_context.py`
- `ac14/generated_codegen.py`
- `ac14/llm_codegen.py`
- `prompts/generate_component.yaml`
- `ac14/empirical_comparison.py`

---

## Open Questions

### Q1: What reusable rule-grounding surface should AC14 add without widening packet scope?
**Status:** Resolved
**Why it matters:** The repair should strengthen local salience, not smuggle in
global context.
**Resolution:** AC14 now derives bounded rule-grounding summaries directly from
packet-local cases and carries them in the codegen context alongside raw
fixtures.

### Q2: What is the minimum verification needed before spending another smoke rerun?
**Status:** Resolved
**Why it matters:** The repair should earn a bounded empirical attempt through
targeted tests, not by hope.
**Resolution:** Targeted codegen-context and prompt-contract tests are enough to
prove the new surface exists and stays bounded before the next smoke rerun.

---

## Files Affected

- `ac14/codegen_context.py` (modify)
- `ac14/llm_codegen.py` (modify if needed for context rendering)
- `prompts/generate_component.yaml` (modify)
- `tests/test_codegen_context.py` (modify)
- `tests/test_llm_codegen.py` (modify if prompt/context contract changes)
- `docs/plans/78_reusable_packet_rule_grounding.md` (create)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)

---

## Plan

### Steps

1. Add a reusable rule-grounding summary to the codegen context derived from
   packet-local cases and local contracts.
2. Expose that summary in the component-generation prompt.
3. Add targeted tests that prove the new surface is present, bounded, and
   informative.
4. Update the active docs before running the next smoke.

---

## Required Tests

### New Or Updated Tests

| Test File | What It Verifies |
|-----------|------------------|
| `tests/test_codegen_context.py` | The codegen context carries bounded rule-grounding summaries |
| `tests/test_llm_codegen.py` | The prompt/context contract includes the new grounding surface |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q tests/test_codegen_context.py tests/test_llm_codegen.py` | Targeted verification for the new grounding surface |
| `python -m mypy ac14 tests` | Type safety remains clean |
| `python -m ruff check ac14 tests` | Lint/import hygiene remains clean |

---

## Acceptance Criteria

- [x] AC14 has one reusable rule-grounding surface in the bounded codegen context.
- [x] The generation prompt consumes that surface explicitly.
- [x] Targeted tests prove the new surface is present and bounded.
- [x] The next smoke rerun can point to this repair instead of benchmark-local prompt edits.

---

## Notes

This plan is intentionally reusable. It should not add another
`resource_scaling_v1`-only repair rule unless the repair is already encoded in
the existing benchmark-local guidance surfaces.

## Implementation Summary (2026-04-02)

What landed:

- `CodegenContext` now carries `rule_grounding_summaries`
- those summaries are derived from packet-local cases only and restate fixture
  inputs -> expected outputs as bounded decision-oriented bullets
- the shared component-generation prompt now exposes those summaries explicitly
  in addition to the raw packet cases

Verification:

- `python -m pytest -q tests/test_codegen_context.py tests/test_llm_codegen.py`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

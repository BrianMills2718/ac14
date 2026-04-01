# Plan #7: Realistic-Input LLM Acceptance

**Status:** In Progress
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 can persist realistic-input full-system acceptance in
`reference` and `deterministic` modes, plus one suite-level artifact across
those supported modes.

**Target:** AC14 can exercise one honest realistic-input full-system acceptance
path in `llm` mode, persist one mode-comparison artifact for realistic inputs,
and keep the operator/docs surface explicit about what `llm` coverage exists
and what remains deferred.

**Why:** The project vision is not deterministic-only. After proving the
controlled lanes, the next honest step is to bring the LLM generation path into
the realistic-input final gate without pretending suite-wide `llm` coverage is
already solved.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and current proof-expansion rule
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis on realistic-input final gates
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current gap around `llm` realistic-input acceptance
- `docs/UNCERTAINTIES.md` - broader mode-coverage and cost uncertainties
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/06_realistic_input_acceptance_breadth.md` - just-completed reference/deterministic breadth lane
- `ac14/acceptance.py` - current realistic-input acceptance surface
- `ac14/llm_codegen.py` - current LLM generator contract
- `ac14/generated_codegen.py` - generated module loading/runtime assumptions
- `tests/test_llm_codegen.py` - current unit coverage for the LLM generator contract

---

## Open Questions

### Q1: Should AC14 jump straight to suite-wide `llm` realistic-input acceptance?
**Status:** Resolved
**Why it matters:** The next lane should strengthen the final gate without
making broader claims than the implementation can support honestly.
**Resolution:** No. First prove one reviewable realistic-input `llm` lane on a
single shipped slice, then add one per-blueprint comparison artifact. Suite
`llm` breadth remains deferred.

### Q2: How should non-live tests cover `llm` realistic-input execution?
**Status:** Resolved
**Why it matters:** The repo needs deterministic verification for the new lane
without requiring live provider credentials on every run.
**Resolution:** Add an explicit fixture-driven test path for LLM codegen so the
`llm` realistic-input acceptance lane can be exercised in unit/CLI/Make tests
without live keys.

### Q3: What counts as “done” for realistic-input `llm` comparison?
**Status:** Resolved
**Why it matters:** The comparison artifact should strengthen reviewability,
not become a vague reporting layer.
**Resolution:** Done means one persisted artifact for one shipped blueprint
that records realistic-input acceptance results across `reference`,
`deterministic`, and `llm` modes, with explicit verdicts and report paths.

---

## Files Affected

- `CLAUDE.md` (modify)
- `ac14/acceptance.py` (modify)
- `ac14/llm_codegen.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_acceptance.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `tests/test_llm_codegen.py` (modify)
- `README.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Add a fixture-driven verification path for LLM codegen so non-live tests can
   exercise `llm` realistic-input acceptance honestly.
2. Prove realistic-input full-system acceptance in `llm` mode on the existing
   support-ticket slice.
3. Persist one realistic-input mode-comparison artifact across `reference`,
   `deterministic`, and `llm` for one shipped blueprint.
4. Expose any required CLI/Make surfaces cleanly.
5. Run full verification and lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_llm_codegen.py` | `test_generate_component_module_with_llm_uses_fixture_env` | LLM codegen can use a deterministic fixture path for non-live verification |
| `tests/test_acceptance.py` | `test_build_acceptance_report_supports_realistic_input_llm_mode` | `llm` mode supports realistic-input full-system acceptance on one shipped slice |
| `tests/test_acceptance.py` | `test_build_realistic_mode_comparison_report_supports_llm` | One realistic-input comparison artifact persists reference/deterministic/llm results |
| `tests/test_cli.py` | `test_cli_acceptance_review_with_realistic_input_llm_mode_runs_end_to_end` | CLI surface supports `llm` realistic-input acceptance |
| `tests/test_make_targets.py` | `test_make_acceptance_review_with_realistic_input_llm_mode_runs_end_to_end` | Make surface supports `llm` realistic-input acceptance |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `tests/test_acceptance.py::test_build_acceptance_report_supports_realistic_input_deterministic_mode` | Existing deterministic realistic-input lane remains intact |
| `tests/test_acceptance.py::test_build_realistic_suite_acceptance_report_supports_realistic_inputs` | Existing supported-mode suite artifact remains intact |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [ ] AC14 supports realistic-input full-system acceptance in `llm` mode on the support-ticket slice.
- [ ] Non-live tests can exercise the `llm` realistic-input lane deterministically.
- [ ] AC14 can persist one realistic-input comparison artifact across `reference`, `deterministic`, and `llm` for one blueprint.
- [ ] CLI and Make expose the widened lane without manual glue code.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

- This lane should strengthen the realistic-input final gate without claiming
  that suite-wide `llm` breadth is already solved.
- Keep `llm` realistic-input coverage reviewable and bounded. Do not let one
  passing slice turn into an over-broad default-generator claim.

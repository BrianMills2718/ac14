# Plan #6: Realistic-Input Acceptance Breadth

**Status:** In Progress
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 can persist realistic-input full-system acceptance, but only
in `reference` mode and only on the support-ticket slice.

**Target:** AC14 can run realistic-input full-system acceptance in
`deterministic` mode as well, exercise a second shipped realistic-input slice,
and persist one suite-level realistic-input acceptance artifact across shipped
examples.

**Why:** The current final gate is real but still too narrow. The next honest
step is not broader theory; it is broader evidence on realistic inputs while
preserving explicit artifacts and bounded proof claims.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and current proof-expansion rule
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis on realistic-input final gates
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current statement that realistic-input full-system acceptance is `reference`-mode only
- `docs/UNCERTAINTIES.md` - realistic-input and mode-breadth uncertainties
- `docs/TODO.md` - current control surface
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should track the active lane
- `docs/plans/05_realistic_input_full_system_acceptance.md` - just-completed reference slice
- `ac14/acceptance.py` - current realistic-input acceptance surface
- `ac14/generated_codegen.py` - deterministic generated component behavior
- `ac14/reference_components.py` - reference runtime state assumptions
- `examples/support_ticket_digest/` - current realistic-input acceptance slice
- `examples/incident_alert_digest/` - second shipped slice for broader realistic-input evidence

---

## Open Questions

### Q1: Should the next realistic-input mode be `deterministic` or `llm`?
**Status:** Resolved
**Why it matters:** The proof slice should widen through the most controlled and
reviewable path first.
**Resolution:** `deterministic` comes next. `llm` remains deferred until
realistic-input acceptance is stable outside the manual reference lane.

### Q2: Should realistic-input breadth mean more examples or more modes first?
**Status:** Resolved
**Why it matters:** Breadth can expand in multiple directions, but the plan
should remove ambiguity before implementation starts.
**Resolution:** This lane does both in a narrow order: first deterministic mode
for the existing slice, then one second shipped realistic-input slice, then one
suite-level artifact.

### Q3: What counts as “done” for the suite-level artifact?
**Status:** Resolved
**Why it matters:** The suite surface should strengthen the proof slice, not
turn into a vague reporting layer.
**Resolution:** Done means one persisted suite-level realistic-input acceptance
artifact over shipped examples and supported realistic-input modes, with clear
counts and report paths.

---

## Files Affected

- `ac14/acceptance.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `examples/incident_alert_digest/input/realistic_alert_batch.json` (create)
- `tests/test_acceptance.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `README.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Extend realistic-input full-system acceptance from `reference` to
   `deterministic` mode without hiding generated-state assumptions.
2. Add one second shipped realistic-input input artifact for the incident slice
   and prove realistic-input acceptance there.
3. Add one suite-level realistic-input acceptance artifact across shipped
   examples and supported realistic-input modes.
4. Expose any required CLI/Make surfaces cleanly.
5. Run full verification and lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_acceptance.py` | `test_build_acceptance_report_supports_realistic_input_deterministic_mode` | Deterministic mode supports realistic-input full-system acceptance |
| `tests/test_acceptance.py` | `test_build_acceptance_report_supports_incident_realistic_input` | A second shipped realistic-input slice works |
| `tests/test_acceptance.py` | `test_build_suite_acceptance_report_supports_realistic_inputs` | Suite-level realistic-input acceptance artifact persists across shipped examples |
| `tests/test_cli.py` | `test_cli_acceptance_review_with_realistic_input_deterministic_mode_runs_end_to_end` | CLI surface supports deterministic realistic-input acceptance |
| `tests/test_make_targets.py` | `test_make_acceptance_review_with_realistic_input_deterministic_mode_runs_end_to_end` | Make surface supports deterministic realistic-input acceptance |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `tests/test_front_half_acceptance.py` | Front-half realistic-input lane stays coherent |
| `tests/test_acceptance.py::test_build_acceptance_report_supports_realistic_input_artifact` | Existing reference realistic-input acceptance remains intact |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [ ] AC14 supports realistic-input full-system acceptance in `deterministic` mode for the existing support-ticket slice.
- [ ] AC14 supports at least one second shipped realistic-input slice.
- [ ] AC14 can persist one suite-level realistic-input acceptance artifact across shipped examples and supported modes.
- [ ] CLI and Make expose the widened lane without manual glue code.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

- This lane should strengthen evidence breadth without claiming that `llm`
  realistic-input acceptance is already solved.
- If deterministic realistic-input acceptance exposes hidden fixture-derived
  state assumptions, those assumptions should be surfaced and resolved
  explicitly rather than hidden behind fallbacks.

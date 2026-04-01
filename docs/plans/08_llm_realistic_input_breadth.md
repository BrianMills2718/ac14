# Plan #8: LLM Realistic-Input Breadth

**Status:** In Progress
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 has one honest realistic-input `llm` acceptance slice and one
per-blueprint realistic-input comparison artifact, but the fixture-backed LLM
codegen path is still keyed only by component ID and therefore too narrow for
multi-blueprint `llm` breadth.

**Target:** AC14 can run one suite-level realistic-input `llm` acceptance
artifact across shipped examples in a blueprint-aware fixture-backed lane and
keep the docs explicit that this is proof breadth, not live default readiness.

**Why:** One working `llm` slice is materially better than zero, but it is
still too easy to overfit to one blueprint. The next honest step is broader
`llm` realistic-input evidence across shipped examples while keeping the proof
claim bounded and reviewable.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and current proof-expansion rule
- `docs/AC14_ROADMAP.md` - Horizon 1 focus on realistic-input final gates
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current bounded statement about one `llm` slice
- `docs/UNCERTAINTIES.md` - current `llm` breadth and cost uncertainties
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/07_realistic_input_llm_acceptance.md` - just-completed one-slice `llm` lane
- `ac14/llm_codegen.py` - current fixture-backed LLM codegen path
- `ac14/acceptance.py` - current realistic-input acceptance and comparison surfaces

---

## Open Questions

### Q1: Should the next `llm` breadth lane be live-only?
**Status:** Resolved
**Why it matters:** The repo needs deterministic verification, but it also must
not hide the difference between fixture-backed and live `llm` behavior.
**Resolution:** No. The core lane should be fixture-backed and reviewable. Live
smoke remains optional and explicitly secondary.

### Q2: What is the main blocker to suite-level `llm` breadth today?
**Status:** Resolved
**Why it matters:** The plan should attack the narrowest real blocker first.
**Resolution:** The current fixture-backed LLM codegen surface is keyed only by
component ID, which is too weak for multiple blueprints that reuse component
IDs with different embedded deterministic state.

### Q3: What counts as “done” for this breadth lane?
**Status:** Resolved
**Why it matters:** The lane should broaden evidence without overclaiming live
readiness.
**Resolution:** Done means one persisted suite-level realistic-input acceptance
artifact in `llm` mode across shipped examples using blueprint-aware fixture
codegen, plus docs that explicitly scope the claim to bounded proof breadth.

---

## Files Affected

- `CLAUDE.md` (modify)
- `ac14/llm_codegen.py` (modify)
- `ac14/acceptance.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_llm_codegen.py` (modify)
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

1. Make the fixture-backed LLM codegen surface blueprint-aware so multi-blueprint
   `llm` tests do not collide on shared component IDs.
2. Prove one suite-level realistic-input `llm` acceptance artifact across
   shipped examples in the fixture-backed lane.
3. Keep suite artifacts explicit about fixture-backed scope and non-default
   status.
4. Expose any required CLI/Make surfaces cleanly.
5. Run full verification and lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_llm_codegen.py` | `test_generate_component_module_with_llm_uses_blueprint_aware_fixture_env` | Fixture-backed LLM codegen can disambiguate repeated component IDs across blueprints |
| `tests/test_acceptance.py` | `test_build_realistic_suite_acceptance_report_supports_llm_mode` | Suite-level realistic-input `llm` acceptance persists across shipped examples |
| `tests/test_cli.py` | `test_cli_acceptance_review_realistic_suite_with_llm_runs_end_to_end` | CLI surface supports suite-level realistic-input `llm` breadth |
| `tests/test_make_targets.py` | `test_make_acceptance_review_realistic_suite_with_llm_runs_end_to_end` | Make surface supports suite-level realistic-input `llm` breadth |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `tests/test_acceptance.py::test_build_acceptance_report_supports_realistic_input_llm_mode` | Single-slice `llm` realistic-input acceptance remains intact |
| `tests/test_acceptance.py::test_build_realistic_mode_comparison_report_supports_llm` | Per-blueprint realistic-input comparison remains intact |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [ ] Fixture-backed LLM codegen is blueprint-aware rather than only component-ID-aware.
- [ ] AC14 can persist one suite-level realistic-input acceptance artifact in `llm` mode across shipped examples.
- [ ] CLI and Make expose the widened `llm` breadth lane without manual glue.
- [ ] The docs state clearly that this is bounded proof breadth, not live default readiness.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

- Keep this lane honest: breadth is the goal, not inflated claims about live
  `llm` reliability.
- Do not silently reuse fixture module code across blueprints when embedded
  state differs. Fail loud if the fixture payload is ambiguous.

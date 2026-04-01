# Plan #4: Realistic-Input Front-Half Acceptance

**Status:** In Progress
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 has strong artifact discipline for discovery, planning,
probing, draft authoring, freeze decisions, and end-to-end acceptance on frozen
blueprints, but it still lacks one persisted artifact that judges the whole
front half on a realistic discovered input.

**Target:** AC14 can run discovery through freeze decision on a real input file,
persist every intermediate artifact, and then produce a front-half acceptance
review that judges whether the requirements, discovered input, dependency
choices, draft decomposition, and freeze state look sound.

**Why:** The current front half is still weaker than the back half. This lane
proves that AC14 can do meaningful, reviewable work on real input data before a
finished frozen system exists.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion rule
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis on realistic-input acceptance
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current statement that the front half is still weaker than the back half
- `docs/UNCERTAINTIES.md` - realistic-input and semantic-review uncertainties
- `docs/TODO.md` - current control surface
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should track the real lane
- `ac14/acceptance.py` - current semantic acceptance patterns
- `ac14/discovery.py` - realistic input inspection surface
- `ac14/dependency_planning.py` - dependency-planning artifact
- `ac14/dependency_execution.py` - dependency execution probes
- `ac14/blueprint_planning.py` - draft planning artifact
- `ac14/draft_authoring.py` - draft bundle and freeze readiness surface
- `ac14/freeze_decision.py` - explicit freeze decision artifact
- `ac14/__main__.py` - current CLI surface
- `Makefile` - current operator surface

---

## Open Questions

### Q1: Should front-half acceptance require freeze approval?
**Status:** Resolved
**Why it matters:** Realistic input acceptance should still be useful even when
the first draft bundle is blocked by known provisional gaps.
**Resolution:** No. The front-half review should assess whether the pipeline
looks requirements-sound and promising, even when freeze is blocked.

### Q2: Should front-half acceptance replace full-system acceptance?
**Status:** Resolved
**Why it matters:** AC14 still needs frozen-blueprint acceptance later; this
lane should strengthen the front half, not redefine the whole validation model.
**Resolution:** No. This is a complementary front-half artifact, not a
replacement for blueprint-level acceptance review.

### Q3: What counts as a realistic input for the first lane?
**Status:** Resolved
**Why it matters:** The proof should move beyond tiny single-record toy inputs
without requiring full messy-corpus ingestion yet.
**Resolution:** Use a small but plausibly realistic multi-record structured
input file and persist it as a shipped example input.

---

## Files Affected

- `ac14/front_half_acceptance.py` (create)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `prompts/review_front_half_acceptance.yaml` (create)
- `examples/support_ticket_digest/input/realistic_ticket_batch.json` (create)
- `tests/test_front_half_acceptance.py` (create)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Add a front-half acceptance artifact that runs discovery, dependency plan,
   dependency probe, draft planning, draft authoring, and freeze decision on a
   realistic input file.
2. Add a structured LLM review that judges the whole front-half result against
   the requirements and current freeze state.
3. Expose the lane through CLI and Make and add one shipped realistic input.
4. Add deterministic fixture-backed tests for the artifact and operator surface.
5. Run full verification and lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_report_runs_pipeline` | Front-half acceptance persists the full realistic-input pipeline and review |
| `tests/test_cli.py` | `test_cli_front_half_acceptance_runs_end_to_end` | CLI surface runs the lane end to end |
| `tests/test_make_targets.py` | `test_make_front_half_acceptance_runs_end_to_end` | Make surface runs the lane end to end |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `tests/test_acceptance.py` | Existing semantic review surface stays coherent |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [ ] AC14 can persist a realistic-input front-half acceptance artifact from discovery through freeze decision.
- [ ] The artifact includes a structured LLM review of the front-half result against requirements.
- [ ] CLI and Make expose the lane without manual glue code.
- [ ] A shipped realistic input file exists for at least one example slice.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

- This lane should strengthen the front half without pretending the provisional
  draft bundle is already a production-ready frozen system.
- The review should stay complementary to later full-system acceptance rather
  than replacing it.

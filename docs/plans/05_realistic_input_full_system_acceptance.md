# Plan #5: Realistic-Input Full-System Acceptance

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 now persists a realistic-input front-half acceptance artifact
from discovery through freeze decision, but the strongest realistic-input
artifact still stops before running the resulting system outputs through a final
requirements-aware acceptance review.

**Target:** AC14 can take realistic input data, run it through a chosen frozen
or shipped blueprint execution mode, persist the outputs, and then add a final
LLM acceptance review that judges those outputs against explicit requirements.

**Why:** The user-facing thesis is not just that AC14 can plan and freeze
systems from realistic inputs. It also needs to judge whether the resulting
system behavior on realistic input looks sensible, useful, and aligned with the
requirements.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and current proof-expansion rule
- `docs/AC14_ROADMAP.md` - Horizon 1 and Horizon 2 priorities
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current statement that semantic validation is weaker than desired at the final gate
- `docs/UNCERTAINTIES.md` - realistic-input and semantic-review uncertainties
- `docs/TODO.md` - active control surface
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should track the real lane
- `ac14/acceptance.py` - current blueprint-level semantic acceptance surface
- `ac14/front_half_acceptance.py` - current realistic-input front-half acceptance surface
- `ac14/recomposition.py` - scenario execution and output persistence
- `ac14/reference_components.py` - reference execution mode
- `ac14/generated_codegen.py` - deterministic and LLM-backed generated execution modes
- `ac14/models.py` - scenario and evaluator definitions
- `examples/support_ticket_digest/` - current realistic-input slice

---

## Open Questions

### Q1: Should the first full-system realistic-input lane require front-half approval?
**Status:** Resolved
**Why it matters:** The realistic-input full-system lane should strengthen final
acceptance, not wait for a perfect front half before providing evidence.
**Resolution:** No. The first lane should be able to consume a shipped/frozen
blueprint plus realistic input and still provide a final acceptance verdict even
if a separate front-half artifact remains blocked.

### Q2: Which execution modes should the first lane support?
**Status:** Resolved
**Why it matters:** Supporting every mode immediately would increase surface
area before the artifact shape is proven.
**Resolution:** Start with `reference` only. Defer `deterministic` and `llm`
until the realistic-input final-acceptance artifact is proven on the narrowest
honest slice.

### Q3: Where should realistic-input expectations live?
**Status:** Resolved
**Why it matters:** The final acceptance lane needs explicit realistic-input
fixtures without hardcoding them in code.
**Resolution:** Keep realistic-input examples as persisted input artifacts and
wire them into the acceptance surface via explicit artifact paths.

---

## Files Affected

- `ac14/acceptance.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
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

1. Extend the acceptance surface so one realistic-input artifact can persist
   actual system outputs for a chosen blueprint and mode.
2. Add a final structured LLM review that judges those realistic-input outputs
   against explicit requirements.
3. Expose the lane through CLI and Make with one shipped realistic-input slice.
4. Add deterministic fixture-backed tests for the artifact and operator
   surface.
5. Run full verification and lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_acceptance.py` | `test_build_acceptance_report_supports_realistic_input_artifact` | One realistic-input acceptance artifact persists outputs plus final review |
| `tests/test_cli.py` | `test_cli_acceptance_review_with_realistic_input_runs_end_to_end` | CLI surface runs the realistic-input full-system acceptance lane |
| `tests/test_make_targets.py` | `test_make_acceptance_review_with_realistic_input_runs_end_to_end` | Make surface runs the realistic-input full-system acceptance lane |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `tests/test_front_half_acceptance.py` | Front-half realistic-input lane stays coherent |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [x] AC14 can persist a realistic-input full-system acceptance artifact that includes actual outputs and final semantic review.
- [x] The first lane works in `reference` mode.
- [x] CLI and Make expose the lane without manual glue code.
- [x] At least one shipped realistic-input slice is exercised by the new lane.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

- This lane should strengthen final realistic-input acceptance without replacing
  the separate front-half artifact.
- The first slice should stay narrow and reuse shipped/frozen blueprints rather
  than trying to solve messy blueprint derivation and final acceptance in one
  jump.

# Plan #83: Structured Spec Input Contract

**Status:** In Progress
**Type:** implementation
**Priority:** Critical
**Blocked By:** 82
**Blocks:** None

---

## Gap

**Current:** AC14 discovery is good at local data artifacts and directory
inputs, but it does not yet accept a richer structured specification artifact
as the front-half input for blueprint drafting.

**Target:** Add one minimal structured-spec input contract that lets AC14
accept a structured specification document plus bounded human context for draft
blueprint planning.

**Why:** This is the smallest honest implementation slice toward the
front-half-first empirical contract and toward consumer surfaces like
theory-forge.

---

## Acceptance Criteria

- [ ] AC14 has one explicit structured-spec input contract for draft planning.
- [ ] The contract is bounded and reviewable; it does not pretend to be a full
      free-prose NL-to-blueprint system.
- [ ] The next benchmark or consumer lane can build on this contract directly.

---

## References Reviewed

- `docs/plans/82_front_half_first_empirical_contract.md`
- `ac14/blueprint_planning.py`
- `ac14/discovery.py`
- `ac14/draft_authoring.py`
- `ac14/__main__.py`
- `prompts/draft_blueprint_plan.yaml`
- `tests/test_blueprint_planning.py`
- `~/projects/theory-forge/docs/plans/08_ac14_codegen_integration.md`

---

## Open Questions

### Q1: Should this lane replace discovery as the only front-half input?
**Status:** Resolved
**Why it matters:** Replacing discovery would create unnecessary instability in
an already verified path.
**Resolution:** No. The structured-spec contract should be a parallel input
surface for draft planning, not a refactor of the existing discovery path.

### Q2: What is the smallest truthful structured-spec surface?
**Status:** Resolved
**Why it matters:** The contract should be useful for front-half benchmarking
without pretending broad NL-to-blueprint capability already exists.
**Resolution:** Accept one persisted structured-spec artifact containing:
- system metadata and purpose
- explicit requirements
- bounded business rules
- declared inputs and outputs
- bounded workflow/component hints
- optional human context notes

### Q3: What downstream surface must consume this contract first?
**Status:** Resolved
**Why it matters:** The lane should terminate in a real consumer, not a dead
artifact format.
**Resolution:** Draft blueprint planning is the first consumer. The resulting
planning artifact must preserve enough provenance for later draft authoring and
freeze stages.

---

## Files Affected

- `docs/plans/83_structured_spec_input_contract.md` (update)
- `ac14/structured_spec.py` (create)
- `ac14/blueprint_planning.py` (modify)
- `ac14/draft_authoring.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `prompts/draft_blueprint_plan.yaml` (modify)
- `tests/test_structured_spec.py` (create)
- `tests/test_blueprint_planning.py` (modify)
- `tests/test_draft_authoring.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Define and persist one bounded structured-spec artifact model.
2. Add a parallel draft-planning entrypoint that consumes that artifact.
3. Preserve provenance so draft authoring and freeze can still trace the plan
   back to its source.
4. Expose the new surface through CLI and Make.
5. Verify with targeted tests before touching broader empirical lanes.

---

## Required Tests

| Command | Why |
|---------|-----|
| `python -m pytest -q tests/test_structured_spec.py tests/test_blueprint_planning.py tests/test_draft_authoring.py tests/test_cli.py tests/test_make_targets.py` | Proves the new structured-spec contract, planning integration, provenance, and operator surfaces |
| `python -m mypy ac14 tests` | Keeps the new contract typed and consistent |
| `python -m ruff check ac14 tests` | Keeps the new lane clean and reviewable |

---

## Notes

This lane is intentionally smaller than broad NL-to-blueprint. It is the first
truthful front-half input contract, not the final front-half schema.

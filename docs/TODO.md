# AC14 TODO

Status: Active control surface
Last updated: 2026-03-30

## Short-Term Active Lane

- [x] Phase 1: freeze the scenario-and-acceptance lane
  - [x] strengthen `CLAUDE.md` for explicit scenario semantics and final acceptance
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md` with new phases and success criteria
  - [x] keep this TODO as the running control surface during implementation
  - Success criteria: the active lane is documented honestly and can run without stop-and-ask interpretation

- [x] Phase 2: make scenario semantics explicit
  - [x] add explicit scenario kinds and evaluator definitions to the blueprint model
  - [x] stop using naming heuristics where scenario metadata can be explicit
  - [x] update shipped examples to use the explicit scenario contract
  - Success criteria: full-recomposition, negative, and semantic-acceptance scenarios are distinguished by blueprint data rather than inference

- [x] Phase 3: strengthen coverage validation
  - [x] require every component to have fixture coverage
  - [x] require every blueprint to have explicit end-to-end scenarios
  - [x] require at least one realistic-input acceptance path
  - Success criteria: weak fixture/scenario coverage fails loud during validation

- [x] Phase 4: add requirements-aware semantic acceptance
  - [x] implement a persisted acceptance artifact for semantic-acceptance scenarios
  - [x] use `llm_client` with prompts-as-data and structured output for final review
  - [x] expose acceptance through CLI and Make
  - Success criteria: AC14 can run realistic inputs through the system and produce an LLM-backed acceptance artifact against scenario requirements

- [x] Phase 5: verify and lock the lane
  - [x] add deterministic tests for scenario semantics, coverage validation, and acceptance artifacts
  - [x] run full `pytest -q`
  - [x] run full `python -m mypy ac14 tests`
  - [x] run full `python -m ruff check ac14 tests`
  - [x] update TODO and plan docs to reflect actual final state
  - Success criteria: local verification passes and the control docs match the implemented lane

## Logged Uncertainties

- the generated component logic is still semantic-responsibility-specific rather than general synthesis
- realistic-input acceptance will still be synthetic-but-plausible until the pre-freeze discovery layer exists
- proof breadth is still narrow even though the suite now has multiple blueprints
- live LLM acceptance may be too expensive for the default gate and may remain optional outside targeted runs

## Latest Verified Results

- full lane verification passed:
  - `pytest -q` passed with `57 passed`
  - `python -m mypy ac14 tests` passed on 42 source files
  - `python -m ruff check ac14 tests` passed
- targeted lane verification passed:
  - `pytest -q tests/test_validation.py tests/test_acceptance.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- `pytest -q` passed
- `python -m mypy ac14 tests` passed
- `python -m ruff check ac14 tests` passed
- live unit smoke for `tests/test_live_llm_codegen.py` passed
- live CLI generation with `python -m ac14 generate-components ... --generator llm` passed
- targeted recomposition-proof tests passed after removing example-specific proof assumptions
- targeted suite discovery, suite proof, suite comparison, CLI, and Make tests passed
- `pytest -q` passed with `43 passed`
- `python -m mypy ac14 tests` passed on 35 source files
- `python -m ruff check ac14 tests` passed
- targeted reference, semantic comparison, recommendation, CLI, and Make tests passed
- `pytest -q` passed with `50 passed`
- `python -m mypy ac14 tests` passed on 40 source files
- `python -m ruff check ac14 tests` passed

## Longer-Term Next Steps

- [ ] widen proof breadth beyond the current ticket-digest slice
- [ ] add the pre-freeze discovery layer for data inspection, schema discovery, and dependency/doc/repo context

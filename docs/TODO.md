# AC14 TODO

Status: Active control surface
Last updated: 2026-03-30

## Short-Term Active Lane

- [ ] Phase 1: freeze the draft-authoring lane
  - [ ] update `CLAUDE.md` to make draft blueprint authoring the active proof-expansion rule
  - [ ] refresh `docs/AC14_NEXT_24_HOURS.md` with authoring phases and success criteria
  - [ ] keep this TODO as the running control surface during implementation
  - Success criteria: the active lane is documented honestly and can run without stop-and-ask interpretation

- [ ] Phase 2: materialize the draft bundle
  - [ ] generate a six-file draft bundle from the persisted planning artifact
  - [ ] synthesize explicit placeholders where freeze-time data is still missing
  - [ ] keep the draft bundle distinct from frozen proof artifacts
  - Success criteria: AC14 can turn a persisted planning artifact into a concrete draft bundle on disk

- [ ] Phase 3: add freeze-readiness reporting
  - [ ] run validation-backed readiness checks against the draft bundle
  - [ ] add authoring-specific findings for placeholders and unresolved planning questions
  - [ ] persist the readiness report next to the draft bundle
  - Success criteria: AC14 can explain why a draft bundle is or is not freeze-ready

- [ ] Phase 4: operator surface and lock
  - [ ] expose draft authoring through CLI and Make
  - [ ] add deterministic tests for authoring and readiness
  - [ ] run full `pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update TODO and plan docs to reflect actual final state
  - Success criteria: local verification passes and the control docs match the implemented lane

## Logged Uncertainties

- the generated component logic is still semantic-responsibility-specific rather than general synthesis
- realistic-input acceptance will still be synthetic-but-plausible until the pre-freeze discovery layer exists
- proof breadth is still narrow even though the suite now has multiple blueprints
- live LLM acceptance may be too expensive for the default gate and may remain optional outside targeted runs
- discovery will start with local input inspection and environment/dependency planning before broader doc/repo retrieval is implemented
- the next bridge will produce draft planning artifacts, not claim that blueprint freeze is solved
- the next bridge will materialize draft bundles and readiness reports, not claim those drafts are frozen

## Latest Verified Results

- discovery-to-plan lane verification passed:
  - `pytest -q` passed with `69 passed`
  - `python -m mypy ac14 tests` passed on 46 source files
  - `python -m ruff check ac14 tests` passed
- targeted planning verification passed:
  - `pytest -q tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- discovery lane verification passed:
  - `pytest -q` passed with `66 passed`
  - `python -m mypy ac14 tests` passed on 44 source files
  - `python -m ruff check ac14 tests` passed
- targeted discovery verification passed:
  - `pytest -q tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
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
- [ ] connect draft planning artifacts into actual blueprint authoring and freeze transitions
- [ ] extend discovery beyond local files into shared doc/repo/dependency retrieval surfaces
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

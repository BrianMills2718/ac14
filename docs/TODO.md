# AC14 TODO

Status: Active control surface
Last updated: 2026-03-30

## Short-Term Active Lane

- [x] Phase 1: freeze the freeze-decision lane
  - [x] update `CLAUDE.md` to make freeze decisioning the active proof-expansion rule
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md` with freeze-decision phases and success criteria
  - [x] keep this TODO as the running control surface during implementation
  - Success criteria: the active lane is documented honestly and can run without stop-and-ask interpretation

- [x] Phase 2: add the freeze decision artifact
  - [x] persist an explicit approve/block artifact for freeze decisions
  - [x] support decisions driven by readiness reports
  - [x] support decisions on already-authored bundles without a readiness report
  - Success criteria: AC14 can explain in one artifact why a bundle is approved or blocked

- [x] Phase 3: add promotion behavior
  - [x] promote approved bundles into a frozen-bundle directory
  - [x] keep blocked bundles from promoting
  - [x] expose the same surface through CLI and Make
  - Success criteria: approved bundles promote deterministically and blocked bundles fail loud without silent promotion

- [x] Phase 4: verify and lock the lane
  - [x] add deterministic tests for freeze decisions and promotion
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
- discovery will start with local input inspection and environment/dependency planning before broader doc/repo retrieval is implemented
- the next bridge will produce draft planning artifacts, not claim that blueprint freeze is solved
- the next bridge will materialize draft bundles and readiness reports, not claim those drafts are frozen
- the next bridge will decide and promote only when approval is explicit; it still does not broaden proof breadth

## Latest Verified Results

- freeze-decision lane verification passed:
  - `pytest -q` passed with `78 passed`
  - `python -m mypy ac14 tests` passed on 50 source files
  - `python -m ruff check ac14 tests` passed
- targeted freeze-decision verification passed:
  - `pytest -q tests/test_freeze_decision.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- draft-authoring lane verification passed:
  - `pytest -q` passed with `73 passed`
  - `python -m mypy ac14 tests` passed on 48 source files
  - `python -m ruff check ac14 tests` passed
- targeted draft-authoring verification passed:
  - `pytest -q tests/test_draft_authoring.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
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
- [ ] make freeze decisions richer than pass/block by connecting them to actual authoring loops
- [ ] extend discovery beyond local files into shared doc/repo/dependency retrieval surfaces
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

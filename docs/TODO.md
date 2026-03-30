# AC14 TODO

Status: Active control surface
Last updated: 2026-03-30

## Short-Term Active Lane

- [x] Phase 1: freeze the pre-freeze discovery lane
  - [x] update `CLAUDE.md` to make discovery the active proof-expansion rule
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md` with discovery phases and success criteria
  - [x] keep this TODO as the running control surface during implementation
  - Success criteria: the active lane is documented honestly and can run without stop-and-ask interpretation

- [x] Phase 2: add discovery artifacts
  - [x] define a persisted discovery artifact for local inputs, inferred schemas, and open concerns
  - [x] distinguish discovery outputs from frozen blueprints so draft work does not masquerade as proof
  - [x] capture realistic samples and inferred field structure from local files
  - Success criteria: AC14 can inspect local inputs and persist a discovery artifact before blueprint freeze

- [x] Phase 3: plan dependencies and environment needs
  - [x] inventory the current environment relevant to a discovery run
  - [x] represent dependency needs and installation status as explicit artifact data
  - [x] expose discovery and environment planning through CLI and Make
  - Success criteria: AC14 can persist what libraries/context it already has and what still needs to be installed or researched

- [x] Phase 4: verify and lock the discovery slice
  - [x] add deterministic tests for discovery parsing, schema inference summaries, and dependency planning
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

## Latest Verified Results

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
- [ ] connect discovery artifacts back into blueprint freeze and packet planning
- [ ] extend discovery beyond local files into shared doc/repo/dependency retrieval surfaces
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

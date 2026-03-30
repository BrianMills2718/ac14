# AC14 TODO

Status: Active control surface
Last updated: 2026-03-30

## Short-Term Active Lane

- [ ] Phase 1: freeze the discovery-to-draft-planning lane
  - [ ] update `CLAUDE.md` to make draft blueprint planning the active proof-expansion rule
  - [ ] refresh `docs/AC14_NEXT_24_HOURS.md` with planning phases and success criteria
  - [ ] keep this TODO as the running control surface during implementation
  - Success criteria: the active lane is documented honestly and can run without stop-and-ask interpretation

- [ ] Phase 2: add the draft blueprint planning artifact
  - [ ] define a persisted planning artifact that consumes discovery output and requirements
  - [ ] keep the draft artifact distinct from frozen blueprint proof artifacts
  - [ ] persist proposed schemas, components, bindings, scenarios, and packetization notes
  - Success criteria: AC14 can turn a discovery artifact into a reviewable draft blueprint planning artifact

- [ ] Phase 3: expose discovery-to-plan operator surface
  - [ ] add a CLI entrypoint for draft blueprint planning
  - [ ] add a Make target for the same surface
  - [ ] add deterministic tests that validate the planning artifact contract without live LLM calls
  - Success criteria: the draft planning surface is invokable and testable locally

- [ ] Phase 4: verify and lock the lane
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

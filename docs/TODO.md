# AC14 TODO

Status: Active control surface
Last updated: 2026-03-29

## Short-Term Active Lane

- [x] Phase 1: freeze the semantic-comparison lane
  - [x] strengthen `CLAUDE.md` for semantic comparison and explicit default decisions
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md` with new phases and success criteria
  - [x] keep this TODO as the running control surface during implementation
  - Success criteria: the active lane is documented honestly and can run without stop-and-ask interpretation

- [x] Phase 2: generalize the reference lane
  - [x] derive reference runtime configuration from blueprint fixtures rather than one hard-coded example
  - [x] make the reference runtime reusable across the shipped suite
  - [x] preserve fail-loud behavior when a blueprint does not support the current reference component family
  - Success criteria: reference execution works on every shipped example in the current semantic family

- [x] Phase 3: add semantic comparison artifacts
  - [x] build blueprint-level semantic comparison across reference and generator modes
  - [x] build suite-level semantic comparison aggregates
  - [x] persist machine-readable semantic comparison artifacts
  - Success criteria: AC14 can report semantic agreement with expected outputs and with the reference lane

- [x] Phase 4: make the default-generator decision explicit
  - [x] define promotion criteria for the LLM generator
  - [x] build a persisted default-generator recommendation artifact
  - [x] expose the recommendation through CLI and Make
  - Success criteria: the repo can answer "what should be the default generator today?" from local evidence

- [ ] Phase 5: verify and lock the lane
  - [ ] add deterministic tests for reference generalization, semantic comparison, and recommendation artifacts
  - [ ] run full `pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update TODO and plan docs to reflect actual final state
  - Success criteria: local verification passes and the control docs match the implemented lane

## Logged Uncertainties

- the generated component logic is still semantic-responsibility-specific rather than general synthesis
- blueprint scenarios do not currently carry an explicit "full recomposition" flag, so suite execution must infer runnable scenarios conservatively
- negative scenarios may remain packet-only if they do not provide enough information for a whole-graph run
- the shipped suite is still one semantic-responsibility family even though it now has multiple blueprints
- live LLM semantic comparison may be too expensive for the default gate and may remain optional

## Latest Verified Results

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

## Longer-Term Next Steps

- [ ] widen semantic-responsibility coverage beyond the current ticket-digest slice

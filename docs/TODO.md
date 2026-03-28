# AC14 TODO

Status: Active control surface
Last updated: 2026-03-28

## Short-Term Active Lane

- [x] Phase 1: freeze the suite-proof plan
  - [x] strengthen `CLAUDE.md` for the proof-expansion lane
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md` with explicit phases and success criteria
  - [x] keep this TODO as the running source of truth while the lane executes
  - Success criteria: docs describe the active lane honestly and phases can be executed without stopping for interpretation

- [x] Phase 2: remove example-specific proof assumptions
  - [x] replace hard-coded recomposition fixture/component assumptions with blueprint-driven scenario execution
  - [x] define what makes a scenario runnable for full recomposition proof
  - [x] preserve fail-loud behavior for negative or underspecified scenarios
  - Success criteria: generated proof execution no longer depends on `support_ticket_digest`-specific component ids or fixture ids

- [ ] Phase 3: ship broader blueprint coverage
  - [ ] add example discovery or registry for shipped blueprints
  - [ ] add at least one additional shipped blueprint bundle
  - [ ] ensure the second bundle exercises the existing semantic responsibilities without relying on copied proof artifacts
  - Success criteria: AC14 can enumerate more than one shipped blueprint and execute the full local proof lane on each

- [ ] Phase 4: add suite-level evidence and comparison
  - [ ] add suite proof runner across shipped examples
  - [ ] add aggregate suite comparison across generator modes
  - [ ] persist machine-readable suite artifacts
  - Success criteria: one CLI/Make surface can produce a suite-level proof artifact and comparison artifact

- [ ] Phase 5: verify and lock the lane
  - [ ] add deterministic unit tests for suite discovery, suite proof, and suite comparison
  - [ ] run full `pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update TODO and plan docs to reflect the actual final state
  - Success criteria: all local verification passes and the control docs match the implemented state

## Logged Uncertainties

- the generated component logic is still semantic-responsibility-specific rather than general synthesis
- blueprint scenarios do not currently carry an explicit "full recomposition" flag, so suite execution must infer runnable scenarios conservatively
- negative scenarios may remain packet-only if they do not provide enough information for a whole-graph run
- the second shipped example should widen proof coverage without forcing a new semantic-responsibility family in the same lane
- live LLM suite comparison may be too expensive for the default gate and may remain optional

## Latest Verified Results

- `pytest -q` passed
- `python -m mypy ac14 tests` passed
- `python -m ruff check ac14 tests` passed
- live unit smoke for `tests/test_live_llm_codegen.py` passed
- live CLI generation with `python -m ac14 generate-components ... --generator llm` passed
- targeted recomposition-proof tests passed after removing example-specific proof assumptions

## Longer-Term Next Steps

- [ ] compare deterministic, LLM, and reference outputs with richer semantic checks
- [ ] decide whether any suite lane should promote the LLM generator from optional to default
- [ ] widen semantic-responsibility coverage beyond the current ticket-digest slice

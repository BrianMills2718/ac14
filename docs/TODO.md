# AC14 TODO

Status: Active control surface
Last updated: 2026-03-28

## Short-Term Active Lane

- [x] Phase 1: executable proof surface plan/doc alignment
  - [x] strengthen `CLAUDE.md` continuation language
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md`
  - [x] create and maintain this TODO ledger

- [x] Phase 2: evidence bundle packaging
  - [x] package blueprint snapshot, packet summaries, generated package manifest, packet-test report, recomposition result, and fresh-run summary
  - [x] persist bundle to disk from one callable entrypoint
  - [x] verify bundle contents in tests

- [x] Phase 3: CLI surface
  - [x] `python -m ac14 verify-blueprint`
  - [x] `python -m ac14 generate-components`
  - [x] `python -m ac14 prove-example`
  - [x] `python -m ac14 fresh-runs`
  - [x] verify CLI behavior in tests

- [x] Phase 4: Make-driven proof lane
  - [x] add domain make targets for proof commands
  - [x] add smoke tests for end-to-end execution
  - [x] confirm clean local operator workflow

- [x] Phase 5: final verification and evidence
  - [x] `pytest -q`
  - [x] `python -m mypy ac14 tests`
  - [x] `python -m ruff check ac14 tests`
  - [x] update TODO states and plan progress

## Logged Uncertainties

- generated code is still proof-slice-specific and deterministic
- CLI output format should stay simple unless a stronger operator workflow is required
- evidence bundle schema can evolve later if more than one example is added

## Longer-Term Next Steps

- [ ] add first true LLM-backed generator that consumes codegen contexts
- [ ] widen proof surface beyond the shipped example
- [ ] add richer evidence comparison between reference and generated implementations

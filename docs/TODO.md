# AC14 TODO

Status: Active control surface
Last updated: 2026-03-28

## Short-Term Active Lane

- [x] Phase 1: LLM generator planning surface
  - [x] strengthen `CLAUDE.md` for the LLM-generator lane
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md` with new phases
  - [x] preserve deterministic generator as explicit control

- [x] Phase 2: structured LLM-backed generator
  - [x] add prompt YAML for component generation
  - [x] add structured response model
  - [x] implement `llm_client`-backed generator from `CodegenContext`
  - [x] fail loud on malformed or unsupported output

- [x] Phase 3: operator surface integration
  - [x] add generator selection to CLI
  - [x] add generator selection to Make targets
  - [x] keep deterministic generator as the default unless explicitly overridden

- [x] Phase 4: verification
  - [x] deterministic unit tests for the LLM generator path using controlled mocks
  - [x] optional live smoke path if environment and keys support it
  - [x] full `pytest -q`
  - [x] full `mypy`
  - [x] full `ruff`

- [x] Phase 5: generator comparison evidence
  - [x] compare deterministic and LLM-backed generated packages
  - [x] persist comparison artifacts to disk
  - [x] expose comparison through CLI and Make
  - [x] verify comparison artifact contents in tests

## Logged Uncertainties

- generated code is still proof-slice-specific and deterministic
- CLI output format should stay simple unless a stronger operator workflow is required
- evidence bundle schema can evolve later if more than one example is added
- live LLM availability may vary by environment; this is not a blocker for the local contract lane
- live comparison across all components may cost more than the local smoke path

## Latest Verified Results

- `pytest -q` passed
- `python -m mypy ac14 tests` passed
- `python -m ruff check ac14 tests` passed
- live unit smoke for `tests/test_live_llm_codegen.py` passed
- live CLI generation with `python -m ac14 generate-components ... --generator llm` passed

## Longer-Term Next Steps

- [ ] compare deterministic vs LLM-backed generator outputs more deeply
- [ ] widen proof surface beyond the shipped example
- [ ] add richer evidence comparison between reference and generated implementations

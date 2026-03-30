# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-29

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The first honest slice is already in place:

1. six-file blueprint bundle
2. canonical models and loader
3. B1 validation
4. packet compilation and B2 validation
5. manual recomposition proof
6. packet-local test materialization
7. packet-to-codegen-context projection
8. deterministic generated-component flow
9. executable proof surface
10. `llm_client`-backed generator with prompt YAML and structured output
11. persisted comparison artifacts for one shipped example

The suite-proof lane is complete. The next gap is that comparison is still too
shallow: it mostly records pass/fail and module hashes, and the repo still has
no explicit evidence-backed answer for whether the LLM generator should become
the default anywhere.

## Progress Update

Completed:

1. suite-proof lane closed cleanly
2. shipped suite now has more than one blueprint
3. CLI and Make can prove and compare the shipped suite
4. reference runtime generalized across the shipped suite
5. blueprint-level and suite-level semantic comparison artifacts
6. explicit default-generator recommendation surface
7. targeted verification for reference, semantic, recommendation, CLI, and Make paths

Next:

1. full repo verification
2. final doc lock for the semantic-comparison lane

## Execution Rule

Do not stop because of uncertainty that can be documented.

If something is underspecified:

1. record it in this file and `docs/TODO.md`
2. choose the smallest thesis-preserving option
3. continue immediately

Only stop if the next step would clearly contradict the frozen AC14 spec.

## Phases

### Phase 1: Control Surface Reset

Deliverables:

- updated `CLAUDE.md`
- updated `docs/TODO.md`
- updated this plan with explicit phase criteria

Acceptance criteria:

- the active lane is described honestly
- each phase has explicit success criteria
- the TODO ledger can be used as the running control surface without extra explanation

### Phase 2: Generalized Reference Lane

Deliverables:

- blueprint-derived reference runtime configuration
- reference execution support across the shipped suite
- fail-loud handling for unsupported blueprint shapes

Acceptance criteria:

- reference execution works on every shipped example in the current semantic family
- no reference path remains tied to one example's fixture ids or static maps

### Phase 3: Semantic Comparison Artifacts

Deliverables:

- per-blueprint semantic comparison report
- suite-level semantic comparison report
- machine-readable artifacts capturing agreement with expected outputs and reference outputs

Acceptance criteria:

- deterministic comparison can run across the shipped suite locally
- semantic mismatches are explicit and attributable by scenario and mode

### Phase 4: Default-Generator Decision

Deliverables:

- promotion criteria for the LLM generator
- persisted default-generator recommendation artifact
- CLI and Make entrypoints for the decision surface

Acceptance criteria:

- the repo can answer the default-generator question from local artifacts
- the decision remains deterministic unless stronger evidence justifies change

### Phase 5: Verification And Lock

Deliverables:

- deterministic unit tests for generic proof and suite execution
- updated TODO/plan state
- clean local verification

Acceptance criteria:

- `pytest -q` passes
- `python -m mypy ac14 tests` passes
- `python -m ruff check ac14 tests` passes
- docs match the implemented state

## Known Uncertainties

1. blueprint scenarios still do not declare an explicit recomposition-proof mode
2. the shipped suite is still only one semantic family
3. live suite-wide LLM semantic comparison may remain optional if cost or latency is too high
4. recommendation logic should stay conservative until broader evidence exists

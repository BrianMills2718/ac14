# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-30

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

The semantic-comparison lane is complete. The next gap is that scenario meaning,
coverage requirements, and final semantic acceptance are still too implicit.
The repo can compare outputs, but it still infers too much about which
scenarios are runnable, which are negative, and what counts as final acceptance.

## Progress Update

Completed:

1. semantic-comparison lane closed cleanly
2. blueprint-level and suite-level semantic comparison artifacts
3. explicit default-generator recommendation surface
4. full repo verification after that lane

Next:

1. explicit scenario kinds and evaluator definitions
2. stronger fixture and acceptance coverage rules
3. requirements-aware semantic acceptance artifacts

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

### Phase 2: Explicit Scenario Semantics

Deliverables:

- blueprint-level scenario kinds
- evaluator definitions
- shipped examples updated to the explicit scenario model

Acceptance criteria:

- scenario meaning is explicit in the blueprint
- negative and full-system scenarios are not distinguished by naming conventions

### Phase 3: Coverage Validation

Deliverables:

- fixture coverage checks for every component
- explicit full-system scenario requirements
- realistic-input acceptance requirement

Acceptance criteria:

- missing coverage fails loud during validation
- shipped examples satisfy the stronger coverage contract

### Phase 4: Requirements-Aware Semantic Acceptance

Deliverables:

- persisted acceptance artifact for semantic-acceptance scenarios
- `llm_client`-backed review prompt and structured result
- CLI and Make entrypoints for final acceptance

Acceptance criteria:

- AC14 can run a semantic-acceptance scenario and persist an LLM review artifact
- the review is tied to requirements and actual outputs, not just generic judgment

### Phase 5: Verification And Lock

Deliverables:

- deterministic tests for scenario semantics, coverage, and acceptance artifacts
- updated TODO/plan state
- clean local verification

Acceptance criteria:

- `pytest -q` passes
- `python -m mypy ac14 tests` passes
- `python -m ruff check ac14 tests` passes
- docs match the implemented state

## Known Uncertainties

1. realistic-input acceptance is still bounded by the current synthetic shipped examples
2. the shipped suite is still only one semantic family
3. live LLM acceptance may remain optional if cost or latency is too high
4. the pre-freeze discovery layer still does not exist in the implementation

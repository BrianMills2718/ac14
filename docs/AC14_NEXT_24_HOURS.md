# AC14 Next 24 Hours

Status: Complete
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

Delivered in this lane:

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

## Lane Outcome

Completed:

1. blueprint scenarios now carry explicit `kind`, `evaluator_ids`, `realistic_input`, and requirements fields
2. validation now fails loud when components lack fixtures, when blueprints lack end-to-end coverage, and when semantic-acceptance scenarios omit LLM review requirements
3. recomposition and packet-test surfaces now use explicit scenario metadata instead of scenario-id naming heuristics
4. semantic-acceptance review is implemented as a persisted `llm_client`-backed artifact with prompts-as-data and structured output
5. CLI and Make now expose `acceptance-review` and `acceptance-review-suite`
6. deterministic regression tests cover the new scenario, validation, and acceptance surface

Verification:

1. `pytest -q tests/test_validation.py tests/test_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
2. `python -m mypy ac14 tests` passed
3. `python -m ruff check ac14 tests` passed
4. full repo verification passed:
   - `pytest -q` passed with `57 passed`
   - `python -m mypy ac14 tests` passed on 42 source files
   - `python -m ruff check ac14 tests` passed

Next lane:

1. widen proof breadth beyond the current ticket-digest slice
2. add the pre-freeze discovery layer for data inspection, schema discovery, dependency planning, library installation, and doc/repo retrieval
3. connect that discovery layer back into blueprint freeze without weakening the anti-drift hierarchy

## Known Uncertainties

1. realistic-input acceptance is still bounded by the current synthetic shipped examples
2. proof breadth is still narrow even though the suite has multiple blueprints
3. live LLM acceptance may remain optional if cost or latency is too high
4. the pre-freeze discovery layer still does not exist in the implementation

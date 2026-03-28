# AC14 Next 24 Hours

Status: Completed
Last updated: 2026-03-28

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

The current gap is not "more generation." It is that proof is still too tied to
one shipped example. This lane broadens proof coverage and removes the remaining
example-specific execution assumptions.

## Progress Update

Completed:

1. control-surface reset for the suite-proof lane
2. blueprint-driven recomposition scenario inference
3. removal of hard-coded `support_ticket_digest` recomposition assumptions
4. targeted proof/lint/type checks for the generic recomposition path
5. shipped blueprint discovery and second bundled example
6. suite-level proof and comparison artifacts
7. CLI and Make support for suite workflows
8. targeted suite verification across discovery, CLI, Make, and aggregate artifacts

Next:

1. richer semantic comparison between reference, deterministic, and LLM-backed outputs
2. decision on whether any suite lane should promote LLM generation from optional to default
3. broader semantic-responsibility coverage beyond the current ticket-digest family

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

### Phase 2: Generic Recomposition Proof

Deliverables:

- blueprint-driven recomposition scenario selection
- removal of hard-coded example-specific fixture/component assumptions
- fail-loud handling for non-runnable scenarios

Acceptance criteria:

- recomposition proof logic works from blueprint structure and fixtures
- generated proof execution is no longer tied to `support_ticket_digest` internals
- negative or incomplete scenarios are either rejected loudly or skipped under explicit rules

### Phase 3: Multi-Example Coverage

Deliverables:

- example discovery or registry
- at least one additional shipped blueprint bundle
- proof execution across more than one blueprint

Acceptance criteria:

- AC14 can enumerate the shipped blueprint suite
- the full local proof lane passes on each shipped blueprint

### Phase 4: Suite Artifacts And Operator Surface

Deliverables:

- suite-level proof runner
- suite-level comparison runner
- CLI and Make targets for suite execution
- persisted machine-readable suite artifacts

Acceptance criteria:

- operator can prove the shipped suite without importing Python modules manually
- operator can compare generator modes across the suite from the CLI/Make surface
- suite artifacts record per-example and aggregate results

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

1. blueprint scenarios do not currently declare an explicit recomposition-proof mode
2. the second shipped example should broaden coverage without forcing a new semantic-responsibility family in the same lane
3. live suite-wide LLM comparison may remain optional if cost or latency is too high
4. richer semantic comparison can remain a later lane after suite execution is honest

# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-30

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The draft planning lane is now complete. The next honest gap is that AC14 can
propose decomposition from discovery, but it still cannot turn that plan into a
real draft bundle or say explicitly why the bundle is not freeze-ready.

The immediate goal is a narrow, explicit authoring bridge:

1. draft planning artifact in
2. six-file draft bundle out
3. freeze-readiness report out

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. explicit scenario semantics and semantic acceptance
3. pre-freeze discovery for local inputs and environment planning
4. discovery-to-draft blueprint planning

Next:

1. materialize a six-file draft bundle from the planning artifact
2. run freeze-readiness checks against that draft bundle
3. expose the authoring surface through CLI and Make

## Execution Rule

Do not stop because of uncertainty that can be documented.

If something is underspecified:

1. record it in this file and `docs/TODO.md`
2. choose the smallest thesis-preserving option
3. continue immediately

Only stop if the next step would clearly contradict the frozen AC14 spec or the
anti-drift doctrine.

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

### Phase 2: Draft Bundle Authoring

Deliverables:

- deterministic draft bundle authoring from the planning artifact
- six YAML files written to disk
- default authoring placeholders where freeze-time information is still missing

Acceptance criteria:

- AC14 can materialize a draft bundle from a persisted planning artifact
- the draft bundle stays clearly distinct from the frozen proof surface

### Phase 3: Freeze Readiness

Deliverables:

- freeze-readiness report
- validation-backed findings against the draft bundle
- authoring-specific findings for placeholders and unresolved questions

Acceptance criteria:

- AC14 can explain why a draft bundle is or is not freeze-ready
- readiness findings are persisted as artifacts rather than implied by missing work

### Phase 4: Operator Surface And Lock

Deliverables:

- CLI and Make entrypoints for draft bundle authoring
- deterministic tests for authoring and readiness
- clean local verification

Acceptance criteria:

- `pytest -q` passes
- `python -m mypy ac14 tests` passes
- `python -m ruff check ac14 tests` passes
- docs match the implemented state

## Known Uncertainties

1. the first authoring bridge will synthesize placeholders for invariants, fixtures, and constraints that are still unresolved
2. draft bundles may intentionally fail freeze-readiness until fixtures and richer proof details are authored
3. broader proof breadth and retrieval expansion remain outside this narrow lane

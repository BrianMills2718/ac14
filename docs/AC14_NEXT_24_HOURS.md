# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-30

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The freeze-remediation lane is complete, but the shipped proof suite still
mostly demonstrates one ticket-digest workflow pattern. That is not enough
proof breadth for the broader decomposition thesis.

The immediate goal for this lane is a narrow proof-breadth bridge:

1. broaden the shipped suite beyond the ticket-digest slice
2. support the broader slice in the reference and deterministic lanes
3. replace `semantic family` wording with `proof breadth` wording where it is
   only acting as an evaluation heuristic

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery and draft planning
3. draft bundle authoring and freeze-readiness reporting
4. explicit freeze decisions, remediation tasks, and deterministic promotion

Required in this lane:

1. one additional shipped workflow with a distinct semantic-responsibility signature
2. reference and deterministic support for that new workflow
3. recommendation metrics and wording that describe proof breadth honestly

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

### Phase 2: Broader Shipped Example

Deliverables:

- one additional shipped blueprint bundle outside the ticket-digest vocabulary
- reference-runtime support for that bundle
- deterministic generator support for that bundle

Acceptance criteria:

- the new example passes blueprint validation, packet tests, recomposition proof,
  and semantic comparison
- the shipped suite now contains at least two distinct workflow signatures

### Phase 3: Proof-Breadth Terminology And Recommendation Surface

Deliverables:

- recommendation artifacts use `proof breadth` terminology instead of
  `semantic family`
- tests and docs reflect the broader suite honestly

Acceptance criteria:

- code and docs no longer imply that `semantic family` is core project ontology
- the default-generator recommendation reasons about proof breadth using the
  broader shipped suite

### Phase 4: Verification And Lock

Deliverables:

- clean local verification
- updated TODO/plan/README/KNOWLEDGE state
- clean committed repo state

Acceptance criteria:

- `pytest -q` passes
- `python -m mypy ac14 tests` passes
- `python -m ruff check ac14 tests` passes
- docs match the implemented state

## Known Uncertainties

1. the next breadth example may keep a similar graph shape while changing the
   workflow vocabulary and acceptance semantics
2. deterministic generation is still responsibility-specific, so each new
   shipped slice currently expands the hard-coded proof surface
3. retrieval/doc/repo expansion remains outside this narrow lane

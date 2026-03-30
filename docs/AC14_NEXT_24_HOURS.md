# AC14 Next 24 Hours

Status: Complete
Last updated: 2026-03-30

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The draft authoring lane was complete, but AC14 still could not produce an
explicit approve/block decision artifact for promotion.

The immediate goal for this lane was a narrow freeze-decision bridge:

1. draft bundle plus readiness report in
2. explicit freeze decision out
3. promoted frozen bundle only when approval is true

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery and draft planning
3. draft bundle authoring and freeze-readiness reporting

Delivered in this lane:

1. explicit approve/block freeze decision artifact
2. deterministic promotion path for approved bundles
3. CLI and Make surface for freeze decisions

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

### Phase 2: Freeze Decision Artifact

Deliverables:

- persisted approve/block decision artifact
- support for readiness-report-driven decisions
- support for direct freeze-candidate decisions on already-authored bundles

Acceptance criteria:

- AC14 can explain in one persisted artifact why a bundle is approved or blocked
- decision artifacts carry the blocking findings forward instead of discarding them

### Phase 3: Promotion Surface

Deliverables:

- deterministic promotion path for approved bundles
- no promotion when approval is false
- CLI and Make entrypoints for the same surface

Acceptance criteria:

- approved bundles are copied into a promoted frozen-bundle directory
- blocked bundles do not silently promote

### Phase 4: Verification And Lock

Deliverables:

- deterministic tests for freeze decisions and promotion
- clean local verification
- updated TODO/plan state

Acceptance criteria:

- `pytest -q` passes
- `python -m mypy ac14 tests` passes
- `python -m ruff check ac14 tests` passes
- docs match the implemented state

## Lane Outcome

Completed:

1. AC14 can build a persisted freeze decision artifact from either a readiness-backed draft bundle or a direct freeze candidate
2. decision artifacts preserve the blocking findings instead of reducing them to an implicit yes/no
3. approved bundles are promoted into a deterministic `frozen_bundle` directory
4. blocked bundles remain unpromoted without silent fallbacks
5. CLI and Make now expose `decide-freeze`
6. deterministic tests cover decision artifacts, promotion, CLI, and Make surfaces

Verification:

1. `pytest -q tests/test_freeze_decision.py tests/test_cli.py tests/test_make_targets.py` passed
2. `python -m mypy ac14 tests` passed on 50 source files
3. `python -m ruff check ac14 tests` passed
4. full repo verification passed with `78 passed`

Next lane:

1. make freeze decisions richer than pass/block by connecting them to actual authoring loops
2. widen proof breadth beyond the current ticket-digest slice
3. extend discovery beyond local files into shared doc/repo/dependency retrieval surfaces without coupling AC14 to agent-only MCP assumptions

## Known Uncertainties

1. the first freeze-decision bridge still relies on current proof-slice validation semantics
2. bundles with placeholders are expected to block rather than promote
3. broader proof breadth and retrieval expansion remain outside this narrow lane

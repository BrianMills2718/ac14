# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-31

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The dependency-planning lane is now complete. AC14 can inspect local inputs,
environment state, local project docs, external retrieval artifacts, and then
produce an explicit advisory dependency/library plan. The next missing piece is
to feed that plan back into draft blueprint planning and freeze preparation so
library decisions do not disappear into side artifacts.

The immediate goal for this lane is a dependency-aware planning bridge:

1. let draft blueprint planning consume an explicit dependency plan artifact
2. preserve the provenance between retrieval, dependency decisions, and draft planning
3. keep freeze-readiness aware of unresolved dependency questions

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery, draft planning, authoring, freeze remediation, and promotion
3. broader proof breadth across ticket and incident workflow slices
4. local project-context inventory inside discovery artifacts
5. persisted external web/repository retrieval artifacts with discovery integration
6. evidence-backed dependency and library planning artifacts

Required in this lane:

1. dependency-plan-aware draft blueprint planning artifact
2. CLI and Make surfaces for the enriched planning bridge
3. deterministic tests and persisted outputs

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

### Phase 2: Dependency-Aware Planning Artifact

Deliverables:

- draft blueprint planning can consume a dependency plan artifact
- persisted planning output records the dependency-plan provenance
- unresolved dependency questions are preserved as planning context

Acceptance criteria:

- draft planning no longer loses explicit dependency decisions
- operators can inspect how dependency choices influenced the draft plan

### Phase 3: Operator Surface And Tests

Deliverables:

- CLI and Make surfaces for dependency-aware planning
- deterministic tests for artifact persistence and provenance flow

Acceptance criteria:

- operators can build dependency-aware draft plans without manual glue code
- tests prove the handoff from discovery to dependency plan to draft plan

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

1. the first dependency-aware planning bridge should consume dependency plans, not execute installs
2. some dependency questions should remain open through draft planning rather than being prematurely forced closed
3. freeze readiness should surface unresolved dependency issues without silently mutating the dependency plan

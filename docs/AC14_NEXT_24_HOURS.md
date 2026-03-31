# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-31

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The shared-retrieval lane is now complete. AC14 can inspect local inputs,
environment state, local project docs, and persisted external retrieval
artifacts. The next missing piece is turning that context into explicit
dependency and library planning before blueprint freeze.

The immediate goal for this lane is a narrow dependency-planning bridge:

1. define a persisted dependency and library planning artifact
2. ground recommendations in discovery plus retrieved evidence
3. expose the planning bridge through the same operator surface as discovery

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery, draft planning, authoring, freeze remediation, and promotion
3. broader proof breadth across ticket and incident workflow slices
4. local project-context inventory inside discovery artifacts
5. persisted external web/repository retrieval artifacts with discovery integration

Required in this lane:

1. dependency/library planning artifact with explicit actions
2. CLI and Make surfaces for dependency planning
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

### Phase 2: Dependency Planning Artifact

Deliverables:

- persisted artifact shape for dependency/library planning
- evidence-backed actions such as `reuse`, `install`, `investigate`
- explicit provenance linking the recommendation to discovery and retrieval context

Acceptance criteria:

- dependency planning output is reviewable and persisted
- install/reuse decisions are tied to explicit evidence rather than hidden judgment

### Phase 3: Operator Surface And Tests

Deliverables:

- CLI and Make surfaces for the dependency-planning bridge
- deterministic tests for artifact persistence and planning behavior

Acceptance criteria:

- operators can produce dependency plans without manual glue code
- tests prove the planning bridge persists and loads cleanly

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

1. the first dependency-planning bridge should recommend actions, not perform installs automatically
2. some library choices will still require LLM judgment, but the artifact should preserve the evidence and open questions
3. dependency planning should stay part of blueprint freeze preparation rather than becoming a disconnected package-management workflow

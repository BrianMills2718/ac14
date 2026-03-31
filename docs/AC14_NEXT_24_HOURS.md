# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-31

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The proof-breadth lane is complete, but discovery still focuses almost entirely
on local input files plus package inventory. That is too thin for the longer
term vision where blueprint drafting should use repo docs, setup knowledge, and
other persisted context before freeze.

The immediate goal for this lane is a narrow discovery-context bridge:

1. persist local project-document context alongside input and environment context
2. expose that context through the same operator surface as discovery
3. keep the artifact reviewable so it can later compose with broader
   documentation/GitHub/web retrieval

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery and draft planning
3. draft bundle authoring, freeze remediation, and promotion
4. broader proof breadth across ticket and incident workflow slices

Required in this lane:

1. project-context inventory from local repo docs
2. discovery artifact integration for that project context
3. CLI, Make, and tests for the new context surface

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

### Phase 2: Project-Context Inventory

Deliverables:

- persisted inventory of local project docs
- compact document summaries suitable for blueprint planning review
- integration into the main discovery artifact

Acceptance criteria:

- discovery captures README/CLAUDE/docs context when `project_root` is available
- project-document context is persisted as a first-class artifact, not hidden in logs

### Phase 3: Operator Surface And Tests

Deliverables:

- CLI and Make surfaces for project-context inspection
- deterministic tests for inventory persistence and discovery integration

Acceptance criteria:

- operators can inspect project context without writing Python glue code
- tests cover discovery with project context plus the standalone context inventory

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

1. the first context bridge will stay local to the repo and will not yet claim
   GitHub/web/Context7 retrieval
2. local doc inventory is only a first context layer, not the whole pre-freeze
   research system
3. broader external retrieval should still persist reviewable artifacts rather
   than acting as opaque prompt stuffing

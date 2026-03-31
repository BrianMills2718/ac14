# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-31

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The discovery-context lane is complete, but discovery still stops at local
inputs, package inventory, and local project docs. The longer-term system needs
reviewable retrieval artifacts for external documentation and repository search
before blueprint freeze.

The immediate goal for this lane is a narrow shared-retrieval bridge:

1. define persisted external retrieval artifacts
2. expose them through the same operator surface as discovery
3. keep them compatible with shared infrastructure rather than agent-only MCP assumptions

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery, draft planning, authoring, freeze remediation, and promotion
3. broader proof breadth across ticket and incident workflow slices
4. local project-context inventory inside discovery artifacts

Required in this lane:

1. retrieval artifact model for external docs/repo search
2. operator surfaces for the retrieval bridge
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

### Phase 2: Retrieval Artifact Model

Deliverables:

- persisted artifact shape for external documentation and repository retrieval
- integration points back into discovery and planning
- explicit provenance for what was searched and what was found

Acceptance criteria:

- retrieval output is reviewable and persisted
- discovery/planning can consume the artifact without scraping ad hoc logs

### Phase 3: Operator Surface And Tests

Deliverables:

- CLI and Make surfaces for the retrieval bridge
- deterministic tests for artifact persistence and integration

Acceptance criteria:

- operators can build retrieval artifacts without manual glue code
- tests prove the retrieval bridge persists and loads cleanly

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

1. the next bridge should still prefer shared library surfaces over agent-only
   MCP assumptions
2. GitHub/web/documentation retrieval will need persisted provenance to stay
   reviewable
3. dependency-install planning should stay tied to discovery rather than become
   a separate opaque side channel

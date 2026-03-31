# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-31

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The planning-artifact resynchronization lane is complete. AC14 now has an
AC14-native canonical notebook and a blunt implementation-status document. The
next missing piece is to probe whether advisory dependency decisions actually
work in the current environment.

The immediate goal for this lane is a dependency execution bridge:

1. define a persisted execution-probe artifact for dependency recommendations
2. execute reviewable reuse/install probes without hidden side effects
3. record post-probe environment state and blocking failures explicitly

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery, draft planning, authoring, freeze remediation, and promotion
3. broader proof breadth across ticket and incident workflow slices
4. local project-context inventory inside discovery artifacts
5. persisted external web/repository retrieval artifacts with discovery integration
6. evidence-backed dependency and library planning artifacts
7. dependency-aware draft planning with preserved dependency provenance

Required in this lane:

1. dependency execution-probe artifact
2. CLI and Make surfaces for advisory execution probing
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

### Phase 2: Dependency Execution Artifact

Deliverables:

- persisted execution-probe artifact for reuse/install recommendations
- explicit result states such as `confirmed`, `blocked`, `skipped`
- explicit post-probe environment observations

Acceptance criteria:

- dependency execution attempts are reviewable and persisted
- failures surface as explicit artifacts rather than silent shell behavior

### Phase 3: Operator Surface And Tests

Deliverables:

- CLI and Make surfaces for execution probing
- deterministic tests for probe persistence and fail-loud behavior

Acceptance criteria:

- operators can run dependency probes without manual glue code
- tests prove the probe artifact and failure handling

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

1. the first execution bridge should probe explicit recommendations, not attempt broad automatic environment mutation
2. install probes may need a dry-run or no-op mode for deterministic tests and cautious operation
3. environment deltas should be explicit artifacts so follow-on planning can inspect what changed

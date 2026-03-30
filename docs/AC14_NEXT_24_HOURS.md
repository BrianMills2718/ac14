# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-30

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The explicit freeze-decision lane is complete, but a blocked decision still
lands as a flat finding list. That is not yet a usable authoring loop.

The immediate goal for this lane is a narrow remediation bridge:

1. blocked freeze decision in
2. persisted authoring tasks out
3. explicit rerun path for bundle editing and freeze retry

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery and draft planning
3. draft bundle authoring and freeze-readiness reporting
4. explicit freeze approve/block decisions and deterministic promotion

Required in this lane:

1. persisted freeze-remediation artifact tied to each decision
2. actionable task grouping from readiness and validation findings
3. bundle-edit retry command so blocked drafts can move forward without
   stop-and-ask interpretation

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

### Phase 2: Freeze Remediation Artifact

Deliverables:

- persisted remediation artifact produced alongside freeze decisions
- actionable grouping from readiness and validation findings
- concrete target files and rerun commands in the remediation artifact

Acceptance criteria:

- a blocked freeze decision produces at least one remediation task
- tasks point at concrete bundle files or upstream planning artifacts
- remediation output explains how to retry freeze after edits

### Phase 3: CLI, Make, And Test Surface

Deliverables:

- `decide-freeze` emits remediation-path information
- Make surface exposes the same behavior
- deterministic tests cover blocked and approved cases

Acceptance criteria:

- CLI users can discover and read remediation artifacts without extra code
- Make-driven freeze decisions write the remediation artifact
- tests prove both blocked-worklist and approved-no-work paths

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

1. the first remediation loop will route humans through direct bundle editing
   and freeze retry, not through automated draft rewriting
2. some findings originate from draft authoring heuristics and may still need
   upstream planning changes in addition to bundle edits
3. broader proof breadth and retrieval expansion remain outside this narrow lane

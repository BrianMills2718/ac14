# AC14 Next 24 Hours

Status: Complete
Last updated: 2026-03-30

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The discovery lane is now complete. The next honest gap was that AC14 could
inspect inputs before blueprint freeze, but it still could not persist how
those findings should shape draft decomposition decisions.

The immediate goal for this lane was a narrow, explicit bridge:

1. discovery artifact in
2. LLM-backed draft blueprint planning artifact out
3. proposed schemas, components, bindings, scenarios, and packet notes captured explicitly

## Progress Update

Completed before this lane:

1. six-file blueprint bundle
2. canonical models and loader
3. packet compilation and proof surfaces
4. explicit scenario semantics and semantic acceptance
5. pre-freeze discovery for local inputs and environment planning

Delivered in this lane:

1. persisted draft blueprint planning artifact
2. prompt-as-data and structured-output planning call
3. CLI and Make surface for discovery-to-plan transition

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

### Phase 2: Draft Blueprint Planning Artifact

Deliverables:

- persisted draft planning artifact models
- prompt-as-data for discovery-to-plan transition
- structured-output planning call backed by `llm_client`

Acceptance criteria:

- AC14 can load a persisted discovery artifact and persist a draft blueprint planning artifact
- the draft artifact proposes schemas, components, bindings, scenarios, and packet notes
- the draft artifact remains explicitly separate from the frozen blueprint proof surface

### Phase 3: Operator Surface And Tests

Deliverables:

- CLI entrypoint for draft blueprint planning
- Make target for the same surface
- deterministic tests for the planning artifact and operator surface

Acceptance criteria:

- the planning surface is invokable without manual imports
- tests cover the planning artifact contract without relying on live LLM calls

### Phase 4: Verification And Lock

Deliverables:

- updated TODO/plan state
- clean local verification

Acceptance criteria:

- `pytest -q` passes
- `python -m mypy ac14 tests` passes
- `python -m ruff check ac14 tests` passes
- docs match the implemented state

## Lane Outcome

Completed:

1. AC14 can load a persisted discovery artifact and build a reviewable draft blueprint planning artifact
2. the draft artifact persists planning summary, proposed schemas, components, bindings, proof scenarios, packetization notes, dependency decisions, and open questions
3. the planning bridge uses prompt-as-data plus `llm_client` structured output
4. programmatic validation fails loud when the LLM proposes duplicate schemas/components or invalid binding references
5. CLI and Make now expose `draft-blueprint-plan`
6. deterministic tests cover the planning contract without relying on live LLM calls

Verification:

1. `pytest -q tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py` passed
2. `python -m mypy ac14 tests` passed on 46 source files
3. `python -m ruff check ac14 tests` passed
4. full repo verification passed with `69 passed`

Next lane:

1. connect draft planning artifacts into actual blueprint authoring and freeze transitions
2. widen proof breadth beyond the current ticket-digest slice
3. extend discovery beyond local files into shared doc/repo/dependency retrieval surfaces without coupling AC14 to agent-only MCP assumptions

## Known Uncertainties

1. this lane proposes draft decomposition; it does not claim blueprint freeze is solved
2. broader doc/repo retrieval remains out of scope for this narrow bridge
3. the first planning artifact may still lean on current proof-slice heuristics until proof breadth grows

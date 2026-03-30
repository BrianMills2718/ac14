# AC14 Next 24 Hours

Status: Complete
Last updated: 2026-03-30

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The scenario-and-acceptance lane is now complete. The next honest gap is the
front half of the thesis: AC14 still freezes blueprints without first inspecting
real local inputs or persisting what the environment already provides.

The immediate goal is not full autonomous research. The immediate goal is a
small, explicit pre-freeze discovery layer that:

1. inspects real local inputs
2. infers and summarizes likely schema structure
3. records open concerns before blueprint freeze
4. records dependency and environment needs before code generation

## Progress Update

Completed before this lane:

1. six-file blueprint bundle
2. canonical models and loader
3. B1 validation
4. packet compilation and B2 validation
5. deterministic and LLM-backed generation
6. recomposition proof
7. suite proof and comparison
8. explicit scenario semantics and requirements-aware semantic acceptance

Delivered in this lane:

1. persisted discovery artifact for local inputs
2. dependency and environment planning artifact
3. CLI and Make surface for pre-freeze discovery

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

### Phase 2: Discovery Artifact

Deliverables:

- persisted discovery artifact models
- local input inspection with compact schema summaries and example samples
- clear separation between discovery outputs and frozen blueprints

Acceptance criteria:

- AC14 can inspect local input files and persist a discovery artifact
- discovery findings are explicit enough to review before blueprint freeze
- inferred structure and open concerns are persisted, not only printed

### Phase 3: Dependency And Environment Planning

Deliverables:

- environment inventory relevant to discovery
- dependency planning artifact with installation status
- CLI and Make entrypoints for discovery and environment planning

Acceptance criteria:

- AC14 can record what libraries and runtime capabilities are already present
- missing dependencies or open context needs are persisted as explicit findings
- discovery can be run without importing the whole project manually

### Phase 4: Verification And Lock

Deliverables:

- deterministic tests for discovery artifacts and environment planning
- updated TODO/plan state
- clean local verification

Acceptance criteria:

- `pytest -q` passes
- `python -m mypy ac14 tests` passes
- `python -m ruff check ac14 tests` passes
- docs match the implemented state

## Lane Outcome

Completed:

1. AC14 can inspect local JSON, JSONL, CSV, YAML, and text inputs before blueprint freeze
2. discovery persists inferred field summaries, compact samples, and deterministic open concerns
3. environment inventory persists baseline project dependencies plus explicitly requested packages
4. missing dependencies are recorded as artifact data instead of staying implicit
5. CLI and Make now expose `discover-input` and `inspect-environment`
6. deterministic tests cover discovery parsing, environment planning, CLI, and Make surfaces

Verification:

1. `pytest -q tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py` passed
2. `python -m mypy ac14 tests` passed on 44 source files
3. `python -m ruff check ac14 tests` passed
4. full repo verification passed with `66 passed`

Next lane:

1. connect discovery artifacts back into blueprint freeze and packet planning
2. widen proof breadth beyond the current ticket-digest slice
3. extend discovery beyond local files into shared doc/repo/dependency retrieval surfaces without coupling AC14 to agent-only MCP assumptions

## Known Uncertainties

1. the first discovery slice will inspect local inputs only; broader doc/repo retrieval still needs a later shared-infra-aligned design
2. inferred schemas will start as pragmatic summaries, not a final universal schema language
3. environment planning may record unmet dependency needs before AC14 automates installation decisions
4. realistic example data is still bounded by the current shipped examples until the discovery layer is applied to external inputs

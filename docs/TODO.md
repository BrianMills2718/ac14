# AC14 TODO

Status: Active control surface
Last updated: 2026-03-31

The active implementation contract is:

- [Plan #1: Dependency Execution Probing](/home/brian/projects/ac14/docs/plans/01_dependency_execution_probing.md)

This file is the running checklist and short verification ledger for that plan.

Detailed uncertainty tracking now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

## Short-Term Active Lane

- [x] Phase 0: establish numbered planning surfaces
  - [x] create `docs/plans/`
  - [x] create `docs/plans/CLAUDE.md`
  - [x] create `docs/plans/TEMPLATE.md`
  - [x] convert the active lane into Plan #1
  - Success criteria: roadmap, active plan, and TODO no longer compete as parallel authorities

- [ ] Phase 1: add dependency execution probes
  - [ ] define a persisted dependency execution-probe artifact
  - [ ] keep probe results explicit with states such as confirmed, blocked, or skipped
  - [ ] record post-probe environment observations rather than only shell output
  - Success criteria: AC14 can test dependency recommendations without hiding side effects

- [ ] Phase 2: connect dependency execution into operator surfaces
  - [ ] expose the probing bridge through CLI and Make
  - [ ] add deterministic tests for artifact persistence and fail-loud probe behavior
  - Success criteria: operators can run dependency probes without manual glue code and the behavior is tested

- [ ] Phase 3: verify and lock the lane
  - [ ] run full `pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update TODO, plan, README, and KNOWLEDGE to reflect actual final state
  - Success criteria: local verification passes and the control docs match the implemented lane

## Current Open Uncertainties

- the dependency execution-probe result model is still open
- the acceptable amount of environment mutation in the first probe lane is still open
- the exact post-probe environment observations to persist are still open

## Latest Verified Results

- numbered planning surfaces now exist:
  - `docs/plans/CLAUDE.md`
  - `docs/plans/TEMPLATE.md`
  - `docs/plans/01_dependency_execution_probing.md`
- dedicated uncertainty tracking now exists:
  - `docs/UNCERTAINTIES.md`
- notebook governance tightening verification passed:
  - `notebooks/notebook_registry.yaml` parses successfully
  - `notebooks/01_ac14_execution_status_journey.ipynb` parses successfully
  - notebook code cells execute successfully from repo root
- detailed implementation reality and broader risk framing now live in [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md)
- planning-artifact resynchronization verification passed:
  - notebook JSON parsed successfully for `notebooks/01_ac14_execution_status_journey.ipynb`
  - notebook registry YAML parsed successfully for `notebooks/notebook_registry.yaml`
  - AC14-native canonical notebook and implementation-status doc now exist
- dependency-aware planning lane verification passed:
  - `pytest -q` passed with `93 passed`
  - `python -m mypy ac14 tests` passed on 54 source files
  - `python -m ruff check ac14 tests` passed
- targeted dependency-aware planning verification passed:
  - `pytest -q tests/test_blueprint_planning.py tests/test_draft_authoring.py tests/test_cli.py tests/test_make_targets.py -x` passed with `42 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- dependency-planning lane verification passed:
  - `pytest -q` passed with `91 passed`
  - `python -m mypy ac14 tests` passed on 54 source files
  - `python -m ruff check ac14 tests` passed
- targeted dependency-planning verification passed:
  - `pytest -q tests/test_dependency_planning.py tests/test_cli.py tests/test_make_targets.py -x` passed with `40 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- shared-retrieval lane verification passed:
  - `pytest -q` passed with `86 passed`
  - `python -m mypy ac14 tests` passed on 52 source files
  - `python -m ruff check ac14 tests` passed
- targeted shared-retrieval verification passed:
  - `pytest -q tests/test_retrieval.py tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py -x` passed with `43 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`

## Longer-Term Next Steps

- [ ] connect broader proof breadth to less hard-coded deterministic generation
- [ ] connect remediation tasks to automated draft-refinement loops when the current manual bundle-edit loop is proven
- [ ] feed dependency planning into draft planning and freeze readiness so library decisions stay explicit
- [ ] connect dependency planning to installation execution only after the advisory layer is proven
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

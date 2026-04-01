# AC14 TODO

Status: Active control surface
Last updated: 2026-03-31

The most recently completed implementation contracts are:

- [Plan #1: Dependency Execution Probing](/home/brian/projects/ac14/docs/plans/01_dependency_execution_probing.md)
- [Plan #2: Dependency Probe Integration](/home/brian/projects/ac14/docs/plans/02_dependency_probe_integration.md)

This file is the running checklist and short verification ledger for the current
or most recently completed plan.

Detailed uncertainty tracking now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

## Short-Term Active Lane

- [x] Phase 1: integrate dependency execution into draft planning
  - [x] accept a dependency execution artifact alongside the dependency plan
  - [x] persist confirmed probe summaries and blocked probe summaries in the draft planning artifact
  - [x] fail loud if a dependency execution artifact points at a different dependency plan than the one provided
  - Success criteria: draft planning artifacts carry usable probe evidence instead of dropping it

- [x] Phase 2: turn blocked dependency probes into freeze blockers
  - [x] add readiness findings for blocked dependency probes
  - [x] keep confirmed probe results as informative context, not blockers
  - [x] ensure readiness fails when blocked probe findings remain unresolved
  - Success criteria: blocked dependency evidence can stop freeze promotion explicitly

- [x] Phase 3: connect remediation and operator surfaces
  - [x] group dependency blockers into actionable freeze-remediation tasks
  - [x] expose the integrated path through CLI surfaces
  - [x] cover the new path with deterministic tests
  - Success criteria: operators can see and remediate dependency blockers without reading code

- [x] Phase 4: verify and lock the lane
  - [x] run targeted pytest for planning, authoring, freeze, CLI, and Make surfaces
  - [x] run full `python -m pytest -q`
  - [x] run full `python -m mypy ac14 tests`
  - [x] run full `python -m ruff check ac14 tests`
  - [x] update TODO, active plan, README, KNOWLEDGE, and uncertainties to reflect the implemented state
  - Success criteria: local verification passes and the docs match the integrated dependency-probe lane

## Current Open Uncertainties

- dependency probes now feed freeze, but broader install remediation remains deferred
- the next decision is whether blocked dependency remediation should stay manual or become a later controlled automation lane

## Latest Verified Results

- numbered planning surfaces now exist:
  - `docs/plans/CLAUDE.md`
  - `docs/plans/TEMPLATE.md`
  - `docs/plans/01_dependency_execution_probing.md`
- the new active lane is:
  - `docs/plans/02_dependency_probe_integration.md`
- targeted dependency-probe integration verification passed:
  - `python -m pytest -q tests/test_blueprint_planning.py tests/test_draft_authoring.py tests/test_freeze_decision.py tests/test_cli.py tests/test_make_targets.py -x` passed with `50 passed`
- dedicated uncertainty tracking now exists:
  - `docs/UNCERTAINTIES.md`
- notebook governance tightening verification passed:
  - `notebooks/notebook_registry.yaml` parses successfully
  - `notebooks/01_ac14_execution_status_journey.ipynb` parses successfully
  - notebook code cells execute successfully from repo root
- light enforcement now exists:
  - `meta-process.yaml`
  - `hooks/commit-msg`
  - `scripts/setup_hooks.sh`
- targeted dependency execution verification passed:
  - `pytest -q tests/test_dependency_execution.py tests/test_cli.py tests/test_make_targets.py -x` passed with `43 passed`
  - `python -m mypy ac14 tests` passed on `56` source files
  - `python -m ruff check ac14 tests` passed
- full verification passed:
  - `python -m pytest -q` passed with `101 passed`
  - `python -m mypy ac14 tests` passed on `56` source files
  - `python -m ruff check ac14 tests` passed
- current implementation reality and broader historical verification context live in [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md)

## Longer-Term Next Steps

- [ ] connect broader proof breadth to less hard-coded deterministic generation
- [ ] connect remediation tasks to automated draft-refinement loops when the current manual bundle-edit loop is proven
- [ ] feed dependency-probe integration into richer remediation and later draft-refinement loops
- [ ] connect dependency planning to installation execution only after the advisory layer is proven
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

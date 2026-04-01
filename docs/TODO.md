# AC14 TODO

Status: Active control surface
Last updated: 2026-03-31

The most recently completed implementation contracts are:

- [Plan #1: Dependency Execution Probing](/home/brian/projects/ac14/docs/plans/01_dependency_execution_probing.md)
- [Plan #2: Dependency Probe Integration](/home/brian/projects/ac14/docs/plans/02_dependency_probe_integration.md)
- [Plan #3: Meta-Process Dependency Probe Policy](/home/brian/projects/ac14/docs/plans/03_meta_process_dependency_probe_policy.md)
- [Plan #4: Realistic-Input Front-Half Acceptance](/home/brian/projects/ac14/docs/plans/04_realistic_input_front_half_acceptance.md)

This file is the running checklist and short verification ledger for the current
or most recently completed plan.

Detailed uncertainty tracking now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

## Short-Term Active Lane

- [x] Phase 1: add the realistic-input front-half artifact
  - [x] persist discovery, dependency planning, probing, draft planning, draft bundle, freeze decision, and final review paths together
  - [x] keep the final review separate from the underlying programmatic artifacts
  - Success criteria: one artifact shows the whole front-half chain for a real input file

- [x] Phase 2: add structured front-half review
  - [x] review the front-half result against explicit requirements
  - [x] allow promising-but-blocked front-half outcomes instead of requiring freeze approval
  - Success criteria: the front half gets a semantic verdict instead of only a collection of sub-artifacts

- [x] Phase 3: expose operator surfaces and shipped input
  - [x] add CLI and Make entrypoints
  - [x] add one shipped realistic input file for a current example slice
  - Success criteria: operators can run the lane without manual assembly

- [x] Phase 4: verify and lock the lane
  - [x] run targeted front-half acceptance tests
  - [x] run full `python -m pytest -q`
  - [x] run full `python -m mypy ac14 tests`
  - [x] run full `python -m ruff check ac14 tests`
  - [x] update TODO, active plan, README, KNOWLEDGE, and uncertainties to reflect the implemented state
  - Success criteria: verification passes and the docs match the realistic-input front-half lane

## Current Open Uncertainties

- realistic-input front-half acceptance now exists, but it is still synthetic-but-plausible rather than a broad messy-corpus proof
- the next decision after this lane is whether blocked dependency remediation should stay manual or become a later controlled automation lane

## Latest Verified Results

- numbered planning surfaces now exist:
  - `docs/plans/CLAUDE.md`
  - `docs/plans/TEMPLATE.md`
  - `docs/plans/01_dependency_execution_probing.md`
- the most recently completed lane before this one was:
  - `docs/plans/03_meta_process_dependency_probe_policy.md`
- the current completed lane is:
  - `docs/plans/04_realistic_input_front_half_acceptance.md`
- targeted realistic-input front-half acceptance verification passed:
  - `python -m pytest -q tests/test_front_half_acceptance.py tests/test_cli.py::test_cli_front_half_acceptance_runs_end_to_end tests/test_make_targets.py::test_make_front_half_acceptance_runs_end_to_end` passed with `3 passed`
- targeted dependency-probe integration verification passed:
  - `python -m pytest -q tests/test_blueprint_planning.py tests/test_draft_authoring.py tests/test_freeze_decision.py tests/test_cli.py tests/test_make_targets.py -x` passed with `50 passed`
- targeted meta-process policy verification passed:
  - `python -m pytest -q tests/test_meta_process_policy.py tests/test_draft_authoring.py -x` passed with `7 passed`
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
  - `python -m pytest -q` passed with `109 passed`
  - `python -m mypy ac14 tests` passed on `60` source files
  - `python -m ruff check ac14 tests` passed
- current implementation reality and broader historical verification context live in [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md)

## Longer-Term Next Steps

- [ ] connect broader proof breadth to less hard-coded deterministic generation
- [ ] connect remediation tasks to automated draft-refinement loops when the current manual bundle-edit loop is proven
- [ ] feed dependency-probe integration into richer remediation and later draft-refinement loops
- [ ] connect dependency planning to installation execution only after the advisory layer is proven
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

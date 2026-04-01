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

- [x] Phase 1: add realistic-input full-system acceptance artifact
  - [x] persist actual blueprint outputs for one realistic-input acceptance run
  - [x] keep the full-system acceptance artifact distinct from the front-half artifact
  - Success criteria: one artifact shows realistic inputs, actual outputs, and final review together

- [x] Phase 2: add final structured review
  - [x] review realistic-input outputs against explicit requirements
  - [x] support `reference` mode on the first honest slice
  - Success criteria: realistic-input system behavior gets a final semantic verdict instead of only raw outputs

- [x] Phase 3: expose operator surfaces
  - [x] add CLI and Make entrypoints or extend the existing acceptance surface cleanly
  - [x] wire at least one shipped realistic-input slice into the lane
  - Success criteria: operators can run the lane without manual assembly

- [x] Phase 4: verify and lock the lane
  - [x] run targeted realistic-input full-system acceptance tests
  - [x] run full `python -m pytest -q`
  - [x] run full `python -m mypy ac14 tests`
  - [x] run full `python -m ruff check ac14 tests`
  - [x] update TODO, active plan, README, KNOWLEDGE, and uncertainties to reflect the implemented state
  - Success criteria: verification passes and the docs match the realistic-input full-system acceptance lane

## Current Open Uncertainties

- realistic-input full-system acceptance now exists, but it is still `reference`-mode only
- realistic-input front-half acceptance now exists, but it is still synthetic-but-plausible rather than a broad messy-corpus proof
- the next decision after this lane is whether blocked dependency remediation should stay manual or become a later controlled automation lane

## Latest Verified Results

- numbered planning surfaces now exist:
  - `docs/plans/CLAUDE.md`
  - `docs/plans/TEMPLATE.md`
  - `docs/plans/01_dependency_execution_probing.md`
- the most recently completed lane before this one was:
  - `docs/plans/03_meta_process_dependency_probe_policy.md`
- the most recently completed lane is:
  - `docs/plans/05_realistic_input_full_system_acceptance.md`
- targeted realistic-input full-system acceptance verification passed:
  - `python -m pytest -q tests/test_acceptance.py::test_build_acceptance_report_supports_realistic_input_artifact tests/test_cli.py::test_cli_acceptance_review_with_realistic_input_runs_end_to_end tests/test_make_targets.py::test_make_acceptance_review_with_realistic_input_runs_end_to_end` passed with `3 passed`
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
  - `python -m pytest -q` passed with `112 passed`
  - `python -m mypy ac14 tests` passed on `60` source files
  - `python -m ruff check ac14 tests` passed
- current implementation reality and broader historical verification context live in [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md)

## Longer-Term Next Steps

- [ ] connect broader proof breadth to less hard-coded deterministic generation
- [ ] extend realistic-input full-system acceptance beyond `reference` mode
- [ ] connect remediation tasks to automated draft-refinement loops when the current manual bundle-edit loop is proven
- [ ] feed dependency-probe integration into richer remediation and later draft-refinement loops
- [ ] connect dependency planning to installation execution only after the advisory layer is proven
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

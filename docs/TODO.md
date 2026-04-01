# AC14 TODO

Status: Active control surface
Last updated: 2026-03-31

The most recently completed implementation contracts are:

- [Plan #1: Dependency Execution Probing](/home/brian/projects/ac14/docs/plans/01_dependency_execution_probing.md)
- [Plan #2: Dependency Probe Integration](/home/brian/projects/ac14/docs/plans/02_dependency_probe_integration.md)
- [Plan #3: Meta-Process Dependency Probe Policy](/home/brian/projects/ac14/docs/plans/03_meta_process_dependency_probe_policy.md)
- [Plan #4: Realistic-Input Front-Half Acceptance](/home/brian/projects/ac14/docs/plans/04_realistic_input_front_half_acceptance.md)
- [Plan #5: Realistic-Input Full-System Acceptance](/home/brian/projects/ac14/docs/plans/05_realistic_input_full_system_acceptance.md)
- [Plan #6: Realistic-Input Acceptance Breadth](/home/brian/projects/ac14/docs/plans/06_realistic_input_acceptance_breadth.md)
- [Plan #7: Realistic-Input LLM Acceptance](/home/brian/projects/ac14/docs/plans/07_realistic_input_llm_acceptance.md)

This file is the running checklist and short verification ledger for the active
plan.

Detailed uncertainty tracking now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

## Short-Term Active Lane

- [ ] Phase 1: blueprint-aware fixture-backed llm codegen
  - [ ] make LLM-codegen fixtures disambiguate repeated component IDs across blueprints
  - [ ] fail loud when a fixture payload is ambiguous for the current blueprint
  - Success criteria: multi-blueprint `llm` tests can run without hidden fixture collisions

- [ ] Phase 2: suite-level llm realistic-input acceptance
  - [ ] persist one realistic-input suite artifact in `llm` mode across shipped examples
  - [ ] keep the suite artifact explicit about its fixture-backed scope
  - Success criteria: one persisted artifact broadens `llm` realistic-input evidence beyond a single blueprint

- [ ] Phase 3: operator surface and lock
  - [ ] expose any widened CLI and Make surfaces cleanly
  - [ ] run targeted `llm` breadth tests
  - [ ] run full `python -m pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update TODO, active plan, README, KNOWLEDGE, and uncertainties to reflect the implemented state
  - Success criteria: verification passes and the docs match the `llm` breadth lane

## Current Open Uncertainties

- realistic-input full-system acceptance now has one `llm` slice, but suite-level `llm` breadth is still unproven
- realistic-input front-half acceptance now exists, but it is still synthetic-but-plausible rather than a broad messy-corpus proof
- fixture-backed `llm` codegen is still too narrow for multi-blueprint breadth because it keys by component ID only

## Latest Verified Results

- numbered planning surfaces now exist:
  - `docs/plans/CLAUDE.md`
  - `docs/plans/TEMPLATE.md`
  - `docs/plans/01_dependency_execution_probing.md`
- the most recently completed lane before this one was:
  - `docs/plans/03_meta_process_dependency_probe_policy.md`
- the current active lane is:
  - `docs/plans/06_realistic_input_acceptance_breadth.md`
- the most recently completed lane before this one was:
  - `docs/plans/05_realistic_input_full_system_acceptance.md`
- targeted realistic-input full-system acceptance verification passed:
  - `python -m pytest -q tests/test_acceptance.py::test_build_acceptance_report_supports_realistic_input_artifact tests/test_cli.py::test_cli_acceptance_review_with_realistic_input_runs_end_to_end tests/test_make_targets.py::test_make_acceptance_review_with_realistic_input_runs_end_to_end` passed with `3 passed`
- targeted deterministic realistic-input acceptance verification passed:
  - `python -m pytest -q tests/test_acceptance.py::test_build_acceptance_report_supports_realistic_input_deterministic_mode tests/test_cli.py::test_cli_acceptance_review_with_realistic_input_deterministic_mode_runs_end_to_end tests/test_make_targets.py::test_make_acceptance_review_with_realistic_input_deterministic_mode_runs_end_to_end` passed with `3 passed`
- targeted incident realistic-input acceptance verification passed:
  - `python -m pytest -q tests/test_acceptance.py::test_build_acceptance_report_supports_incident_realistic_input` passed with `1 passed`
- targeted realistic-input suite acceptance verification passed:
  - `python -m pytest -q tests/test_acceptance.py::test_build_realistic_suite_acceptance_report_supports_realistic_inputs tests/test_cli.py::test_cli_acceptance_review_realistic_suite_help tests/test_cli.py::test_cli_acceptance_review_realistic_suite_runs_end_to_end tests/test_make_targets.py::test_make_acceptance_review_realistic_suite_runs_end_to_end tests/test_make_targets.py::test_make_help_lists_proof_targets` passed with `5 passed`
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
- realistic-input acceptance breadth verification passed:
  - `python -m pytest -q` passed with `120 passed`
  - `python -m mypy ac14 tests` passed on `60` source files
  - `python -m ruff check ac14 tests` passed
- targeted realistic-input `llm` verification passed:
  - `python -m pytest -q tests/test_llm_codegen.py::test_generate_component_module_with_llm_uses_fixture_env tests/test_acceptance.py::test_build_acceptance_report_supports_realistic_input_llm_mode tests/test_acceptance.py::test_build_realistic_mode_comparison_report_supports_llm tests/test_cli.py::test_cli_acceptance_review_realistic_compare_help tests/test_cli.py::test_cli_acceptance_review_with_realistic_input_llm_mode_runs_end_to_end tests/test_cli.py::test_cli_acceptance_review_realistic_compare_runs_end_to_end tests/test_make_targets.py::test_make_help_lists_proof_targets tests/test_make_targets.py::test_make_acceptance_review_with_realistic_input_llm_mode_runs_end_to_end tests/test_make_targets.py::test_make_acceptance_review_realistic_compare_runs_end_to_end` passed with `9 passed`
  - `python -m mypy ac14/generated_codegen.py ac14/llm_codegen.py ac14/acceptance.py ac14/__main__.py tests/test_llm_codegen.py tests/test_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/generated_codegen.py ac14/llm_codegen.py ac14/acceptance.py ac14/__main__.py tests/test_llm_codegen.py tests/test_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `128 passed`
    - `python -m mypy ac14 tests` passed on `60` source files
    - `python -m ruff check ac14 tests` passed

## Longer-Term Next Steps

- [ ] connect broader proof breadth to less hard-coded deterministic generation
- [ ] connect remediation tasks to automated draft-refinement loops when the current manual bundle-edit loop is proven
- [ ] feed dependency-probe integration into richer remediation and later draft-refinement loops
- [ ] connect dependency planning to installation execution only after the advisory layer is proven
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

# AC14 TODO

Status: Active control surface
Last updated: 2026-04-01

The most recently completed implementation contracts are:

- [Plan #1: Dependency Execution Probing](/home/brian/projects/ac14/docs/plans/01_dependency_execution_probing.md)
- [Plan #2: Dependency Probe Integration](/home/brian/projects/ac14/docs/plans/02_dependency_probe_integration.md)
- [Plan #3: Meta-Process Dependency Probe Policy](/home/brian/projects/ac14/docs/plans/03_meta_process_dependency_probe_policy.md)
- [Plan #4: Realistic-Input Front-Half Acceptance](/home/brian/projects/ac14/docs/plans/04_realistic_input_front_half_acceptance.md)
- [Plan #5: Realistic-Input Full-System Acceptance](/home/brian/projects/ac14/docs/plans/05_realistic_input_full_system_acceptance.md)
- [Plan #6: Realistic-Input Acceptance Breadth](/home/brian/projects/ac14/docs/plans/06_realistic_input_acceptance_breadth.md)
- [Plan #7: Realistic-Input LLM Acceptance](/home/brian/projects/ac14/docs/plans/07_realistic_input_llm_acceptance.md)
- [Plan #8: LLM Realistic-Input Breadth](/home/brian/projects/ac14/docs/plans/08_llm_realistic_input_breadth.md)
- [Plan #9: Live LLM Readiness Boundary](/home/brian/projects/ac14/docs/plans/09_live_llm_readiness_boundary.md)
- [Plan #10: Packet Sufficiency Evidence](/home/brian/projects/ac14/docs/plans/10_packet_sufficiency_evidence.md)
- [Plan #11: Realistic-Input Default Gate](/home/brian/projects/ac14/docs/plans/11_realistic_input_default_gate.md)
- [Plan #12: Realistic-Input Suite Default Gate](/home/brian/projects/ac14/docs/plans/12_realistic_input_suite_default_gate.md)

This file is the running checklist and short verification ledger for the active
plan.

Detailed uncertainty tracking now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

## Short-Term Active Lane

- [ ] Phase 1: structured-input loading design
  - [ ] pre-make one shared structured-input contract for discovery and acceptance
  - [ ] pre-make the supported realistic-input formats and fail-loud boundary
  - Success criteria: the loading lane is explicit enough to implement without duplicating discovery-only helpers

- [ ] Phase 2: structured-input loading implementation
  - [ ] extract shared structured-input loading from discovery
  - [ ] reuse it from realistic-input acceptance and broaden default realistic-input discovery beyond `.json`
  - Success criteria: realistic-input acceptance can load structured non-JSON inputs without weakening the semantic-acceptance contract

- [ ] Phase 3: verification and lock
  - [ ] run targeted structured-input loading tests
  - [ ] run full `python -m pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update TODO, active plan, README, KNOWLEDGE, and implementation-status docs to reflect the lane
  - Success criteria: verification passes and the docs match Plan #26

## Current Open Uncertainties

- realistic-input front-half acceptance now exists, but it is still synthetic-but-plausible rather than a broad messy-corpus proof
- recommendation now consumes suite live-readiness evidence, but broader automatic dependency execution remains intentionally out of scope
- retry-aware messy-input front-half proof now exists, but full-system realistic-input acceptance still assumes top-level JSON lists

## Latest Verified Results

- numbered planning surfaces now exist:
  - `docs/plans/CLAUDE.md`
  - `docs/plans/TEMPLATE.md`
  - `docs/plans/01_dependency_execution_probing.md`
- the most recently completed lane before this one was:
  - `docs/plans/25_messy_input_retry_proof.md`
- the current active lane is:
  - `docs/plans/26_structured_realistic_input_loading.md`
- targeted messy-input retry verification passed:
  - `python -m pytest -q tests/test_front_half_acceptance.py::test_build_front_half_acceptance_report_supports_retry_freeze_on_messy_input tests/test_cli.py::test_cli_front_half_acceptance_supports_retry_freeze_on_messy_input tests/test_make_targets.py::test_make_front_half_acceptance_supports_retry_freeze_on_messy_input` passed with `3 passed`
  - `python -m mypy ac14/front_half_acceptance.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/front_half_acceptance.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
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
    - `python -m pytest -q` passed with `132 passed`
    - `python -m mypy ac14 tests` passed on `60` source files
    - `python -m ruff check ac14 tests` passed
- targeted live-readiness boundary verification passed:
  - `python -m pytest -q tests/test_recommendation.py tests/test_cli.py::test_cli_recommend_default_generator_deterministic_only tests/test_cli.py::test_cli_live_llm_readiness_reports_skipped_without_keys tests/test_make_targets.py::test_make_recommend_default_generator_deterministic_only tests/test_make_targets.py::test_make_live_llm_readiness_reports_skipped_without_keys` passed with `6 passed`
  - `python -m mypy ac14/recommendation.py ac14/__main__.py tests/test_recommendation.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/recommendation.py ac14/__main__.py tests/test_recommendation.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `135 passed`
    - `python -m mypy ac14 tests` passed on `60` source files
    - `python -m ruff check ac14 tests` passed
- targeted packet-sufficiency verification passed:
  - `python -m pytest -q tests/test_packets.py::test_build_packet_sufficiency_report_flags_complete_packet_context tests/test_cli.py::test_cli_packet_sufficiency_runs_end_to_end tests/test_make_targets.py::test_make_help_lists_proof_targets tests/test_make_targets.py::test_make_packet_sufficiency_runs_end_to_end` passed with `4 passed`
  - `python -m mypy ac14/packet_sufficiency.py ac14/__main__.py tests/test_packets.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/packet_sufficiency.py ac14/__main__.py tests/test_packets.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `138 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted realistic-input default-gate verification passed:
  - `python -m pytest -q tests/test_evidence_bundle.py tests/test_cli.py::test_cli_prove_example tests/test_make_targets.py::test_make_prove_example_runs_end_to_end` passed with `4 passed`
  - `python -m mypy ac14/evidence_bundle.py tests/test_evidence_bundle.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/evidence_bundle.py tests/test_evidence_bundle.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `139 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted realistic-input suite default-gate verification passed:
  - `python -m pytest -q tests/test_suite.py::test_build_suite_proof_report_for_deterministic_generator tests/test_cli.py::test_cli_prove_suite tests/test_make_targets.py::test_make_prove_suite_runs_end_to_end` passed with `3 passed`
  - `python -m mypy ac14/suite.py tests/test_suite.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/suite.py tests/test_suite.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `139 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted recommendation default-gate verification passed:
  - `python -m pytest -q tests/test_recommendation.py tests/test_cli.py::test_cli_recommend_default_generator_deterministic_only tests/test_make_targets.py::test_make_recommend_default_generator_deterministic_only` passed with `4 passed`
  - `python -m mypy ac14/recommendation.py tests/test_recommendation.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/recommendation.py tests/test_recommendation.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `139 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted suite live-readiness verification passed:
  - `python -m pytest -q tests/test_recommendation.py tests/test_cli.py::test_cli_live_llm_readiness_reports_skipped_without_keys tests/test_cli.py::test_cli_live_llm_readiness_suite_reports_skipped_without_keys tests/test_make_targets.py::test_make_help_lists_proof_targets tests/test_make_targets.py::test_make_live_llm_readiness_reports_skipped_without_keys tests/test_make_targets.py::test_make_live_llm_readiness_suite_reports_skipped_without_keys` passed with `8 passed`
  - `python -m mypy ac14/recommendation.py ac14/__main__.py tests/test_recommendation.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/recommendation.py ac14/__main__.py tests/test_recommendation.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `142 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted recommendation suite-live verification passed:
  - `python -m pytest -q tests/test_recommendation.py tests/test_cli.py::test_cli_recommend_default_generator_deterministic_only tests/test_make_targets.py::test_make_recommend_default_generator_deterministic_only` passed with `5 passed`
  - `python -m mypy ac14/recommendation.py tests/test_recommendation.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/recommendation.py tests/test_recommendation.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `142 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted freeze-semantic verification passed:
  - `python -m pytest -q tests/test_freeze_decision.py tests/test_front_half_acceptance.py tests/test_cli.py::test_cli_front_half_acceptance_runs_end_to_end tests/test_make_targets.py::test_make_front_half_acceptance_runs_end_to_end` passed with `6 passed`
  - `python -m mypy ac14/freeze_decision.py ac14/front_half_acceptance.py tests/test_freeze_decision.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/freeze_decision.py ac14/front_half_acceptance.py tests/test_freeze_decision.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `142 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted front-half-suite verification passed:
  - `python -m pytest -q tests/test_front_half_acceptance.py tests/test_cli.py::test_cli_front_half_acceptance_suite_runs_end_to_end tests/test_make_targets.py::test_make_front_half_acceptance_suite_runs_end_to_end` passed with `4 passed`
  - `python -m mypy ac14/front_half_acceptance.py ac14/__main__.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/front_half_acceptance.py ac14/__main__.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `145 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted messy-input front-half verification passed:
  - `python -m pytest -q tests/test_front_half_acceptance.py::test_build_front_half_acceptance_report_supports_messy_input_artifact` passed with `1 passed`
  - `python -m mypy tests/test_front_half_acceptance.py` passed
  - `python -m ruff check tests/test_front_half_acceptance.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `146 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted remediation verification passed:
  - `python -m pytest -q tests/test_dependency_execution.py tests/test_cli.py::test_cli_remediate_dependencies_runs_end_to_end tests/test_make_targets.py::test_make_remediate_dependencies_runs_end_to_end` passed with `5 passed`
  - `python -m mypy ac14/dependency_execution.py ac14/__main__.py tests/test_dependency_execution.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/dependency_execution.py ac14/__main__.py tests/test_dependency_execution.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `149 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted remediation hand-off verification passed:
  - `python -m pytest -q tests/test_blueprint_planning.py::test_build_draft_blueprint_plan_accepts_dependency_remediation_artifact tests/test_cli.py::test_cli_draft_blueprint_plan_accepts_dependency_remediation_artifact tests/test_make_targets.py::test_make_draft_blueprint_plan_accepts_dependency_remediation_artifact` passed with `3 passed`
  - `python -m mypy ac14/blueprint_planning.py ac14/__main__.py tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/blueprint_planning.py ac14/__main__.py tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py` passed
- targeted refinement verification passed:
  - `python -m pytest -q tests/test_blueprint_planning.py::test_refine_draft_blueprint_plan_from_freeze_remediation_preserves_provenance tests/test_cli.py::test_cli_refine_draft_blueprint_plan_runs_end_to_end tests/test_make_targets.py::test_make_refine_draft_blueprint_plan_runs_end_to_end` passed with `3 passed`
  - `python -m mypy ac14/blueprint_planning.py ac14/__main__.py tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/blueprint_planning.py ac14/__main__.py tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py` passed
  - full verification passed:
    - `python -m pytest -q` passed with `155 passed`
    - `python -m mypy ac14 tests` passed on `61` source files
    - `python -m ruff check ac14 tests` passed
- targeted retry-chain verification passed:
  - `python -m pytest -q tests/test_freeze_retry.py::test_build_freeze_retry_artifact_runs_refine_materialize_and_refreeze tests/test_cli.py::test_cli_retry_freeze_runs_end_to_end tests/test_make_targets.py::test_make_retry_freeze_runs_end_to_end` passed with `3 passed`
  - `python -m mypy ac14/freeze_retry.py ac14/__main__.py tests/test_freeze_retry.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/freeze_retry.py ac14/__main__.py tests/test_freeze_retry.py tests/test_cli.py tests/test_make_targets.py` passed
- targeted retry-aware front-half verification passed:
  - `python -m pytest -q tests/test_front_half_acceptance.py::test_build_front_half_acceptance_report_supports_retry_freeze tests/test_cli.py::test_cli_front_half_acceptance_supports_retry_freeze tests/test_make_targets.py::test_make_front_half_acceptance_supports_retry_freeze` passed with `3 passed`
  - `python -m mypy ac14/freeze_retry.py ac14/front_half_acceptance.py ac14/__main__.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/freeze_retry.py ac14/front_half_acceptance.py ac14/__main__.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
- targeted retry-aware suite verification passed:
  - `python -m pytest -q tests/test_front_half_acceptance.py::test_build_front_half_acceptance_suite_report_supports_retry_freeze tests/test_cli.py::test_cli_front_half_acceptance_suite_supports_retry_freeze tests/test_make_targets.py::test_make_front_half_acceptance_suite_supports_retry_freeze` passed with `3 passed`
  - `python -m mypy ac14/front_half_acceptance.py ac14/__main__.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed
  - `python -m ruff check ac14/front_half_acceptance.py ac14/__main__.py tests/test_front_half_acceptance.py tests/test_cli.py tests/test_make_targets.py` passed

## Longer-Term Next Steps

- [ ] connect broader proof breadth to less hard-coded deterministic generation
- [ ] broaden front-half acceptance into an explicit suite-level breadth artifact
- [ ] prove one messier-input front-half lane without hiding ambiguity in prompts
- [ ] turn dependency blockers into one explicit remediation lane instead of only diagnosis
- [ ] prove retry-aware front-half acceptance on the messy CSV slice
- [ ] remove JSON-only realistic-input assumptions from the final semantic gate
- [ ] prove messy-input full-system acceptance in non-LLM modes
- [ ] prove one bounded messy-input `llm` comparison lane without implying live readiness
- [ ] feed dependency-probe integration into richer remediation and later draft-refinement loops
- [ ] connect dependency planning to installation execution only after the advisory layer is proven
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

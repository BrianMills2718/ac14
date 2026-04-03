# AC14 TODO

Status: Active control surface
Last updated: 2026-04-02

This file is the running checklist for the active numbered plan, not a full
history log.

Detailed uncertainty tracking lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

The active implementation contract is:

- [Plan #71: Empirical Full-Trial Resume Integrity](/home/brian/projects/ac14/docs/plans/71_empirical_full_trial_resume_integrity.md)

The explicit active chain is:

- [Plan #67: Second-Gate Blocker Diagnosis](/home/brian/projects/ac14/docs/plans/67_second_gate_blocker_diagnosis.md) -> complete
- [Plan #68: Deterministic Exact-Match Semantic Review Policy](/home/brian/projects/ac14/docs/plans/68_deterministic_exact_match_semantic_review_policy.md) -> complete
- [Plan #69: Monolithic Input-Port Contract Validation](/home/brian/projects/ac14/docs/plans/69_monolithic_input_port_contract_validation.md) -> complete
- [Plan #70: Second-Gate Smoke Rerun](/home/brian/projects/ac14/docs/plans/70_second_gate_smoke_rerun.md) -> complete
- [Plan #71: Empirical Full-Trial Resume Integrity](/home/brian/projects/ac14/docs/plans/71_empirical_full_trial_resume_integrity.md) -> active
- if Plan #71 lands cleanly -> resume [Plan #66: Second-Gate Full Trial](/home/brian/projects/ac14/docs/plans/66_second_gate_full_trial.md)
- if rerun says `blocked_on_harness` or `blocked_on_infrastructure` -> freeze Plan #71 immediately

The experiment contract remains frozen in:

- [Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md)

The completed execution lanes are:

- [Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md)
- [Plan #43: Full Trial Gate](/home/brian/projects/ac14/docs/plans/43_full_trial_gate.md)
- [Plan #44: Verdict Interpretation and Next Horizon](/home/brian/projects/ac14/docs/plans/44_verdict_interpretation_and_next_horizon.md)
- [Plan #61: Executable Journey Notebook Remediation](/home/brian/projects/ac14/docs/plans/61_executable_journey_notebook_remediation.md)
- [Plan #62: Inconclusive Comparison Diagnosis](/home/brian/projects/ac14/docs/plans/62_inconclusive_comparison_diagnosis.md)
- [Plan #63: Runtime-First Comparison Contract](/home/brian/projects/ac14/docs/plans/63_runtime_first_comparison_contract.md)

The previously active propagation lane remains blocked:

- [Plan #37: Directory Divergence Front-Half Proof](/home/brian/projects/ac14/docs/plans/37_directory_divergence_front_half_proof.md)

## Short-Term Active Lane

- [x] Plan #63: freeze the runtime-first empirical comparison contract
  - Result: runtime outputs are now the primary trial-success gate and the next chain is explicit as Plans #64–#67

- [x] Plan #64: build the second-gate benchmark bundle
  - Result: `resource_scaling_v1` now exists with 13 components, four runtime cases, categorical-only final outputs, benchmark-local repair guidance, and full verification green

- [x] Plan #65: run the bounded smoke gate on the new benchmark
  - Result: `.ac14_out/full_trials_gate_2_smoke/smoke_readiness_report.json` exists with verdict `blocked_on_harness`

- [x] Plan #67: diagnose the blocked smoke artifact
  - Result: the blocker chain is now explicit as Plans #68-#70

- [x] Plan #68: make semantic review advisory for deterministic exact-match benchmarks
  - Result: exact-match runtime attempts can no longer fail solely because the semantic review says `concern`

- [x] Plan #69: add pre-emit monolithic input-port contract validation
  - Result: unknown `inputs[...]` ports now fail before runtime with persisted failed source

- [x] Plan #70: rerun the smoke gate after the harness fixes
  - Result: `.ac14_out/full_trials_gate_2_smoke_rerun/smoke_readiness_report.json` exists with verdict `ready_for_full_trials`

- [ ] Plan #71: make the interrupted full trial resume-safe and archive partial evidence

- [ ] Plan #66: spend the full five-trial budget and lock the second verdict with the repaired runner

## Current Open Uncertainties

- the first empirical gate is complete but inconclusive; AC14 still lacks a decisive empirical result in either direction
- the current comparison is still a bounded back-half gate over a fixed decomposition and should not be mistaken for the strongest end-to-end thesis test
- provider `503` demand noise appeared during the first full five-trial run and may contaminate secondary time/cost interpretation even though the primary success outcome completed
- the second gate is now open for full trials on the harder benchmark; the active question is what verdict the five-trial artifact will produce
- the current full-trial output directory contains partial zero-byte artifacts from an interrupted run, so the active blocker-clearing lane is restart integrity rather than benchmark semantics

## Latest Verified Baseline

- latest full code verification baseline:
  - `python -m pytest -q` with `250 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- latest empirical verification baseline:
  - `.ac14_out/full_trials_gate_1/experiment_decision.json` with verdict `inconclusive`
  - `.ac14_out/full_trials_gate_2_smoke/smoke_readiness_report.json` with verdict `blocked_on_harness`
  - `.ac14_out/full_trials_gate_2_smoke_rerun/smoke_readiness_report.json` with verdict `ready_for_full_trials`
  - `.ac14_out/full_trials_gate_2/` contains partial full-trial artifacts from an interrupted run and no final decision artifact yet
  - `ac14`: `2/5` successes on gate 1
  - `monolithic`: `2/5` successes on gate 1
- latest notebook/governance verification baseline:
  - both notebook JSON files parse cleanly
  - both notebooks' code cells execute top-to-bottom
  - `notebooks/notebook_registry.yaml` parses cleanly

## Longer-Term Next Steps

- [ ] complete Plan #71 and then complete Plan #66 to lock the second empirical verdict
- [ ] only after that decide whether the first benchmark should be retained, expanded, or replaced for broader proof breadth
- [ ] keep blocked propagation lanes blocked until the second empirical contract is executed honestly

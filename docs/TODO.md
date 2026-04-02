# AC14 TODO

Status: Active control surface
Last updated: 2026-04-02

This file is the running checklist for the active numbered plan, not a full
history log.

Detailed uncertainty tracking lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

The active implementation contract is:

- [Plan #63: Runtime-First Comparison Contract](/home/brian/projects/ac14/docs/plans/63_runtime_first_comparison_contract.md)

The immediate follow-on lane is:

- the implementation lane that executes the runtime-first comparison contract after Plan #63 freezes it

The experiment contract remains frozen in:

- [Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md)

The completed execution lanes are:

- [Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md)
- [Plan #43: Full Trial Gate](/home/brian/projects/ac14/docs/plans/43_full_trial_gate.md)
- [Plan #44: Verdict Interpretation and Next Horizon](/home/brian/projects/ac14/docs/plans/44_verdict_interpretation_and_next_horizon.md)
- [Plan #61: Executable Journey Notebook Remediation](/home/brian/projects/ac14/docs/plans/61_executable_journey_notebook_remediation.md)
- [Plan #62: Inconclusive Comparison Diagnosis](/home/brian/projects/ac14/docs/plans/62_inconclusive_comparison_diagnosis.md)

The previously active propagation lane remains blocked:

- [Plan #37: Directory Divergence Front-Half Proof](/home/brian/projects/ac14/docs/plans/37_directory_divergence_front_half_proof.md)

## Short-Term Active Lane

- [x] Plan #43: run the full five-trial gate
  - Result: `.ac14_out/full_trials_gate_1/experiment_decision.json` exists with verdict `inconclusive`

- [x] Plan #44: interpret the verdict and set the next horizon
  - Result: the next honest move is diagnosis and a sharper next comparison direction, not another same-benchmark micro-repair lane

- [x] Plan #62: diagnose why the first benchmark failed to separate the conditions
  - Result: the project now treats `order_exception_resolution` as one completed data point and freezes a sharper next empirical direction instead of defaulting back into the same repair loop

- [x] Plan #61: remediate the notebook surface after the verdict lock
  - Result: the empirical comparison notebook is artifact-backed, the status notebook is clearly governance-only, and the registry/docs are truthful

- [ ] Plan #63: freeze the runtime-first empirical comparison contract
  - Success criteria: final runtime output correctness becomes the primary gate, packet/recomposition reports stay explicit secondary evidence, and the comparison stays fair

## Current Open Uncertainties

- the first empirical gate is complete but inconclusive; AC14 still lacks a decisive empirical result in either direction
- the current comparison is still a bounded back-half gate over a fixed decomposition and should not be mistaken for the strongest end-to-end thesis test
- provider `503` demand noise appeared during the full five-trial run and may contaminate time/cost interpretation even though the primary success outcome completed
- the runtime-first contract still needs to be frozen before the next empirical rerun can begin

## Latest Verified Baseline

- latest full code verification baseline:
  - `python -m pytest -q` with `244 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- latest empirical verification baseline:
  - `.ac14_out/full_trials_gate_1/experiment_decision.json` with verdict `inconclusive`
  - `ac14`: `2/5` successes
  - `monolithic`: `2/5` successes
- latest notebook/governance verification baseline:
  - both notebook JSON files parse cleanly
  - both notebooks' code cells execute top-to-bottom
  - `notebooks/notebook_registry.yaml` parses cleanly

## Longer-Term Next Steps

- [ ] complete Plan #63 and then execute the runtime-first empirical rerun lane
- [ ] only after that decide whether the first benchmark should be retained, expanded, or replaced for broader proof breadth
- [ ] keep blocked propagation lanes blocked until the next empirical contract exists and is executed

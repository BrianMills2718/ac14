# AC14 TODO

Status: Active control surface
Last updated: 2026-04-01

This file is the running checklist for the active numbered plan, not a full
history log.

Detailed uncertainty tracking lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

The active implementation contract is:

- [Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md)

The experiment contract is frozen in:

- [Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md)

The previously active propagation lane remains blocked:

- [Plan #37: Directory Divergence Front-Half Proof](/home/brian/projects/ac14/docs/plans/37_directory_divergence_front_half_proof.md)

## Short-Term Active Lane

- [ ] Phase 1: benchmark asset bundle and validation
  - [ ] create `benchmarks/order_exception_resolution/`
  - [ ] write the requirements contract, input artifacts, allowed dependency surface, and evaluation harness
  - [ ] make the benchmark assets reviewable without chat context
  - [ ] validate that the benchmark blueprint, runtime inputs, and expected outputs load coherently
  - Success criteria: the experiment target exists as a bounded artifact bundle and the bundle loads cleanly

- [ ] Phase 2: monolithic condition
  - [ ] implement one runner for the `monolithic` condition
  - [ ] bound attempts, cost capture, and artifact persistence explicitly
  - [ ] persist monolithic outputs and pass/fail reasons
  - Success criteria: one monolithic trial can run end to end under the frozen fairness rules

- [ ] Phase 3: AC14 condition
  - [ ] implement one runner for the `AC14` condition
  - [ ] persist packet-test, recomposition, realistic-input, and output artifacts
  - [ ] preserve cost, time, repair loops, and pass/fail reasons
  - Success criteria: one AC14 trial can run end to end under the frozen fairness rules

- [ ] Phase 4: scoring and decision
  - [ ] apply the frozen primary outcome and secondary metrics
  - [ ] persist one final decision artifact with `ac14_wins`, `monolithic_wins`, or `inconclusive`
  - [ ] make the decision traceable back to per-trial evidence
  - Success criteria: the experiment result is artifact-backed rather than conversational

- [ ] Phase 5: repeated trials and lock
  - [ ] run 5 fresh paired trials
  - [ ] run full `python -m pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update status docs to reflect the result
  - Success criteria: the experiment is complete, verified, and reviewable

## Current Open Uncertainties

- AC14 still lacks executed comparison evidence even though the comparison contract is now frozen
- five paired fresh trials may still yield an inconclusive result
- the first ablation should isolate the decomposition claim itself; if full unrestricted front-half derivation starts to dominate the lane, that needs to be logged explicitly

## Latest Verified Baseline

- the repo is clean
- the most recent fully verified implementation state passed:
  - `python -m pytest -q` with `212 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- the most recently completed planning lane was:
  - [Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md)

## Longer-Term Next Steps

- [ ] run the experiment defined by Plan #39
- [ ] decide whether AC14 materially beats a fair monolithic baseline
- [ ] only then resume blocked propagation lanes such as Plan #37 if they still matter to the thesis

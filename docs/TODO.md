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

- [ ] Phase 1: benchmark asset bundle
  - [ ] create `benchmarks/order_exception_resolution/`
  - [ ] write the requirements contract, input artifacts, allowed dependency surface, and evaluation harness
  - [ ] make the benchmark assets reviewable without chat context
  - Success criteria: the experiment target exists as a bounded artifact bundle, not a prose-only idea

- [ ] Phase 2: paired-trial runner
  - [ ] implement one runner for the `monolithic` condition
  - [ ] implement one runner for the `AC14` condition
  - [ ] persist paired trial artifacts with cost, time, repair loops, and outputs
  - Success criteria: one paired trial can run end to end under the frozen fairness rules

- [ ] Phase 3: scoring and decision
  - [ ] apply the frozen primary outcome and secondary metrics
  - [ ] persist one final decision artifact with `ac14_wins`, `monolithic_wins`, or `inconclusive`
  - [ ] make the decision traceable back to per-trial evidence
  - Success criteria: the experiment result is artifact-backed rather than conversational

- [ ] Phase 4: repeated trials and lock
  - [ ] run 5 fresh paired trials
  - [ ] run full `python -m pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update status docs to reflect the result
  - Success criteria: the experiment is complete, verified, and reviewable

## Current Open Uncertainties

- AC14 still lacks executed comparison evidence even though the comparison contract is now frozen
- the benchmark asset bundle and paired-trial runner do not exist yet
- five paired fresh trials may still yield an inconclusive result

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

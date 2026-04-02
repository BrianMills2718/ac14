# AC14 TODO

Status: Active control surface
Last updated: 2026-04-01

This file is the running checklist for the active numbered plan, not a full
history log.

Detailed uncertainty tracking lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

The active implementation contract is:

- [Plan #42: Empirical Benchmark Fidelity Repair](/home/brian/projects/ac14/docs/plans/42_empirical_benchmark_fidelity_repair.md)

The experiment contract is frozen in:

- [Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md)

The parent experiment lane remains:

- [Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md)

Completed blocker-clearing lanes:

- [Plan #40: Empirical Smoke Stabilization](/home/brian/projects/ac14/docs/plans/40_empirical_smoke_stabilization.md)
- [Plan #41: Empirical Harness Repair](/home/brian/projects/ac14/docs/plans/41_empirical_harness_repair.md)

The previously active propagation lane remains blocked:

- [Plan #37: Directory Divergence Front-Half Proof](/home/brian/projects/ac14/docs/plans/37_directory_divergence_front_half_proof.md)

## Short-Term Active Lane

- [x] Plan #39 foundation: benchmark bundle, paired-trial runner, and decision artifact exist
- [x] Plan #40: smoke stabilization completed with explicit `blocked_on_harness` verdict
- [x] Plan #41: first harness-repair slice completed and moved AC14 from import-time failure to packet-level failure
- [ ] Phase 1: turn current packet/runtime failures into benchmark-local repair guidance
  - Success criteria: guidance names deterministic `generated_at`, required parsed fields, and key business-rule mismatches

- [ ] Phase 2: apply tighter benchmark-fidelity guidance to the empirical lane
  - Success criteria: the next smoke rerun is testing benchmark fidelity rather than the looser previous guidance

- [ ] Phase 3: rerun one bounded smoke gate
  - Success criteria: the next blocker is narrower or one condition reaches a hard-harness success

- [ ] Phase 4: resume or keep blocking Plan #39 explicitly
  - Success criteria: the active docs say clearly whether the five-trial budget is justified

## Current Open Uncertainties

- AC14 still lacks a completed five-trial comparison result even though the comparison contract and runner now exist
- five paired fresh trials may still yield an inconclusive result
- the first ablation should isolate the decomposition claim itself; if full unrestricted front-half derivation starts to dominate the lane, that needs to be logged explicitly
- the current empirical comparison is a back-half gate over a fixed decomposition and should not be mistaken for the full end-to-end thesis test
- current bounded smoke trials have not yet produced a hard-harness success in either condition
- the latest explicit smoke verdict is `blocked_on_harness`, not `blocked_on_infrastructure`
- the next queued lane is benchmark-fidelity repair, not immediate five-trial execution

## Latest Verified Baseline

- the repo is clean
- the most recent fully verified implementation state passed:
  - `python -m pytest -q` with `220 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- the most recently completed planning lane was:
  - [Plan #41: Empirical Harness Repair](/home/brian/projects/ac14/docs/plans/41_empirical_harness_repair.md)

## Longer-Term Next Steps

- [ ] complete Plan #42 so the next smoke rerun is benchmark-fidelity-focused
- [ ] resume Plan #39 only if the smoke artifact says the five-trial budget is justified
- [ ] decide what the back-half empirical gate actually proves for the broader thesis
- [ ] only then resume blocked propagation lanes such as Plan #37 if they still matter to the thesis

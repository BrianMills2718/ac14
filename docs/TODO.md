# AC14 TODO

Status: Active control surface
Last updated: 2026-04-02

This file is the running checklist for the active numbered plan, not a full
history log.

Detailed uncertainty tracking lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

The active implementation contract is:

- [Plan #50: Empirical Contract And Benchmark Fidelity Repair](/home/brian/projects/ac14/docs/plans/50_empirical_contract_and_benchmark_fidelity_repair.md)

The experiment contract is frozen in:

- [Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md)

The parent experiment lane remains:

- [Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md)

The next smoke gate is frozen in:

- [Plan #51: Empirical Smoke Gate Refresh III](/home/brian/projects/ac14/docs/plans/51_empirical_smoke_gate_refresh_iii.md)

The full-trial and interpretation gates remain blocked behind smoke readiness:

- [Plan #43: Full Trial Gate](/home/brian/projects/ac14/docs/plans/43_full_trial_gate.md)
- [Plan #44: Verdict Interpretation and Next Horizon](/home/brian/projects/ac14/docs/plans/44_verdict_interpretation_and_next_horizon.md)

The previously active propagation lane remains blocked:

- [Plan #37: Directory Divergence Front-Half Proof](/home/brian/projects/ac14/docs/plans/37_directory_divergence_front_half_proof.md)

## Short-Term Active Lane

- [x] Plan #39 foundation: benchmark bundle, paired-trial runner, and decision artifact exist
- [x] Plan #40: smoke stabilization completed with explicit `blocked_on_harness` verdict
- [x] Plan #41: first harness-repair slice completed and moved AC14 from import-time failure to packet-level failure
- [x] Plan #42: benchmark-local repair guidance landed, but the smoke gate stayed blocked on harness fidelity
- [x] Plan #45: schema-aware empirical repair landed and passed verification
- [x] Plan #46: bounded smoke rerun narrowed the remaining blocker further
- [x] Plan #47: prompt and benchmark-guidance hardening landed and passed verification
- [x] Plan #48: bounded smoke rerun stayed `blocked_on_harness` on the repair7 artifact
- [x] Plan #49: empirical attempts now persist `packet_test_report.json` and `recomposition_report.json`, and semantic-eval prompt inputs are JSON-safe for datetime-bearing fixtures

- [ ] Plan #50 Phase 1: clear the remaining generator-contract failures
  - Success criteria: prompt/guidance hardening explicitly covers unparenthesized multiline boolean conditions and pre-class `GeneratedComponent` return annotations

- [ ] Plan #50 Phase 2: clear the remaining benchmark-fidelity misses
  - Success criteria: benchmark-local guidance explicitly covers ORX-101 shipping-only handling and exact `case_parser.normalized_notes` lowercasing-only behavior

- [ ] Plan #50 Phase 3: verify and lock docs
  - Success criteria: targeted tests, full `pytest`, `mypy`, and `ruff` pass; the control docs point to Plan #51 for the next smoke rerun

- [ ] Plan #51 Phase 1: rerun one bounded smoke gate on the repaired lane
  - Success criteria: one fresh smoke artifact exists after Plan #50

- [ ] Plan #51 Phase 2: decide whether Plan #43 is unblocked
  - Success criteria: the active docs say clearly whether the five-trial budget is justified after the fresh smoke artifact

## Current Open Uncertainties

- AC14 still lacks a completed five-trial comparison result even though the comparison contract and runner exist
- the first ablation is still a back-half gate over a fixed decomposition and should not be mistaken for the full end-to-end thesis test
- the latest bounded smoke artifact is `.ac14_out/empirical_smoke_gate_repair7/`, and it remained `blocked_on_harness`
- manual reruns should no longer be needed to diagnose packet and recomposition failures because every empirical attempt now persists those reports directly
- the current remaining blocker set is narrow: multiline boolean syntax without parentheses, pre-class `GeneratedComponent` annotations, ORX-101 shipping-only benchmark fidelity, and `case_parser.normalized_notes` punctuation drift

## Latest Verified Baseline

- the most recent fully verified implementation state passed:
  - `python -m pytest -q` with `235 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- the most recently completed planning lane was:
  - [Plan #49: Empirical Attempt Observability And Harness Serialization](/home/brian/projects/ac14/docs/plans/49_empirical_attempt_observability_and_harness_serialization.md)

## Longer-Term Next Steps

- [ ] complete Plan #50, then run Plan #51 and only unblock Plan #43 if the fresh smoke artifact says the five-trial budget is justified
- [ ] interpret the full-trial verdict via Plan #44 before broadening adjacent lanes
- [ ] only then resume blocked propagation lanes such as Plan #37 if they still matter to the thesis

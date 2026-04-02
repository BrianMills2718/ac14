# AC14 TODO

Status: Active control surface
Last updated: 2026-04-02

This file is the running checklist for the active numbered plan, not a full
history log.

Detailed uncertainty tracking lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

The active implementation contract is:

- [Plan #48: Empirical Smoke Gate Refresh II](/home/brian/projects/ac14/docs/plans/48_empirical_smoke_gate_refresh_ii.md)

The experiment contract is frozen in:

- [Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md)

The parent experiment lane remains:

- [Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md)

The next smoke gate is frozen in:

- [Plan #48: Empirical Smoke Gate Refresh II](/home/brian/projects/ac14/docs/plans/48_empirical_smoke_gate_refresh_ii.md)

The full-trial and interpretation gates remain blocked behind smoke readiness:

- [Plan #43: Full Trial Gate](/home/brian/projects/ac14/docs/plans/43_full_trial_gate.md)
- [Plan #44: Verdict Interpretation and Next Horizon](/home/brian/projects/ac14/docs/plans/44_verdict_interpretation_and_next_horizon.md)

Completed blocker-clearing lanes:

- [Plan #40: Empirical Smoke Stabilization](/home/brian/projects/ac14/docs/plans/40_empirical_smoke_stabilization.md)
- [Plan #41: Empirical Harness Repair](/home/brian/projects/ac14/docs/plans/41_empirical_harness_repair.md)
- [Plan #42: Empirical Benchmark Fidelity Repair](/home/brian/projects/ac14/docs/plans/42_empirical_benchmark_fidelity_repair.md)

The previously active propagation lane remains blocked:

- [Plan #37: Directory Divergence Front-Half Proof](/home/brian/projects/ac14/docs/plans/37_directory_divergence_front_half_proof.md)

## Short-Term Active Lane

- [x] Plan #39 foundation: benchmark bundle, paired-trial runner, and decision artifact exist
- [x] Plan #40: smoke stabilization completed with explicit `blocked_on_harness` verdict
- [x] Plan #41: first harness-repair slice completed and moved AC14 from import-time failure to packet-level failure
- [x] Plan #42: benchmark-local repair guidance landed, but the smoke gate stayed blocked on harness fidelity
- [x] Plan #45 Phase 1: render packet-local schema definitions in the component prompt
  - Success criteria: the AC14 component prompt now exposes local schema fields, optionality, and descriptions

- [x] Plan #45 Phase 2: add benchmark-local repair guidance targeted by condition and component
  - Success criteria: the empirical lane explicitly reinforces the 24h shipping rule, compound-exception rule, and optional override handling

- [x] Plan #45 Phase 3: verify and lock docs
  - Success criteria: local tests pass and the control docs point to Plan #46 for the smoke rerun

- [x] Plan #46 Phase 1: rerun one bounded smoke gate on the repaired lane
  - Success criteria: one fresh smoke artifact exists

- [x] Plan #46 Phase 2: decide whether Plan #43 is unblocked
  - Success criteria: the active docs say clearly whether the five-trial budget is justified
  - Result: the fresh smoke artifact persisted at `.ac14_out/empirical_smoke_gate_repair6/` and remained `blocked_on_harness`

- [x] Plan #47 Phase 1: harden prompts against the classifier syntax pathology and schema-invalid fallback labels
  - Success criteria: shared prompts explicitly discourage comment-only branches, speculative fallback labels, and essay-style branch commentary

- [x] Plan #47 Phase 2: add benchmark-local repair guidance for the exact repair6 blockers
  - Success criteria: AC14 guidance names the classifier direct-rule requirement; monolithic guidance names the missing `shipping_risk.shipment_status` field and forbids out-of-schema labels

- [x] Plan #47 Phase 3: verify and lock docs
  - Success criteria: targeted tests, full tests, mypy, and ruff pass; the control docs point to Plan #48 for the next smoke rerun

- [ ] Plan #48 Phase 1: rerun one bounded smoke gate on the repaired lane
  - Success criteria: one fresh smoke artifact exists after Plan #47

- [ ] Plan #48 Phase 2: decide whether Plan #43 is unblocked
  - Success criteria: the active docs say clearly whether the five-trial budget is justified after the fresh smoke artifact

## Current Open Uncertainties

- AC14 still lacks a completed five-trial comparison result even though the comparison contract and runner now exist
- five paired fresh trials may still yield an inconclusive result
- the first ablation should isolate the decomposition claim itself; if full unrestricted front-half derivation starts to dominate the lane, that needs to be logged explicitly
- the current empirical comparison is a back-half gate over a fixed decomposition and should not be mistaken for the full end-to-end thesis test
- current bounded smoke trials have not yet produced a hard-harness success in either condition
- the latest explicit smoke verdict is still `blocked_on_harness`, not `blocked_on_infrastructure`
- the latest bounded smoke artifact is `.ac14_out/empirical_smoke_gate_repair6/`
- AC14 is still losing early attempts to syntax-invalid `exception_classifier` modules before the benchmark harness can judge the logic cleanly
- the monolithic lane is still violating benchmark-local schema fidelity by reading `shipping_risk['shipment_status']` and by inventing fallback labels outside the schema
- the current queued lane is Plan #47 benchmark repair, then Plan #48 smoke rerun, not immediate five-trial execution

## Latest Verified Baseline

- the repo is clean
- the most recent fully verified implementation state passed:
  - `python -m pytest -q` with `232 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- the most recently completed planning lane was:
  - [Plan #47: Syntax-Stable Empirical Benchmark Repair](/home/brian/projects/ac14/docs/plans/47_syntax_stable_empirical_benchmark_repair.md)

## Longer-Term Next Steps

- [ ] complete Plan #48 and only unblock Plan #43 if the fresh smoke artifact says the five-trial budget is justified
- [ ] interpret the full-trial verdict via Plan #44 before broadening adjacent lanes
- [ ] only then resume blocked propagation lanes such as Plan #37 if they still matter to the thesis

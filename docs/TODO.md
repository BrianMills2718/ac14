# AC14 TODO

Status: Active control surface
Last updated: 2026-04-02

This file is the running checklist for the active numbered plan, not a full
history log.

Detailed uncertainty tracking lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

The active implementation contract is:

- [Plan #58: Shipping-Only Priority And Correlator Repair](/home/brian/projects/ac14/docs/plans/58_shipping_only_priority_and_correlator_repair.md)

The immediate follow-on repair chain is:

- [Plan #59: Generation Stability And Pre-Emit Validation Repair](/home/brian/projects/ac14/docs/plans/59_generation_stability_and_pre_emit_validation_repair.md)
- [Plan #60: Empirical Smoke Gate Refresh VI](/home/brian/projects/ac14/docs/plans/60_empirical_smoke_gate_refresh_vi.md)

The experiment contract is frozen in:

- [Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md)

The parent experiment lane remains:

- [Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md)

The full-trial and interpretation gates remain blocked behind smoke readiness:

- [Plan #43: Full Trial Gate](/home/brian/projects/ac14/docs/plans/43_full_trial_gate.md)
- [Plan #44: Verdict Interpretation and Next Horizon](/home/brian/projects/ac14/docs/plans/44_verdict_interpretation_and_next_horizon.md)
- [Plan #57: Empirical Smoke Gate Refresh V](/home/brian/projects/ac14/docs/plans/57_empirical_smoke_gate_refresh_v.md)
- [Plan #60: Empirical Smoke Gate Refresh VI](/home/brian/projects/ac14/docs/plans/60_empirical_smoke_gate_refresh_vi.md)

The previously active propagation lane remains blocked:

- [Plan #37: Directory Divergence Front-Half Proof](/home/brian/projects/ac14/docs/plans/37_directory_divergence_front_half_proof.md)

## Short-Term Active Lane

- [x] Plan #39 foundation: benchmark bundle, paired-trial runner, and decision artifact exist
- [x] Plans #40-#50: smoke stabilization, harness repair, schema-aware repair, and repair7 follow-up landed
- [x] Plan #51: fresh repair8 smoke artifact exists and honestly stayed `blocked_on_harness`
- [x] Plan #52: packet/recomposition reports now persist bounded mismatch details and empirical attempts run inside a real `llm_client` experiment context
- [x] Plan #53: benchmark-local parser, rationale, priority-branch, and ASCII-source contract hardening landed
- [x] Plan #54: repair9 smoke artifact exists and honestly stayed `blocked_on_harness` without an infrastructure-only explanation

- [x] Plan #55: repair the shared benchmark-local shipping, correlator, and compound-inventory semantics now exposed by repair9
  - Success criteria: benchmark contract plus empirical guidance state those rules explicitly enough to target both conditions

- [x] Plan #56: repair monolithic invalid-source observability and prompt stability
  - Success criteria: failed monolithic modules are persisted and the monolithic guidance is explicit about shipping-only classification plus syntax discipline

- [x] Plan #57: rerun one bounded smoke gate on the post-55/post-56 lane
  - Success criteria: one fresh smoke artifact exists under `.ac14_out/empirical_smoke_gate_repair10/` and the next gate is locked honestly

- [ ] Plan #58: repair the shared shipping-only priority and correlator rule exposed by repair10
  - Success criteria: benchmark contract and empirical guidance say directly that shipping-only standard-customer cases may route to logistics, keep `escalation_required=false`, and still remain `priority_band='high'`

- [ ] Plan #59: repair generation stability and the remaining monolithic pre-emit validation observability gap
  - Success criteria: the remaining monolithic invalid-module path persists failed source and AC14 `resolution_assembler` guidance explicitly names the current contract failures

- [ ] Plan #60: rerun one bounded smoke gate on the post-58/post-59 lane
  - Success criteria: one fresh smoke artifact exists under `.ac14_out/empirical_smoke_gate_repair11/` and the next gate is locked honestly

## Current Open Uncertainties

- AC14 still lacks a completed five-trial comparison result even though the comparison contract and runner exist
- the first ablation is still a back-half gate over a fixed decomposition and should not be mistaken for the full end-to-end thesis test
- repair10 proved the current blocker is still harness-local rather than infrastructure-local
- the remaining blocker set is now concrete: shipping-only standard-customer semantics plus generation-stability/failed-source persistence gaps
- if repair11 still blocks on harness, the next plan should be driven by the fresh bounded mismatch artifacts rather than by generic packet/recomposition failure labels

## Latest Verified Baseline

- the most recent fully verified implementation state passed:
  - `python -m pytest -q` with `242 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- the most recently completed planning lanes are:
  - [Plan #52: Structured Empirical Harness Diffs](/home/brian/projects/ac14/docs/plans/52_structured_empirical_harness_diffs.md)
  - [Plan #53: Benchmark-Local Contract Hardening IV](/home/brian/projects/ac14/docs/plans/53_benchmark_local_contract_hardening_iv.md)
  - [Plan #54: Empirical Smoke Gate Refresh IV](/home/brian/projects/ac14/docs/plans/54_empirical_smoke_gate_refresh_iv.md)
  - [Plan #55: Shared Benchmark Shipping And Escalation Semantics Repair](/home/brian/projects/ac14/docs/plans/55_shared_benchmark_shipping_and_escalation_semantics_repair.md)
  - [Plan #56: Monolithic Syntax And Failure Artifact Repair](/home/brian/projects/ac14/docs/plans/56_monolithic_syntax_and_failure_artifact_repair.md)

## Longer-Term Next Steps

- [ ] complete Plans #58, #59, and #60 and only unblock Plan #43 if the fresh smoke artifact says the five-trial budget is justified
- [ ] interpret the full-trial verdict via Plan #44 before broadening adjacent lanes
- [ ] only then resume blocked propagation lanes such as Plan #37 if they still matter to the thesis

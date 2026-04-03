# AC14 TODO

Status: Active control surface
Last updated: 2026-04-02

This file is the running checklist for the active numbered plan, not a full
history log.

Detailed uncertainty tracking lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

The active implementation contract is:

- [Plan #91: Front-Half-First Smoke Rerun](/home/brian/projects/ac14/docs/plans/91_front_half_first_smoke_rerun.md)

The explicit active chain is:

- [Plan #67: Second-Gate Blocker Diagnosis](/home/brian/projects/ac14/docs/plans/67_second_gate_blocker_diagnosis.md) -> complete
- [Plan #68: Deterministic Exact-Match Semantic Review Policy](/home/brian/projects/ac14/docs/plans/68_deterministic_exact_match_semantic_review_policy.md) -> complete
- [Plan #69: Monolithic Input-Port Contract Validation](/home/brian/projects/ac14/docs/plans/69_monolithic_input_port_contract_validation.md) -> complete
- [Plan #70: Second-Gate Smoke Rerun](/home/brian/projects/ac14/docs/plans/70_second_gate_smoke_rerun.md) -> complete
- [Plan #71: Empirical Full-Trial Resume Integrity](/home/brian/projects/ac14/docs/plans/71_empirical_full_trial_resume_integrity.md) -> complete
- [Plan #66: Second-Gate Full Trial](/home/brian/projects/ac14/docs/plans/66_second_gate_full_trial.md) -> complete
- [Plan #72: Second-Gate Verdict Interpretation](/home/brian/projects/ac14/docs/plans/72_second_gate_verdict_interpretation.md) -> complete
- [Plan #73: Resource Scaling Failure Diagnosis](/home/brian/projects/ac14/docs/plans/73_resource_scaling_failure_diagnosis.md) -> complete
- [Plan #74: Resource Scaling Packet-Context Diagnosis](/home/brian/projects/ac14/docs/plans/74_resource_scaling_packet_context_diagnosis.md) -> complete
- [Plan #75: Resource Scaling Prompt-Schema Grounding Repair](/home/brian/projects/ac14/docs/plans/75_resource_scaling_prompt_schema_grounding_repair.md) -> complete
- [Plan #76: Second-Gate Repair Boundary](/home/brian/projects/ac14/docs/plans/76_second_gate_repair_boundary.md) -> complete
- [Plan #77: Cross-Benchmark Failure Taxonomy](/home/brian/projects/ac14/docs/plans/77_cross_benchmark_failure_taxonomy.md) -> complete
- [Plan #78: Reusable Packet Rule Grounding](/home/brian/projects/ac14/docs/plans/78_reusable_packet_rule_grounding.md) -> complete
- [Plan #79: Post-Grounding Smoke Rerun](/home/brian/projects/ac14/docs/plans/79_post_grounding_smoke_rerun.md) -> complete
- [Plan #81: Post-Grounding Strategic Pivot](/home/brian/projects/ac14/docs/plans/81_post_grounding_strategic_pivot.md) -> complete
- [Plan #82: Front-Half-First Empirical Contract](/home/brian/projects/ac14/docs/plans/82_front_half_first_empirical_contract.md) -> complete
- [Plan #83: Structured Spec Input Contract](/home/brian/projects/ac14/docs/plans/83_structured_spec_input_contract.md) -> complete
- [Plan #84: Structured-Spec Front-Half Acceptance](/home/brian/projects/ac14/docs/plans/84_structured_spec_front_half_acceptance.md) -> complete
- [Plan #85: Structured-Spec Benchmark Bundle](/home/brian/projects/ac14/docs/plans/85_structured_spec_benchmark_bundle.md) -> complete
- [Plan #86: Front-Half-First Smoke Gate Contract And Runner](/home/brian/projects/ac14/docs/plans/86_front_half_first_smoke_gate.md) -> complete
- [Plan #87: Front-Half-First Smoke Execution](/home/brian/projects/ac14/docs/plans/87_front_half_first_smoke_execution.md) -> complete, verdict `blocked_on_front_half`
- [Plan #88: Front-Half-First Full Trial Gate](/home/brian/projects/ac14/docs/plans/88_front_half_first_full_trial_gate.md) -> planned, conditional on Plan #87 verdict `ready_for_full_trials`
- [Plan #89: Front-Half-First Blocker Diagnosis](/home/brian/projects/ac14/docs/plans/89_front_half_first_blocker_diagnosis.md) -> complete
- [Plan #90: Front-Half-First Contract And Observability Repair](/home/brian/projects/ac14/docs/plans/90_front_half_first_contract_and_observability_repair.md) -> complete
- [Plan #91: Front-Half-First Smoke Rerun](/home/brian/projects/ac14/docs/plans/91_front_half_first_smoke_rerun.md) -> active
- [Plan #92: Front-Half-First Second Blocker Boundary](/home/brian/projects/ac14/docs/plans/92_front_half_first_second_blocker_boundary.md) -> planned, conditional on Plan #91 verdict `blocked_*`

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

- [x] Plan #71: make the interrupted full trial resume-safe and archive partial evidence

- [x] Plan #66: spend the full five-trial budget and lock the second verdict with the repaired runner

- [x] Plan #72: lock the second-gate verdict honestly across the project docs and story surfaces

- [x] Plan #73: diagnose why AC14 lost `resource_scaling_v1` before any more benchmark-local tuning

- [x] Plan #74: determine whether the repeated `resource_scaling_v1` misses reflect insufficient packet context or poor use of sufficient local context

- [x] Plan #75: strengthen local rule salience for the failing `resource_scaling_v1` component cluster and earn a fresh bounded smoke result

- [x] Plan #76: decide whether another `resource_scaling_v1` micro-repair is justified after the non-winning grounding smoke
  - Result: no; `resource_scaling_v1` benchmark-local micro-repairs stay frozen

- [x] Plan #77: classify which empirical failure surfaces are benchmark-local versus reusable AC14 weaknesses and freeze the next lane from that taxonomy
  - Result: the strongest reusable weakness is packet-local rule grounding for semantically coupled business logic

- [x] Plan #78: add one reusable packet-rule-grounding surface and verify it with targeted tests
  - Result: codegen context now carries bounded rule-grounding summaries and the prompt consumes them explicitly

- [x] Plan #79: rerun the harder smoke gate after the reusable grounding repair and freeze the next branch from the result
  - Result: smoke remained `ready_for_full_trials` only because monolithic passed; AC14 still failed `0/3` attempts

- [x] Plan #81: freeze the post-grounding strategic pivot instead of reopening the harder back-half gate
  - Result: the harder second gate stays closed and back-half local tuning remains frozen

- [x] Plan #82: define the next empirical horizon as front-half-first and freeze one bounded next implementation lane
  - Result: the next lane is the structured-spec input contract in Plan #83

- [x] Plan #83: implement the first bounded structured-spec input contract for draft planning
  - Result: AC14 now has a bounded structured-spec artifact and a parallel structured-spec draft-planning path

- [x] Plan #84: implement one structured-spec front-half acceptance artifact through freeze and review
  - Result: AC14 now proves one full structured-spec front-half lane through freeze decision and review

- [x] Plan #85: freeze one benchmark-ready structured-spec bundle for the next empirical gate
  - Result: the repo now has a typed structured-spec benchmark bundle anchored to the existing `resource_scaling` runtime evaluation assets

- [x] Plan #86: implement the front-half-first smoke contract and runner
  - Result: the repo now persists a staged-combined front-half-first smoke artifact and verified CLI/Make runner surface

- [ ] Plan #87: spend one bounded front-half-first smoke trial on the structured-spec benchmark bundle
  - Result: `.ac14_out/front_half_first_smoke_1/smoke_readiness_report.json` now exists with verdict `blocked_on_front_half`

- [x] Plan #89: diagnose the first blocked front-half-first smoke artifact and freeze the next bounded repair lane
  - Result: the blocker is a combined contract failure: AC14 invalid structured-spec bindings plus monolithic raw-record runtime mismatch

- [x] Plan #90: repair the front-half-first contract and failed-front-half observability surfaces
  - Result: structured-spec planning now persists invalid-plan diagnostics, gets one bounded binding-error retry, and monolithic runtime generation now fails loud with persisted failed source for raw-record contract mistakes

- [ ] Plan #91 or Plan #92:
  - if Plan #91 says `ready_for_full_trials`, run Plan #88
  - otherwise freeze Plan #92 before any more local tuning

## Current Open Uncertainties

- the first empirical gate is complete but inconclusive; AC14 still lacks a decisive empirical result in either direction
- the current comparison is still a bounded back-half gate over a fixed decomposition and should not be mistaken for the strongest end-to-end thesis test
- provider `503` demand noise appeared during the first full five-trial run and may contaminate secondary time/cost interpretation even though the primary success outcome completed
- the second gate is no longer open; it finished decisively as `monolithic_wins`
- the current open question is no longer what the first front-half-first smoke gate should judge; that contract is now the staged-combined rule in Plan #86
- the current active uncertainty is whether the Plan #90 repair lane is enough to reopen the front-half-first smoke gate or whether a second blocker boundary is needed

## Latest Verified Baseline

- latest full code verification baseline:
  - `python -m pytest -q` with `278 passed, 1 skipped`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- latest empirical verification baseline:
  - `.ac14_out/full_trials_gate_1/experiment_decision.json` with verdict `inconclusive`
  - `.ac14_out/full_trials_gate_2_smoke/smoke_readiness_report.json` with verdict `blocked_on_harness`
  - `.ac14_out/full_trials_gate_2_smoke_rerun/smoke_readiness_report.json` with verdict `ready_for_full_trials`
  - `.ac14_out/full_trials_gate_2/experiment_decision.json` with verdict `monolithic_wins`
  - `.ac14_out/full_trials_gate_2_smoke_grounding1/smoke_readiness_report.json` with verdict `ready_for_full_trials` but `0` AC14 hard-harness successes
  - `.ac14_out/full_trials_gate_2_smoke_reusable_grounding1/smoke_readiness_report.json` with verdict `ready_for_full_trials` but still `0` AC14 hard-harness successes
  - `.ac14_out/front_half_first_smoke_1/smoke_readiness_report.json` with verdict `blocked_on_front_half`
  - `.ac14_out/full_trials_gate_2/_interrupted_trials/` preserves the interrupted pre-repair trial state
  - `ac14`: `2/5` successes on gate 1
  - `monolithic`: `2/5` successes on gate 1
- latest notebook/governance verification baseline:
  - both notebook JSON files parse cleanly
  - both notebooks' code cells execute top-to-bottom
  - `notebooks/notebook_registry.yaml` parses cleanly

## Longer-Term Next Steps

- [x] complete Plan #86 so the front-half-first empirical contract has a runnable smoke gate
- [x] complete Plan #87 so the front-half-first empirical contract has one persisted smoke verdict
- [x] complete Plan #89 from that verdict instead of drifting into a side lane
- [ ] complete Plan #90 so the next smoke rerun is testing repaired contracts and better failed-front-half observability
- [ ] complete Plan #91 or Plan #92 from the repaired smoke rerun
- [ ] only after that decide whether the first front-half-first benchmark should be retained, expanded, or replaced for broader proof breadth
- [ ] keep blocked propagation lanes blocked until the second empirical contract is executed honestly

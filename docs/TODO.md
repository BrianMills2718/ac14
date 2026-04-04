# AC14 TODO

Status: Active control surface
Last updated: 2026-04-04

This file is the running checklist for the active numbered plan, not a full
history log.

Detailed uncertainty tracking lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

The active implementation contract is:

- [Plan #121: Front-Half Runtime-Output Repair II And Smoke Rerun XII](/home/brian/projects/ac14/docs/plans/121_front_half_runtime_output_repair_ii_and_smoke_rerun_xii.md)

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
- [Plan #91: Front-Half-First Smoke Rerun](/home/brian/projects/ac14/docs/plans/91_front_half_first_smoke_rerun.md) -> complete, verdict `blocked_on_front_half`
- [Plan #92: Front-Half-First Second Blocker Boundary](/home/brian/projects/ac14/docs/plans/92_front_half_first_second_blocker_boundary.md) -> complete
- [Plan #93: Async-Safe Freeze Review Repair](/home/brian/projects/ac14/docs/plans/93_async_safe_freeze_review_repair.md) -> complete
- [Plan #94: Front-Half-First Smoke Rerun II](/home/brian/projects/ac14/docs/plans/94_front_half_first_smoke_rerun_ii.md) -> complete, verdict `blocked_on_infrastructure` (Gemini 429, front-half not tested)
- [Plan #95: Front-Half Infrastructure Boundary](/home/brian/projects/ac14/docs/plans/95_front_half_infrastructure_boundary.md) -> complete
- [Plan #96: Front-Half-First Smoke Rerun III](/home/brian/projects/ac14/docs/plans/96_front_half_first_smoke_rerun_iii.md) -> complete, verdict `blocked_on_infrastructure`
- [Plan #97: Front-Half Freeze Fidelity Boundary](/home/brian/projects/ac14/docs/plans/97_front_half_freeze_fidelity_boundary.md) -> complete
- [Plan #98: Front-Half Runtime-Harness Boundary](/home/brian/projects/ac14/docs/plans/98_front_half_runtime_harness_boundary.md) -> complete
- [Plan #99: Front-Half Infrastructure Boundary For Hidden Default Model Paths](/home/brian/projects/ac14/docs/plans/99_front_half_infrastructure_availability_boundary.md) -> complete
- [Plan #100: Front-Half-First Verdict Interpretation And Next Horizon](/home/brian/projects/ac14/docs/plans/100_front_half_first_verdict_interpretation.md) -> planned, conditional on Plan #88 completion
- [Plan #104: Front-Half Freeze-Fidelity Repair And Smoke Rerun V](/home/brian/projects/ac14/docs/plans/104_front_half_freeze_fidelity_repair_and_smoke_rerun_iv.md) -> complete, verdict `blocked_on_harness`
- [Plan #105: Front-Half Runtime-Harness Repair And Smoke Rerun IV](/home/brian/projects/ac14/docs/plans/105_front_half_runtime_harness_repair_and_smoke_rerun_iv.md) -> complete, verdict `blocked_on_harness`
- [Plan #106: Front-Half Model Propagation Repair And Smoke Rerun IV](/home/brian/projects/ac14/docs/plans/106_front_half_provider_fallback_and_smoke_rerun_iv.md) -> complete, verdict `blocked_on_front_half`
- [Plan #107: Front-Half External Provider Boundary II](/home/brian/projects/ac14/docs/plans/107_front_half_external_provider_boundary_ii.md) -> planned, conditional on a later rerun verdict `blocked_on_infrastructure`
- [Plan #108: Front-Half Freeze Fidelity Boundary II](/home/brian/projects/ac14/docs/plans/108_front_half_freeze_fidelity_boundary_ii.md) -> planned, conditional on Plan #104 verdict `blocked_on_front_half`
- [Plan #109: Front-Half Freeze-Fidelity Repair II And Smoke Rerun VI](/home/brian/projects/ac14/docs/plans/109_front_half_freeze_fidelity_repair_ii_and_smoke_rerun_vi.md) -> planned, conditional on Plan #108 completion
- [Plan #110: Front-Half Runtime-Harness Boundary II](/home/brian/projects/ac14/docs/plans/110_front_half_runtime_harness_boundary_ii.md) -> complete
- [Plan #111: Front-Half Runtime-Harness Repair II And Smoke Rerun VII](/home/brian/projects/ac14/docs/plans/111_front_half_runtime_harness_repair_ii_and_smoke_rerun_vii.md) -> complete, verdict `blocked_on_harness`
- [Plan #112: Front-Half Runtime-Harness Boundary III](/home/brian/projects/ac14/docs/plans/112_front_half_runtime_harness_boundary_iii.md) -> complete
- [Plan #113: Front-Half Runtime-Harness Repair III And Smoke Rerun VIII](/home/brian/projects/ac14/docs/plans/113_front_half_runtime_harness_repair_iii_and_smoke_rerun_viii.md) -> complete, smoke_10 verdict `blocked_on_harness`
- [Plan #114: Front-Half Runtime-Harness Boundary IV](/home/brian/projects/ac14/docs/plans/114_front_half_runtime_harness_boundary_iv.md) -> complete, blocker was final-output binding fidelity
- [Plan #115: Front-Half Runtime-Harness Repair IV And Smoke Rerun IX](/home/brian/projects/ac14/docs/plans/115_front_half_runtime_harness_repair_iv_and_smoke_rerun_ix.md) -> complete, smoke_11 verdict `blocked_on_harness` but output binding now works
- [Plan #116: Front-Half Runtime-Harness Boundary V](/home/brian/projects/ac14/docs/plans/116_front_half_runtime_harness_boundary_v.md) -> complete, smoke_11 shows both conditions now fail in `runtime_outputs`
- [Plan #117: Front-Half Runtime-Harness Repair V And Smoke Rerun X](/home/brian/projects/ac14/docs/plans/117_front_half_runtime_harness_repair_v_and_smoke_rerun_x.md) -> complete, smoke_12 still `blocked_on_harness`
- [Plan #118: Front-Half Runtime-Output Boundary I](/home/brian/projects/ac14/docs/plans/118_front_half_runtime_output_boundary_i.md) -> complete, smoke_12 froze the pre-runtime contract blocker mix
- [Plan #119: Front-Half Runtime-Output Repair I And Smoke Rerun XI](/home/brian/projects/ac14/docs/plans/119_front_half_runtime_output_repair_i_and_smoke_rerun_xi.md) -> complete, smoke_13 exposed a repo-local structured dependency blocker
- [Plan #124: Front-Half Structured Dependency Boundary](/home/brian/projects/ac14/docs/plans/124_front_half_structured_dependency_boundary.md) -> complete, smoke_13 froze the missing `llm_client[structured]` / `instructor` contract
- [Plan #125: Front-Half Structured-Dependency Repair And Smoke Rerun XIV](/home/brian/projects/ac14/docs/plans/125_front_half_structured_dependency_repair_and_smoke_rerun_xiv.md) -> complete, smoke_14 cleared the dependency blocker but stayed `blocked_on_harness`
- [Plan #122: Front-Half Runtime-Harness Boundary VI](/home/brian/projects/ac14/docs/plans/122_front_half_runtime_harness_boundary_vi.md) -> complete, smoke_14 froze repeated ambiguous final-output inference as the dominant harness blocker
- [Plan #123: Front-Half Runtime-Harness Repair VI And Smoke Rerun XIII](/home/brian/projects/ac14/docs/plans/123_front_half_runtime_harness_repair_vi_and_smoke_rerun_xiii.md) -> complete, smoke_15 verdict `blocked_on_harness` (terminal inference fix landed)
- [Plan #130: Front-Half Runtime-Harness Boundary VII](/home/brian/projects/ac14/docs/plans/130_front_half_runtime_harness_boundary_vii.md) -> complete, smoke_16 froze two-component-same-schema topology as next harness blocker
- [Plan #131: Front-Half Runtime-Harness Repair VII And Smoke Rerun XVII](/home/brian/projects/ac14/docs/plans/131_front_half_runtime_harness_repair_vii_and_smoke_rerun_xvii.md) -> complete, smoke_17 verdict `blocked_on_runtime_outputs` (all attempts reached runtime eval, RSC-100..103 mismatched)
- [Plan #120: Front-Half Runtime-Output Boundary II](/home/brian/projects/ac14/docs/plans/120_front_half_runtime_output_boundary_ii.md) -> complete, smoke_17 froze missing approval/strategy/alert/deploy-risk rules in spec
- [Plan #121: Front-Half Runtime-Output Repair II And Smoke Rerun XII](/home/brian/projects/ac14/docs/plans/121_front_half_runtime_output_repair_ii_and_smoke_rerun_xii.md) -> in progress (spec expanded with 19 rules; smoke_18 pending)
- [Plan #126: Front-Half Dependency Boundary II](/home/brian/projects/ac14/docs/plans/126_front_half_dependency_boundary_ii.md) -> planned if smoke_15 still says `blocked_on_front_half`
- [Plan #127: Front-Half Dependency Repair II And Smoke Rerun XV](/home/brian/projects/ac14/docs/plans/127_front_half_dependency_repair_ii_and_smoke_rerun_xv.md) -> planned
- [Plan #128: Front-Half External Provider Boundary III](/home/brian/projects/ac14/docs/plans/128_front_half_external_provider_boundary_iii.md) -> planned if smoke_15 says `blocked_on_infrastructure`
- [Plan #129: Front-Half Provider Fallback And Smoke Rerun XVI](/home/brian/projects/ac14/docs/plans/129_front_half_provider_fallback_and_smoke_rerun_xvi.md) -> planned

The experiment contract remains frozen in:

- [Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md)

## Active Checklist

- [x] Commit the verified Plan #113 structured-spec/runtime-contract repair.
- [x] Freeze smoke_10 as the canonical blocker artifact.
- [x] Repair final-output binding fidelity in the runtime contract and execution path.
- [x] Prove the repair with targeted tests.
- [x] Run smoke_11 at `.ac14_out/front_half_first_smoke_11`.
- [x] Split true runtime-output smoke failures from genuine harness failures.
- [x] Prove the verdict split with targeted tests.
- [x] Run smoke_12 at `.ac14_out/front_half_first_smoke_12`.
- [x] Lock the next branch immediately from the smoke_12 verdict.
- [x] Repair the smoke_12 pre-runtime contract blocker mix inside Plan #119.
- [x] Prove the Plan #119 repair with targeted tests plus `mypy` and `ruff`.
- [x] Run smoke_13 at `.ac14_out/front_half_first_smoke_13`.
- [x] Lock the smoke_13 verdict as a new dependency boundary instead of pretending the old branch tree still fits.
- [x] Repair the repo-local structured dependency contract inside Plan #125.
- [x] Prove the Plan #125 repair with a repo-local import check plus targeted tests, `mypy`, and `ruff`.
- [x] Run smoke_14 at `.ac14_out/front_half_first_smoke_14`.
- [x] Lock the smoke_14 verdict as a harness boundary instead of leaving the dependency lane active.
- [x] Repair repeated ambiguous final-output inference inside Plan #123.
- [x] Prove the Plan #123 repair with targeted tests plus `mypy` and `ruff`.
- [x] Run smoke_15 at `.ac14_out/front_half_first_smoke_15` — verdict `blocked_on_harness` (harness was loading draft bundle instead of approved retry bundle; confirmed by 3rd attempt error "multiple non-source schema-name candidates").
- [x] Plan #130: Lock smoke_15 blocked_on_harness verdict as harness boundary VII — root cause: harness loaded `draft_bundle_dir` not `refined_draft_bundle_dir` from FreezeRetryArtifact.
- [x] Plan #123: Fix harness to load `refined_draft_bundle_dir` from FreezeRetryArtifact when `retry_freeze_approved=True`. Merged to master.
- [x] Run smoke_16 at `.ac14_out/front_half_first_smoke_16` — verdict `blocked_on_harness` (attempt_2 new topology: PolicyEvaluator and ComplianceAndExecution both emitted scaling_decision_entry but neither was a leaf; `non_source_schema_name_candidates` tier found both).
- [x] Plan #131: add `terminal_non_source_schema_name_candidates` tier — a port is terminal if its consuming component does NOT produce the same schema. Merged to master.
- [x] Run smoke_17 at `.ac14_out/front_half_first_smoke_17` — verdict `blocked_on_runtime_outputs`. All 3 attempts reached runtime evaluation (no harness inference failures). Code ran but outputs mismatched (RSC-100..103). Front-half success: true. Pre-runtime proof failed: true.
- [x] Branch: smoke_17 `blocked_on_runtime_outputs` → execute Plan #120 (boundary) then Plan #121 (repair + smoke_18).
- [ ] Plan #120: document the dominant runtime-output blocker from smoke_17.
- [ ] Plan #121: repair it and run smoke_18.

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

- [x] Plan #91: rerun one bounded front-half-first smoke trial after Plan #90
  - Result: `.ac14_out/front_half_first_smoke_2/smoke_readiness_report.json` exists with verdict `blocked_on_front_half`

- [x] Plan #92: freeze the second blocker boundary from the rerun verdict
  - Result: the next chain is now explicit as Plan #93 -> Plan #94 -> Plan #88 or Plan #95

- [x] Plan #93: make freeze decision and semantic review async-safe inside retry-enabled front-half paths
  - Result: the next smoke rerun can now test front-half approval and runtime instead of dying on nested `asyncio.run()` reentry

- [x] Plan #94: smoke rerun II completed with verdict `blocked_on_infrastructure`
  - Result: all 6 attempts hit Gemini 429 rate limit; async-safe fix NOT empirically tested yet

- [x] Plan #95: freeze the blocker boundary — dominant blocker is Gemini 429 quota, not freeze fidelity
  - Result: the blocker is now explicitly `infrastructure_quota_exhausted`; next move is Plan #96 with explicit `MODEL=gpt-5-mini`

- [x] Plan #96: rerun one bounded front-half-first smoke trial with explicit `MODEL=gpt-5-mini`
  - Result: `.ac14_out/front_half_first_smoke_5/smoke_readiness_report.json` exists with verdict `blocked_on_infrastructure`
  - Monolithic reached real `runtime_outputs` evaluation; AC14 still failed on hidden Gemini-default subcalls after draft planning and freeze remediation

- [x] Plan #106: repair hidden front-half default-model plumbing and rerun one bounded smoke trial immediately
  - Result: `.ac14_out/front_half_first_smoke_6/smoke_readiness_report.json` exists with verdict `blocked_on_front_half`
  - AC14 now persists full front-half artifacts through freeze decision and retry; the infrastructure blocker is cleared and the active lane is freeze fidelity

- [ ] Plan #88: spend the front-half-first full-trial budget if and only if Plan #96 opens the gate
  - implementation note: this plan must add the missing full-trial runner surface before spending the five-trial budget
  - after Plan #88 completes, immediately execute Plan #100

- [ ] Plan #100: interpret the front-half-first verdict and freeze the next horizon from the actual result

- [x] Plan #97: freeze the clean front-half blocker boundary from smoke_6
  - Result: the dominant blocker class is now explicit as schema-field alias mismatch + empty fixture coverage + warning-vs-blocker readiness semantics

- [x] Plan #104: repair the dominant freeze-fidelity blocker class and rerun one bounded smoke trial immediately
  - Result: `.ac14_out/front_half_first_smoke_7/smoke_readiness_report.json` exists with verdict `blocked_on_harness`
  - AC14 now reaches approved front-half artifacts; the active blocker moved to runtime-contract inference

- [x] Plan #98: freeze the clean runtime-harness boundary from smoke_7
  - Result: the dominant blocker class is now explicit as runtime-contract inference that assumes the structured-spec input name must exactly match the generated root input-port name

- [x] Plan #105: repair the dominant runtime/harness blocker and rerun one bounded smoke trial immediately
  - Result: `.ac14_out/front_half_first_smoke_8/smoke_readiness_report.json` exists with verdict `blocked_on_harness`
  - The root-input inference bug is fixed; the active blocker moved to split final-output inference

- [ ] Plan #107: if a later smoke rerun says `blocked_on_infrastructure`, freeze the next external-provider boundary before spending more empirical budget

- [ ] Plan #108: if Plan #104 still says `blocked_on_front_half`, freeze the next narrower front-half blocker boundary

- [ ] Plan #109: if Plan #108 lands, repair that narrower blocker and rerun one bounded smoke trial immediately

- [x] Plan #110: if Plan #105 still says `blocked_on_harness`, freeze the next narrower runtime/harness blocker boundary
  - Result: the dominant blocker class is now explicit as the runner's single-final-component assumption over split-output generated graphs

- [x] Plan #111: repair the split-output runtime/harness blocker and rerun one bounded smoke trial immediately
  - Result: `.ac14_out/front_half_first_smoke_9/smoke_readiness_report.json` exists with verdict `blocked_on_harness`
  - The split final-output blocker is cleared; the active blocker moved to the structured-spec/runtime contract boundary itself

- [x] Plan #112: if Plan #111 still says `blocked_on_harness`, freeze the next narrower runtime/harness blocker boundary
  - Result: the dominant blocker class is now explicit as structured-spec benchmark/runtime contract drift plus zero-input `source`-component runtime entry

- [ ] Plan #113: repair the structured-spec/runtime contract blocker and rerun one bounded smoke trial immediately
  - implementation note: the current bounded scope is truthful structured-spec benchmark/runtime fidelity plus support for one unique top-level `source` component runtime contract

- [ ] Plan #114: if Plan #113 still says `blocked_on_harness`, freeze the next narrower runtime/harness blocker boundary

- [ ] Plan #115: if Plan #114 lands, repair that narrower runtime/harness blocker and rerun one bounded smoke trial immediately

## Current Open Uncertainties

- the first empirical gate is complete but inconclusive; AC14 still lacks a decisive empirical result in either direction
- the current comparison is still a bounded back-half gate over a fixed decomposition and should not be mistaken for the strongest end-to-end thesis test
- provider `503` demand noise appeared during the first full five-trial run and may contaminate secondary time/cost interpretation even though the primary success outcome completed
- the second gate is no longer open; it finished decisively as `monolithic_wins`
- the infrastructure blocker is cleared and front-half approval now succeeds; the current active uncertainty is whether Plan #113 is enough to make the structured-spec benchmark/runtime contract truthful enough for at least one real runtime hard-harness attempt
- Plan #113 is repairing that structured-spec/runtime contract boundary before the next smoke rerun is spent

## Latest Verified Baseline

- latest full code verification baseline:
  - `python -m pytest -q` with `288 passed, 1 skipped`
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
  - `.ac14_out/front_half_first_smoke_2/smoke_readiness_report.json` with verdict `blocked_on_front_half`
  - `.ac14_out/front_half_first_smoke_4/smoke_readiness_report.json` with verdict `blocked_on_infrastructure` (Gemini 429, not a thesis signal)
  - `.ac14_out/front_half_first_smoke_5/smoke_readiness_report.json` with verdict `blocked_on_infrastructure` (top-level explicit model honored, hidden Gemini-default subcalls still blocking AC14)
  - `.ac14_out/front_half_first_smoke_6/smoke_readiness_report.json` with verdict `blocked_on_front_half` (infrastructure cleared; AC14 then blocked on draft freeze fidelity)
  - `.ac14_out/front_half_first_smoke_7/smoke_readiness_report.json` with verdict `blocked_on_harness` (front-half approval now succeeds; runtime-contract inference still blocks generation)
  - `.ac14_out/front_half_first_smoke_8/smoke_readiness_report.json` with verdict `blocked_on_harness` (root-input inference is fixed; split final-output inference still blocks generation)
  - `.ac14_out/front_half_first_smoke_9/smoke_readiness_report.json` with verdict `blocked_on_harness` (split final-output inference is fixed; the structured-spec/runtime contract is now the active blocker)
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
- [x] complete Plan #90 so the next smoke rerun is testing repaired contracts and better failed-front-half observability
- [x] complete Plan #91 and Plan #92 from the repaired smoke rerun
- [x] complete Plan #93 so the next smoke rerun is testing async-safe front-half review/decision paths
- [x] complete Plan #94 — verdict `blocked_on_infrastructure` (all 429, no thesis signal)
- [x] complete Plan #95 (blocker boundary: infrastructure, not freeze fidelity)
- [x] run smoke rerun III (Plan #96) with explicit `MODEL=gpt-5-mini`
- [ ] complete Plan #113 and branch directly into Plan #88 plus Plan #100 if the gate opens, Plan #114 plus Plan #115 if runtime/harness still dominates, Plan #107 if infrastructure reappears, or Plan #108 plus Plan #109 if front-half regresses
- [ ] only after the front-half-first branch finishes should the repo decide whether the first front-half-first benchmark should be retained, expanded, or replaced for broader proof breadth
- [ ] keep blocked propagation lanes blocked until the second empirical contract is executed honestly

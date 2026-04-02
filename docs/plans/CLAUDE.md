# AC14 Implementation Plans

Status: Canonical numbered-plan index
Last updated: 2026-04-02

Use numbered plans for implementation work that changes AC14's code or active
control surfaces. The roadmap defines direction; numbered plans define the
current executable lane.

## Active Plans

| # | Name | Priority | Status | Blocks |
|---|------|----------|--------|--------|
| 1 | [Dependency Execution Probing](01_dependency_execution_probing.md) | High | Complete | - |
| 2 | [Dependency Probe Integration](02_dependency_probe_integration.md) | High | Complete | - |
| 3 | [Meta-Process Dependency Probe Policy](03_meta_process_dependency_probe_policy.md) | High | Complete | - |
| 4 | [Realistic-Input Front-Half Acceptance](04_realistic_input_front_half_acceptance.md) | High | Complete | - |
| 5 | [Realistic-Input Full-System Acceptance](05_realistic_input_full_system_acceptance.md) | High | Complete | - |
| 6 | [Realistic-Input Acceptance Breadth](06_realistic_input_acceptance_breadth.md) | High | Complete | - |
| 7 | [Realistic-Input LLM Acceptance](07_realistic_input_llm_acceptance.md) | High | Complete | - |
| 8 | [LLM Realistic-Input Breadth](08_llm_realistic_input_breadth.md) | High | Complete | - |
| 9 | [Live LLM Readiness Boundary](09_live_llm_readiness_boundary.md) | High | Complete | - |
| 10 | [Packet Sufficiency Evidence](10_packet_sufficiency_evidence.md) | High | Complete | - |
| 11 | [Realistic-Input Default Gate](11_realistic_input_default_gate.md) | High | Complete | - |
| 12 | [Realistic-Input Suite Default Gate](12_realistic_input_suite_default_gate.md) | High | Complete | - |
| 13 | [Recommendation Default-Gate Awareness](13_recommendation_default_gate_awareness.md) | High | Complete | - |
| 14 | [Live LLM Suite Readiness](14_live_llm_suite_readiness.md) | High | Complete | - |
| 15 | [Recommendation Live Suite Awareness](15_recommendation_live_suite_awareness.md) | High | Complete | - |
| 16 | [Freeze Semantic Review Gate](16_freeze_semantic_review_gate.md) | High | Complete | - |
| 17 | [Front-Half Suite Breadth](17_front_half_suite_breadth.md) | High | Complete | - |
| 18 | [Messy-Input Front-Half Proof](18_messy_input_front_half_proof.md) | High | Complete | - |
| 19 | [Controlled Dependency Remediation](19_controlled_dependency_remediation.md) | High | Complete | - |
| 20 | [Remediation Hand-Off Automation](20_remediation_handoff_automation.md) | High | Complete | - |
| 21 | [Freeze Remediation Plan Refinement](21_freeze_remediation_plan_refinement.md) | High | Complete | - |
| 22 | [Freeze Retry Chain](22_freeze_retry_chain.md) | High | Complete | - |
| 23 | [Front-Half Retry Integration](23_front_half_retry_integration.md) | High | Complete | - |
| 24 | [Front-Half Retry Suite Breadth](24_front_half_retry_suite_breadth.md) | High | Complete | - |
| 25 | [Messy-Input Retry Proof](25_messy_input_retry_proof.md) | High | Complete | - |
| 26 | [Structured Realistic-Input Loading](26_structured_realistic_input_loading.md) | High | Complete | - |
| 27 | [Messy-Input Full-System Acceptance](27_messy_input_full_system_acceptance.md) | High | Complete | 26 |
| 28 | [Messy-Input LLM Comparison](28_messy_input_llm_comparison.md) | High | Complete | 27 |
| 29 | [Explicit Realistic-Input Policy](29_explicit_realistic_input_policy.md) | High | Complete | 28 |
| 30 | [Profile-Aware Realistic-Input Parity](30_profile_aware_realistic_input_parity.md) | High | Complete | 29 |
| 31 | [Messy-Profile Suite Proof](31_messy_profile_suite_proof.md) | High | Complete | 30 |
| 32 | [Multi-Artifact Discovery Inputs](32_multi_artifact_discovery_inputs.md) | High | Complete | 31 |
| 33 | [Directory Front-Half Acceptance Proof](33_directory_front_half_acceptance_proof.md) | High | Complete | 32 |
| 34 | [Directory Context Summaries](34_directory_context_summaries.md) | High | Complete | 33 |
| 35 | [Directory Summary Front-Half Proof](35_directory_summary_front_half_proof.md) | High | Complete | 34 |
| 36 | [Directory Schema Divergence Concerns](36_directory_schema_divergence_concerns.md) | High | Complete | 35 |
| 37 | [Directory Divergence Front-Half Proof](37_directory_divergence_front_half_proof.md) | High | Blocked | 39 |
| 38 | [Empirical Comparison Gate](38_empirical_comparison_gate.md) | Critical | Complete | - |
| 39 | [Monolithic Vs AC14 Comparison Execution](39_monolithic_vs_ac14_comparison_execution.md) | Critical | Blocked | 48 |
| 40 | [Empirical Smoke Stabilization](40_empirical_smoke_stabilization.md) | Critical | Complete | - |
| 41 | [Empirical Harness Repair](41_empirical_harness_repair.md) | Critical | Complete | 40 |
| 42 | [Empirical Benchmark Fidelity Repair](42_empirical_benchmark_fidelity_repair.md) | Critical | Complete | - |
| 43 | [Full Trial Gate](43_full_trial_gate.md) | Critical | Blocked | 48 |
| 44 | [Verdict Interpretation and Next Horizon](44_verdict_interpretation_and_next_horizon.md) | Critical | Blocked | 43 |
| 45 | [Schema-Aware Empirical Repair](45_schema_aware_empirical_repair.md) | Critical | Complete | - |
| 46 | [Empirical Smoke Gate Refresh](46_empirical_smoke_gate_refresh.md) | Critical | Complete | 45 |
| 47 | [Syntax-Stable Empirical Benchmark Repair](47_syntax_stable_empirical_benchmark_repair.md) | Critical | Complete | - |
| 48 | [Empirical Smoke Gate Refresh II](48_empirical_smoke_gate_refresh_ii.md) | Critical | Complete | 47 |
| 49 | [Empirical Attempt Observability And Harness Serialization](49_empirical_attempt_observability_and_harness_serialization.md) | Critical | Complete | - |
| 50 | [Empirical Contract And Benchmark Fidelity Repair](50_empirical_contract_and_benchmark_fidelity_repair.md) | Critical | Complete | - |
| 51 | [Empirical Smoke Gate Refresh III](51_empirical_smoke_gate_refresh_iii.md) | Critical | Complete | 50 |
| 52 | [Structured Empirical Harness Diffs](52_structured_empirical_harness_diffs.md) | Critical | Complete | 51 |
| 53 | [Benchmark-Local Contract Hardening IV](53_benchmark_local_contract_hardening_iv.md) | Critical | Complete | 51 |
| 54 | [Empirical Smoke Gate Refresh IV](54_empirical_smoke_gate_refresh_iv.md) | Critical | Complete | 52, 53 |
| 55 | [Shared Benchmark Shipping And Escalation Semantics Repair](55_shared_benchmark_shipping_and_escalation_semantics_repair.md) | Critical | Complete | 54 |
| 56 | [Monolithic Syntax And Failure Artifact Repair](56_monolithic_syntax_and_failure_artifact_repair.md) | Critical | Complete | 54 |
| 57 | [Empirical Smoke Gate Refresh V](57_empirical_smoke_gate_refresh_v.md) | Critical | In Progress | 55, 56 |

## Status Key

| Status | Meaning |
|--------|---------|
| Planned | Ready for implementation |
| In Progress | Actively being implemented |
| Blocked | Waiting on a real unresolved dependency or decision |
| Complete | Implemented and verified |

## Working Rules

1. Every significant implementation lane should have a numbered plan.
2. Each plan must include `References Reviewed`, `Open Questions`,
   `Files Affected`, and `Required Tests`.
3. The numbered plan is the authoritative implementation contract for the lane.
4. `TODO.md` is the active checklist, not the long-form plan.
5. `AC14_NEXT_24_HOURS.md` is the tactical summary, not the source of detailed
   implementation requirements.
6. When a sequence of propagation-proof plans appears, insert an explicit
   empirical gate before continuing if the main thesis is still unmeasured.

## Creating A New Plan

1. Copy `TEMPLATE.md` to `NN_name.md`.
2. Fill in the gap, questions, references, files, steps, tests, and criteria.
3. Add the plan to this index.
4. Link active tactical docs back to the new plan if it becomes the current lane.

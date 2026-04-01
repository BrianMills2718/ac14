# AC14 Implementation Plans

Status: Canonical numbered-plan index
Last updated: 2026-04-01

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
| 24 | [Front-Half Retry Suite Breadth](24_front_half_retry_suite_breadth.md) | High | Planned | - |

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

## Creating A New Plan

1. Copy `TEMPLATE.md` to `NN_name.md`.
2. Fill in the gap, questions, references, files, steps, tests, and criteria.
3. Add the plan to this index.
4. Link active tactical docs back to the new plan if it becomes the current lane.

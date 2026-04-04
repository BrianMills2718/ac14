# Plan #121: Front-Half Runtime-Output Repair II And Smoke Rerun XII

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 120
**Blocks:** None

---

## Gap

**Current:** smoke_17 produced `blocked_on_runtime_outputs` — all 3 AC14
attempts reached runtime evaluation but RSC-100..103 all mismatched expected
outputs. Root cause (from Plan #120): `structured_spec_input.yaml`
business_rules lacked the detailed approval, strategy/cooldown, deploy-risk,
and alert-tier rules needed to generate correct code.

**Target:** Expand `structured_spec_input.yaml` business_rules with the missing
rules, verify the YAML is valid, and rerun smoke_18 immediately.

**Why:** The spec is the primary context provided to the LLM code generator.
Filling the missing rules gives the generator everything it needs to produce
correct approval, strategy, cooldown, and alert logic.

---

## Acceptance Criteria

- [x] The dominant runtime-output blocker from Plan #120 is repaired explicitly.
- [x] structured_spec_input.yaml business_rules expanded from 7 vague to 19 detailed rules.
- [x] YAML syntax verified valid (19 rules parsed correctly).
- [x] Changes committed and merged to master.
- [x] One fresh smoke artifact exists (smoke_18) after the repair.
- [x] The next branch is explicit: smoke_18 verdict `blocked_on_harness` (3 exact-name candidates) → Plan #133 boundary + Plan #134 repair.

---

## Execution Contract

1. expand structured_spec_input.yaml with 19 detailed rules (DONE)
2. verify YAML valid (DONE — 19 rules parsed)
3. commit and merge to master (DONE)
4. rerun one bounded smoke trial immediately (smoke_18 — NEXT)
5. if the rerun still says `blocked_on_runtime_outputs`, freeze the next
   narrower runtime-output boundary immediately rather than broadening scope

---

## Files Affected

- `benchmarks/resource_scaling_structured_spec/structured_spec_input.yaml` — business_rules expanded with 19 detailed rules (merged in plan-121-spec-rules worktree)

---

## Rules Added

- THRESHOLD: cpu_breach, memory_breach, error_breach, breach_count
- ACTION: scale_out ONLY when both cpu+memory breach; scale_up ONLY when cpu breach without memory
- URGENCY: critical/high/medium/low tiers by breach_count and error_breach
- TIER MAPPING: bronze->budget, silver/gold->standard, platinum->premium
- DEPLOY RISK: high(<4h), medium(<24h), low(otherwise)
- TARGET ADJUSTMENT: max(1,min(breach_count,max_scale_adjustment)) per tier
- MIN HEALTHY: budget=1, standard=2, premium=3
- AUTO SCALE ENABLED: standard+premium=true, budget=false
- REQUIRES APPROVAL: false for premium OR (standard AND low/medium urgency); true otherwise
- APPROVAL TIER: auto/manager/director by tier+urgency combinations
- STRATEGY AND COOLDOWN: immediate+5min/staged+15min/deferred+30min/blocked+0min
- ALERT TIER: critical/warning/info by error_breach+urgency
- COMPLIANCE CONFLICT: change-freeze AND maintenance-window blocking rules
- AUTHORIZATION MODE: auto/manual/compliance_blocked logic
- FINAL ACTION and FINAL STRATEGY: blocked when execution_gate.blocked

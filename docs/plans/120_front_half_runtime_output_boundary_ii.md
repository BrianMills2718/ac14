# Plan #120: Front-Half Runtime-Output Boundary II

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 119
**Blocks:** 121

---

## Gap

**Current:** smoke_17 says `blocked_on_runtime_outputs` — all 3 AC14 attempts
reached runtime evaluation with no harness inference failures, but RSC-100..103
all mismatched expected outputs.

**Dominant blocker (from smoke_17 attempt_1 analysis):**

The `structured_spec_input.yaml` business_rules section specifies the high-level
action discrimination (`scale_out` when both CPU+memory breach, `scale_up` when
only CPU breaches) but is MISSING the detailed rules for:

1. **Approval logic**: `requires_approval: false when premium or (standard and urgency in [low, medium])`;
   `approval_tier: auto/manager/director` mapping by tier+urgency
2. **Authorization mode**: `auto` (not requires_approval AND authorized), `manual` (not authorized, not blocked),
   `compliance_blocked` (blocked)
3. **Scaling strategy and cooldown**: `immediate=5min/critical+low_deploy_risk`, `staged=15min/medium_high_deploy_risk`,
   `deferred=30min/low_urgency+low_deploy_risk`, `blocked=0min`
4. **Deploy risk**: `high if last_deploy_hours < 4`, `medium if < 24`, `low otherwise`
5. **Alert tier**: `critical` if `create_incident` (error_breach OR urgency=critical), `warning` if
   `notify_oncall` only (urgency=high), `info` otherwise

**RSC-100 mismatches (premium tier, urgency=critical, scale_out):**
- Expected `approval_tier=auto, authorization_mode=auto, requires_approval=false, cooldown_minutes=5`
- Got `approval_tier=manager, authorization_mode=manual, requires_approval=true, cooldown_minutes=10`
- Root: generated code used wrong approval rule (budget/standard logic) and wrong cooldown (staged vs immediate)

**RSC-101 mismatches (budget tier, only CPU breach, scale_up):**
- Expected `action=scale_up, urgency=medium, strategy=deferred, cooldown_minutes=30, target_adjustment=1, alert_tier=info`
- Got `action=scale_out, urgency=critical, strategy=immediate, cooldown_minutes=10, target_adjustment=2, alert_tier=warning`
- Root: generated code treated single CPU breach as scale_out (both-breach logic), cascading to wrong urgency/strategy/cooldown

**Fix direction:** Expand `structured_spec_input.yaml` business_rules to include
the detailed approval, strategy/cooldown, deploy-risk, and alert-tier rules from
`benchmarks/resource_scaling/requirements.md`. Both monolithic AND AC14 fail
RSC-100..103 with similar errors, confirming the spec is the right fix point.

---

## Acceptance Criteria

- [x] Smoke_17 produced `blocked_on_runtime_outputs`.
- [x] Dominant runtime-output blocker named: missing detailed approval/strategy/alert rules in spec.
- [x] The next move is explicit as Plan #121.

---

## Continuation Contract

If this boundary activates, immediately continue into
[Plan #121: Front-Half Runtime-Output Repair II And Smoke Rerun XII](121_front_half_runtime_output_repair_ii_and_smoke_rerun_xii.md).

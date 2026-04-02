# Cloud Resource Auto-Scaling Decision System — Requirements

## Purpose

Process a raw cloud service metrics event and produce a fully authorized
scaling decision. Every output field is categorical (enum/bool/int) so that
comparison trials have unambiguous pass/fail criteria with no free-form text
to vary across generations.

## Business Rules

### 1. Threshold Detection

Breach thresholds are fixed and deterministic:

- `cpu_breach`: `cpu_utilization >= 0.80`
- `memory_breach`: `memory_utilization >= 0.85`
- `error_breach`: `error_rate >= 0.05`
- `any_breach`: any of the above is true
- `breach_count`: count of true breach flags (0–3)

### 2. Scaling Action

- `scale_out` when both `cpu_breach` and `memory_breach` are true
- `scale_up` when only `cpu_breach` is true (memory_breach false)
- `scale_down` when no breach and `request_rate_rps < 20`
- `none` when no breach and request rate is not below 20

### 3. Urgency Classification

- `critical`: `error_breach` is true OR `breach_count >= 3`
- `high`: `breach_count == 2` (and not critical)
- `medium`: `breach_count == 1` (and not critical)
- `low`: `breach_count == 0`

### 4. Trend Signals

- `cpu_trend`: `spiking` if `cpu_utilization >= 0.90`; `increasing` if `>= 0.80`; `stable` otherwise
- `memory_trend`: `spiking` if `memory_utilization >= 0.92`; `increasing` if `>= 0.85`; `stable` otherwise
- `sustained_pressure`: true when both cpu_trend and memory_trend are `increasing` or `spiking`

### 5. Deploy Risk

- `deploy_risk`: `high` if `last_deploy_hours < 4`; `medium` if `< 24`; `low` otherwise
- `rollback_eligible`: true if `last_deploy_hours < 48`
- `risk_factor`: `fresh_deploy` / `recent_deploy` / `stable_deploy` matching the deploy_risk band

### 6. Service Policy

- `scale_tier`: `bronze` -> `budget`, `silver`/`gold` -> `standard`, `platinum` -> `premium`
- `auto_scale_enabled`: true for `standard` and `premium`; false for `budget`
- `max_scale_adjustment`: `budget`=1, `standard`=2, `premium`=4
- `min_healthy_instances`: `budget`=1, `standard`=2, `premium`=3

### 7. Scale Recommendation

- `target_adjustment = max(1, min(breach_count, max_scale_adjustment))` when action is not `none`; 0 otherwise

### 8. Approval Requirement

- `requires_approval`: false when `premium` or (`standard` and urgency in `[low, medium]`); true otherwise
- `approval_tier`:
  - `auto`: premium tier, or standard with urgency in `[low, medium]`
  - `manager`: standard with urgency `high`, or any budget tier
  - `director`: standard with urgency `critical`
- `budget_risk`: `low` if `target_adjustment <= 1`; `medium` if `== 2`; `high` if `> 2`

### 9. Scaling Strategy

- `blocked`: compliance conflict is present
- `immediate`: urgency `critical` AND `deploy_risk == low`
- `staged`: `deploy_risk in [high, medium]` OR urgency `high`
- `deferred`: urgency in `[low, medium]` AND `deploy_risk == low`
- `cooldown_minutes`: `immediate`=5, `staged`=15, `deferred`=30, `blocked`=0

### 10. Compliance

- `conflict`: (`in_change_freeze` AND urgency != `critical`) OR (`in_maintenance_window` AND action != `none`)
- `compliance_tier`: `blocked` if conflict; `clear` otherwise
- `conflict_source`: `change_freeze` / `maintenance_window` / `none`

### 11. Alert Plan

- `notify_oncall`: true when urgency in `[high, critical]`
- `create_incident`: true when `error_breach` OR urgency `== critical`
- `alert_tier`: `critical` if `create_incident`; `warning` if `notify_oncall` only; `info` otherwise

### 12. Execution Gate

- `authorized`: NOT conflict AND `auto_scale_enabled`
- `blocked`: equals `conflict`
- `authorization_mode`:
  - `auto`: authorized and NOT requires_approval
  - `manual`: NOT authorized and NOT blocked
  - `compliance_blocked`: blocked

### 13. Final Decision Entry

- `action`: `blocked` if `execution_gate.blocked`; else `recommendation.action`
- `strategy`: `blocked` if `execution_gate.blocked`; else `scaling_plan.strategy`
- All other fields are propagated from upstream categorical components

## Non-Goals

- No free-form text output fields.
- No live metrics API calls; all inputs are provided in the runtime case.
- No rolling state window for trend analysis; trend is derived from the single current event.

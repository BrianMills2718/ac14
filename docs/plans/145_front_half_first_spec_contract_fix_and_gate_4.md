# Plan #145: Front-Half-First Spec Contract Fix And Gate_4

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 144
**Blocks:** None

---

## Gap

**Current:** gate_3 verdict monolithic_wins (0/5 AC14 successes). AC14 gets 3/4 runtime
cases correct (75% accuracy). The remaining failure (RSC-102) is a spec ambiguity:
the top-level `business_rules` say "FINAL ACTION: blocked if execution_gate.blocked"
which the LLM interprets as action='none' rather than action='blocked' (the string).

**Target:** Fix the ambiguous FINAL ACTION / FINAL STRATEGY rules in the structured spec.
Run gate_4 at TRIALS=5 MAX_BUDGET=1.50 as the final gate in this repair arc.

---

## Acceptance Criteria

- [ ] Spec fix: replace ambiguous "FINAL ACTION" / "FINAL STRATEGY" rules in
  `benchmarks/resource_scaling_structured_spec/structured_spec_input.yaml` with explicit
  "BLOCKED FLAG" rule stating: "when compliance_conflict=True, set action='blocked',
  strategy='blocked', cooldown_minutes=0, blocked=True — override ALL other values"
- [ ] Gate_4 run at `.ac14_out/front_half_first_full_gate_4/` TRIALS=5 MAX_BUDGET=1.50
- [ ] Decision artifact persisted
- [ ] Verdict is one of: ac14_wins, monolithic_wins, inconclusive
- [ ] Verdict interpretation frozen as next plan

---

## Spec Fix

**Files:** `benchmarks/resource_scaling_structured_spec/structured_spec_input.yaml`

Replace:
```yaml
- "FINAL ACTION: blocked if execution_gate.blocked is true; else recommendation.action"
- "FINAL STRATEGY: blocked if execution_gate.blocked is true; else scaling_plan.strategy"
```

With:
```yaml
- "BLOCKED FLAG: when compliance_conflict is true, the final outputs are: action='blocked' (the string value 'blocked'), strategy='blocked', cooldown_minutes=0, blocked=True. This OVERRIDES the computed action, strategy, and cooldown. target_adjustment, approval_tier, min_healthy_instances, urgency, alert_tier, authorization_mode, scale_tier, requires_approval, case_id, and service_id are NOT overridden."
```

This matches the workflow hint that already correctly states:
`"BLOCKED FLAG: set blocked=true and override action=blocked, strategy=blocked, cooldown_minutes=0, authorization_mode=compliance_blocked when compliance conflict is true."`

---

## Branch Matrix

| Verdict | Next plan |
|---------|-----------|
| `ac14_wins` | Plan #146: Final verdict interpretation + thesis claim — AC14 decomposition achieves runtime parity |
| `inconclusive` | Plan #146: Inconclusive interpretation — secondary metrics show real progress |
| `monolithic_wins` | Plan #146: Strategic pivot — fundamental capability boundary acknowledged, thesis narrowed |

---

## Files Affected

- `benchmarks/resource_scaling_structured_spec/structured_spec_input.yaml` — spec contract fix

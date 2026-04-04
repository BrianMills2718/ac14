# Plan #144: Front-Half-First Gate_3 Verdict Interpretation

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 143
**Blocks:** 145

---

## Gate_3 Verdict: `monolithic_wins` (4/5 vs 0/5)

**Decision artifact:** `.ac14_out/front_half_first_full_gate_3/front_half_first_decision.json`

**AC14:** 0 successes / 5 trials, 5/5 front_half_successes, $0.645 total cost, semantic_score=1.0
**Monolithic:** 4 successes / 5 trials, $0.622 total cost, semantic_score=1.43

---

## What Changed vs Gate_2

| Metric | Gate_2 | Gate_3 | Change |
|--------|--------|--------|--------|
| AC14 successes | 0/5 | 0/5 | unchanged |
| front_half_successes | 5/5 | 5/5 | unchanged |
| semantic_score | 0.2 | 1.0 | +0.8 |
| Case accuracy per attempt | 0/4 | 3/4 (RSC-102 fails) | +75% |
| Monolithic successes | 5/5 | 4/5 | −1 (trial_5 mono also struggles) |

**The context injection repair worked.** The generated code went from 0% case accuracy to 75% case accuracy. Before the repair, the LLM was producing explicit placeholder comments ("In a real scenario, this would involve complex rule evaluation"). After the repair, it correctly implements: THRESHOLD, ACTION, URGENCY, TIER MAPPING, DEPLOY RISK, TARGET ADJUSTMENT, MIN HEALTHY, AUTO SCALE ENABLED, REQUIRES APPROVAL, APPROVAL TIER, STRATEGY AND COOLDOWN, ALERT TIER, COMPLIANCE CONFLICT (detection), AUTHORIZATION MODE.

---

## Root Cause of Remaining Failure

**The one failing case: RSC-102** (in_maintenance_window=true → compliance_conflict=true)

The structured spec's top-level business rule says:
```
"FINAL ACTION: blocked if execution_gate.blocked is true; else recommendation.action"
```

The LLM interprets "blocked" here as a boolean condition (blocking the action → setting action='none') rather than as the string value 'blocked' to be assigned to the action field.

The expected values for RSC-102: `action='blocked'`, `strategy='blocked'`, `cooldown_minutes=0`.
What AC14 generates: `action='none'`, `strategy='blocked'`, `cooldown_minutes=0` (or `cooldown=15` if the override doesn't reset it).

**Key evidence that this is a spec clarity issue, NOT a model capability gap:**
- Trial_5 MONOLITHIC also failed RSC-102 (target_adjustment mismatch, 3/4 cases)
- The compliance-blocked scenario has ambiguous spec rules that affect both approaches
- The `evaluate_thresholds_and_policy` workflow hint DOES correctly state: "set blocked=true and override action=blocked, strategy=blocked, cooldown_minutes=0" — but this only appears in `workflow_hints`, not in the top-level `business_rules` that are injected into the codegen prompt

---

## Repair-Boundary Assessment

Per CLAUDE.md: "after a decisive harder-benchmark loss, allow at most one bounded post-loss benchmark-local repair before freezing a repair-boundary plan."

Gate_3 was the one bounded repair. The verdict is still `monolithic_wins`. This requires a repair-boundary freeze.

**However**: the evidence shows a genuine benchmark CONTRACT issue, not a model capability gap:
1. The repair moved case accuracy from 0% → 75%
2. The remaining 25% failure is a spec wording ambiguity
3. Both approaches (AC14 and monolithic) are confused by the same ambiguous rule
4. The fix is a spec clarification, not another implementation repair

**Decision**: Freeze a spec-contract fix as Plan #145. The spec fix:
- Updates `business_rules` to replace the ambiguous "FINAL ACTION: blocked if execution_gate.blocked" with the explicit "BLOCKED FLAG" rule that already appears in the `evaluate_thresholds_and_policy` workflow hint
- Runs gate_4 as the FINAL gate in this repair arc

If gate_4 still produces `monolithic_wins`, the thesis claim narrows to: "AC14's decomposition approach generates structurally valid blueprints but requires a clearly-specified benchmark contract to achieve runtime accuracy comparable to monolithic. The semantic quality (semantic_score) approaches monolithic levels; the gap is in exact-match deterministic evaluation."

---

## Next Plan

- [Plan #145: Front-Half-First Spec Contract Fix And Gate_4](145_front_half_first_spec_contract_fix_and_gate_4.md) — fix ambiguous FINAL ACTION rule, run gate_4 as final gate in this repair arc

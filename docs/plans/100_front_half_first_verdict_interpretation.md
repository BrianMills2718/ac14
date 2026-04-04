# Plan #100: Front-Half-First Verdict Interpretation And Next Horizon

**Status:** Complete
**Type:** evaluation + planning
**Priority:** Critical
**Blocked By:** 88
**Blocks:** None

---

## Gap

**Current:** A completed front-half-first full-trial gate would produce a real
verdict artifact, but that artifact alone would not lock the thesis claim,
story surfaces, or next horizon.

**Target:** Interpret the front-half-first verdict honestly, update the active
docs from the persisted artifact, and freeze the next horizon directly from the
result instead of from expectation.

**Why:** A five-trial verdict is only useful if it changes the repo's active
control surface immediately.

---

## Acceptance Criteria

- [x] The front-half-first verdict is stated plainly across the active docs.
- [x] The thesis impact is described honestly at the front-half-first scope.
- [x] The next horizon is explicit and frozen from the actual verdict.

---

## Execution Contract

This plan activates immediately after Plan #88 completes. It must:

1. read the front-half-first decision artifact
2. update the active control docs from that artifact
3. state plainly whether the result is `ac14_wins`, `inconclusive`, or
   `monolithic_wins`
4. freeze the next numbered plan from that verdict before any unrelated work

---

## Verdict: monolithic_wins (5/5 vs 0/5)

**Decision artifact:** `.ac14_out/front_half_first_full_gate_1/front_half_first_decision.json`

**AC14:** 0 successes / 5 trials, 2.0 avg repair loops, 1 trial with observed cost ($0.556 total)
**Monolithic:** 5 successes / 5 trials, 0.6 avg repair loops, 5 trials with observed cost ($0.596 total)

### Root Cause Analysis

**The verdict was driven by budget overflow, not capability failure.**

Every single AC14 attempt across all 5 trials failed with the same error:
```
Budget exceeded for trace ac14/draft_blueprint_plan_from_structured_spec/
structured_spec_artifact/attempt1: $0.5006 spent >= $0.5000 limit
```

The $0.50/attempt budget is insufficient for the AC14 front-half pipeline:
- `build_structured_spec_artifact()` + `build_structured_spec_front_half_acceptance_report()`
  together require $0.50–$0.60+ for the draft blueprint planning phase alone
- The monolithic pipeline (single LLM call to generate code) fits within $0.50

Note: smoke_21 attempt_1 succeeded at $0.242 — this was due to lucky model sampling
producing a short enough response. The full gate showed this is not reliable: 0/15
attempts succeeded within the $0.50 budget.

### Thesis Impact

The `monolithic_wins` verdict under the $0.50 budget constraint does NOT measure
whether AC14's decomposition approach produces higher-quality code when given
sufficient compute. It measures only that the AC14 pipeline is more expensive per
attempt.

### Next Plan

The next step is to diagnose and repair the budget constraint:
- [Plan #139: Front-Half-First Full-Gate Budget Boundary](139_front_half_first_full_gate_budget_boundary.md)
  — freeze the budget overflow as a concrete boundary
- [Plan #140: Budget Repair And Rerun](140_front_half_first_budget_repair_and_rerun.md)
  — increase per-attempt budget and rerun the full gate


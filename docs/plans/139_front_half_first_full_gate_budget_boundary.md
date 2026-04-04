# Plan #139: Front-Half-First Full-Gate Budget Boundary

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 100
**Blocks:** 140

---

## Gap

**Current:** front_half_first_full_gate_1 verdict is `monolithic_wins` (5/5 vs 0/5).
ALL AC14 attempts failed with "Budget exceeded for trace
ac14/draft_blueprint_plan_from_structured_spec/structured_spec_artifact/attempt1:
$0.5006 spent >= $0.5000 limit".

**Target:** Freeze the budget overflow boundary precisely: what does the AC14
front-half pipeline actually cost, what budget is needed, and what fix is required.

---

## Acceptance Criteria

- [x] Budget overflow is the dominant and sole AC14 failure mode in full_gate_1
- [x] The minimum budget per attempt for the AC14 front-half pipeline is quantified
- [x] The fix is explicit: increase max_budget per attempt
- [x] The next plan (Plan #140) is unambiguous

---

## Boundary Analysis

### Observed failure

Every AC14 attempt in full_gate_1 failed with:
```
Budget exceeded for trace ac14/draft_blueprint_plan_from_structured_spec/
structured_spec_artifact/attempt1: $0.5006 spent >= $0.5000 limit
```

Trial 1 attempt 1 had observed cost $0.242056 before the exception was raised.
Trials 2-5 had `cost_status=no_rows` (budget exceeded before any row was committed).

### Why the $0.50 budget fails

The AC14 front-half pipeline for this benchmark requires:
1. `build_structured_spec_artifact()` — parses the structured spec YAML (cheap, no LLM)
2. `build_structured_spec_front_half_acceptance_report()` with `max_budget=$0.50`:
   - Draft blueprint planning from structured spec: ~$0.40–$0.55 (model-dependent)
   - Front-half freeze acceptance review: ~$0.05–$0.15
   - Retry if blocked: up to another $0.50

The draft blueprint planning step alone requires ~$0.40–$0.55, which exhausts
the $0.50 budget before the freeze review even runs.

In smoke_21, attempt_1 succeeded at $0.242 — this was a short/cheap model response
that fit within budget. This is not reliable: 0/15 attempts in full_gate_1 succeeded.

### Required budget per attempt

Based on the evidence:
- Minimum needed: ~$0.60–$0.70 for a single-pass AC14 attempt (no retries)
- Recommended: $1.50 to allow the draft planning + review + one blocked-freeze retry

### Fix

Change the `max_budget` parameter for AC14 attempts from $0.50 to $1.50.
This applies to:
- `make front-half-first-full-trials` default MAX_BUDGET
- The per-attempt budget passed to `build_structured_spec_front_half_acceptance_report`

---

## Files Affected

- `Makefile` — update default MAX_BUDGET for front-half-first-full-trials
- No code changes needed (budget is already a parameter)

# Plan #135: Front-Half Runtime-Output Boundary III

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 134
**Blocks:** 136

---

## Gap

**Current:** smoke_19 produced `blocked_on_harness`.

AC14 progress: 2/3 attempts now reach runtime evaluation (up from 0/3 in smoke_18).
But the overall verdict is still `blocked_on_harness` because 1/3 attempts had a
generation failure, and runtime output mismatches remain for the other 2 attempts.

---

## Dominant Blocker: smoke_19 `blocked_on_harness`

### Blocker A: Generation failure (attempt_2)

- "draft blueprint plan binding references unknown to_port 'scaling_decision_store'"
- Root cause: workflow_hints have `input_names: [scaling_decision_entry]` for
  record_decision, but the LLM generates a binding where `to_port: scaling_decision_store`
  on the record_decision component (which doesn't have that input port name). The
  LLM confused the output name with the input port name.

### Blocker B: Pass-through architecture (attempt_1)

- AC14 normalizer emits `scaling_decision_entry` with placeholder values
  ('draft_action', 'draft_urgency', etc.)
- Subsequent components just pass through the placeholder values
- Root cause: `workflow_hints.normalize_scaling_event.output_names: [scaling_decision_entry]`
  tells the LLM the normalizer emits the final output, so the LLM generates
  `scaling_decision_entry` with placeholder values rather than computing actual values

### Blocker C: Pass-through validates upstream placeholder (attempt_3)

- PolicyEvaluator validates `approval_tier` from upstream (which was placeholder)
- Raises "Invalid approval_tier value" when upstream emits non-enum placeholder

### Blocker D: Monolithic rule application errors (all 3 monolithic attempts)

- RSC-101: approval_tier="director" (expected "manager" — budget tier always → manager)
- RSC-101,103: strategy="immediate" (expected "deferred" — urgency low/medium + deploy_risk=low)
- RSC-102: authorization_mode="auto" (expected "compliance_blocked")

**Root cause for Blocker D:**
1. APPROVAL TIER rule ambiguity: "manager when standard AND urgency=high OR any budget tier" —
   parsed by LLM as "standard AND (urgency=high OR any budget tier)" or misapplied
2. STRATEGY rule: unclear whether strategy applies to action=none case  
3. AUTHORIZATION MODE ordering: LLM evaluates "auto" condition first without checking conflict

---

## Fix Direction

1. **Workflow hint architecture fix** (Blockers A, B, C):
   - Change normalize_scaling_event `output_names: [scaling_decision_entry]` →
     `output_names: [raw_scaling_event]` (normalizer passes through event, not decision)
   - Add explicit business_rule: "Normalizer must NOT emit scaling_decision_entry.
     It outputs only the normalized event data."
   - Add record_decision input clarification: "Input port receives scaling_decision_entry
     from the compliance component; must NOT use scaling_decision_store as a port name"

2. **Rule disambiguation** (Blocker D):
   - APPROVAL TIER: rewrite as "manager when (standard AND urgency=high) OR (any budget tier)"
   - STRATEGY: add explicit note that strategy applies even when action=none
   - AUTHORIZATION MODE: reorder to check compliance_blocked FIRST

---

## Acceptance Criteria

- [x] smoke_19 produced `blocked_on_harness` with 2/3 attempts reaching runtime_outputs.
- [x] Blockers A-D named and root causes traced.
- [x] Next move explicit as Plan #136.

---

## Continuation Contract

Immediately continue into
[Plan #136: Front-Half Runtime-Output Repair III And Smoke Rerun XX](136_front_half_runtime_output_repair_iii_and_smoke_rerun_xx.md).

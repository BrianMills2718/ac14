# Plan #136: Front-Half Runtime-Output Repair III And Smoke Rerun XX

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 135
**Blocks:** None

---

## Gap

**Current:** smoke_19 `blocked_on_harness` — 2/3 AC14 attempts reach runtime_outputs
but 1 still fails at generation. Both monolithic and AC14 have output mismatches
in the runtime cases. Root causes in Plan #135.

**Target:** Fix structured_spec_input.yaml workflow hints and business rules to
address all four blockers, then run smoke_20.

---

## Acceptance Criteria

- [x] Workflow hint architecture fixed: normalizer output_names changed to raw_scaling_event
- [x] Approval tier rule disambiguated: explicit "(standard AND urgency=high) OR (any budget tier)"
- [x] Strategy rule clarified: applies even when action=none
- [x] Authorization mode reordered: compliance_blocked checked FIRST
- [x] Record_decision input port naming clarified
- [x] YAML syntax valid (19 business_rules, 4 workflow_hints)
- [x] Changes committed and merged to master
- [x] One fresh smoke artifact (smoke_20) exists after the repair — verdict: blocked_on_harness (source inference collision introduced by this plan's spec change, diagnosed in Plan #137, fixed in Plan #138)
- [x] The next branch is explicit: Plan #137 (boundary) → Plan #138 (repair) → smoke_21

---

## Execution Contract

### Spec changes to make

1. **Workflow hint for normalize_scaling_event**:
   - Change `output_names: [scaling_decision_entry]` → `output_names: [raw_scaling_event]`
   - Add business_rule: "This component normalizes and validates the raw event data.
     It MUST output a normalized version of the input event (same fields, cleaned).
     It must NOT emit scaling_decision_entry — that is the job of the policy evaluation
     and compliance components."

2. **Workflow hint for record_decision**:
   - Add business_rule: "The input port for this component receives scaling_decision_entry
     from the compliance/execution component. The input port name must match what the
     upstream component emits. Never create an input port named 'scaling_decision_store'."

3. **APPROVAL TIER business rule** — replace with:
   "APPROVAL TIER: auto when premium OR (standard AND urgency in [low, medium]);
    director when standard AND urgency=critical;
    manager when (standard AND urgency=high) OR (any budget tier, regardless of urgency)"

4. **STRATEGY AND COOLDOWN** — add explicit note:
   "Strategy follows urgency+deploy_risk regardless of action (even when action=none or blocked)"

5. **AUTHORIZATION MODE** — reorder to check compliance first:
   "AUTHORIZATION MODE: compliance_blocked FIRST when conflict is true; then auto when
    NOT requires_approval AND auto_scale_enabled; manual otherwise"

### Steps

1. Create worktree for this plan
2. Apply spec changes to structured_spec_input.yaml
3. Verify YAML valid
4. Commit in worktree, merge to master
5. Update docs
6. Run smoke_20 immediately

---

## Files Affected

- `benchmarks/resource_scaling_structured_spec/structured_spec_input.yaml` — workflow hints and business rules

# Plan #138: Front-Half Runtime-Harness Repair IX And Smoke Rerun XXI

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 137
**Blocks:** None

---

## Gap

**Current:** smoke_20 `blocked_on_harness` — source inference collision from Plan #136
spec change. apply_compliance_and_execution has raw_scaling_event input port, colliding
with normalize_scaling_event.

**Target:** Fix spec to remove raw_scaling_event from apply_compliance_and_execution
inputs. Consolidate compliance logic in evaluate_thresholds_and_policy.

---

## Acceptance Criteria

- [x] apply_compliance_and_execution `input_names` changed to `[scaling_decision_entry]` only
- [x] evaluate_thresholds_and_policy explicitly instructed to compute compliance conflict
- [x] YAML valid
- [x] Changes merged to master
- [x] One fresh smoke artifact (smoke_21) exists — verdict: ready_for_full_trials
- [x] Next branch is explicit: Plan #88 (full trial gate) → Plan #100 (verdict interpretation)

---

## Execution Contract

1. Change apply_compliance_and_execution `input_names: [raw_scaling_event, scaling_decision_entry]`
   to `input_names: [scaling_decision_entry]`
2. Update apply_compliance_and_execution business_rules to reflect it receives the
   fully-computed recommendation (not the raw event)
3. Update evaluate_thresholds_and_policy to explicitly include compliance conflict
   computation (already has raw_scaling_event, already has in_change_freeze and
   in_maintenance_window available — instruct it to apply compliance gating inline)
4. Verify YAML valid
5. Commit, merge, run smoke_21

---

## Files Affected

- `benchmarks/resource_scaling_structured_spec/structured_spec_input.yaml`

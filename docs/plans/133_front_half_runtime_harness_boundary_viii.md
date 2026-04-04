# Plan #133: Front-Half Runtime-Harness Boundary VIII

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 131
**Blocks:** 134

---

## Gap

**Current:** smoke_18 produced `blocked_on_harness` — AC14 all 3 attempts failed
with `generation` category.

**Dominant blocker (from smoke_18):**

2 of 3 AC14 attempts failed with:
```
unable to infer one unique final component from structured spec output
'scaling_decision_entry': multiple non-source exact-name candidates
['apply_compliance_and_execution.scaling_decision_entry:scaling_decision_entry',
 'evaluate_thresholds_and_policy.scaling_decision_entry:scaling_decision_entry',
 'normalize_scaling_event.scaling_decision_entry:scaling_decision_entry']
```

1 of 3 AC14 attempts failed with:
```
draft blueprint plan binding references unknown to_port 'scaling_decision_entry'
```

The LLM generates blueprints where 3 components
(normalize_scaling_event, evaluate_thresholds_and_policy, apply_compliance_and_execution)
all have output ports named `scaling_decision_entry`. None is a sink. None is a leaf.
The `leaf_non_source_exact_name_candidates` tier returns empty. The
`non_source_exact_name_candidates` tier finds all 3 and raises.

**Root cause:** The terminal-tier fix in Plan #131 added
`terminal_non_source_schema_name_candidates` (filters by schema match, checks
consumer doesn't produce same schema) but did NOT add the equivalent tier for
**exact-name** candidates. The exact-name tiers fire first in the cascade:

1. sink_exact_name → 0
2. leaf_non_source_exact_name → 0
3. non_source_exact_name → 3 → **RAISES**

The terminal logic must be applied before step 3 raises.

**Fix direction:** Add `terminal_non_source_exact_name_candidates` tier between
`leaf_non_source_exact_name` and `non_source_exact_name`. Computation mirrors
the schema-name terminal tier:
- For each binding, if the consuming component has an output port with the same
  port name as `structured_output.name`, mark `(from_component, from_port)` as
  intermediate (not terminal)
- `terminal_non_source_exact_name_candidates` = `non_source_exact_name_candidates`
  minus those that are intermediate

In the 3-component chain:
- normalize_scaling_event.scaling_decision_entry → evaluate_thresholds_and_policy
  (which has output `scaling_decision_entry`) → **intermediate**
- evaluate_thresholds_and_policy.scaling_decision_entry → apply_compliance_and_execution
  (which has output `scaling_decision_entry`) → **intermediate**
- apply_compliance_and_execution.scaling_decision_entry → record_decision
  (which does NOT have output `scaling_decision_entry`) → **terminal**

---

## Acceptance Criteria

- [x] smoke_18 produced `blocked_on_harness`.
- [x] Dominant harness blocker named: 3 non-source exact-name candidates, no terminal tier.
- [x] The next move is explicit as Plan #134.

---

## Continuation Contract

If this boundary activates, immediately continue into
[Plan #134: Front-Half Runtime-Harness Repair VIII And Smoke Rerun XIX](134_front_half_runtime_harness_repair_viii_and_smoke_rerun_xix.md).

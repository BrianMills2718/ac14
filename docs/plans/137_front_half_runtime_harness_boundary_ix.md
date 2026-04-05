# Plan #137: Front-Half Runtime-Harness Boundary IX

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 136
**Blocks:** 138

---

## Gap

**Current:** smoke_20 produced `blocked_on_harness`.

1/3 AC14 attempts failed with generation failure. 2/3 reached `runtime_outputs`.
Monolithic attempt_3 now only fails RSC-102 (progress from all 4 failures).

---

## Dominant Blocker: Source Inference Collision (attempt_1)

- "unable to infer one unique source component from structured spec input
  'raw_scaling_event': multiple exact-name input port candidates
  ['apply_compliance_and_execution.raw_scaling_event:raw_scaling_event',
   'normalize_scaling_event.raw_scaling_event:raw_scaling_event']"

**Root cause**: Plan #136 spec change added `input_names: [raw_scaling_event, scaling_decision_entry]`
to apply_compliance_and_execution. The LLM generated a blueprint where
apply_compliance_and_execution has an input port named `raw_scaling_event`.
When the harness tries to find which component should receive the benchmark's
raw_scaling_event fixture, it finds two candidates and raises.

**Fix direction**: Change apply_compliance_and_execution `input_names` to
`[scaling_decision_entry]` only. The compliance/execution logic needs in_change_freeze
and in_maintenance_window from the raw event — move that responsibility to
evaluate_thresholds_and_policy (which already takes raw_scaling_event and has
access to all fields). The policy evaluator computes the compliance conflict and
final blocked/authorization_mode; the compliance executor just receives the
recommendation and validates/confirms it.

---

## Acceptance Criteria

- [x] smoke_20 produced `blocked_on_harness`
- [x] Source inference collision blocker named and root cause traced
- [x] The next move is explicit as Plan #138

---

## Continuation Contract

Immediately continue into
[Plan #138: Front-Half Runtime-Harness Repair IX And Smoke Rerun XXI](138_front_half_runtime_harness_repair_ix_and_smoke_rerun_xxi.md).

# Order Exception Resolution Benchmark

## Goal

Resolve order-exception cases into deterministic operator-facing digest entries.

This benchmark exists to compare:

1. a whole-task monolithic generation condition
2. an AC14 packetized decomposition condition

on the same business problem, requirements, inputs, and evaluation harness.

## Problem Shape

The system must handle:

1. multi-factor exception reasoning across inventory, shipping, customer, and override data
2. one optional manual-override path
3. at least one real fan-in boundary before final resolution
4. one state-owning sink that accumulates digest entries across multiple cases

## Business Rules

1. Inventory shortage takes priority when requested quantity exceeds available quantity, unless a manual override is present.
2. Shipping delay becomes material at 24+ hours and severe at 48+ hours or when shipment status is `exception`.
3. Platinum customers and gold customers with open_case_count >= 3 should be treated as `expedite` customer_priority_lane and escalated more aggressively than standard customers. Standard customers and gold customers with open_case_count < 3 use `standard` customer_priority_lane.
4. Manual override should remain explicit in the final digest entry rather than disappearing into implicit priority changes.
5. The final digest store must preserve entry order and contain at most one entry per case_id.
6. When BOTH an inventory shortage (quantity_requested > available_quantity) AND a severe shipping delay (delay >= 48h OR shipment_status == "exception") are present simultaneously, classify the case as a compound exception: set exception_type to `compound_exception`, blocker_source to `compound`, priority_band to `critical`, recommended_team to `exception_desk`, and action_summary to indicate coordinated exception desk escalation. Compound exceptions override individual exception routing.
7. The `resolution_digest_store.generated_at` field must be a valid ISO 8601 timestamp. Its exact value is not compared by the harness because it is a wall-clock timestamp; existence and format are what matter.
8. The `resolution_digest_entry.action_summary` field must be present but its exact text is not compared by the harness. Semantic review evaluates whether the action summary is appropriate given the case. Example: "expedite allocation and notify account team", "open carrier escalation", "coordinate exception desk escalation".
9. The `resolution_digest_store.entries` list must be present. Its exact entry-level content (including action_summary text) is evaluated by semantic review rather than exact comparison, because the cumulative store reflects free-form summaries. The categorical fields on `resolution_digest_entry` (exception_type, priority_band, blocker_source, etc.) are still compared exactly.

## Output Contract

For each case, the system must return:

1. `resolution_digest_entry`
2. `resolution_digest_store`

`resolution_digest_entry` must include:

1. `case_id`
2. `order_id`
3. `exception_type`
4. `blocker_source`
5. `priority_band`
6. `recommended_team`
7. `customer_priority_lane`
8. `action_summary`
9. optional `override_applied`

`resolution_digest_store` must include:

1. `generated_at`
2. ordered `entries`

## Fairness Constraints For The Comparison

1. Both conditions receive these requirements plus the same input artifacts and evaluation harness.
2. Both conditions use the same model family/version when practical.
3. Both conditions are allowed up to 3 bounded attempts per trial.
4. Manual code edits inside a counted trial are not allowed.

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
3. Platinum customers and gold customers with repeated open cases should escalate more aggressively than standard customers.
4. Manual override should remain explicit in the final digest entry rather than disappearing into implicit priority changes.
5. The final digest store must preserve entry order and contain at most one entry per case_id.

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

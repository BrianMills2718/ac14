# Plan #112: Front-Half Runtime-Harness Boundary III

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 111
**Blocks:** 113

---

## Gap

**Current:** If smoke_9 still says `blocked_on_harness`, AC14 will have moved
past both source-input and final-output contract inference but still failed the
runtime hard harness.

**Target:** Freeze the next runtime/harness blocker boundary from the fresh
smoke_9 artifact instead of letting the chain dissolve into vague follow-up
work.

**Why:** The front-half-first lane only stays empirically honest if each smoke
artifact unlocks one explicit next blocker class.

---

## Acceptance Criteria

- [x] One explicit blocker-boundary artifact exists if smoke_9 still returns
      `blocked_on_harness`.
- [x] The dominant remaining blocker class is named precisely enough for one
      bounded repair lane.
- [x] The next move is explicit as Plan #113.

---

## Continuation Contract

If this boundary plan activates, the next required move is
[Plan #113: Front-Half Runtime-Harness Repair III And Smoke Rerun VIII](113_front_half_runtime_harness_repair_iii_and_smoke_rerun_viii.md).

## Implementation Summary (2026-04-03)

Smoke_9 ended with verdict `blocked_on_harness` and no infrastructure
contamination. The dominant blocker class is now explicit:

1. the structured-spec benchmark bundle still under-specifies the reused
   runtime contract, so runtime cases inject legacy fields like `service_id`,
   `service_tier`, `in_change_freeze`, and `in_maintenance_window` while
   generated front-half bundles often require structured-spec fields like
   `service_name`, `account_tier`, `change_freeze`, and `maintenance_mode`
2. one bounded retry emitted a zero-input `source` component, and the current
   runtime contract can only inject port-keyed inputs into input ports

The next required move is therefore not generic runtime tuning. It is one
bounded structured-spec/runtime contract repair plus one immediate smoke rerun.

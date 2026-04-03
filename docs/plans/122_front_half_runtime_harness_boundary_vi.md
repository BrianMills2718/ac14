# Plan #122: Front-Half Runtime-Harness Boundary VI

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 119
**Blocks:** 123

---

## Gap

**Current:** Smoke_14 still says `blocked_on_harness` after the structured
dependency repair. The dependency blocker is gone, but AC14 still loses two
attempts before full evaluation because runtime-contract inference cannot pick
one unique final component for `scaling_decision_entry`.

**Target:** Freeze the remaining harness-only blocker from smoke_14 into one
bounded repair lane:

1. AC14 attempts 1 and 3 both emit two non-source candidates for
   `scaling_decision_entry`
2. the ambiguous pair is the same shape both times: an intermediate compliance
   component emits the final decision and a downstream recorder re-emits the
   same schema as the leaf system output
3. the next repair must prefer the unique leaf output instead of failing loud on
   that duplicate pass-through pattern

**Why:** If pre-runtime contract hardening is insufficient, the next move must
be a narrower harness repair rather than drifting into benchmark-local tuning.

---

## Acceptance Criteria

- [x] Smoke_14 still says `blocked_on_harness`.
- [x] The remaining harness blocker is named precisely enough for one bounded
      repair lane.
- [x] The next move is explicit as Plan #123.

---

## Continuation Contract

The next required move is
[Plan #123: Front-Half Runtime-Harness Repair VI And Smoke Rerun XIII](123_front_half_runtime_harness_repair_vi_and_smoke_rerun_xiii.md).

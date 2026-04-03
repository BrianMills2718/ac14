# Plan #129: Front-Half Provider Fallback And Smoke Rerun XVI

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 128
**Blocks:** None

---

## Gap

**Current:** If smoke_14 returns `blocked_on_infrastructure`, then AC14 needs
one bounded provider or routing repair lane before another smoke artifact can
say anything about the thesis.

**Target:** Repair the exact infrastructure blocker frozen by Plan #128, verify
the provider surface honestly, then rerun one bounded smoke trial immediately.

**Why:** Infrastructure failures should be cleared explicitly and cheaply rather
than silently poisoning front-half verdicts.

---

## Acceptance Criteria

- [ ] The provider or routing blocker frozen by Plan #128 is repaired or
      deliberately rerouted.
- [ ] Verification proves the repair before the rerun.
- [ ] One fresh smoke artifact exists after the repair.
- [ ] The next branch is explicit from the new artifact.

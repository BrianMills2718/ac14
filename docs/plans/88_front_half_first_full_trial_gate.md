# Plan #88: Front-Half-First Full Trial Gate

**Status:** Planned
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 87
**Blocks:** None

---

## Gap

**Current:** The repo can reach a bounded front-half-first smoke verdict, but
that alone is not the actual empirical comparison.

**Target:** If Plan #87 says `ready_for_full_trials`, spend the bounded
front-half-first full-trial budget and persist the verdict artifact.

**Why:** This is the next honest thesis-facing gate once the smoke artifact says
the benchmark is worth spending.

---

## Acceptance Criteria

- [ ] A full front-half-first trial artifact set exists.
- [ ] The final empirical verdict is persisted explicitly.
- [ ] The repo updates its story surfaces from that verdict instead of from
      expectation.

---

## Notes

This plan is conditional. It only activates if Plan #87 produces
`ready_for_full_trials`.

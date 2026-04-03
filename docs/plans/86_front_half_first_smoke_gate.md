# Plan #86: Front-Half-First Smoke Gate

**Status:** Planned
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 85
**Blocks:** None

---

## Gap

**Current:** The repo has the front-half-first empirical direction, but no
bounded smoke gate yet for the new structured-spec comparison surface.

**Target:** Run one bounded smoke paired trial comparing:

1. AC14 from structured-spec input through front half and generated system
2. a monolithic baseline from the same structured-spec input and requirements

**Why:** The project needs a cheap stop/go artifact before it spends another
full empirical budget.

---

## Acceptance Criteria

- [ ] One bounded front-half-first smoke artifact exists.
- [ ] The next branch is explicit: full trial or blocker-clearing lane.

# Plan #86: Front-Half-First Smoke Gate

**Status:** In Progress
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

---

## Open Question

### Q1: What should the first front-half-first smoke gate treat as success?
**Status:** Investigating
**Why it matters:** The existing empirical runner judges generated systems
against runtime outputs from a frozen blueprint benchmark. The new bundle adds a
front-half input surface, so the smoke gate must decide whether success means:

1. strong front-half artifacts only
2. strong front-half artifacts plus final generated runtime outputs
3. a staged combination of both

**Current direction:** Keep the gate honest by reusing the existing runtime
evaluation assets where possible, but do not pretend this decision is already
fully pre-made.

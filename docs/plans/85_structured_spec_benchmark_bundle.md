# Plan #85: Structured-Spec Benchmark Bundle

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 84
**Blocks:** 86

---

## Gap

**Current:** AC14 will have a structured-spec front-half lane, but not yet one
benchmark-ready structured-spec bundle that both AC14 and a monolithic baseline
can consume fairly.

**Target:** Freeze one benchmark-ready structured-spec bundle with matching
requirements, review criteria, and baseline inputs for the next empirical gate.

**Why:** The front-half-first comparison needs one shared input contract instead
of ad hoc benchmark assembly.

---

## Acceptance Criteria

- [ ] One benchmark-ready structured-spec bundle exists.
- [ ] Both AC14 and the monolithic condition can consume it from the same raw inputs.
- [ ] The artifact states what the next smoke gate should measure.

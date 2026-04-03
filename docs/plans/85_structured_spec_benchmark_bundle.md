# Plan #85: Structured-Spec Benchmark Bundle

**Status:** Complete
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

- [x] One benchmark-ready structured-spec bundle exists.
- [x] Both AC14 and the monolithic condition can consume it from the same raw inputs.
- [x] The artifact states what the next smoke gate should measure.

## Implementation Summary (2026-04-02)

What landed:

- a typed structured-spec benchmark loader in `ac14/structured_spec_benchmark.py`
- a benchmark-ready bundle in `benchmarks/resource_scaling_structured_spec/`
- an explicit reference from the new front-half-first bundle back to the
  existing `resource_scaling` runtime evaluation assets

What this resolves:

- the next empirical gate now has a shared structured-spec input contract
- the bundle is anchored to a real existing runtime evaluation surface instead
  of inventing a disconnected benchmark

What remains for the next plan:

- the runner still needs an explicit decision about what the smoke gate judges:
  front-half artifacts only, final generated runtime outputs, or both

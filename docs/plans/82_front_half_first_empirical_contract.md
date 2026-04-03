# Plan #82: Front-Half-First Empirical Contract

**Status:** Complete
**Type:** evaluation + planning
**Priority:** Critical
**Blocked By:** 81
**Blocks:** 83

---

## Gap

**Current:** AC14 now has one inconclusive back-half gate, one decisive harder
back-half loss, and one non-winning reusable grounding rerun. The project needs
an empirical next move that actually tests where AC14 claims advantage:
pre-freeze context gathering, decomposition, and blueprint derivation.

**Target:** Define one explicit front-half-first empirical contract that
compares:

1. AC14 from messy or structured specification inputs through draft/freeze into
   generated system outputs
2. a fair monolithic baseline from the same raw inputs and requirements

**Why:** The current back-half slice is now measured. The next honest thesis
test should include the front half instead of spending more energy on a slice
that has already lost the harder benchmark.

---

## References Reviewed

- `docs/plans/81_post_grounding_strategic_pivot.md`
- `docs/AC14_ROADMAP.md`
- `docs/AC14_IMPLEMENTATION_STATUS.md`
- `KNOWLEDGE.md`
- `~/projects/theory-forge/docs/plans/08_ac14_codegen_integration.md`

---

## Open Questions

### Q1: What should the next empirical surface compare?
**Status:** Resolved
**Why it matters:** The next benchmark must match the thesis, not only the current machinery.
**Resolution:** Compare end-to-end front-half-plus-back-half generation from
structured or messy specification inputs against a monolithic baseline from the
same raw inputs.

### Q2: What is the smallest next implementation slice that moves AC14 toward that test?
**Status:** Resolved
**Why it matters:** The project needs one bounded next lane, not a vague pivot.
**Resolution:** Add a minimal structured-spec input contract for blueprint
drafting. This is smaller than broad free-prose NL-to-blueprint and directly
supports the first consumer-aligned front-half benchmark surface.

---

## Files Affected

- `docs/plans/82_front_half_first_empirical_contract.md` (create)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/plans/CLAUDE.md` (modify)

---

## Plan

### Steps

1. Freeze the claim boundary from the completed back-half gates.
2. Define the next empirical contract as front-half-first.
3. Freeze one bounded implementation lane to support that contract.

---

## Acceptance Criteria

- [x] The repo states that the next empirical horizon is front-half-first.
- [x] The repo states what the next comparison should compare.
- [x] One bounded implementation lane is frozen from that contract.

---

## Notes

This plan intentionally does not reopen the harder back-half gate.

## Implementation Summary (2026-04-02)

Front-half-first empirical contract:

- AC14 condition:
  - structured or messy specification inputs
  - discovery / retrieval / dependency context as needed
  - draft planning -> draft bundle -> freeze decision
  - generated system outputs
- monolithic condition:
  - the same raw specification inputs and requirements
  - no frozen blueprint packetization advantage
  - direct whole-task generation

Decision rule:

- the next benchmark should measure whether AC14's front-half decomposition and
  context management produce better final systems or better reviewable
  intermediate artifacts than the monolithic baseline

Frozen next move:

- [Plan #83: Structured Spec Input Contract](/home/brian/projects/ac14/docs/plans/83_structured_spec_input_contract.md)

Why this lane:

- it is smaller and more truthful than claiming a broad free-prose
  NL-to-blueprint path immediately
- it aligns with the theory-forge consumer direction without pretending that
  the full NL path already exists

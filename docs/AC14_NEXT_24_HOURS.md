# AC14 Next 24 Hours

Status: In Progress
Last updated: 2026-04-01

## Purpose

This document is the tactical summary for the active numbered plan.

The authoritative implementation contract for the current lane is:

- [Plan #37: Directory Divergence Front-Half Proof](/home/brian/projects/ac14/docs/plans/37_directory_divergence_front_half_proof.md)

Plan #36 closed the raw discovery divergence lane. The active 24-hour
chain is now:

1. prove that the new directory schema-divergence concerns survive the
   front-half chain
2. keep one explicit primary structured planning input while preserving the new
   divergence evidence
3. keep CLI and Make parity so the propagation proof is reviewable

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery, draft planning, authoring, freeze remediation, and promotion
3. realistic-input front-half acceptance from discovery through freeze decision
4. realistic-input full-system acceptance in `reference`, `deterministic`, and one bounded `llm` slice
5. suite-level realistic-input acceptance artifacts across shipped examples for supported non-LLM modes
6. suite-level realistic-input acceptance artifact in `llm` mode via the fixture-backed breadth lane
7. blueprint-aware fixture-backed LLM codegen so repeated component IDs no longer collide across blueprints

Completed in Plan #36:

1. directory discovery now compares the primary structured candidate against
   alternate structured candidates explicitly
2. directory discovery now persists bounded schema-divergence concerns instead
   of leaving shape drift implicit
3. CLI and Make discovery surfaces preserve the same divergence concerns

Required in Plan #37:

1. one front-half proof that preserves the new divergence concerns
2. CLI and Make parity for the same divergence propagation story
3. no duplicate schema-truth surface outside the discovery artifact

## Tactical Phase Summary

Detailed references, write scope, tests, and acceptance criteria live in Plan
#37.

### Phase 1: direct front-half divergence proof

- prove that directory-input front-half acceptance preserves the new
  schema-divergence concerns
- keep the divergence evidence inside the persisted discovery artifact

### Phase 2: operator parity

- prove the same divergence story through CLI
- prove the same divergence story through Make

### Phase 3: verification and lock

- run targeted directory-input front-half verification
- run full verification and lock the docs

## Known Uncertainties

The detailed uncertainty ledger now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

Current lane-specific uncertainties:

1. divergence propagation must not create a second conflicting truth surface
2. one explicit primary structured planning input must remain visible
3. the front-half proof should stay on the standard path, not broaden into
   retry-aware proof yet

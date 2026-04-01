# AC14 Next 24 Hours

Status: In Progress
Last updated: 2026-04-01

## Purpose

This document is the tactical summary for the active numbered plan.

The authoritative implementation contract for the current lane is:

- [Plan #29: Explicit Realistic-Input Policy](/home/brian/projects/ac14/docs/plans/29_explicit_realistic_input_policy.md)

Plan #28 closed the first bounded messy-input `llm` final-gate lane. The active
24-hour chain is now:

1. explicit per-example realistic-input policy with a named default and named alternate profiles
2. profile-aware parity across front-half, final-gate, and suite/default realistic-input surfaces
3. one explicit suite-level `messy` profile proof that preserves the clean default path

Plan #28 closed the bounded messy-input `llm` final-gate proof. The immediate
active gap is now that realistic-input choice is still implicit and inconsistent
across surfaces once one shipped example has both a clean JSON input and a
messy CSV input.

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery, draft planning, authoring, freeze remediation, and promotion
3. realistic-input front-half acceptance from discovery through freeze decision
4. realistic-input full-system acceptance in `reference`, `deterministic`, and one bounded `llm` slice
5. suite-level realistic-input acceptance artifacts across shipped examples for supported non-LLM modes
6. suite-level realistic-input acceptance artifact in `llm` mode via the fixture-backed breadth lane
7. blueprint-aware fixture-backed LLM codegen so repeated component IDs no longer collide across blueprints

Completed in Plan #15:

1. recommendation now consumes the suite-level live-readiness artifact explicitly
2. recommendation reasons now fail loud when suite live readiness is not ready
3. status/docs now stop presenting recommendation as dependent on only the bounded one-example live probe

Required in Plan #29:

1. explicit realistic-input manifests for shipped examples
2. one shared resolver with named default and alternate profiles
3. fail-loud behavior for invalid profile selection

## Tactical Phase Summary

Detailed references, write scope, tests, and acceptance criteria live in Plan
#29 through Plan #31.

### Phase 1: explicit realistic-input policy

- define a small manifest format for shipped example input directories
- make the default realistic-input choice explicit instead of relying on hidden precedence

### Phase 2: cross-surface profile parity

- make front-half and final-gate realistic-input resolution consume the same profile-aware resolver
- persist selected-profile or missing-profile state explicitly in suite artifacts

### Phase 3: messy-profile suite proof

- prove one explicit suite-level `messy` profile lane without silently redefining the clean default proof path
- keep missing-profile states reviewable rather than silently falling back

## Known Uncertainties

The detailed uncertainty ledger now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

Current lane-specific uncertainties:

1. realistic-input selection should not remain hidden extension precedence once examples ship more than one candidate artifact
2. front-half and final-gate defaults should stay aligned instead of drifting by format support
3. suite/profile behavior should stay explicit about `missing_profile` rather than silently falling back

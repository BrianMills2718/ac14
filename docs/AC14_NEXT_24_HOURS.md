# AC14 Next 24 Hours

Status: In Progress
Last updated: 2026-04-01

## Purpose

This document is the tactical summary for the active numbered plan.

The authoritative implementation contract for the current lane is:

- [Plan #31: Messy-Profile Suite Proof](/home/brian/projects/ac14/docs/plans/31_messy_profile_suite_proof.md)

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

Required in Plan #31:

1. one explicit front-half suite lane on the `messy` profile
2. one realistic-input suite lane on the same `messy` profile across bounded modes
3. explicit included-versus-missing-profile accounting without changing the clean default proof path

## Tactical Phase Summary

Detailed references, write scope, tests, and acceptance criteria live in Plan
#31.

### Phase 1: front-half messy-profile suite proof

- verify the explicit `messy` profile through the front-half suite artifact
- keep missing-profile states reviewable and keep the clean default path unchanged

### Phase 2: realistic-input messy-profile suite proof

- verify the same explicit `messy` profile through the realistic-input suite artifact
- extend the proof across bounded modes, including fixture-backed `llm`

### Phase 3: verification and lock

- run targeted messy-profile suite verification
- run full verification and lock the docs

## Known Uncertainties

The detailed uncertainty ledger now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

Current lane-specific uncertainties:

1. the first alternate-profile suite proof should stay bounded and reviewable instead of pretending broad breadth
2. the `llm` part of the messy-profile suite proof must stay fixture-backed and separate from live readiness
3. the clean default path should remain the default proof story even after the alternate-profile suite proof exists

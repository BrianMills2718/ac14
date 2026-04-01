# AC14 Next 24 Hours

Status: In Progress
Last updated: 2026-04-01

## Purpose

This document is the tactical summary for the active numbered plan.

The authoritative implementation contract for the current lane is:

- [Plan #32: Multi-Artifact Discovery Inputs](/home/brian/projects/ac14/docs/plans/32_multi_artifact_discovery_inputs.md)

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

Required in Plan #32:

1. directory-based discovery support with explicit candidate inventory
2. one explicit primary structured candidate plus explicit alternatives
3. CLI and Make parity for directory-based discovery

## Tactical Phase Summary

Detailed references, write scope, tests, and acceptance criteria live in Plan
#32.

### Phase 1: directory discovery contract

- allow discovery to accept an input directory as one reviewable unit
- inventory supported structured candidates and supporting context files explicitly

### Phase 2: explicit primary-candidate persistence

- choose one primary structured candidate deterministically
- persist the chosen primary candidate and the alternatives in the discovery artifact

### Phase 3: verification and lock

- run targeted multi-artifact discovery verification
- run full verification and lock the docs

## Known Uncertainties

The detailed uncertainty ledger now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

Current lane-specific uncertainties:

1. multi-artifact discovery should not silently turn into hidden multi-file orchestration
2. primary-candidate choice must stay explicit and reviewable
3. discovery breadth should strengthen the front half without weakening packet/freeze explicitness

# AC14 Next 24 Hours

Status: In Progress
Last updated: 2026-04-01

## Purpose

This document is the tactical summary for the active numbered plan.

The authoritative implementation contract for the current lane is:

- [Plan #27: Messy-Input Full-System Acceptance](/home/brian/projects/ac14/docs/plans/27_messy_input_full_system_acceptance.md)

Plan #25 closed the first retry-aware messy-input front-half lane. The active
24-hour chain is now:

1. shared structured-input loading for realistic-input acceptance
2. messy-input full-system acceptance in non-LLM modes
3. bounded messy-input `llm` comparison

Plan #26 closed the structured-loading blocker. The immediate active gap is now
that the messy CSV asset still has no explicit full-system realistic-input
acceptance proof even though the final gate can now load it.

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

Required in Plan #27:

1. one explicit messy-input full-system acceptance lane in `reference` mode
2. one explicit messy-input full-system acceptance lane in `deterministic` mode
3. one messy-input realistic mode-comparison artifact across the non-LLM modes

## Tactical Phase Summary

Detailed references, write scope, tests, and acceptance criteria live in Plan
#27.

### Phase 1: messy-input final-gate scope design

- reuse the shipped support-ticket CSV asset as the next full-system proof target
- keep the first messy-input final-gate lane within `reference` and `deterministic`

### Phase 2: messy-input non-LLM acceptance implementation

- prove the messy CSV asset through `acceptance-review`
- prove the same asset through the realistic mode-comparison surface for `reference` and `deterministic`

### Phase 3: Verification And Lock

- targeted messy-input full-system verification
- full local verification
- doc lock, then advance immediately to Plan #28 in the same 24-hour chain

## Known Uncertainties

The detailed uncertainty ledger now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

Current lane-specific uncertainties:

1. the first full-system messy-input lane should stay within existing semantic-acceptance rules instead of inventing a new execution model
2. bounded messy-input `llm` proof must remain clearly separate from live readiness
3. suite defaults should not silently switch from the clean JSON input to the messy CSV asset

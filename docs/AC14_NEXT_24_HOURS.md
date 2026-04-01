# AC14 Next 24 Hours

Status: In Progress
Last updated: 2026-04-01

## Purpose

This document is the tactical summary for the active numbered plan.

The authoritative implementation contract for the current lane is:

- [Plan #28: Messy-Input LLM Comparison](/home/brian/projects/ac14/docs/plans/28_messy_input_llm_comparison.md)

Plan #25 closed the first retry-aware messy-input front-half lane. The active
24-hour chain is now:

1. shared structured-input loading for realistic-input acceptance
2. messy-input full-system acceptance in non-LLM modes
3. bounded messy-input `llm` comparison

Plan #27 closed the non-LLM messy-input final-gate proof. The immediate active
gap is now that the bounded `llm` realistic-input lane still has no explicit
proof on the same messy CSV asset.

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

Required in Plan #28:

1. one bounded messy-input `llm` realistic-input acceptance lane
2. one messy-input realistic mode-comparison artifact across `reference`, `deterministic`, and `llm`
3. explicit separation between fixture-backed `llm` breadth and live readiness

## Tactical Phase Summary

Detailed references, write scope, tests, and acceptance criteria live in Plan
#28.

### Phase 1: bounded messy-input `llm` scope design

- reuse the same shipped support-ticket CSV asset as the next bounded `llm` proof target
- keep the first messy-input `llm` lane fixture-backed and clearly separate from live readiness

### Phase 2: bounded messy-input `llm` implementation

- prove the messy CSV asset through `acceptance-review` in `llm` mode
- prove the same asset through the realistic mode-comparison surface for `reference`, `deterministic`, and `llm`

### Phase 3: Verification And Lock

- targeted messy-input `llm` verification
- full local verification
- doc lock and clean commit

## Known Uncertainties

The detailed uncertainty ledger now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

Current lane-specific uncertainties:

1. bounded messy-input `llm` proof must remain clearly separate from live readiness
2. suite defaults should not silently switch from the clean JSON input to the messy CSV asset
3. the messy CSV asset should remain schema-sufficient instead of relying on hidden runtime normalization

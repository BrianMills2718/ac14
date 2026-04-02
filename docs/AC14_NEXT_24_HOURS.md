# AC14 Next 24 Hours

Status: In Progress
Last updated: 2026-04-01

## Purpose

This document is the tactical summary for the active numbered plan.

The authoritative implementation contract for the current lane is:

- [Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md)

The empirical gate is now frozen in
[Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md).
The active 24-hour chain is now:

1. build the benchmark asset bundle for the frozen comparison target
2. execute paired `monolithic` and `AC14` trials under the frozen fairness rules
3. persist one reviewable decision artifact instead of treating experiment
   results as conversational judgment

## Progress Update

Completed before this lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery, draft planning, authoring, freeze remediation, and promotion
3. realistic-input front-half acceptance from discovery through freeze decision
4. realistic-input full-system acceptance in `reference`, `deterministic`, and one bounded `llm` slice
5. suite-level realistic-input acceptance artifacts across shipped examples for supported non-LLM modes
6. suite-level realistic-input acceptance artifact in `llm` mode via the fixture-backed breadth lane
7. blueprint-aware fixture-backed LLM codegen so repeated component IDs no longer collide across blueprints

Completed before this lane as the immediate predecessor:

1. the active control surface now points to an empirical gate instead of
   another default propagation-proof lane
2. one AC14-native notebook now freezes the first comparison target, fairness
   protocol, primary outcome, and decision rule
3. Plan #37 is now explicitly blocked behind the comparison result

Required in Plan #39:

1. one concrete benchmark asset bundle for `order_exception_resolution`
2. one paired-trial runner that records both conditions explicitly
3. one decision artifact that applies the frozen success rule

## Tactical Phase Summary

Detailed references, write scope, tests, and acceptance criteria live in Plan
#39.

### Phase 1: benchmark assets

- create the `order_exception_resolution` benchmark bundle
- keep requirements, inputs, dependency surface, and evaluation harness explicit

### Phase 2: paired execution

- run one `monolithic` condition and one `AC14` condition per paired trial
- preserve cost, time, repair-loop, and output artifacts for both

### Phase 3: scoring and lock

- apply the frozen decision rule to five paired trials
- lock the docs around the result

## Known Uncertainties

The detailed uncertainty ledger now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

Current lane-specific uncertainties:

1. the benchmark assets and harness do not exist yet
2. the paired-trial runner will need to keep both conditions equally bounded
3. the first experiment may still end inconclusive if five trials do not separate the conditions

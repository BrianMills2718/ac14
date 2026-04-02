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

1. finalize and validate the benchmark asset bundle for the frozen comparison target
2. implement the bounded `monolithic` trial path
3. implement the bounded `AC14` trial path
4. persist one reviewable decision artifact instead of treating experiment
   results as conversational judgment
5. run the five fresh paired trials and lock the docs to the result

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

1. one validated benchmark asset bundle for `order_exception_resolution`
2. one paired-trial runner that records both conditions explicitly
3. one decision artifact that applies the frozen success rule
4. one five-trial experiment result that is reviewable artifact-by-artifact

Current empirical-gate reality:

1. the benchmark bundle exists and validates
2. the paired-trial runner and decision artifact exist
3. bounded live smoke trials have been run
4. no smoke run has yet produced a hard-harness success in either condition
5. repeated provider disconnects and `503` demand errors were observed during live runs

That means Phase 5 is not ready yet. The immediate next step is to get one
successful smoke paired trial or document a benchmark/generator blocker clearly
enough to justify stopping the five-trial execution.

## Tactical Phase Summary

Detailed references, write scope, tests, and acceptance criteria live in Plan
#39.

### Phase 1: benchmark assets and validation

- create the `order_exception_resolution` benchmark bundle
- keep requirements, inputs, dependency surface, and evaluation harness explicit
- validate that the benchmark blueprint loads and that runtime inputs and
  expected outputs are structurally coherent

Success criteria:

- the bundle is fully reviewable without chat context
- the benchmark blueprint loads cleanly
- runtime inputs and expected outputs match the declared source and sink contract

### Phase 2: monolithic condition

- generate the whole benchmark system in one bounded condition
- keep attempts, cost capture, and output artifacts explicit

Success criteria:

- one `monolithic` trial can run end to end without manual code edits
- the trial artifact records attempts, outputs, and pass/fail reasons

### Phase 3: AC14 condition

- generate the benchmark system through packetized AC14 codegen
- preserve packet tests, recomposition proof, realistic-input execution, and
  output artifacts inside the paired-trial result

Success criteria:

- one `AC14` trial can run end to end without manual code edits
- the trial artifact records attempts, outputs, and pass/fail reasons

### Phase 4: scoring and decision

- apply the frozen decision rule to five paired trials
- persist one final decision artifact plus per-trial summaries

Success criteria:

- the decision is traceable back to trial-level evidence
- the result can be `ac14_wins`, `monolithic_wins`, or `inconclusive` only

### Phase 5: repeated trials and lock

- run the five fresh paired trials under the frozen fairness rules
- run full verification
- lock the docs around the result

Success criteria:

- the experiment is complete, verified, and reviewable without chat context
- the active control surface reflects the actual result instead of a planned one

Current blocker before Phase 5:

- one bounded smoke paired trial has not yet produced a hard-harness success
- live provider instability is currently mixed into the experiment surface
- do not spend the full five-trial budget until one smoke trial either succeeds
  or proves that the current benchmark/prompt setup is itself the blocker

## Known Uncertainties

The detailed uncertainty ledger now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

Current lane-specific uncertainties:

1. the first experiment may still end inconclusive if five trials do not separate the conditions
2. the monolithic condition must be bounded without silently giving it a looser repair budget
3. the first ablation should isolate the decomposition claim itself; if the front-half derivation question starts to dominate this lane, that needs to be logged explicitly instead of smuggled in
4. current live smoke trials have not yet produced a single hard-harness success
5. provider disconnects and demand errors may contaminate the empirical gate unless they are recorded explicitly

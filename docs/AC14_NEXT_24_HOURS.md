# AC14 Next 24 Hours

Status: In Progress
Last updated: 2026-04-02

## Purpose

This document is the tactical summary for the active numbered plan.

The authoritative implementation contract for the current lane is:

- [Plan #50: Empirical Contract And Benchmark Fidelity Repair](/home/brian/projects/ac14/docs/plans/50_empirical_contract_and_benchmark_fidelity_repair.md)

The empirical gate is frozen in
[Plan #38: Empirical Comparison Gate](/home/brian/projects/ac14/docs/plans/38_empirical_comparison_gate.md).
The parent experiment lane remains:

- [Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md)

The next bounded smoke rerun is already frozen in:

- [Plan #51: Empirical Smoke Gate Refresh III](/home/brian/projects/ac14/docs/plans/51_empirical_smoke_gate_refresh_iii.md)

## Active 24-Hour Chain

1. complete Plan #50 benchmark-contract and fidelity repair
2. rerun one bounded smoke paired trial via Plan #51
3. unblock Plan #43 only if the fresh smoke artifact says `ready_for_full_trials`
4. if the smoke artifact still says `blocked_on_harness`, freeze the next narrower blocker-clearing plan immediately instead of spending the five-trial budget
5. only after full trials exist should Plan #44 interpret the verdict

## Progress Update

Completed before the current lane:

1. six-file frozen blueprint bundle and proof surfaces
2. pre-freeze discovery, draft planning, authoring, freeze remediation, and promotion
3. realistic-input front-half acceptance from discovery through freeze decision
4. realistic-input full-system acceptance in `reference`, `deterministic`, and bounded `llm` slices
5. suite-level realistic-input acceptance artifacts across shipped examples
6. blueprint-aware fixture-backed LLM codegen so repeated component IDs no longer collide across blueprints
7. an explicit empirical comparison gate instead of an endless propagation-plan loop
8. a validated benchmark asset bundle, paired-trial runner, and persisted decision artifact
9. bounded smoke gates through repair7, which proved the lane is still `blocked_on_harness`
10. Plan #49 observability hardening so every empirical attempt now persists packet and recomposition reports directly and semantic-eval prompt inputs are JSON-safe for datetime-bearing fixtures

Current empirical-gate reality:

1. the benchmark bundle exists and validates
2. the paired-trial runner and decision artifact exist
3. bounded live smoke trials have been run through repair7
4. the latest explicit smoke verdict remains `blocked_on_harness`
5. the harness is now substantially more observable: packet and recomposition failures no longer require manual reruns for basic diagnosis
6. the remaining blocker set is now narrow and concrete:
   - multiline boolean conditions without parentheses
   - pre-class `GeneratedComponent` return annotations
   - ORX-101 shipping-only routing/classification fidelity
   - exact `case_parser.normalized_notes` lowercasing-only behavior

## Tactical Phase Summary

Detailed references, write scope, tests, and acceptance criteria live in the numbered plans.

### Phase 1: Plan #50 repair lane

- harden prompts and benchmark-local guidance against the remaining generator-contract failures
- harden benchmark-local guidance against the remaining business-logic fidelity misses
- verify locally and update the active control docs

Success criteria:

- the remaining repair7 blocker classes are addressed explicitly in prompt/guidance text
- targeted tests and full verification pass
- the active docs point to Plan #51 as the next smoke rerun

### Phase 2: Plan #51 bounded smoke rerun

- rerun one bounded smoke paired trial under the repaired lane
- read the resulting smoke artifact and paired-trial artifact directly

Success criteria:

- AC14 has one fresh smoke verdict tied to one persisted smoke run
- the verdict says either `ready_for_full_trials`, `blocked_on_harness`, or `blocked_on_infrastructure`

### Phase 3: Gate decision and lock

- update the active control docs to reflect the smoke verdict
- either unblock Plan #43 honestly or keep it blocked with a narrower explicit reason

Success criteria:

- the active control surface matches the smoke outcome
- the next numbered plan is explicit and no longer ambiguous

## Known Uncertainties

The detailed uncertainty ledger now lives in:

- [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)

Current lane-specific uncertainties:

1. the first experiment may still end inconclusive even after the smoke gate clears
2. the monolithic condition must stay bounded without silently receiving a looser repair budget
3. the current comparison gate is back-half only and should not be mistaken for full end-to-end thesis validation
4. the next smoke artifact must show whether the remaining contract/fidelity repair materially changes the gate outcome

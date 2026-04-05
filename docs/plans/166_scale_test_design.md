# Plan #166 — Scale Test: Strategic Analysis and Large Benchmark Design

## Status: ACTIVE

## Empirical Evidence Summary (Plans #149–#165)

After 16 plans and 7 experimental conditions, the data is clear:

| Benchmark | Model | AC14 | Mono | Verdict |
|-----------|-------|------|------|---------|
| IT (10 comp) | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| PT (5 comp) | Gemini flash | 2/5 | 5/5 | monolithic_wins |
| BS (10 comp) | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| BS (10 comp) | Gemini flash | 4/5 | 5/5 | inconclusive |
| Zeta (10 comp) | gpt-4.1 | 4/5 | 5/5 | inconclusive |
| Zeta (10 comp) | Gemini flash | 1/5 | 5/5 | monolithic_wins |
| Zeta (10 comp) | DeepSeek | N/A (structure) | 0/5 (structure) | infrastructure |

**Key finding**: Monolithic 5/5 on ALL available benchmarks and models. AC14 consistently 
1-5/5 depending on model and codegen reliability.

## Root Cause Analysis

### Why does mono always pass?
- The structured_spec_input.yaml contains EXPLICIT formula hints for each component
- 10-component specs fit easily in any model's context window (~3,000 tokens)
- Models read the spec and implement correctly — formula memorization is irrelevant

### Why does AC14 sometimes fail?
- Code generation bugs (syntax errors, wrong function names)
- Budget split issues (planning step gets $0.30 limit when spec needs $0.46)
- Output structure mismatches in per-component codegen
- NOT because of context capacity issues

### What the thesis actually claims
"Large software generation FAILS when one model must hold TOO MUCH in context."

At 10 components: NO model fails. The benchmark is too small to stress context capacity.

## The Discriminating Scale

Based on LLM context windows and typical component code length (~100 lines/component):
- 10 components: ~1,000 lines = ~3,000 tokens → trivially fits in context
- 50 components: ~5,000 lines = ~15,000 tokens → still fits (GPT-4.1 has 128K context)
- 200 components: ~20,000 lines = ~60,000 tokens → approaching limits with reasoning
- 500 components: ~50,000 lines = ~150,000 tokens → exceeds GPT-4.1 output limits

The thesis may require 100-500 components to create genuine context capacity stress.
However, building such a benchmark is a significant engineering effort.

## Thesis Refinement Options

### Option A: Scale up dramatically (50+ components)
Build a realistic 50-component system (e.g., full order management, trading system,
data pipeline). Requires weeks of benchmark engineering.

### Option B: Noisy specification test
Instead of explicit formula hints, give monolithic a VAGUE spec requiring inference.
AC14 packets would still have explicit local hints.
Test: Can AC14 better handle specification ambiguity than monolithic?

### Option C: Cross-component invariant test
Design a benchmark where correct implementation requires tracking 20+ cross-component
constraints simultaneously. Monolithic must hold all constraints in context.
AC14 packets have local invariants; final validation checks cross-component consistency.

### Option D: Accept 10-component negative evidence and publish findings
Write up: "AC14 decomposition does not improve reliability at 10-component scale.
The benefit (if any) requires either a larger scale or weaker models than are
practically available."

## Recommended Next Step

**Option B (Noisy Specification) + limited Option C** — This is faster to build than
Option A and tests a more fundamental AC14 advantage:

Design a benchmark where:
1. The monolithic spec describes WHAT to compute but not HOW (no formula hints)
2. AC14 packets have local implementation hints derived from the blueprint
3. The correct formulas cannot be trivially derived from the spec

Example: Instead of "delta_call = zeta * N(d1_zeta)", give monolithic "delta_call should
be scaled by the variance parameter" — ambiguous enough that models make different choices.

This tests the REAL AC14 advantage: explicit per-component implementation contracts.

## Immediate Action

For this session:
1. Write this plan doc (done)
2. Commit Plan #165 and Plan #166
3. Design the noisy-spec variant of zeta_options
4. Run gate_1 with gpt-4.1

The noisy-spec variant removes the CRITICAL DIFFERENCE callouts from structured_spec_input.yaml
and replaces them with ambiguous descriptions. AC14 packets still have the explicit formulas.


# Theory Forge Benchmark Series — Summary

**Date**: 2026-04-04  
**Plans**: #149-#169  
**Status**: Complete

## What Was Tested

A series of 8 benchmarks across 4 mathematical domains to find a case where
AC14's decomposition advantage produces better code than monolithic generation.

### Benchmarks Run

| Benchmark | Domain | Components | Model | AC14 | Mono | Verdict |
|-----------|--------|------------|-------|------|------|---------|
| IT v1 | Information Theory | 10 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| PT v1 | Prospect Theory | 10 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| BS v1 | Black-Scholes | 10 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| PT v1 | Prospect Theory | 10 | Gemini flash | 4/5 | 5/5 | mono_wins (AC14 codegen errors) |
| BS v1 | Black-Scholes | 10 | Gemini flash | 4/5 | 5/5 | mono_wins (AC14 codegen errors) |
| zeta v1 | Zeta-Modified Options | 10 | gpt-4.1 | 4/5 | 5/5 | inconclusive |
| zeta v1 | Zeta-Modified Options | 10 | Gemini flash | 1/5 | 5/5 | mono_wins (budget + formula) |
| noisy_spec | Zeta Options (vague spec) | 10 | gpt-4.1 | 0/5 | 0/5 | both_fail (mono better: 10/13 fields) |

### Model Availability Tested

- claude-haiku-4-5: NOT available on OpenRouter
- gpt-4o-mini: HARD BLOCKED in llm_client
- DeepSeek: correct formulas but fails output structure (wrapper issue)
- Formula memorization hypothesis: DEFINITIVELY FALSIFIED — all models implement zeta/alpha correctly when given explicit hints

## Key Findings

### Finding 1: 10-Component Scale Doesn't Discriminate

At 10 components with explicit specs, modern capable LLMs (gpt-4.1, Gemini flash)
can implement all formulas correctly in a single monolithic call. The total code is
~80-100 lines — well within context capacity of any modern LLM.

**Implication**: The AC14 scale advantage (if it exists) requires much larger systems
(estimated 50-100+ components for a simple pipeline, or 30-50 for complex interdependencies).

### Finding 2: Explicit Spec Gives Monolithic Same Advantage as AC14

The Theory Forge design flaw: the structured_spec_input.yaml contains explicit formula
hints for BOTH conditions. AC14 uses these hints to populate component packets; monolithic
reads the same hints directly. When both conditions have the same information, the
comparison is meaningless.

**Implication**: AC14 would only have an advantage if it could:
(a) access MORE information than monolithic (e.g., library lookup, spec synthesis), OR
(b) USE the same information more efficiently through decomposition

### Finding 3: AC14 Planning Step Does NOT Synthesize Formulas

The noisy-spec experiment tested whether AC14 could infer explicit contracts from vague
descriptions. The planning step produced TODO placeholders — it restructures the problem
but does NOT derive new implementation information.

**Implication**: AC14 is not a formula synthesis system. It's a context management system.
The noisy-spec test was predicated on a capability AC14 doesn't have.

### Finding 4: Formula Memorization is Not the Discriminating Factor

All tested models (gpt-4.1, Gemini flash, DeepSeek) correctly implemented all zeta/alpha
modifications when given explicit formula hints. Formula memorization was NOT causing
failures — the models can implement novel formulas when told explicitly what to do.

**Implication**: The Theory Forge benchmark design (novel mathematical formulas to avoid
memorization) is not the right discriminating axis. The formulas are novel, but the
models are good at following specs regardless of whether the formulas are memorized.

## Root Cause: Wrong Discriminating Axis

The Theory Forge series was designed around "formula memorization" as the discriminating
axis. But all models can follow explicit specs regardless of formula novelty.

The REAL AC14 discriminating axis should be:

1. **Scale pressure**: when total code exceeds ~1000 lines, monolithic starts making
   inconsistent choices across components
2. **Contract propagation**: when cross-component invariants are complex, AC14's
   explicit per-packet contracts prevent drift from upstream constraints
3. **Implementation density**: when each component has many interacting requirements,
   bounded context helps

None of these are tested at 10-component math pipeline scale.

## What Should Have Been Different

In hindsight, the Theory Forge benchmark design was too simple:
1. Too few components (10 is trivial context load)
2. Too much information in the shared spec (mono gets same hints as AC14)
3. Too linear (components don't have complex interdependencies)
4. Math problems are well within LLM capability

A discriminating benchmark would need:
- 50+ components with complex interdependencies
- Spec that's LONG but vague about implementation (forcing inference)
- Cross-component invariants that are easy to violate when not explicitly tracked
- OR: a weaker model (haiku, gpt-4o-mini) where formula synthesis fails for both
  but AC14 provides explicit enough packets that the weaker model can succeed

## Thesis Status

**The AC14 decomposition thesis is neither confirmed nor falsified.**

The Theory Forge series provides evidence for: "At ≤10 component scale with explicit
specs, AC14 provides no measurable advantage."

The thesis remains untested for: "At ≥50 component scale, OR for complex-interdependency
systems, OR with weaker models that need more explicit contracts."

The honest conclusion: **AC14's advantage (if it exists) requires scale or complexity
beyond what the Theory Forge benchmarks tested.**

## Recommended Next Steps

### Option A: Large-Scale Benchmark (50+ components)
- Design a 50-component system with genuine cross-component interdependencies
- Run with gpt-4.1 and Gemini flash
- Cost: 5-10 days of work + significant compute
- Expected discrimination point: around 50-100 components for capable models

### Option B: Weaker Model Test
- Find a model that struggles with 10 components monolithically
- The model must be available and not hard-blocked
- Challenge: current ecosystem doesn't have a clear candidate
- DeepSeek fails on output structure (not formula), haiku/gpt-4o-mini unavailable

### Option C: Complex-Interdependency Benchmark (preferred)
- Design a 15-20 component system where components have complex invariants
- Example: compiler pipeline, financial risk system, security protocol
- Monolithic might fail at 15-20 components because of constraint propagation complexity
- AC14's explicit contracts would capture these constraints in each packet
- Cost: 3-5 days for design + 2-3 days for implementation
- Higher probability of finding ac14_wins at this scale

### Option D: Refocus on Human-Workflow Value
- Accept the evidence: at ≤10 component scale, mono is competitive
- Focus AC14 development on the human workflow value (structured planning, review)
- Defer the empirical comparison to a later stage when scale infrastructure exists


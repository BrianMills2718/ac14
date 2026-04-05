# Plan #168: Strategic Direction After Theory Forge Series

## Status: ACTIVE

## Evidence Summary (Plans #149-#167)

After 8 benchmarks (IT, PT, BS × gpt-4.1/flash; zeta_options × gpt-4.1/flash/DeepSeek;
noisy_spec × gpt-4.1):

| Benchmark | Model | AC14 | Mono | Verdict |
|-----------|-------|------|------|---------|
| IT v1 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| PT v1 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| BS v1 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| PT v1 | Gemini flash | 4/5 | 5/5 | mono_wins |
| BS v1 | Gemini flash | 4/5 | 5/5 | mono_wins |
| zeta_options | gpt-4.1 | 4/5 | 5/5 | inconclusive |
| zeta_options | Gemini flash | 1/5 | 5/5 | mono_wins (budget) |
| noisy_spec | gpt-4.1 | 0/5 | 0/5 | both_fail (mono better) |

## Root Cause: Scale is Insufficient

The current benchmarks have 10 components with ~100 lines of code each. This is
well within the context capacity of modern LLMs (gpt-4.1: 1M token context).
Even the "hardest" benchmark (zeta_options with novel formulas) is trivially
implementable by a capable model in a single call.

**AC14's advantage is a context-pressure advantage**: when the total context
(spec + all component logic + invariants + ports) exceeds what a single LLM call
can coherently implement, decomposition wins. At 10 components, this pressure
does not exist.

## Options

### Option A: Scale to 50+ Components
Build a benchmark with 50+ components, ~500+ lines of total logic, with realistic
cross-component dependencies. At this scale, single-call monolithic generation
becomes genuinely harder.
- **Pro**: tests the core thesis directly
- **Con**: large build effort; modern LLMs have 1M+ context, so "scale pressure"
  may not appear until 200+ components
- **Con**: verifying expected outputs for 50 components is significant work

### Option B: Domain Complexity (Not Scale)
Find a domain where the LOGIC is complex enough that monolithic fails even at
10-15 components. Examples: full compiler pipeline, cryptographic protocol
implementation, real-time control system.
- **Pro**: doesn't require 50+ components
- **Con**: hard to find a domain where monolithic actually fails
- **Con**: same risk as theory forge: capable models may still pass

### Option C: Accept Current Evidence, Pivot to System-Level Test
The Theory Forge series tested the narrow "formula implementation" use case.
A broader AC14 test would be: can AC14 successfully implement an end-to-end
software system (not just math pipelines) where monolithic generation regularly
fails? Move from academic benchmarks to realistic software engineering tasks.
- **Pro**: more representative of actual AC14 use case
- **Con**: harder to define "success" for open-ended software tasks

### Option D: Add Formula Synthesis to Planning Step (Fix the Gap)
The noisy-spec experiment revealed that AC14's planning step doesn't synthesize
formulas. Adding a synthesis step would let AC14 fill in implementation details
that the spec leaves vague. This is actually a capability gap in the AC14 system.
- **Pro**: fills a real gap in AC14; makes AC14 more useful
- **Con**: doesn't test the decomposition thesis directly; tests a different capability

## Recommended Path: Option A (Scale Test) with Explicit Spec

### Design

Build `benchmarks/large_scale_v1/` — a benchmark with 30-50 components where:
1. Each component has explicit formula/logic contracts (not vague)
2. Total spec is 2000+ lines (stresses monolithic context)
3. Components have realistic cross-dependencies (not just linear pipeline)
4. Expected outputs are programmatically generated from a reference implementation

**Target scale**: where monolithic must generate 800+ lines of coherent code in one call
while AC14 generates each component independently with bounded context.

### First Step: Determine the Scale Threshold

Before building a 50-component benchmark, determine the minimum scale at which
monolithic starts failing:
1. Build `benchmarks/zeta_options_scale_v1/` — extend zeta to 20 components by
   adding second-order Greeks (vanna, volga, charm, veta, speed, zomma, color)
2. Run smoke gate with gpt-4.1 and Gemini flash
3. If mono still 5/5 → scale to 40 components
4. If mono starts failing → that's our discriminating scale

### Acceptance Criteria

- At least one model at some component scale produces: AC14 > 3/5, mono < 3/5
- The failure reason for mono is "too much to hold in context" (errors in early
  components due to late-component context overflow), NOT formula misidentification

## Immediate Next Steps

1. Build `benchmarks/zeta_scale_20/` — add 10 second-order Greeks to zeta_options
2. Run smoke gate with Gemini flash (the weakest model that worked)
3. If mono passes: try 40 components
4. If mono fails: we've found the discriminating scale

## Alternative: Declare Theory Forge Series Complete

If the scale-test direction is too speculative given the pattern (all models pass
monolithically up to 10 components), the honest conclusion is:

**AC14's decomposition advantage does not manifest at ≤10 component scale with
modern capable LLMs.** The thesis may be valid at larger scale but is not
demonstrable with the current benchmark design.

This is valid evidence and should be documented. The AC14 system may still have
value for human-authored workflows (structured planning, component-level review)
even if the pure LLM-comparison advantage isn't measurable at this scale.


# Plan #169: Scale Threshold Analysis

## Status: COMPLETE (analysis only, no build)

## Question: What Scale Would Actually Discriminate?

After 8 benchmarks showing monolithic wins or ties at 10-component scale, Plan #168
recommended building a 20-component extension. This plan assesses whether 20 components
would actually discriminate, or whether the threshold is much higher.

## Evidence-Based Reasoning

### Why Modern LLMs Pass 10 Components

GPT-4.1 (1M token context) and Gemini flash can trivially hold a 10-component
mathematical pipeline in context. A 10-component zeta benchmark requires generating
~80-100 lines of Python in a single call. This is far below any context pressure.

### The Real Context Pressure Threshold

For monolithic generation to FAIL due to context pressure, the model must:
1. Generate enough code that early components get "forgotten" in the generation
2. Make inconsistent choices across components (e.g., implements disc_alpha correctly
   in stage 1 but uses wrong formula in stage 6 theta_call)

For SIMPLE LINEAR PIPELINES (zeta-style):
- Each component is ~5-10 lines
- 20 components = ~100-200 lines → still trivial
- 50 components = ~250-500 lines → probably still fine for gpt-4.1
- 100 components = ~500-1000 lines → might start seeing inconsistency

For COMPLEX INTERCONNECTED SYSTEMS:
- Cross-component invariants stress monolithic more than pure line count
- Dependency chains where component B must respect component A's output contract
- This is where AC14's explicit contracts might actually help

### The Diminishing Return Problem

Building zeta_scale_20 with 10 second-order Greeks:
- Second-order Greeks (vanna, volga, charm, veta, etc.) are well-known formulas
- LLMs are trained on quantitative finance textbooks — they know these formulas
- Even with zeta/alpha modifications, a capable model can DERIVE the correct formulas
- Prediction: gpt-4.1 passes 5/5, Gemini flash passes 4-5/5

This prediction is based on the pattern from the Theory Forge series:
- ALL benchmarks showed mono ≥ 4/5 at 10-component scale
- The only failures were infrastructure issues (budget) or subtle sign errors
- No benchmark showed mono failing due to "too much to hold in context"

## Honest Assessment: Scale Threshold

| Scale | Estimated Mono Pass Rate | Build Cost | Discrimination Risk |
|-------|------------------------|------------|---------------------|
| 20 components | 4-5/5 | 1-2 days | 80% likely fails to discriminate |
| 50 components | 3-4/5 | 3-5 days | Maybe starts to discriminate |
| 100 components | 2-3/5 | 7-10 days | Higher chance of discrimination |

## Alternative: Problem Domain Change

Instead of scaling a math pipeline, find a domain where:
1. Components have COMPLEX INTERDEPENDENCIES (not just linear flow)
2. Getting one component right requires holding multiple upstream contracts in mind
3. The spec is explicit enough that AC14 doesn't need formula synthesis

Candidate domains:
- **Compiler pipeline**: lexer → parser → semantic analyzer → type checker → code gen
  (each stage has complex invariants about the AST it receives and emits)
- **Protocol implementation**: request parsing → authentication → authorization → 
  rate limiting → routing → response building
  (cross-cutting concerns create many invariants)
- **Financial risk system**: exposure calculation → netting → margin → stress testing
  (complex regulatory rules that interact across components)

At 10-20 components with COMPLEX INTERDEPENDENCIES, monolithic might fail where
AC14 succeeds, because each packet explicitly states what constraints it must satisfy.

## Recommendation

### Option A: Build zeta_scale_20 (specified in Plan #168)
- **Risk**: Unlikely to discriminate at 20 components
- **Value**: Provides definitive evidence that scale threshold > 20
- **Cost**: 1-2 days
- **Expected outcome**: Identical to current evidence (mono 5/5)

### Option B: Skip to 50-component benchmark
- **Risk**: Might discriminate, or might not
- **Value**: More likely to find actual threshold
- **Cost**: 3-5 days
- **Problem**: Second-order Greeks formula still well-known

### Option C: Change domain to complex-interdependency problem
- **Risk**: Harder to define "success" than math pipeline
- **Value**: Tests the ACTUAL AC14 advantage (contract propagation, not just scale)
- **Cost**: 3-5 days to design + implement
- **Expected outcome**: Higher chance of finding ac14_wins

### Option D: Declare Theory Forge complete, document thesis limitation
- **Honest finding**: AC14 decomposition advantage doesn't manifest at ≤10 component
  scale with modern capable LLMs on math pipeline tasks
- The thesis may be valid at much larger scale or for different problem classes
- **Value**: Saves significant compute and planning overhead
- **Next step**: Either a much bigger investment (50+ components) or a different
  research direction (formula synthesis, contract propagation, etc.)

## Decision

This analysis suggests that building zeta_scale_20 as specified in Plan #168 is likely
to be a low-information experiment. The threshold for monolithic failure is probably
50-100+ components, which requires a larger investment than the current benchmark design.

**Recommended path**: Option D — declare Theory Forge series complete with honest findings,
document the thesis limitation, and make an explicit decision about the next major
experimental design before investing more compute.

The Theory Forge series has provided clear, reproducible evidence:
- 8 benchmarks across 4 domains and 3 models
- Monolithic consistently wins or ties at 10-component scale
- The AC14 advantage is not measurable at this scale

This is a VALID FINDING, not a failure. It clarifies the scope of the AC14 thesis.


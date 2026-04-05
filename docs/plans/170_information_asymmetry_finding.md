# Plan #170: Information Asymmetry Finding — Theory Forge Series Conclusion

## Status: COMPLETE (analysis only)

## The Key Discovery: Information Asymmetry in Noisy-Spec Test

### What the Noisy-Spec Test Actually Compared

Inspection of the codegen context for compute_zeta_d_params (the component that
failed with disc_alpha = 0.9512 instead of 0.9246) reveals:

**AC14 codegen sees** (12 business rules from workflow_hints + business_rules sections):
- "Compute disc_alpha using the alpha parameter."
- "The alpha parameter appears as an exponent in the discount factor computation"
- "The discount factor disc_alpha uses the alpha parameter: disc_alpha is NOT exp(-rate*T)"
- (no numerical hint about what disc_alpha should equal)

**Monolithic sees** (full structured_spec including success_criteria):
- All the same vague descriptions PLUS:
- "disc_alpha approx 0.9246 (NOT the standard exp(-rT) = 0.9512)"

The success_criteria hint `disc_alpha ≈ 0.9246` directly encodes the correct formula:
- `exp(-r^alpha * T)` = `exp(-0.05^0.85)` = `exp(-0.0784)` ≈ 0.9246 ✓
- `exp(-r * T^alpha)` = `exp(-0.05^0.85)` ... wait that's different → `exp(-0.05)` = 0.9512 ✗

So monolithic correctly chose `exp(-r^alpha * T)` by NUMERICAL INFERENCE from the hint
"disc_alpha ≈ 0.9246". AC14's codegen only had the ambiguous text "alpha is an exponent"
and chose the wrong interpretation: `exp(-r * T^alpha)`.

**Conclusion**: The noisy-spec test was NOT a fair comparison. Monolithic had access to
numerical hints (success_criteria) that AC14's codegen did not. The test measured:
"can monolithic do numerical inference from hints?" vs "can AC14 codegen interpret
ambiguous text?" — not the intended question.

## The Structural Finding: AC14 Plans Architecture, Not Formulas

The freeze_readiness_report for the noisy-spec trial shows 35 warnings:
```
W-DRAFT-PLACEHOLDER-INVARIANT: component still uses placeholder local invariants
W-DRAFT-PLACEHOLDER-CONSTRAINT: component still uses placeholder implementation constraints
```

ALL 10 components had TODO constraints in the frozen bundle. The freeze decision
approved the bundle anyway (TODOs are warnings, not blocking errors).

**The planning step's open questions** are all architectural:
- "Where should input validation live?"
- "Should rho_put be its own node?"
- "Does every field need provenance-traces?"

NOT formula questions like "what is the exact disc_alpha formula?"

**Diagnosis**: AC14's planning step is a STRUCTURAL DECOMPOSER, not a FORMULA SYNTHESIZER.
It creates component boundaries, defines port schemas, and establishes data flow.
It does NOT synthesize implementation contracts from vague descriptions.

## The Core Thesis Gap

The AC14 thesis as currently implemented:
> "Decomposition helps by giving each component a bounded context of what it must implement."

What this actually means:
> "The spec's business rules are distributed to each component. The codegen sees only
> its own component's rules, not all components' rules simultaneously."

**The gap**: If ALL the information is in the shared spec (and mono sees all of it),
distributing that information across components doesn't add value — it just fragments
the same information.

**When AC14 would actually help**:
1. **Information addition**: Planning step uses tool calls to add information
   (library docs, examples, reference implementations) that isn't in the shared spec
2. **Scale pressure**: Total spec + implementation is large enough that holding everything
   in one call causes monolithic to miss/forget later components
3. **Complex invariant propagation**: Cross-component constraints that are easy to miss
   when generating all code simultaneously

None of these conditions hold for the Theory Forge benchmarks (10 components, explicit
spec, no external information needed).

## What Would Make a Fair Test

### Option A: True Noisy Spec (remove ALL implementation hints)
Remove success_criteria numerical hints from the structured_spec. Both conditions
work from purely vague descriptions. Expected result: both fail ~50% on ambiguous
formulas like disc_alpha. No meaningful discrimination.

### Option B: Information-Enhanced Planning Step
Give AC14's planning step the ability to:
- Look up standard formulas in a math library
- Find relevant examples for each component
- Make the "clarifying question" process result in EXPLICIT formula contracts

This would require changing the AC14 system, not just the benchmark.

### Option C: Scale Test (fair at large scale)
With 50+ components, even WITH an explicit spec, monolithic must write 500+ lines of
consistently correct code. Structural decomposition (bounded context per component)
starts helping because each component gets a focused, short prompt.

### Option D: Accept Evidence, Document Thesis Scope

## Recommended Decision

**Declare the Theory Forge series complete. Document thesis scope.**

The series has provided clear, reproducible evidence:
1. At ≤10 component scale: AC14 provides no advantage over capable monolithic models
2. AC14's planning step adds structural clarity but not implementation information
3. The discriminating condition for AC14 is scale OR information synthesis, not formula novelty

**The thesis is not falsified** — it's scoped. AC14 should help at:
- Scale: 50-100+ components (structural decomposition reduces per-call context load)
- Information synthesis: if planning step can look up docs, examples, references

**For immediate next steps**, the most valuable experiments are:
1. A 50-component scale benchmark (tests the pure scale hypothesis)
2. OR: Adding an "information synthesis" step to the planning stage (tests thesis enhancement)

Both require significant investment. This is a natural stopping point for the current
benchmark-only approach and a starting point for either (a) building larger benchmarks
or (b) improving the AC14 system itself.

## Theory Forge Series: Final Status

**8 benchmarks × 3 models. All evidence consistent. Series is COMPLETE.**

The next work should be either:
- `benchmarks/zeta_scale_50/` (large-scale test, ~5-7 days)
- `ac14/planning_step_synthesis/` (planning step enhancement, ~3-5 days)
- Pivot to a completely different research direction


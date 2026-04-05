# Theory Forge Series Conclusion

**Date:** 2026-04-05
**Plans:** #149-#174 (10 benchmarks, ~25 empirical gates)
**Status:** SERIES COMPLETE

---

## Final Evidence Table

| # | Benchmark | Components | Model | AC14 | Mono | Verdict |
|---|-----------|-----------|-------|------|------|---------|
| 1 | it_benchmark | 10 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| 2 | pt_benchmark | 10 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| 3 | pt_benchmark | 10 | Gemini flash | 2/5 | 5/5 | monolithic_wins |
| 4 | bs_benchmark | 10 | Gemini flash | 4/5 | 5/5 | inconclusive |
| 5 | zeta_options | 10 | gpt-4.1 | 4/5 | 5/5 | inconclusive |
| 6 | zeta_options | 10 | Gemini flash | 1/5 | 5/5 | monolithic_wins |
| 7 | zeta_options | 10 | Gemini flash × 10 | 6/10 | 9/10 | monolithic_wins |
| 8 | zeta_noisy_spec | 10 | Gemini flash | 1/13 fields | 10/13 | monolithic_wins |
| 9 | zeta_scale_20 | 20 | Gemini flash × 10 | 10/10 | 10/10 | **inconclusive (tie)** |
| 10 | zeta_scale_20 | 20 | Gemini flash-lite × 5 | 0/5 | 3/5 | **monolithic_wins** |

**Across 10 benchmarks and 3 domains:** AC14 never achieves a meaningful `ac14_wins` verdict.

---

## Root Cause (Definitively Established)

### Primary: Information Asymmetry

`structured_spec_input.yaml` contains `success_criteria` with numerical hints (e.g., `disc_alpha≈0.9246`).
Monolithic sees all hints in one context and anchors math correctly in one pass.
AC14 component packets see only their local hints — but the monolithic model's advantage is seeing ALL hints together, catching cross-formula relationships.

### Secondary: Pipeline Fragility

AC14's 5-step pipeline (spec → blueprint plan → per-component packets → per-component codegen → assembly) has more failure modes than monolithic single-step codegen. With weaker models:
- Blueprint plan step fails more often (invalid bindings, port mismatches)
- Per-component codegen fails more often (Python syntax errors, wrong port names)

Counter-intuitive result: **weaker models favor monolithic over AC14.** The decomposition
pipeline requires accurate structured output at each step, but weaker models produce
structured output less reliably.

### Result: AC14 advantage never materializes at current scale

| Regime | Strong model (gpt-4.1) | Mid model (Gemini flash) | Weak model (flash-lite) |
|--------|----------------------|------------------------|------------------------|
| 10 components | Both pass (inconclusive) | Mono wins | N/A |
| 20 components | N/A | **Tie** | **Mono wins** |

Scale_20 with Gemini flash is the only regime where both tie — because flash is exactly
at the capacity boundary where monolithic works but AC14 also succeeds via retries.

---

## What Would Make AC14 Win?

Based on the evidence, AC14 would likely win under these conditions (not yet tested):

1. **Scale >> 50 components** — Context window of even strong models would overflow.
   Estimated threshold: 50-100+ components for modern LLMs (128k+ context).

2. **Complex interdependency domain** — Where decomposition captures domain structure
   that monolithic cannot hold in context (e.g., large distributed system simulation,
   compiler, OS kernel — not just more formula components).

3. **Planning step synthesis** — If AC14's planning step could SYNTHESIZE correct formulas
   from vague specs (not just decompose well-specified specs), it would gain an accuracy
   advantage that monolithic doesn't have. This requires a different AC14 architecture
   (Plan #170).

4. **Structured output reliability gap** — AC14 components generate simpler, more focused
   code. If per-component code is provably more reliable than monolithic code (beyond
   retries), AC14 has an advantage in production settings even if not in these benchmarks.

---

## Recommended Next Directions

### Option A: Scale_50+ Test
- Build 50-component benchmark (zeta_scale_50 or similar)
- Cost: 3-5 days; Risk: both may still tie if flash has 1M+ context
- Value: empirical threshold finding

### Option B: Planning Step Synthesis (Major Architecture Change)
- Add formula synthesis capability to AC14 planning step
- Rather than just decomposing specs, AC14 plans should derive correct formulas
- This is a fundamental AC14 improvement beyond the Theory Forge scope
- Cost: 2-4 weeks of R&D

### Option C: Declare Series Complete, Pivot to Next Project
- Theory Forge evidence is conclusive: AC14 advantage requires scale >> 20 or new architecture
- The current proof slice (decomposition + runtime generation) is validated at its limits
- Next phase: either implement planning step synthesis, or shift to applying AC14 to a
  domain where it already helps (real software projects, not synthetic math benchmarks)

**Recommended: Option C.** The Theory Forge series has served its purpose: establishing
empirical evidence about where AC14 does and does not win. The answer is clear. The next
productive step is either architectural improvement (Option B) or application (Option C).

---

## Summary for Future Reference

**AC14 is a decomposition system, not a synthesis system.** It excels at:
- Breaking well-specified systems into bounded components
- Running each component through a focused generation loop
- Ensuring structural correctness (ports, types, bindings)

It struggles when:
- The spec requires formula synthesis (not just decomposition)
- The component count is low enough for modern LLMs to handle monolithically
- Structured output reliability matters at each pipeline stage

**The Theory Forge finding** is that modern LLMs (gpt-4.1, Gemini flash) have sufficient
context capacity for 10-20 component systems. AC14's advantage will emerge at 50+ components
OR when the planning step can synthesize domain knowledge that monolithic context cannot hold.

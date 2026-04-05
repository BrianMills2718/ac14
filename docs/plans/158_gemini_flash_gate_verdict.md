# Plan #158: Gemini Flash PT Gate Verdict

**Status**: Complete  
**Gate**: `.ac14_out/pt_gate_gemini_flash2/`  
**Model**: `gemini/gemini-2.5-flash-lite`  
**Date**: 2026-04-04

---

## Gate Results

| Metric | AC14 | Monolithic |
|--------|------|-----------|
| Successes | 2/5 | 5/5 |
| Avg repair loops | 1.4 | 0.2 |
| Avg semantic score | 0.67 | 2.0 |
| Avg duration | 93.0s | 6.9s |
| Total cost | $0.269 | $0.124 |
| Front-half successes | 5/5 | N/A |

**Verdict**: `monolithic_wins`  
**Rationale**: "The monolithic condition beat AC14 by at least two successful trials."

---

## Interpretation

### Hypothesis falsified

The hypothesis for this gate was: "Gemini flash should fail PT monolithic, and AC14
decomposition would enable it to succeed via bounded component context."

**Result**: Gemini flash passes PT monolithic 5/5. The benchmark is too tractable.

### What the data shows

1. **Front-half now 5/5**: The validation fix works consistently across models.
   Gemini flash generates valid blueprints. This is not the bottleneck.

2. **Codegen quality is the bottleneck**: AC14 with Gemini flash passes front-half
   but fails runtime outputs in 3/5 trials. The generated component code has
   numerical formula errors.

3. **Monolithic benefits from full context**: PT requirements are small enough to
   fit in a single context. The LLM sees all formulas simultaneously, enabling
   cross-formula validation that component-local context lacks.

4. **AC14 HURTS performance at lower capability**: gpt-4.1 AC14 = 5/5, Gemini
   flash AC14 = 2/5. AC14's component isolation removes the cross-formula
   context that helps weaker models get the math right.

### Comparison across models

| Condition | gpt-4.1 | Gemini Flash |
|-----------|---------|-------------|
| Monolithic | 5/5 | 5/5 |
| AC14 | 5/5 | 2/5 |

### Root cause of AC14 failures with Gemini flash

Looking at trial failures: `front_half_passed=True, runtime_outputs=False`

The LLM generates syntactically correct code but gets formula details wrong:
- Wrong parameter names (confusing α/β/γ/δ/λ across components)
- Missing sign inversions (CE calculation)
- Off-by-one in piecewise conditions

This is a code quality problem, not a context pressure problem.

---

## Strategic Finding

**Current benchmark class (math formulas, explicit requirements, <200 line spec)
does not create context pressure that discriminates AC14 from monolithic.**

Both gpt-4.1 and Gemini flash pass PT monolithic 5/5. The spec is too small.

**The AC14 thesis requires a benchmark where:**
1. Total requirements are too large/complex for effective single-context reasoning, OR
2. Component interdependencies require isolated testing that catches errors monolithic misses

---

## Next Plan

Plan #159: Design a benchmark that genuinely breaks monolithic.

Options:
A. **Scale up complexity**: 12-component Black-Scholes suite with greeks — similar 
   formula structures but many variants that are easy to confuse
B. **Inject implicit knowledge**: Requirements that deliberately don't spell out
   formulas — forces the LLM to derive from description
C. **Cross-component invariants**: System where getting one component's output
   format wrong causes cascade failures that are obvious in AC14 but hidden in
   monolithic until the very end

Recommended: Option A first (Black-Scholes 12-component), then Option C if still tractable.

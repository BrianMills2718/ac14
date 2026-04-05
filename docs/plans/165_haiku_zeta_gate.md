# Plan #165 — Weak Model Search: claude-haiku not available, DeepSeek incompatible

## Status: COMPLETE

## Summary

Attempted to test with weaker models to find the threshold where monolithic fails.

### Model Attempts:
1. `claude-haiku-4-5-20251001` — NOT on OpenRouter, error 400
2. `anthropic/claude-3-haiku-20240307` — NOT on OpenRouter, error 400
3. `openai/gpt-4o-mini` — HARD-BLOCKED by llm_client (outclassed by DeepSeek)
4. `deepseek/deepseek-chat` — Correctly implements ALL zeta/alpha formulas but:
   - Monolithic generates flat output (`{"case_id": "base", "call_price": 9.716, ...}`)
   - Harness expects nested output (`{"zeta_results": {...}}`)
   - ALL 3 monolithic attempts fail with Pydantic validation errors, not formula errors
   - Numerical values are EXACT matches to expected (correct formulas!)

## Critical Finding

**ALL models (gpt-4.1, Gemini flash, DeepSeek) implement the zeta/alpha formulas correctly
when given the structured spec.** Formula memorization is NOT the bottleneck at 10-component scale.

No available model through OpenRouter fails on formula implementation.

## Formula Memorization Hypothesis: DEFINITIVELY FALSIFIED

| Model | Correctly implements zeta/alpha? | Notes |
|-------|----------------------------------|-------|
| gpt-4.1 | YES (5/5 monolithic) | Perfect semantic score |
| Gemini flash | YES (5/5 monolithic) | Perfect semantic score |
| DeepSeek V3.2 | YES (correct values) | Fails on output structure only |

The structured_spec_input.yaml with explicit "CRITICAL DIFFERENCE FROM STANDARD BS"
callouts is sufficient for any model to implement the formulas correctly. There is no
model-capability bottleneck at 10-component scale with this specification style.

## Next Step: Plan #166 — Scale Test (50+ Components)

The thesis requires a benchmark where context capacity is genuinely exceeded. Options:
A. Design a 50-component benchmark (e.g., full financial risk system, complex simulation)
B. Accept the negative evidence and refine the thesis boundary conditions
C. Explore AC14 advantages in a different dimension (output correctness under noisy specs)

**Recommended: Plan #166 — Strategic analysis and 50-component benchmark design**


# Plan #164 — Zeta Options Gemini Flash Gate Verdict

## Status: COMPLETE

## Gate Results

| Condition | Successes | Semantic Score | Avg Cost | Verdict |
|-----------|-----------|---------------|----------|---------|
| AC14      | 1/5       | 1.167         | $0.135/trial | — |
| Monolithic| 5/5       | 1.667         | $0.034/trial | — |

**Overall verdict: `monolithic_wins`** (gap = 4 trials)

## AC14 Failure Analysis

- **Trials 1, 5**: Budget exceeded — planning step cost $0.46-0.49, budget limit was $0.30.
  Root cause: budget splits 50/50 between AC14 and mono, giving AC14 only $0.30 of $0.60.
  Fix: use MAX_BUDGET=0.80+ to give AC14 $0.40+ per attempt.

- **Trial 2, attempt 1**: All Greeks correct but call_price=-9.05 (expected +9.716), put_price=13.41 (expected 2.179).
  All d-params, delta, gamma, theta, vega, rho are EXACT matches.
  Only the raw prices from `price_zeta_call` and `price_zeta_put` are wrong.
  Gemini flash generates an incorrect formula for the pricer components.

- **Trial 4**: Same pattern — all Greeks correct, only prices wrong.

## Critical Strategic Finding

**The structured_spec_input.yaml gives monolithic the SAME formula hints as AC14 packets.**

Each `workflow_hints` entry explicitly states "CRITICAL DIFFERENCE FROM STANDARD BS" with
the exact formula. Monolithic gets all 10 of these in one context window. Any model that
can read instructions implements them correctly.

Both gpt-4.1 and Gemini flash achieve perfect monolithic implementation (5/5) of all
zeta/alpha modifications. The formula memorization hypothesis is WRONG for these models.

## Pattern Across All Theory Forge Benchmarks

| Benchmark | Model | AC14 | Mono | Verdict |
|-----------|-------|------|------|---------|
| IT | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| BS | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| PT | Gemini flash | 2/5 | 5/5 | monolithic_wins (infra bugs) |
| BS | Gemini flash | 4/5 | 5/5 | inconclusive |
| Zeta | gpt-4.1 | 4/5 | 5/5 | inconclusive |
| Zeta | Gemini flash | 1/5 | 5/5 | monolithic_wins (budget + formula bugs) |

**Consistent pattern**: Monolithic 5/5 on everything. AC14 3-5/5 with gpt-4.1, 1-4/5 with Gemini flash.

## Root Cause of AC14 Failures

AC14's failures are NOT about "holding too much context" — they're about:
1. Code generation reliability (syntax errors, wrong port names, formula bugs)
2. Recomposition failure modes that don't exist in monolithic
3. Budget constraints in the planning step

## Next Step: Plan #165 — Scale Test Design

For the thesis to be testable, we need a benchmark where:
1. The spec is genuinely too large for monolithic (100+ components, 20+ page spec)
2. OR the model is so weak it can't follow 10+ instructions simultaneously (haiku?)

Plan #165 options:
A. Run zeta options with claude-haiku-4-5 (cheapest, weakest available model)
B. Design a 50-component benchmark that exceeds monolithic context capacity
C. Budget fix + rerun with Gemini flash (MAX_BUDGET=0.80) to see if 3/5 AC14

**Recommendation**: Try haiku on zeta options first (cheapest experiment).
If haiku still passes 5/5 monolithic → thesis requires 100+ components.
If haiku fails monolithically → first ac14_wins possible.


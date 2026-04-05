# Plan #162 — Zeta Options Gate_1 Verdict (gpt-4.1) and Next Step

## Status: COMPLETE (verdict written)

## Gate Results

| Condition | Successes | Semantic Score | Avg Cost | Verdict |
|-----------|-----------|---------------|----------|---------|
| AC14      | 4/5       | 0.833         | $0.079/trial | — |
| Monolithic| 5/5       | 1.0           | $0.021/trial | — |

**Overall verdict: `inconclusive`** (gap = 1 trial)

## Failure Analysis — Trial 5 (AC14 only failure)

- **Attempt 1**: `compute_zeta_gamma` — invalid Python (no indented block after function def)
- **Attempt 2**: Correct d-params, Greeks, and all formula outputs EXCEPT call/put price have
  wrong sign (call_price=-9.05 instead of +9.716). All other 12 values correct.
- **Attempt 3**: `compute_zeta_theta_put` — invalid Python (same syntax error pattern)
- All 3 attempts exhausted → trial failed

## Critical Finding

**The formula memorization hypothesis was wrong.** gpt-4.1 achieved perfect semantic score
(1.0) on ALL 5 monolithic trials, correctly implementing every zeta/alpha modification:
- disc_alpha = exp(-r^alpha * T) ✓
- delta_call = zeta * N(d1_zeta) ✓
- vega = S * N'(d1_zeta) * sqrt(T) * zeta^0.5 ✓
- rho = alpha * K * T * r^(alpha-1) * disc_alpha * N(d2_zeta) ✓

gpt-4.1 can follow novel non-standard formula specifications perfectly monolithically.

## AC14 Failure Pattern

AC14's one failure was NOT about formula understanding — it was about code generation reliability:
- Syntax errors (invalid Python) on 2 of 3 attempts
- Sign error in price formula on the remaining attempt
- All Greek formulas were correct in attempt 2

This is a code generation quality failure, not a context capacity failure.

## Pattern Across All gpt-4.1 Benchmarks

| Benchmark | AC14 | Mono | Verdict |
|-----------|------|------|---------|
| IT (10 components) | 5/5 | 5/5 | inconclusive |
| BS (10 components) | 5/5 | 5/5 | inconclusive |
| PT (5 components)  | N/A  | 5/5 | monolithic_wins (infra issues) |
| Zeta options (10 components) | 4/5 | 5/5 | inconclusive |

**gpt-4.1 is too capable for current benchmark sizes. It passes everything monolithically.**

## Next Step: Plan #163 — Zeta Options with Gemini Flash

The Prospect Theory benchmark showed Gemini flash at 2/5 monolithic (Plan #158 verdict).
Zeta options is harder than PT (novel formulas + 10 components vs 5). This is the most
likely setup to find a `monolithic_fails` result.

Run: `make front-half-first-full-trials BENCHMARK=benchmarks/zeta_options MODEL=gemini/gemini-2.5-flash OUTPUT=.ac14_out/zeta_gemini_gate_1 MAX_BUDGET=0.30 TRIALS=5 MAX_ATTEMPTS=3`

Expected:
- Monolithic may fail on novel zeta/alpha formulas (same way PT failed)
- AC14 should maintain ~4/5 (per-component hints spell out the formula explicitly)
- If AC14 > mono: first `ac14_wins` verdict → thesis validated for weak-model regime


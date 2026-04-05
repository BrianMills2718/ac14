# Plan #159: Black-Scholes Gate_1 Verdict — Inconclusive (Both 5/5 with gpt-4.1)

**Status**: Complete  
**Gate**: `.ac14_out/bs_gate_1/`  
**Model**: `openai/gpt-4.1`  
**Date**: 2026-04-04

---

## Gate Results

| Metric | AC14 | Monolithic |
|--------|------|-----------|
| Successes | 5/5 | 5/5 |
| Avg repair loops | 0.0 | 0.0 |
| Avg semantic score | 1.2 | 2.0 |
| Avg duration | 96.4s | 10.5s |
| Total cost | $0.287 | $0.060 |
| Front-half successes | 5/5 | N/A |

**Verdict**: `inconclusive` — tied on success rate, secondary metrics don't separate cleanly.

---

## Interpretation

1. gpt-4.1 still passes BS monolithic 5/5 with 0 repair loops.
   10 components with subtle sign differences is not enough to break gpt-4.1.
2. AC14 also passes 5/5 with 0 repair loops — the 10-component decomposition works.
3. AC14 costs 4.7x more and takes 9x longer — overhead is growing with component count.
4. AC14 semantic score (1.2 vs 2.0) — suggests components may not be implementing
   formula details as cleanly as monolithic, even when exact matching passes.

## Benchmark Progress Arc

| Gate | Benchmark | Components | AC14 (gpt-4.1) | Mono (gpt-4.1) | AC14 (gemini-flash) | Mono (gemini-flash) |
|------|-----------|-----------|----------------|----------------|---------------------|---------------------|
| bs_gate_1 | black_scholes_greeks | 10 | 5/5 | 5/5 | TBD | TBD |
| pt_gate_2d | prospect_theory_tk1992 | 5 | 5/5 | 5/5 | 2/5 | 5/5 |
| it_gate_1 | information_theory | ~4 | 5/5 | 5/5 | TBD | TBD |

Pattern: gpt-4.1 is too strong. Need Gemini flash BS results for discrimination.

---

## Next: Run BS Gate with Gemini Flash

If Gemini flash monolithic still passes 5/5 on BS (10 components), the model
capability hypothesis is completely falsified — even weaker models can handle
the monolithic approach for known mathematical benchmarks.

This would confirm: the AC14 thesis requires benchmarks with NOVEL formulas
or VERY LARGE specifications, not just more components with known math.

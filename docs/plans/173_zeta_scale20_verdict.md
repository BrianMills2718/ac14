# Plan #173: Zeta Scale-20 Gate_1 Verdict

## Status: COMPLETE

## Verdict: `ac14_wins` (TIE-BREAK ONLY — not meaningful discrimination)

Both conditions pass 5/5. The `ac14_wins` verdict is awarded on tie-breaking
criteria (fewer repair loops, higher semantic score), not on pass/fail discrimination.

## Results

| Metric | AC14 | Monolithic |
|--------|------|------------|
| Successes | 5/5 | 5/5 |
| Avg repair loops | 0.2 | 0.4 |
| Avg semantic score | 1.5 | 1.333 |
| Total cost | $0.286 | $0.142 |
| Avg duration | 113s | 20s |
| Front-half successes | 5/5 | 0/5 |

**Both conditions pass all 5 trials. No meaningful discrimination at 20-component scale.**

## Per-Trial Summary

| Trial | AC14 | AC14 repairs | Mono | Mono repairs |
|-------|------|-------------|------|-------------|
| 1 | Pass | 0 | Pass | 2 |
| 2 | Pass | 1 | Pass | 0 |
| 3 | Pass | 0 | Pass | 0 |
| 4 | Pass | 0 | Pass | 0 |
| 5 | Pass | 0 | Pass | 0 |

## Key Findings

1. **20-component scale is still within monolithic capacity**: Gemini 2.5 Flash can
   correctly implement 20 zeta-modified math functions (23 output fields) in a single
   call. Both AC14 and monolithic achieve 100% pass rate.

2. **Monolithic needed more repairs but still succeeded**: Trial 1 mono used 2 repair
   loops vs AC14 using 0. This is a MARGINAL signal that context pressure is starting,
   but not enough to cause failure.

3. **Cost and latency favor monolithic**: Monolithic is 2x cheaper ($0.142 vs $0.286)
   and 5.5x faster (20s vs 113s). For a user choosing between approaches, monolithic
   is cheaper when both succeed.

4. **AC14 front-half still perfect**: 5/5 front-half successes confirms the planning
   step and blueprint generation are robust.

## Interpretation

The zeta_scale_20 benchmark provides MARGINAL evidence of AC14's advantage (fewer
repair loops, better semantic quality) but NOT definitive evidence of monolithic failure.

**9 benchmarks across 4 domains, 3 model scales, and 2 spec types consistently show:**
- At ≤10 components: mono wins or ties (5/5 always)
- At 20 components: both 5/5, AC14 slightly better quality
- The discrimination threshold is higher than 20 components

## What Scale Would Discriminate

Given the pattern:
- 10 components: mono 5/5 easily
- 20 components: mono 5/5, slightly more repairs
- Extrapolation: mono probably fails at 40-60 components for Gemini flash

But this requires building benchmarks that are significantly more complex.

## Strategic Conclusion

**The Theory Forge series (Plans #149-#173) is exhausted.** 9 benchmarks have not
found a discriminating condition at ≤20 component scale. The next decisive test
requires either:

1. **50-component benchmark** (3-5 days build + compute): expected discrimination
   point for Gemini flash
2. **Weaker model with explicit 20-component spec**: find a model where 20 components
   IS enough context pressure
3. **Accept evidence as-is**: document that AC14's advantage is scale-dependent
   and requires 50+ components to manifest

The `ac14_wins` verdict is technically the first win in the series, but it's weak
evidence (repair loop tiebreaker, not pass/fail discrimination). It confirms AC14
is slightly better quality at 20 components, setting up the expectation that at
50 components the quality advantage might become a pass/fail advantage.


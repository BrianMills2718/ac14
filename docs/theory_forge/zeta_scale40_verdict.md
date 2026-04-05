# Zeta Scale-40 Gate Verdict

**Benchmark:** `zeta_scale_40_v1` (40-component dual-option portfolio)
**Model:** Gemini flash (gemini/gemini-2.0-flash-lite or equivalent)
**Trials:** 5
**Date:** 2026-04-05

---

## Verdict: `monolithic_wins`

| Condition | Hard-Harness Successes | Total Cost | Avg Duration | Avg Repairs |
|-----------|----------------------|------------|--------------|-------------|
| Monolithic | **4 / 5** | $0.138 | 56s | 0.8 |
| AC14 | **0 / 5** | $0.365 | 249s | 2.0 (all fail) |

---

## Trial-Level Results

| Trial | AC14 Pass | AC14 Failure Categories | Mono Pass | Mono Failure Categories |
|-------|-----------|------------------------|-----------|------------------------|
| 1 | ✗ | generation, generation, generation | ✓ | success |
| 2 | ✗ | runtime_outputs, generation, runtime_outputs | ✓ | success |
| 3 | ✗ | runtime_outputs, runtime_outputs, generation | ✓ | success (after 2 repairs) |
| 4 | ✗ | runtime_outputs, runtime_outputs, generation | ✓ | success |
| 5 | ✗ | generation, generation, runtime_outputs | ✗ | runtime_outputs (3 fails) |

---

## Findings

### AC14 at 40 Components: Pipeline Fragility Dominates

AC14 0/5 hard-harness successes. Failure modes:
- **Generation failures** (dominant): At 40 components, the LLM must generate 40 independent
  Python modules sequentially. Generation failures in any single module abort the trial.
  With 40 components at ~5-10% per-component failure probability, trial-level success
  probability is (0.90-0.95)^40 ≈ 1-17% — well below threshold.
- **Runtime output failures**: Some components generated code without correctly wrapping
  outputs in the port-name key `{'output_port_name': {...}}`. At 40 components, this
  inconsistency is harder to fix in 3 repair cycles.

### Monolithic at 40 Components: Still Within Capacity

Monolithic 4/5 successes. Gemini flash can generate a ~3200-line Python module for a
40-component dual-option portfolio in a single call. The _a/_b naming discipline held
in 4/5 trials. Trial 5 failed on all 3 attempts (output mismatches), suggesting ~20%
per-trial failure rate at this scale.

### Key Quantitative Comparison (vs Scale-20)

| Scale | Mono Success | AC14 Success | Mono/AC14 Cost Ratio |
|-------|-------------|-------------|---------------------|
| 20 components | 10/10 | 10/10 (tied) | 0.38x mono cheaper |
| 40 components | 4/5 | 0/5 | 0.38x mono cheaper |

At 20 components: both tied. At 40 components: mono holds, AC14 collapses.
This confirms that AC14 pipeline fragility scales with component count.

---

## Strategic Interpretation

This result aligns with and extends the findings from Plans #174-#175:

1. **AC14 advantage requires a scale where monolithic ALSO fails.** At 40 components
   with Gemini flash, monolithic still succeeds 80% of the time. AC14 needs a scale
   where the single-call context pressure on monolithic creates failures faster than
   AC14's per-component failure rate accumulates.

2. **The threshold (if it exists for Gemini flash) is >> 40 components.** Gemini flash
   handles 40-component codegen with ~80% success. At 100+ components (~8000 lines),
   monolithic might finally start failing. But AC14 at 100 components with ~5% per-component
   failure probability → (0.95)^100 ≈ 0.6% success rate — almost zero.

3. **Pipeline fragility is the fundamental constraint.** AC14's advantage requires:
   - Component generation success rate >> 99% per component
   - OR monolithic failure rate high enough that even low AC14 success counts
   Neither condition holds for current LLMs at math benchmarks.

4. **Information asymmetry remains unresolved.** Monolithic still sees all `success_criteria`
   numerical hints at once; AC14 components only see their own context.

---

## Conclusion

`monolithic_wins` decisively at 40 components. This benchmark closes the scale test series.
The threshold for Gemini flash is either unreachable with current AC14 pipeline design,
or requires 100+ components where AC14 success probability approaches zero anyway.

**This evidence supports declaring the Theory Forge series complete (Plan #175) and
pivoting to planning step synthesis or application domain work.**

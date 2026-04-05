# Zeta Scale-20 Gate_1 Verdict

**Date:** 2026-04-05
**Plan:** #172 (gate) + #173 (verdict)
**Benchmark:** `zeta_scale_20_v1` (20 components)
**Model:** `gemini/gemini-2.5-flash`

---

## Result

| Metric | AC14 | Monolithic |
|--------|------|------------|
| Hard-harness successes | **10/10** | **10/10** |
| Front-half successes | 10/10 | 0/10 |
| Avg repair loops | 0.2 | 0.2 |
| Avg semantic score | 1.45 | 1.27 |
| Total cost (10 trials) | $0.82 | $0.32 |
| Avg cost/trial | $0.082 | $0.032 |
| Avg duration/trial | ~120s | ~19s |

**Verdict: `inconclusive` — both conditions pass 10/10. No hard-harness discrimination at scale_20.**

The `ac14_wins` intermediate reading at trial 5 (gate_1) was based on marginal repair loop
differences (0.2 vs 0.4) that did not replicate in gate_1_b (both 0.2).

---

## Analysis

**What happened:** Gemini flash correctly implements all 20 components monolithically when
given the `success_criteria` numerical hints in the structured spec input. Both conditions
passed 100% of trials. AC14 is 2.6x more expensive and 6x slower with no accuracy benefit.

**Why both pass:** Scale_20 is within Gemini flash's context capacity for math formula
implementation. The `success_criteria` in `structured_spec_input.yaml` provide exact
numerical targets (e.g., `disc_alpha≈0.9246`) that anchor both the monolithic and AC14
codegen to the correct formulas. The information asymmetry root cause identified in Plan #170
still applies — the spec gives numerical hints to both conditions equally.

**What this means for the theory:** The scale threshold for meaningful AC14 discrimination
is > 20 components. At 10 components (zeta_options Gate_3), mono wins 9/10 vs AC14 6/10.
At 20 components, both pass 10/10 — actually a reversal of that trend. The explanation:
the 20-component spec is well-structured with clear formulas, while the 10-trial gate had
more formula-specific codegen errors corrected by retries.

---

## Theory Forge Series Summary (Complete)

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
| 9 | **zeta_scale_20** | **20** | **Gemini flash × 10** | **10/10** | **10/10** | **inconclusive** |

**Pattern:** At 10-component scale with Gemini flash, monolithic consistently wins or ties.
At 20-component scale, **both conditions pass equally** — the benchmark is too easy.

---

## Root Cause (Confirmed)

From Plan #170: The information asymmetry is the primary driver. `structured_spec_input.yaml`
provides `success_criteria` with exact numerical outputs (e.g., `disc_alpha=0.9246`).
Monolithic sees these and implements the math correctly in one pass. AC14 sees the same
hints per component. At 20 components, the formulas are well-distributed enough that
both succeed.

The key question — "at what scale does context pressure hurt monolithic generation?" — 
remains open. The answer is empirically > 20 components with Gemini flash.

---

## Next Direction Options (Plan #174)

### Option A: Scale_50 Benchmark
- Build a 50-component benchmark extending zeta_scale_20
- Cost: 3-5 days of benchmark engineering
- Risk: Both may still pass if Gemini flash has enough context capacity
- Expected: 50 components likely to start causing context pressure

### Option B: Weaker Model Test
- Run scale_20 with a weaker model (haiku, deepseek-chat)
- Cost: 1 day (make target already works)
- Expected: weaker model may fail monolithically at 20 components
- This tests the model capacity hypothesis directly

### Option C: Accept Evidence and Pivot
- Theory Forge series: 9 benchmarks, consistent evidence at ≤20 components
- AC14 requires scale > 20 OR weaker model for discrimination
- Scale_50 is buildable but expensive; the main thesis remains unresolved
- Accept: "AC14 advantage emerges at higher scale or lower model capacity"
- Pivot to the next major project phase

### Recommended: Option B + conditional Option C
Run scale_20 with `claude-haiku-4-5-20251001` (available via llm_client, Plan #165 
showed deepseek fails only on output structure). If haiku shows discrimination at 20 
components, that confirms the threshold is model-capacity dependent. If not, pivot 
to Option C. This costs 1 day maximum.

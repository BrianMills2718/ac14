# Plan #164 — Zeta Options Gemini Flash Gate_2 Verdict (Budget Fix)

**Status**: Complete  
**Started**: 2026-04-05  
**Completed**: 2026-04-05

---

## Gate Results

Output: `.ac14_out/zeta_gemini_gate_2/`  
Model: `gemini/gemini-2.5-flash`  
Benchmark: `zeta_options_structured_spec_v1` (10 components)  
Budget: `MAX_BUDGET=1.00` (budget bug fixed in freeze_decision.py)

| Metric | AC14 | Monolithic |
|--------|------|------------|
| Successes | 4/5 | 5/5 |
| Front-half successes | 5/5 | N/A |
| Avg semantic score | 1.3 | 1.6 |
| Total cost | $0.909 | $0.198 |
| Cost ratio | 4.6x | — |

**Verdict**: `inconclusive` — gap = 1 trial

---

## Trial 5 AC14 Failure Analysis

All 3 attempts failed; front-half passed all 3 times:

**Attempt 1**: Generated blueprint fixtures had `disc_alpha=0.0` instead of 0.924.
Packet test failure: `d_params_out.disc_alpha expected=0.0 actual=0.9246`. Code was correct
(it computed the right disc_alpha), but the model's own generated fixture had the wrong value.

**Attempt 2**: Code added over-zealous validation: "Input parameters for d1_zeta calculation 
must be positive." The validation rejected valid inputs, crashing before computing anything.

**Attempt 3**: Similar validation issue: "volatility * sqrt(time_to_expiry) is zero."

**Pattern**: The failure is NOT about formula understanding. The model correctly wrote the
zeta/alpha modifications in attempts 1 and 2 but had:
- Wrong fixture values in generated blueprint (attempt 1)
- Over-zealous input validation that fires on valid inputs (attempts 2-3)

This is codegen quality noise, not a systematic context capacity or formula memorization problem.

---

## Cumulative Benchmark Series (All Models and Benchmarks)

| Gate | Model | AC14 | Mono | Verdict | Notes |
|------|-------|------|------|---------|-------|
| IT gate_1 | gpt-4.1 | 5/5 | 5/5 | inconclusive | Both memorize IT formulas |
| PT gate_2d | gpt-4.1 | 5/5 | 5/5 | monolithic_wins (efficiency) | Both implement PT |
| PT Gemini flash-lite | gemini-2.5-flash-lite | 2/5 | 5/5 | monolithic_wins | Flash-lite decomp fails |
| BS gate_1 | gpt-4.1 | 5/5 | 5/5 | inconclusive | Both implement BS |
| BS Gemini flash | gemini-2.5-flash-lite | 4/5 | 5/5 | inconclusive | Flash-lite mostly works |
| Zeta gate_1 | gpt-4.1 | 4/5 | 5/5 | inconclusive | gpt-4.1 impl. novel formulas |
| Zeta Gemini flash gate_1 | gemini-2.5-flash | 0/5 | 5/5 | INVALID (budget bug) | Infrastructure failure |
| **Zeta Gemini flash gate_2** | **gemini-2.5-flash** | **4/5** | **5/5** | **inconclusive** | **Flash impl. novel formulas!** |

---

## Key Thesis Finding: Models Are Better Spec-Followers Than Hypothesized

All LLMs tested (gpt-4.1, Gemini flash-lite, Gemini flash) correctly implement the zeta/alpha
modifications WITHOUT needing per-component hints:
- disc_alpha = exp(-r^alpha * T) ✓ (not exp(-rT))
- delta_call = zeta * N(d1_zeta) ✓ (not N(d1) alone)
- vega with zeta^0.5 ✓ (not zeta)
- rho with alpha, r^(alpha-1) ✓

**The formula memorization / context capacity hypothesis was wrong for 10-component systems.**

AC14 consistently underperforms monolithic by ~1 trial due to codegen quality issues:
- Generated blueprint fixtures sometimes have wrong values (placeholder-style "0.0")
- Generated code sometimes adds over-zealous input validation
- These are not addressed by per-component business rules

---

## Next Step: Plan #165 — 10-Trial Statistical Gate

Per the overnight chain: `inconclusive` → run 10-trial gate for statistical significance.

Command:
```bash
make front-half-first-full-trials \
  BENCHMARK=benchmarks/zeta_options \
  OUTPUT=.ac14_out/zeta_gemini_gate_3 \
  MODEL=gemini/gemini-2.5-flash \
  MAX_BUDGET=1.00 \
  TRIALS=10 \
  MAX_ATTEMPTS=3
```

If 10-trial result is:
- `monolithic_wins` (mono - AC14 ≥ 2): thesis fails for this benchmark/model combination
- `inconclusive`: consider pivot to haiku model, larger system, or codegen quality repair
- `ac14_wins` (unlikely given pattern): thesis validated

Also worth investigating: codegen quality repair specifically targeting:
1. Blueprint fixture placeholder detection (prevent "0.0" disc_alpha values)
2. Over-validation in generated code (don't add validation against valid inputs)

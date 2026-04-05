# Plan #163 Verdict — Zeta Options Gemini Flash Gate

**Status**: Complete  
**Started**: 2026-04-05  
**Completed**: 2026-04-05

---

## Gate Results

Output: `.ac14_out/zeta_gemini_gate_1/`  
Model: `gemini/gemini-2.5-flash`  
Benchmark: `zeta_options_structured_spec_v1` (10 components)  
Budget: `MAX_BUDGET=0.30`

| Metric | AC14 | Monolithic |
|--------|------|------------|
| Successes | 0/5 | 5/5 |
| Front-half successes | 0/5 | N/A |
| Avg repair loops | 2.0 | 0.0 |
| Avg semantic score | 0.0 | 1.8 |
| Total cost | $0.514 | $0.149 |

**Declared verdict**: `monolithic_wins`

---

## CRITICAL FINDING: Infrastructure Failure, Not Formula Failure

### AC14 failure root cause: Budget accumulation bug

All 5 AC14 trials failed with:
```
Budget exceeded for trace ac14/freeze_semantic/draft_bundle: $0.4603 spent >= $0.3000 limit
```

The trace_id `ac14/freeze_semantic/draft_bundle` is **shared across multiple gate runs**. Prior smoke
runs (`zeta_gemini_smoke_1`, `zeta_gemini_smoke_2`) spent $0.46 under this trace_id. When the full
gate started, ALL attempts immediately exceeded the $0.30 budget limit.

**This is the same budget accumulation bug as Plan #139** — the fix applied to `draft_blueprint_plan_from_structured_spec`
was NOT applied to the `freeze_semantic/draft_bundle` trace path.

**The `monolithic_wins` verdict is INVALID** as a thesis test — AC14 never generated any code.

---

## Monolithic Performance: Gemini Flash Correctly Implements ALL Zeta/Alpha Formulas

Despite the invalid AC14 comparison, the monolithic results are the key thesis finding:

**Gemini flash correctly implemented all 13 novel zeta/alpha modifications, 5/5 trials:**

| Formula | Expected | Verdict |
|---------|----------|---------|
| disc_alpha = exp(-r^alpha * T) | Correctly computed | ✓ satisfied |
| d1_zeta with zeta scaling | Correctly computed | ✓ satisfied |
| d2_zeta = d1_zeta - zeta*sigma*sqrt(T) | Correctly computed | ✓ satisfied |
| call = S*N(d1_zeta) - K*disc_alpha*N(d2_zeta) | Exactly matched | ✓ satisfied |
| put = K*disc_alpha*N(-d2_zeta) - S*N(-d1_zeta) | Exactly matched | ✓ satisfied |
| delta_call = zeta * N(d1_zeta) | Exactly matched | ✓ satisfied |
| delta_put = zeta * N(d1_zeta) - 1 | Exactly matched | ✓ satisfied |
| gamma = zeta * N'(d1_zeta) / (S*sigma*sqrt(T)) | Exactly matched | ✓ satisfied |
| theta_call with r^alpha and zeta | Exactly matched | ✓ satisfied |
| theta_put with +r^alpha and N(-d2_zeta) | Exactly matched | ✓ satisfied |
| vega = S*N'(d1_zeta)*sqrt(T)*zeta^0.5 | Exactly matched | ✓ satisfied |
| rho_call = alpha*K*T*(r^(alpha-1))*disc_alpha*N(d2_zeta) | Exactly matched | ✓ satisfied |
| rho_put = -alpha*K*T*(r^(alpha-1))*disc_alpha*N(-d2_zeta) | Exactly matched | ✓ satisfied |

Semantic score 1.8/2 — the only "concern" was that `put_price` for `low_zeta` case is negative, which is
mathematically correct behavior (deeply ITM case with zeta=0.40 produces negative put price; the formula
is correctly implemented but the value is unusual).

**Runtime outputs: ALL 4 cases matched exactly across all 5 trials.**

---

## Thesis Implications

### The formula memorization hypothesis was completely wrong

The original thesis for Plan #161 was:
> "Novel formulas that are NOT in training data forces both conditions to follow the specification exactly."

**Result**: Both gpt-4.1 AND Gemini flash correctly implement all zeta/alpha modifications WITHOUT AC14's
per-component hints. They read the specification and implement it correctly, regardless of novelty.

LLMs are better at spec-following than hypothesized. The context capacity / memorization bottleneck
appears not to be the limiting factor for 10-component systems.

### Benchmark Series Summary (Through Zeta Gemini Flash)

| Gate | Model | AC14 | Mono | Verdict | Notes |
|------|-------|------|------|---------|-------|
| IT gate_1 | gpt-4.1 | 5/5 | 5/5 | inconclusive | Both implement IT formulas |
| PT gate_2d | gpt-4.1 | 5/5 | 5/5 | monolithic_wins (efficiency) | Both implement PT formulas |
| PT Gemini flash | gemini-2.5-flash-lite | 2/5 | 5/5 | monolithic_wins | Flash fails decomposition, not formulas |
| BS gate_1 | gpt-4.1 | 5/5 | 5/5 | inconclusive | Both implement BS formulas |
| BS Gemini flash | gemini-2.5-flash-lite | 4/5 | 5/5 | inconclusive | Flash mostly implements BS |
| Zeta gate_1 | gpt-4.1 | 4/5 | 5/5 | inconclusive | gpt-4.1 implements novel formulas! |
| **Zeta Gemini flash** | **gemini-2.5-flash** | **INVALID** | **5/5** | **budget bug** | **Flash implements ALL novel formulas!** |

---

## Next Step: Plan #164 — Fix Budget Bug, Rerun with Sufficient Budget

The honest comparison requires AC14 to actually run. Two options:

**Option A**: Fix the budget accumulation in `freeze_semantic/draft_bundle` trace path (replication of Plan #140 fix for different code path), then rerun with `MAX_BUDGET=1.00`.

**Option B**: Accept that Gemini flash is too capable for current benchmark design. Pivot to:
- Haiku model (weaker than flash)
- 20+ component systems
- Multi-file codegen tasks
- Cross-file dependency challenges

**Recommended**: Option A first (clean comparison), then Option B if flash still wins with correct comparison.

---

## Action Items

1. Find the `freeze_semantic/draft_bundle` trace_id in the code and apply the same per-run hash fix
2. Rerun Gemini flash gate with `MAX_BUDGET=1.00` and unique trace_ids  
3. If AC14 also passes: write Plan #165 verdict
4. If AC14 still fails (code generation issues): diagnose whether it's budget, syntax, or formula errors

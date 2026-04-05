# Plan #173: Zeta Scale-20 Gate_1 — Verdict Interpretation

**Status:** ACTIVE (waiting on gate artifact)
**Type:** verdict interpretation
**Priority:** High
**Blocked By:** Plan #172 (full trial gate must complete)
**Blocks:** Plan #174 (next empirical direction)

---

## Gate Inputs

Gate artifact: `.ac14_out/zeta_scale20_gate_1/front_half_first_decision.json`
Smoke artifact: `.ac14_out/zeta_scale20_smoke_3/smoke_readiness_report.json`

Smoke result (smoke_3):
- verdict: `ready_for_full_trials`
- AC14: 4/4 matched_expected, $0.16/trial
- Monolithic: 4/4 matched_expected, $0.06/trial

---

## Verdict Branches (Pre-Defined)

### Branch A: `ac14_wins` (AC14 successes > monolithic + 2 margin)

**Meaning:** Scale-20 is sufficient to discriminate. AC14's decomposition advantage
appears at 20 components — within context capacity of Gemini flash, but AC14 does better.

**Actions:**
1. Write `docs/theory_forge/zeta_scale20_verdict.md` documenting the win
2. Record: minimum discriminating scale is ≤ 20 components for this domain
3. Identify which components caused monolithic to fail (context pressure vs formula errors)
4. Create Plan #174: design a scale-10 vs scale-20 bracket to find the exact threshold
5. Update CLAUDE.md Theory Forge chain with `ac14_wins` at scale_20

### Branch B: `monolithic_wins` (monolithic successes > AC14 + 2 margin)

**Meaning:** Scale-20 is still within Gemini flash context capacity. Monolithic wins again.

**Actions:**
1. Write `docs/theory_forge/zeta_scale20_verdict.md` documenting the loss
2. Confirm: scale threshold is > 20 components for math pipeline domain
3. Create Plan #174: two options (choose based on cost analysis):
   - **Option A (scale):** Build zeta_scale_50 (50-component benchmark) — test at 2.5x scale
   - **Option B (complexity):** Build a domain with complex interdependencies (stat mech,
     control systems) where decomposition captures domain knowledge, not just formula volume
4. Update CLAUDE.md with monolithic_wins at scale_20, estimated threshold > 20

### Branch C: `inconclusive` (within 2 trials of each other)

**Meaning:** Scale-20 is marginal — too close to call with 10 trials.

**Actions:**
1. Write `docs/theory_forge/zeta_scale20_verdict.md` documenting inconclusive result
2. Consider: run 10 more trials (20-trial gate) vs move to scale-50 for cleaner signal
3. If cost per trial > $1.00 for AC14, prefer scale-50 (cheaper to get cleaner signal)
4. Create Plan #174: 20-trial zeta_scale_20 gate or zeta_scale_50 design

---

## Acceptance Criteria

1. `front_half_first_decision.json` exists at `.ac14_out/zeta_scale20_gate_1/`
2. Verdict doc written at `docs/theory_forge/zeta_scale20_verdict.md`
3. Plan #174 created with unambiguous next action
4. CLAUDE.md updated with verdict and Plan #174 as next active

---

## Theory Forge Context

| Gate | Benchmark | Model | AC14 | Mono | Verdict |
|------|-----------|-------|------|------|---------|
| IT gate_1 | it_benchmark | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| PT gate_2d | pt_benchmark | gpt-4.1 | 5/5 | 5/5 | monolithic_wins |
| PT Gemini | pt_benchmark | Gemini flash | 2/5 | 5/5 | monolithic_wins |
| BS Gemini | bs_benchmark | Gemini flash | 4/5 | 5/5 | inconclusive |
| Zeta Gate_1 | zeta_options | gpt-4.1 | 4/5 | 5/5 | inconclusive |
| Zeta Gate_2 | zeta_options | Gemini flash | 1/5 | 5/5 | monolithic_wins |
| Zeta Gate_3 | zeta_options | Gemini flash | 6/10 | 9/10 | monolithic_wins |
| **Zeta Scale_20 Gate_1** | **zeta_scale_20** | **Gemini flash** | **TBD** | **TBD** | **TBD** |

Pattern so far: monolithic wins consistently at 10-component scale. Scale_20 is the
first attempt to find the discrimination threshold.


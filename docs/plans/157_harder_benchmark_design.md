# Plan #157: Harder Benchmark Design — Find Where Monolithic Breaks

**Status**: Active  
**Started**: 2026-04-04  
**Blocked By**: Plan #156 verdict

---

## Problem Statement

Every benchmark tried so far has monolithic succeeding at 100%:
- resource_scaling: 10/10 (10 trials)
- information_theory_shannon: 5/5
- prospect_theory_tk1992: 5/5

AC14 matches or approaches these numbers once the pipeline is working. The thesis
("decomposition holds up where monolithic breaks down") remains empirically untested.

**Root cause of tracability**: All three benchmarks have requirements docs small enough
to fit easily in a single context window, and gpt-4.1/Gemini are capable enough to
hold all the formulas simultaneously.

---

## Discriminating Benchmark Design Criteria

A benchmark that challenges monolithic should have at LEAST two of:

1. **Volume pressure**: 10+ components, each with 3-5 formulas — total requirements
   doc too large for effective single-context reasoning
2. **Similarity confusion**: Components have similar-sounding but distinct parameters
   (e.g., γ for gains vs δ for losses vs γ for something else in another component)
3. **Implicit knowledge required**: Formulas not spelled out explicitly — must be
   derived from description, requiring domain knowledge or careful reading
4. **Subtle sign/branch logic**: Multiple piecewise branches with different formulas
   in different conditions, easy to swap
5. **Cross-component invariants**: One component's output format must match another's
   input contract exactly, and getting it wrong causes subtle downstream errors

---

## Candidate: Black-Scholes Option Pricing Suite (10-12 components)

**Why this works:**
- Greeks (delta/gamma/theta/vega/rho) all use similar N(d1), N(d2) but different
  derivatives — monolithic must correctly differentiate all 5 without confusion
- Theta has DIFFERENT formulas for calls vs puts — easy to get one wrong
- Barrier options require reflection principle — non-trivial, not spoon-fed
- 10+ components total
- Well-known enough that golden test cases can be validated against published values

**Components (12):**
1. `compute_d1` — (ln(S/K) + (r + σ²/2)·T) / (σ·√T)
2. `compute_d2` — d1 - σ·√T  
3. `price_vanilla_call` — S·N(d1) - K·e^(-rT)·N(d2)
4. `price_vanilla_put` — K·e^(-rT)·N(-d2) - S·N(-d1)
5. `compute_delta` — N(d1) for call, N(d1)-1 for put
6. `compute_gamma` — N'(d1) / (S·σ·√T) [same for call and put]
7. `compute_theta_call` — -(S·N'(d1)·σ)/(2√T) - r·K·e^(-rT)·N(d2)
8. `compute_theta_put` — -(S·N'(d1)·σ)/(2√T) + r·K·e^(-rT)·N(-d2)
9. `compute_vega` — S·N'(d1)·√T [same for call and put]
10. `compute_rho_call` — K·T·e^(-rT)·N(d2)
11. `compute_rho_put` — -K·T·e^(-rT)·N(-d2)
12. `compute_implied_volatility` — Newton-Raphson: σ_{n+1} = σ_n - (BS(σ_n) - price) / vega(σ_n)

**Why this challenges monolithic:**
- Monolithic needs to hold all 12 formulas simultaneously
- Theta call and theta put have exactly one sign difference — easy to confuse
- Delta call and delta put have related but different formulas (N(d1) vs N(d1)-1)
- Rho call/put differ by sign on N(±d2) — easy to swap
- Implied volatility requires iterative loop that references vega — cross-component dependency

**Why AC14 should do better:**
- Each component sees its ONE formula clearly
- Component local context includes only the inputs it needs
- Theta call component never sees theta put formula — no confusion possible
- Cross-component invariants enforced by typed port schema

---

## Alternative: Multi-Factor CAPM/APT Attribution (15 components)

Even harder — multiple factors, covariance matrices, factor loading estimation.
More components = more context pressure. Save for later if BS suite isn't
discriminating enough.

---

## Implementation Plan

1. Create `benchmarks/black_scholes_greeks/`
   - `structured_spec_input.yaml` — 12 components with precise formulas in description
   - `requirements.md` — deliberately NOT spelling out every formula step-by-step
   - `runtime_cases.json` — 4 test cases: ATM call, ITM put, barrier call, Greek verification
   - `expected_runtime_outputs.json` — golden values from published BS tables

2. Write `structured_spec_input.yaml`
   - Be sparse on formula hints (no "use this exact formula" handholding)
   - Include edge cases: ATM (d1=d2), deep ITM, near-expiry

3. Run smoke gate to verify the benchmark setup works

4. Run full 5-trial gate

5. Write verdict plan

---

## Acceptance Criteria

- [x] Benchmark design documented (this plan)
- [ ] `benchmarks/black_scholes_greeks/` created with all required files
- [ ] Smoke gate runs and returns a verdict (any verdict is acceptable)
- [ ] Full 5-trial gate run and verdict written
- [ ] If monolithic < 100%: AC14 thesis has first empirical support
- [ ] If monolithic = 100%: escalate to 15-component CAPM benchmark

---

## Success Condition

**Minimal success**: monolithic success rate < 100% on the new benchmark  
**Strong success**: AC14 success rate >= monolithic success rate on the new benchmark

If both conditions fail 100%: the benchmark is too hard and needs calibration.
If both succeed 100%: still too tractable — increase component count or formula complexity.

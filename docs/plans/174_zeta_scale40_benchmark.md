# Plan #174: Zeta Scale-40 Benchmark — Dual-Option Portfolio

## Status: ACTIVE

## Context

Plan #173 showed zeta_scale_20: both conditions 5/5 (AC14 wins tie-break only).
Plan #168 pre-decided: "if mono still 5/5 → scale to 40 components."
This plan builds the 40-component benchmark and runs it with Gemini flash.

Marginal signal from zeta_scale_20: mono needed 2 repairs in trial 1 vs AC14's 0.
Extrapolation from Plan #173: "mono probably fails at 40-60 components for Gemini flash."

## Design: Dual-Option Portfolio Pipeline

**Approach**: Two parallel zeta-option pipelines (Option A + Option B) that compute
independent Greeks, feed into intermediate assemblers, then aggregate into a portfolio
result via a terminal component. Total: 40 components.

**Why this discriminates at 40 vs 20**:
- Monolithic must generate ~3200 lines with consistent `_a` / `_b` naming across two parallel
  pipelines. Any variable cross-binding (using d1_zeta_a in an option_b component) fails the
  test. This naming discipline is hard to maintain over 3200 lines without drift.
- AC14 generates each component in isolation — naming is local, no drift risk.

### Component Layout

**Option A Pipeline (components 1-20):**
1. `compute_option_a_d_params` — source; same d_params formulas as zeta_options
2. `price_option_a_call`
3. `price_option_a_put`
4. `compute_option_a_delta`
5. `compute_option_a_gamma`
6. `compute_option_a_theta_call`
7. `compute_option_a_theta_put`
8. `compute_option_a_vega`
9. `compute_option_a_rho_call`
10. `compute_option_a_rho_put`
11. `compute_option_a_vanna`
12. `compute_option_a_volga`
13. `compute_option_a_charm`
14. `compute_option_a_veta`
15. `compute_option_a_speed`
16. `compute_option_a_zomma`
17. `compute_option_a_color`
18. `compute_option_a_dual_delta`
19. `compute_option_a_ultima`
20. `assemble_option_a_results` — intermediate assembler

**Option B Pipeline (components 21-40):**
21. `compute_option_b_d_params` — second source
22-39. Same pattern as 2-19 but for option B
40. `assemble_portfolio_results` — terminal; combines A+B, computes portfolio Greeks

### Input/Output

**Input**:
- `option_a_request`: `{case_id, spot_a, strike_a, rate_a, vol_a, T_a, zeta_a, alpha_a}`
- `option_b_request`: `{case_id, spot_b, strike_b, rate_b, vol_b, T_b, zeta_b, alpha_b}`

**Output** (`portfolio_results`):
- All Option A Greeks: `call_a, put_a, delta_call_a, delta_put_a, gamma_a, ...`
- All Option B Greeks: `call_b, put_b, delta_call_b, delta_put_b, gamma_b, ...`
- Portfolio: `portfolio_delta = delta_call_a + delta_call_b`
- Portfolio: `portfolio_gamma = gamma_a + gamma_b`
- Portfolio: `portfolio_vega = vega_a + vega_b`
- Portfolio: `portfolio_theta = theta_call_a + theta_call_b`
- Portfolio: `portfolio_rho = rho_call_a + rho_call_b`

### Test Cases (4 cases)

| Case | Option A | Option B |
|------|---------|---------|
| base_spread | S=100,K=100,r=0.05,σ=0.20,T=1.0,ζ=0.70,α=0.85 | S=100,K=110,r=0.05,σ=0.20,T=1.0,ζ=0.70,α=0.85 |
| vol_spread | S=100,K=100,r=0.05,σ=0.15,T=0.5,ζ=0.60,α=0.80 | S=100,K=100,r=0.05,σ=0.25,T=0.5,ζ=0.60,α=0.80 |
| mixed | S=80,K=90,r=0.08,σ=0.30,T=2.0,ζ=0.90,α=0.95 | S=120,K=100,r=0.03,σ=0.15,T=1.5,ζ=0.40,α=0.70 |
| deep | S=100,K=95,r=0.04,σ=0.18,T=0.75,ζ=0.55,α=0.75 | S=105,K=115,r=0.06,σ=0.22,T=1.25,ζ=0.80,α=0.90 |

Expected outputs are generated programmatically from reference_impl.py.

## Formula Summary (same as zeta_scale_20, applied per-option)

For each option (A or B), given S, K, r, sigma, T, zeta, alpha:

```
disc_alpha = exp(-(r**alpha) * T)
d1_zeta = (log(S/K) + (r + zeta*sigma^2/2)*T) / (sigma*sqrt(T))
d2_zeta = d1_zeta - zeta*sigma*sqrt(T)
dd1_dT = (r + zeta*sigma^2/2) / (sigma*sqrt(T)) - d1_zeta / (2*T)

call = S*N(d1_zeta) - K*disc_alpha*N(d2_zeta)
put = K*disc_alpha*N(-d2_zeta) - S*N(-d1_zeta)
delta_call = zeta*N(d1_zeta)
delta_put = zeta*N(d1_zeta) - 1
gamma = zeta*N'(d1_zeta) / (S*sigma*sqrt(T))
theta_call = -(S*N'(d1_zeta)*sigma*zeta)/(2*sqrt(T)) - (r**alpha)*K*disc_alpha*N(d2_zeta)
theta_put = -(S*N'(d1_zeta)*sigma*zeta)/(2*sqrt(T)) + (r**alpha)*K*disc_alpha*N(-d2_zeta)
vega = S*N'(d1_zeta)*sqrt(T)*(zeta**0.5)
rho_call = alpha*K*T*(r**(alpha-1))*disc_alpha*N(d2_zeta)
rho_put = -alpha*K*T*(r**(alpha-1))*disc_alpha*N(-d2_zeta)
vanna = -zeta*N'(d1_zeta)*d2_zeta/sigma
volga = vega*d1_zeta*d2_zeta/sigma
charm = zeta*N'(d1_zeta)*dd1_dT
veta = S*(zeta**0.5)*N'(d1_zeta)*(1/(2*sqrt(T)) - d1_zeta*dd1_dT)
speed = -gamma*(1 + d1_zeta/(sigma*sqrt(T)))/S
zomma = gamma*(d1_zeta*d2_zeta - 1)/sigma
color = -gamma*(d1_zeta*dd1_dT + 1/(2*T))
dual_delta_call = -disc_alpha*N(d2_zeta)
dual_delta_put = disc_alpha*N(-d2_zeta)
ultima = -volga/sigma*(d1_zeta*d2_zeta*(1-d1_zeta*d2_zeta) + d1_zeta^2 + d2_zeta^2)
```

**Portfolio Greeks (component 40 only)**:
```
portfolio_delta = delta_call_a + delta_call_b
portfolio_gamma = gamma_a + gamma_b
portfolio_vega = vega_a + vega_b
portfolio_theta = theta_call_a + theta_call_b
portfolio_rho = rho_call_a + rho_call_b
```

## Implementation Steps

1. Build `benchmarks/zeta_scale_40/reference_impl.py` — generates expected outputs
2. Build `benchmarks/zeta_scale_40/runtime_cases.json` — 4 test cases
3. Build `benchmarks/zeta_scale_40/expected_runtime_outputs.json` — from reference_impl
4. Build `benchmarks/zeta_scale_40/structured_spec_input.yaml` — 40-component spec
5. Run B1 validation on the structured_spec to confirm valid blueprint
6. Build `benchmarks/zeta_scale_40/benchmark.yaml` (front-half-first format)
7. Build `benchmarks/zeta_scale_40/back_half/benchmark.yaml` (full back-half)
8. Run smoke gate (1 trial) — `ready_for_full_trials` → proceed; else fix
9. Run full gate (5 trials) with Gemini flash
10. Write Plan #175 as verdict

## Acceptance Criteria

- B1 validation passes on the structured_spec
- Smoke gate produces `ready_for_full_trials`
- Full gate result interpreted in Plan #175

## Files to Create

- `benchmarks/zeta_scale_40/reference_impl.py`
- `benchmarks/zeta_scale_40/runtime_cases.json`
- `benchmarks/zeta_scale_40/expected_runtime_outputs.json`
- `benchmarks/zeta_scale_40/structured_spec_input.yaml`
- `benchmarks/zeta_scale_40/requirements.md`
- `benchmarks/zeta_scale_40/benchmark.yaml`
- `benchmarks/zeta_scale_40/back_half/benchmark.yaml`
- `docs/plans/175_zeta_scale40_verdict.md` (after gate runs)

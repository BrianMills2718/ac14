# Plan #169: Zeta Scale-20 Benchmark Build

## Status: ACTIVE

## Objective

Build `benchmarks/zeta_scale_20/` — a 20-component extension of zeta_options_v1 that adds
10 second-order Greeks (vanna, volga, charm, veta, speed, zomma, color, dual-delta). The
goal is to find the scale at which monolithic LLM generation starts failing while AC14
decomposition continues to succeed.

## Rationale

Plan #168 concluded that 10-component benchmarks are trivially within context capacity for
modern LLMs (gpt-4.1 128K, Gemini 1M). At 20 components, monolithic must generate ~1500 lines
of code implementing 20+ interdependent formulas. If monolithic still passes 5/5, proceed to
40 components. Scale_20 establishes the lower bound and provides discriminating evidence for
the thesis.

## Architecture (20 Components)

### Stage 1 Source (1 component)
1. **compute_zeta_d_params** — source, same as zeta_options_v1

### Stage 2 First-Order Greeks (10 components, same as v1)
2. price_zeta_call (input: d_params_output)
3. price_zeta_put (input: d_params_output)
4. compute_zeta_delta (input: d_params_output)
5. compute_zeta_gamma (input: d_params_output)
6. compute_zeta_theta_call (input: d_params_output)
7. compute_zeta_theta_put (input: d_params_output)
8. compute_zeta_vega (input: d_params_output)
9. compute_zeta_rho_call (input: d_params_output)
10. compute_zeta_rho_put (input: d_params_output)

### Stage 3 Second-Order Greeks (8 components)
11. compute_zeta_vanna (input: d_params_output)
12. compute_zeta_volga (input: d_params_output, vega_output)
13. compute_zeta_charm (input: d_params_output) → outputs charm_call, charm_put
14. compute_zeta_veta (input: d_params_output, vega_output)
15. compute_zeta_speed (input: d_params_output, gamma_output)
16. compute_zeta_zomma (input: d_params_output, gamma_output)
17. compute_zeta_color (input: d_params_output, gamma_output)
18. compute_zeta_dual_delta (input: d_params_output) → outputs dual_delta_call, dual_delta_put

### Stage 4 Terminal (1 component)
19. **assemble_zeta_extended_results** — SINK, assembles all 24 output fields

Wait — that's only 19. Adding one more:
19. compute_zeta_ultima (input: d_params_output, volga_output) — d³V/dσ³
    ultima = -volga/sigma * (d1_zeta*d2_zeta*(1-d1_zeta*d2_zeta) + d1_zeta² + d2_zeta²)
20. **assemble_zeta_extended_results** — SINK

## Formulas (All Analytically Derived)

### New second-order Greeks:
```python
# d(d1_zeta)/dT = (r + zeta*sigma**2/2) / (sigma*sqrt(T)) - d1_zeta / (2*T)

# Vanna = d(delta_call)/d(sigma)
vanna = -zeta * norm.pdf(d1_zeta) * d2_zeta / sigma

# Volga = d(vega)/d(sigma)
volga = vega * d1_zeta * d2_zeta / sigma

# Charm (delta decay) = d(delta_call)/d(T)
dd1_dT = (r + zeta*sigma**2/2) / (sigma*sqrt(T)) - d1_zeta / (2*T)
charm_call = zeta * norm.pdf(d1_zeta) * dd1_dT
charm_put  = charm_call  # delta_put = delta_call - 1, same partial derivative

# Veta = d(vega)/d(T)
veta = S * (zeta**0.5) * norm.pdf(d1_zeta) * (1/(2*sqrt(T)) - d1_zeta * dd1_dT)

# Speed = d(gamma)/d(S)
speed = -gamma * (1 + d1_zeta / (sigma * sqrt(T))) / S

# Zomma = d(gamma)/d(sigma)
zomma = gamma * (d1_zeta * d2_zeta - 1) / sigma

# Color = d(gamma)/d(T)
color = -gamma * (d1_zeta * dd1_dT + 1/(2*T))

# Dual delta (call) = d(call_price)/d(K)
dual_delta_call = -disc_alpha * norm.cdf(d2_zeta)

# Dual delta (put) = d(put_price)/d(K)
dual_delta_put = disc_alpha * norm.cdf(-d2_zeta)

# Ultima = d(volga)/d(sigma)
ultima = -volga / sigma * (d1_zeta * d2_zeta * (1 - d1_zeta * d2_zeta) + d1_zeta**2 + d2_zeta**2)
```

## Expected Runtime Outputs (Base Case)

| Field | Value |
|-------|-------|
| vanna | -0.2387892315 |
| volga | 9.1330470740 |
| charm_call | 0.0424514189 |
| charm_put | 0.0424514189 |
| veta | 14.2323316903 |
| speed | -0.0003449178 |
| zomma | -0.0625097144 |
| color | -0.0073122569 |
| dual_delta_call | -0.5283534998 |
| dual_delta_put | 0.3962729816 |

## Output Schema: ZetaExtendedResults

Fields (24 total including case_id):
- case_id (str)
- d1_zeta, d2_zeta, disc_alpha (core params)
- call_price, put_price (prices)
- delta_call, delta_put, gamma (first-order)
- theta_call, theta_put, vega (first-order)
- rho_call, rho_put (first-order)
- vanna, volga (second-order volatility)
- charm_call, charm_put (second-order time)
- veta (second-order time-vega)
- speed, zomma, color (third/second-order gamma)
- dual_delta_call, dual_delta_put (strike sensitivity)
- ultima (third-order volatility)

## Acceptance Criteria

- B1 validation passes (20 components, 20 schemas, correct bindings)
- Reference implementation matches expected values within 1e-8
- smoke gate succeeds: AC14 passes in ≤ 3 attempts OR produces meaningful failure categories
- Full 5-trial gate to follow if smoke is `ready_for_full_trials`

## Files to Create

- `benchmarks/zeta_scale_20/benchmark.yaml`
- `benchmarks/zeta_scale_20/structured_spec_input.yaml`
- `benchmarks/zeta_scale_20/requirements.md`
- `benchmarks/zeta_scale_20/blueprint/metadata.yaml`
- `benchmarks/zeta_scale_20/blueprint/schemas.yaml`
- `benchmarks/zeta_scale_20/blueprint/architecture.yaml`
- `benchmarks/zeta_scale_20/blueprint/components.yaml`
- `benchmarks/zeta_scale_20/blueprint/fixtures.yaml`
- `benchmarks/zeta_scale_20/blueprint/validation.yaml`
- `benchmarks/zeta_scale_20/runtime_cases.json`
- `benchmarks/zeta_scale_20/expected_runtime_outputs.json`
- `benchmarks/zeta_scale_20/back_half/benchmark.yaml`

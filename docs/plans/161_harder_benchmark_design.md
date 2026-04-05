# Plan #161: Harder Benchmark Design — Zeta-Modified Option Pricing (10 Components)

**Status**: Active  
**Started**: 2026-04-04

---

## Context

All Theory Forge benchmarks (IT, PT, BS) with both gpt-4.1 and Gemini flash show monolithic
competitive or winning. Root cause identified:

**Fundamental problem**: All benchmarks use formulas memorized in GPT-4.1 training data
(Shannon entropy, Prospect Theory value/weight functions, Black-Scholes Greeks). The model
recalls correct implementations without reading the spec carefully. Both conditions
(AC14 and monolithic) benefit equally from memorization.

**The thesis requires**: Formulas that are NOT in training data. This forces both conditions to
follow the specification exactly. AC14 advantage: per-component context is focused on one
formula with explicit "CRITICAL DIFFERENCE FROM STANDARD" callouts. Monolithic disadvantage:
must track novel modifications across all formulas simultaneously, risking drift back to
memorized patterns.

---

## Benchmark: Zeta-Modified European Option Pricing

### Design Rationale

Take the familiar Black-Scholes structure (provides code scaffolding) but introduce two
free parameters:
- `zeta` (typical value: 0.70): scales variance contribution and delta/gamma calculation
- `alpha` (typical value: 0.85): modifies the discount via fractional power `r^alpha`

These create formulas that:
1. Look structurally like BS but are numerically WRONG if the model uses memorized BS
2. Each component's business rules explicitly call out the modification  
3. The parameters vary across test cases, so hardcoding BS answers fails

### Modified Formula Definitions

Given: S (spot), K (strike), r (risk-free rate), sigma (vol), T (expiry),
       zeta, alpha (per-case parameters)

**Stage 1 — compute_zeta_d_params**:
```
disc_alpha = exp(-r^alpha * T)                           # fractional-power discount
d1_zeta = (ln(S/K) + (r + zeta * sigma^2 / 2) * T) / (sigma * sqrt(T))
d2_zeta = d1_zeta - zeta * sigma * sqrt(T)              # zeta scales d1-d2 gap
```

**Stage 2 — price_zeta_call**:
```
call_price = S * N(d1_zeta) - K * disc_alpha * N(d2_zeta)
```

**Stage 3 — price_zeta_put**:
```
put_price = K * disc_alpha * N(-d2_zeta) - S * N(-d1_zeta)
```

**Stage 4 — compute_zeta_delta**:
```
delta_call = zeta * N(d1_zeta)           # zeta SCALES delta (standard BS uses N(d1) with no scale)
delta_put  = zeta * N(d1_zeta) - 1
```

**Stage 5 — compute_zeta_gamma**:
```
gamma = zeta * N_prime(d1_zeta) / (S * sigma * sqrt(T))   # zeta scales gamma
```

**Stage 6 — compute_zeta_theta_call**:
```
theta_call = -(S * N_prime(d1_zeta) * sigma * zeta) / (2 * sqrt(T))
             - r^alpha * K * disc_alpha * N(d2_zeta)
```
Note: `r^alpha` (NOT `r`) — comes from d/dT[disc_alpha] = -r^alpha * disc_alpha.

**Stage 7 — compute_zeta_theta_put**:
```
theta_put = -(S * N_prime(d1_zeta) * sigma * zeta) / (2 * sqrt(T))
            + r^alpha * K * disc_alpha * N(-d2_zeta)
```
Note: second term is POSITIVE (+) and uses N(-d2_zeta) not N(d2_zeta).

**Stage 8 — compute_zeta_vega**:
```
vega = S * N_prime(d1_zeta) * sqrt(T) * (zeta ** 0.5)   # zeta^0.5 correction
```

**Stage 9 — compute_zeta_rho_call**:
```
rho_call = alpha * K * T * (r ** (alpha - 1)) * disc_alpha * N(d2_zeta)
```

**Stage 10 — compute_zeta_rho_put** (terminal):
```
rho_put = -alpha * K * T * (r ** (alpha - 1)) * disc_alpha * N(-d2_zeta)
```

### Test Cases

Four cases with different zeta and alpha values (so memorized BS answers won't work):

| Case | S | K | r | sigma | T | zeta | alpha |
|------|---|---|---|-------|---|------|-------|
| base | 100 | 100 | 0.05 | 0.20 | 1.0 | 0.70 | 0.85 |
| otm_call | 100 | 110 | 0.05 | 0.25 | 0.5 | 0.60 | 0.80 |
| itm_put | 80 | 90 | 0.08 | 0.30 | 2.0 | 0.90 | 0.95 |
| low_zeta | 120 | 100 | 0.03 | 0.15 | 1.5 | 0.40 | 0.70 |

---

## Expected Discriminating Power

**Predicted failure modes for monolithic** (most likely to revert to memorized BS):

1. **Stage 4 delta**: Model writes `N(d1)` instead of `zeta * N(d1)` — a subtle but
   numerically large error since zeta ≠ 1.0 in all test cases
2. **Stage 8 vega**: Model writes `S * N'(d1) * sqrt(T)` omitting the `zeta^0.5` term
3. **Stage 9/10 rho**: Standard BS uses `K*T*exp(-rT)*N(d2)` — the modified version uses
   `alpha * K * T * r^(alpha-1) * disc_alpha * N(d2)` — three differences, all easy to miss

**AC14 advantage**: Each component's business rules contain ONLY its own formula with the
modification explicitly called out. The component processing context includes a single formula
with no competing formulas from other components.

---

## Implementation Steps

### Step 1: Reference implementation
`benchmarks/zeta_options/reference_impl.py` — compute all modified formulas with scipy.

### Step 2: Benchmark bundle
Mirror Black-Scholes benchmark structure:
- `structured_spec_input.yaml` — 10-component spec with zeta/alpha formulas
- `runtime_cases.json` — 4 test cases
- `expected_runtime_outputs.json` — from reference_impl
- `blueprint/` — reference blueprint
- `back_half/benchmark.yaml` + `benchmark.yaml`

### Step 3: Gate_1 with gpt-4.1
Target: monolithic fails ≥1/5 with gpt-4.1.
Write Plan #162 as the verdict.

---

## Files to Create

- `benchmarks/zeta_options/reference_impl.py`
- `benchmarks/zeta_options/structured_spec_input.yaml`
- `benchmarks/zeta_options/runtime_cases.json`
- `benchmarks/zeta_options/expected_runtime_outputs.json`
- `benchmarks/zeta_options/blueprint/` (mirror BS structure)
- `benchmarks/zeta_options/benchmark.yaml`
- `benchmarks/zeta_options/back_half/benchmark.yaml`

---

## Status

- [ ] Reference implementation and expected outputs
- [ ] Structured spec input with per-component hints
- [ ] Blueprint bundle (adapted from BS structure)
- [ ] B1 validation passes
- [ ] Gate_1 executed with gpt-4.1

EOF

# Black-Scholes Option Pricing & Greeks Suite — Benchmark Requirements

## Overview

Implement the Black-Scholes (1973) option pricing model as a nine-component
sequential pipeline. Each component implements exactly one logical stage.
The pipeline computes vanilla call and put prices, the five standard Greeks
(delta, gamma, theta, vega, rho), and Newton-Raphson implied volatility.

**Required library**: Use `scipy.stats.norm.cdf` for N(x) (standard normal CDF)
and `scipy.stats.norm.pdf` for N'(x) (standard normal PDF). Do not use custom
approximations.

## Parameters (all passed in `bs_request`)

| Parameter | Symbol | Role |
|-----------|--------|------|
| `S` | S | Current stock price |
| `K` | K | Strike price |
| `r` | r | Risk-free rate (continuous compounding) |
| `sigma` | σ | Implied volatility (used for all Greeks) |
| `T` | T | Time to expiry in years |
| `market_price_for_iv` | P | Market call price used for IV computation only |

## Formulas by Stage

### Stage 1: compute_d_values

Compute the two standardized log-return values and auxiliary quantities:

```
sqrt_T = sqrt(T)
d1 = (ln(S/K) + (r + sigma**2/2) * T) / (sigma * sqrt_T)
d2 = d1 - sigma * sqrt_T
discount_factor = exp(-r * T)
```

### Stage 2: compute_normal_values

Evaluate the standard normal CDF and PDF at d1 and d2:

```
N_d1      = norm.cdf(d1)
N_d2      = norm.cdf(d2)
N_neg_d1  = norm.cdf(-d1)    # NOT 1 - N_d1; use norm.cdf(-d1) directly
N_neg_d2  = norm.cdf(-d2)    # NOT 1 - N_d2; use norm.cdf(-d2) directly
N_prime_d1 = norm.pdf(d1)    # PDF at d1 (used for gamma, theta, vega)
```

### Stage 3: price_vanilla_call

```
call_price = S * N_d1 - K * discount_factor * N_d2
```

### Stage 4: price_vanilla_put

```
put_price = K * discount_factor * N_neg_d2 - S * N_neg_d1
```

Note: call uses N_d1, N_d2 with S-term first; put uses N_neg_d2, N_neg_d1 with
K-term first. The signs and CDF arguments are different.

### Stage 5: compute_delta

Delta measures option price sensitivity to S:

```
delta_call = N_d1
delta_put  = N_d1 - 1.0
```

**Critical**: delta_put = N(d1) - 1, NOT N(-d1) - 1. Delta_put is always in [-1, 0].

### Stage 6: compute_gamma

Gamma is the same for call and put:

```
gamma = N_prime_d1 / (S * sigma * sqrt_T)
```

This uses N_prime_d1 (PDF), not N_d1 (CDF). Gamma is always positive.

### Stage 7: compute_theta

Theta measures time decay. **The two formulas share a common first term but
differ critically on the second term:**

```
shared_first_term = -(S * N_prime_d1 * sigma) / (2 * sqrt_T)

theta_call = shared_first_term - r * K * discount_factor * N_d2
theta_put  = shared_first_term + r * K * discount_factor * N_neg_d2
```

- theta_call: subtracts `r * K * discount_factor * N_d2`
- theta_put: adds `r * K * discount_factor * N_neg_d2`
- The sign on the second term flips (+/-) AND the CDF argument changes (d2 vs -d2).

### Stage 8: compute_vega_rho

Vega is the same for call and put. Rho has a sign flip and argument flip:

```
vega = S * N_prime_d1 * sqrt_T

rho_call = K * T * discount_factor * N_d2
rho_put  = -K * T * discount_factor * N_neg_d2
```

- rho_call uses +N(d2); rho_put uses -N(-d2). Both the sign and the CDF argument flip.

### Stage 9: compute_implied_volatility_and_assemble

Compute implied volatility via Newton-Raphson, then assemble the final output:

**Newton-Raphson algorithm** (exactly 20 iterations, starting sigma = 0.25):

```python
sigma_iv = 0.25  # fixed initial guess
for _ in range(20):
    # Recompute d1, d2 using sigma_iv (not the input sigma)
    d1_iv = (ln(S/K) + (r + sigma_iv**2/2) * T) / (sigma_iv * sqrt_T)
    d2_iv = d1_iv - sigma_iv * sqrt_T
    bs_call_iv = S * norm.cdf(d1_iv) - K * discount_factor * norm.cdf(d2_iv)
    vega_iv = S * norm.pdf(d1_iv) * sqrt_T
    sigma_iv = sigma_iv - (bs_call_iv - market_price_for_iv) / vega_iv

implied_volatility = sigma_iv
```

**Final output record** `bs_greeks_result`:
- `case_id`: passed through from input
- `call_price`: from Stage 3
- `put_price`: from Stage 4
- `delta_call`: from Stage 5
- `delta_put`: from Stage 5
- `gamma`: from Stage 6
- `theta_call`: from Stage 7
- `theta_put`: from Stage 7
- `vega`: from Stage 8
- `rho_call`: from Stage 8
- `rho_put`: from Stage 8
- `implied_volatility`: from Stage 9

## Verification Identities

These must hold for any valid implementation:

1. **Put-call parity**: `call_price - put_price = S - K * discount_factor`
2. **Delta bounds**: `0 < delta_call < 1`, `-1 < delta_put < 0`
3. **Gamma positive**: `gamma > 0`
4. **Vega positive**: `vega > 0`
5. **IV round-trip**: if `market_price_for_iv` equals `call_price`, then
   `implied_volatility ≈ sigma` (converges to the input volatility)

## Common Confusion Points

1. **N(d) vs N(-d)**: `N_neg_d1 = norm.cdf(-d1)` must be called with `-d1`, not
   derived as `1 - N_d1` (though mathematically equivalent, use `norm.cdf(-d1)` for
   numerical consistency).
2. **Theta sign flip**: theta_put has `+` where theta_call has `-` on the second term.
   Also theta_put uses `N(-d2)` where theta_call uses `N(d2)`.
3. **Rho sign flip**: rho_put has `-` sign and uses `N(-d2)`.
4. **Delta_put formula**: `N(d1) - 1`, not `N(-d1)`. These are equal by put-call
   symmetry for ATM options but differ otherwise.
5. **Gamma uses PDF (N')**: `N_prime_d1 = norm.pdf(d1)`, not `norm.cdf(d1)`.
6. **IV uses input sigma for all Greeks except the Newton-Raphson loop**: the input
   `sigma` computes d1, d2 for all pricing and Greeks. Only in Stage 9 does a
   separate `sigma_iv` variable iterate starting from 0.25.

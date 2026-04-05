# Zeta-Modified European Option Pricing — Requirements (Noisy Spec)

## Overview

Implement a zeta-modified European option pricing calculator with two free parameters:
- `zeta` (0 < zeta <= 1): a variance scaling factor that modifies how volatility enters the pricing formulas
- `alpha` (0 < alpha <= 1): a fractional exponent that modifies the discount rate computation

These modifications create formulas that look structurally similar to Black-Scholes but
produce numerically different results. The implementation must follow the specification
rather than revert to standard Black-Scholes.

## Input Parameters

| Parameter | Field Name | Type | Description |
|-----------|-----------|------|-------------|
| Spot price | `spot` | float | Current asset price S |
| Strike price | `strike` | float | Option strike K |
| Risk-free rate | `rate` | float | Annualized continuous rate r |
| Volatility | `volatility` | float | Annualized vol sigma |
| Time to expiry | `time_to_expiry` | float | Years to expiration T |
| Zeta parameter | `zeta` | float | Variance scaling parameter (0 < zeta <= 1) |
| Alpha parameter | `alpha` | float | Fractional power (0 < alpha <= 1) |

## Formula Descriptions

### Stage 1: compute_zeta_d_params

Compute `disc_alpha`, `d1_zeta`, and `d2_zeta`.

- `disc_alpha`: an alpha-modified discount factor. It is NOT the standard `exp(-rate * T)`.
  The alpha parameter appears as an exponent in the rate term.
- `d1_zeta`: a zeta-modified version of the Black-Scholes d1. The zeta parameter modifies
  how variance enters the formula. The numerator uses the risk-free rate plus a zeta-scaled
  variance term. The denominator is unchanged from standard BS.
- `d2_zeta`: derived from `d1_zeta` using the zeta parameter and the standard volatility-time term.
  It is NOT equal to `d1_zeta - sigma*sqrt(T)`.

### Stage 2: price_zeta_call

Compute `call_price` using a standard call formula structure but with `disc_alpha` as the
discount factor and `d1_zeta`, `d2_zeta` as the d-parameters.

### Stage 3: price_zeta_put

Compute `put_price` using `disc_alpha` and negated d-parameters (`-d1_zeta`, `-d2_zeta`).
Put-call parity holds using the alpha-modified discount factor.

### Stage 4: compute_zeta_delta

Compute `delta_call` and `delta_put`. The zeta parameter scales the delta values.
`delta_call` is NOT equal to `N(d1_zeta)`. `delta_put = delta_call - 1`.

### Stage 5: compute_zeta_gamma

Compute `gamma` using the zeta parameter, the normal PDF at `d1_zeta`, spot, volatility,
and time. The zeta parameter modifies the standard gamma formula.

### Stage 6: compute_zeta_theta_call

Compute `theta_call` with:
- A zeta-modified first term (time decay from the volatility component)
- An alpha-modified second term that uses `disc_alpha` and `r^alpha`

Theta for long calls is negative.

### Stage 7: compute_zeta_theta_put

Compute `theta_put` similarly to theta_call but with a sign difference in the second term
(uses `N(-d2_zeta)` with a positive coefficient).

### Stage 8: compute_zeta_vega

Compute `vega` using the normal PDF at `d1_zeta`, spot, `sqrt(T)`, and a zeta correction
factor. The correction is based on the zeta parameter.

### Stage 9: compute_zeta_rho_call

Compute `rho_call` using the alpha parameter, strike, time, rate, `disc_alpha`, and
`N(d2_zeta)`. The alpha parameter introduces additional factors compared to standard BS rho.
Result is positive.

### Stage 10: compute_zeta_rho_put

Compute `rho_put` similarly to `rho_call` but using `N(-d2_zeta)`. Result is negative.

## Required Libraries

```python
import math
from scipy.stats import norm
```

## Expected Output Structure

```python
{
    "case_id": str,
    "d1_zeta": float,
    "d2_zeta": float,
    "disc_alpha": float,
    "call_price": float,
    "put_price": float,
    "delta_call": float,
    "delta_put": float,
    "gamma": float,
    "theta_call": float,
    "theta_put": float,
    "vega": float,
    "rho_call": float,
    "rho_put": float,
}
```

## Sanity Checks (Base Case: S=100, K=100, r=0.05, sigma=0.20, T=1.0, zeta=0.70, alpha=0.85)

- `call_price ≈ 9.716`
- `put_price ≈ 2.179`
- `disc_alpha ≈ 0.9246` (NOT the standard `exp(-rT) ≈ 0.9512`)
- `delta_call ≈ 0.438` (NOT the standard `N(d1) ≈ 0.636`)
- Modified put-call parity: `call_price - put_price ≈ spot - strike * disc_alpha`
- `delta_call` is bounded by zeta (not 1)
- `gamma > 0`, `rho_call > 0`, `rho_put < 0`, `vega > 0`

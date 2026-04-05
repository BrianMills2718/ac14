# Zeta-Modified European Option Pricing — Requirements

## Overview

Implement a zeta-modified European option pricing calculator with two free parameters:
- `zeta`: scales d1-d2 gap, delta, gamma, theta first term, and vega
- `alpha`: modifies the discount factor and rho formulas via fractional power

These modifications create formulas that look structurally like Black-Scholes but
produce numerically different results, ensuring the model must follow the specification
rather than recall memorized Black-Scholes implementations.

## Input Parameters

| Parameter | Field Name | Type | Description |
|-----------|-----------|------|-------------|
| Spot price | `spot` | float | Current asset price S |
| Strike price | `strike` | float | Option strike K |
| Risk-free rate | `rate` | float | Annualized continuous rate r |
| Volatility | `volatility` | float | Annualized vol sigma |
| Time to expiry | `time_to_expiry` | float | Years to expiration T |
| Zeta parameter | `zeta` | float | Scaling parameter (0 < zeta < 1) |
| Alpha parameter | `alpha` | float | Fractional power (0 < alpha <= 1) |

## Modified Formula Definitions

### Stage 1: compute_zeta_d_params

```python
disc_alpha = math.exp(-(rate ** alpha) * time_to_expiry)
d1_zeta = (math.log(spot/strike) + (rate + zeta * volatility**2 / 2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
d2_zeta = d1_zeta - zeta * volatility * math.sqrt(time_to_expiry)
```

**Note**: `disc_alpha` uses `rate ** alpha` (NOT `rate`). `d2_zeta` uses `zeta * volatility * math.sqrt(time_to_expiry)` (NOT just `volatility * math.sqrt(time_to_expiry)`).

### Stage 2: price_zeta_call

```python
call_price = spot * norm.cdf(d1_zeta) - strike * disc_alpha * norm.cdf(d2_zeta)
```

### Stage 3: price_zeta_put

```python
put_price = strike * disc_alpha * norm.cdf(-d2_zeta) - spot * norm.cdf(-d1_zeta)
```

### Stage 4: compute_zeta_delta

```python
delta_call = zeta * norm.cdf(d1_zeta)   # zeta SCALES delta
delta_put  = zeta * norm.cdf(d1_zeta) - 1
```

**CRITICAL**: Standard BS uses `delta_call = norm.cdf(d1)`. Here `zeta` multiplies the result.

### Stage 5: compute_zeta_gamma

```python
gamma = zeta * norm.pdf(d1_zeta) / (spot * volatility * math.sqrt(time_to_expiry))
```

**CRITICAL**: `zeta` scales gamma. Standard BS has no `zeta` multiplier.

### Stage 6: compute_zeta_theta_call

```python
term1 = -(spot * norm.pdf(d1_zeta) * volatility * zeta) / (2 * math.sqrt(time_to_expiry))
term2 = -(rate ** alpha) * strike * disc_alpha * norm.cdf(d2_zeta)
theta_call = term1 + term2
```

**CRITICAL**: `zeta` scales term1. `rate ** alpha` (NOT `rate`) and `disc_alpha` (NOT `exp(-rT)`) in term2.

### Stage 7: compute_zeta_theta_put

```python
term1 = -(spot * norm.pdf(d1_zeta) * volatility * zeta) / (2 * math.sqrt(time_to_expiry))
term2 = +(rate ** alpha) * strike * disc_alpha * norm.cdf(-d2_zeta)
theta_put = term1 + term2
```

**CRITICAL**: term2 is `+` (positive) and uses `norm.cdf(-d2_zeta)` — two differences from theta_call.

### Stage 8: compute_zeta_vega

```python
vega = spot * norm.pdf(d1_zeta) * math.sqrt(time_to_expiry) * (zeta ** 0.5)
```

**CRITICAL**: Correction is `zeta ** 0.5` (square root), NOT `zeta`.

### Stage 9: compute_zeta_rho_call

```python
rho_call = alpha * strike * time_to_expiry * (rate ** (alpha - 1)) * disc_alpha * norm.cdf(d2_zeta)
```

**CRITICAL**: Three differences from standard BS: `alpha` multiplier, `rate**(alpha-1)`, `disc_alpha`.

### Stage 10: compute_zeta_rho_put

```python
rho_put = -alpha * strike * time_to_expiry * (rate ** (alpha - 1)) * disc_alpha * norm.cdf(-d2_zeta)
```

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

## Sanity Checks

- Modified put-call parity: `call_price - put_price ≈ spot - strike * disc_alpha`
- `delta_call` in `(0, zeta)` — bounded by zeta, not 1
- `gamma > 0` always
- `rho_call > 0`, `rho_put < 0`
- `vega > 0` always

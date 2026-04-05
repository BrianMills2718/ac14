# Zeta-Modified Option Pricing: Scale-20 Requirements

## Overview

Extends zeta_options_v1 (10 components) to 20 components by adding second-order Greeks.
All formulas use zeta and alpha modifications defined in zeta_options_v1.

## Parameters

- **zeta** (0 < ζ ≤ 1): Variance scaling parameter
- **alpha** (0 < α ≤ 1): Fractional exponent for discount factor and rho

## Stage 1: Core Parameters (same as v1)

```python
disc_alpha = exp(-(rate**alpha) * time_to_expiry)
d1_zeta = (log(S/K) + (rate + zeta*sigma**2/2)*T) / (sigma*sqrt(T))
d2_zeta = d1_zeta - zeta * sigma * sqrt(T)
```

## Stage 2: First-Order Greeks (same as v1)

```python
call_price = S*N(d1_zeta) - K*disc_alpha*N(d2_zeta)
put_price  = K*disc_alpha*N(-d2_zeta) - S*N(-d1_zeta)
delta_call = zeta * N(d1_zeta)
delta_put  = zeta * N(d1_zeta) - 1.0
gamma      = zeta * N'(d1_zeta) / (S*sigma*sqrt(T))
theta_call = -(S*N'(d1_zeta)*sigma*zeta)/(2*sqrt(T)) - r^alpha*K*disc_alpha*N(d2_zeta)
theta_put  = -(S*N'(d1_zeta)*sigma*zeta)/(2*sqrt(T)) + r^alpha*K*disc_alpha*N(-d2_zeta)
vega       = S * N'(d1_zeta) * sqrt(T) * zeta^0.5
rho_call   = alpha * K * T * r^(alpha-1) * disc_alpha * N(d2_zeta)
rho_put    = -alpha * K * T * r^(alpha-1) * disc_alpha * N(-d2_zeta)
```

## Stage 3: Second-Order Greeks (NEW)

### Intermediate

```python
dd1_dT = (rate + zeta*sigma**2/2) / (sigma*sqrt(T)) - d1_zeta / (2*T)
```

### Volatility Sensitivities

```python
# Vanna: d(delta_call)/d(sigma)
# Key derivation: d(d1_zeta)/d(sigma) = -d2_zeta/sigma
vanna = -zeta * N'(d1_zeta) * d2_zeta / sigma

# Volga (Vomma): d(vega)/d(sigma)
volga = vega * d1_zeta * d2_zeta / sigma

# Ultima: d(volga)/d(sigma)
ultima = -volga/sigma * (d1_zeta*d2_zeta*(1 - d1_zeta*d2_zeta) + d1_zeta**2 + d2_zeta**2)
```

### Time Sensitivities

```python
# Charm (call): d(delta_call)/d(T)
charm_call = zeta * N'(d1_zeta) * dd1_dT

# Charm (put): d(delta_put)/d(T) = charm_call  [since delta_put = delta_call - 1]
charm_put = charm_call

# Veta: d(vega)/d(T)
veta = S * (zeta**0.5) * N'(d1_zeta) * (1/(2*sqrt(T)) - d1_zeta * dd1_dT)

# Color: d(gamma)/d(T)
color = -gamma * (d1_zeta * dd1_dT + 1/(2*T))
```

### Spot Sensitivity

```python
# Speed: d(gamma)/d(S)
speed = -gamma * (1 + d1_zeta / (sigma * sqrt(T))) / S
```

### Mixed Sensitivities

```python
# Zomma: d(gamma)/d(sigma)
zomma = gamma * (d1_zeta * d2_zeta - 1) / sigma
```

### Strike Sensitivities

```python
# Dual delta (call): d(call_price)/d(K)
dual_delta_call = -disc_alpha * N(d2_zeta)

# Dual delta (put): d(put_price)/d(K)
dual_delta_put = disc_alpha * N(-d2_zeta)
```

## Reference Values (Base Case: S=K=100, r=0.05, σ=0.20, T=1.0, ζ=0.70, α=0.85)

| Field | Value |
|-------|-------|
| d1_zeta | 0.32 |
| d2_zeta | 0.18 |
| disc_alpha | 0.9246264814 |
| call_price | 9.7162334886 |
| put_price | 2.1788816313 |
| delta_call | 0.4378610843 |
| gamma | 0.0132660684 |
| vega | 31.7119690068 |
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
| ultima | -8.6344849939 |

# Zeta Scale-40: Dual-Option Portfolio Requirements

## System Overview

A 40-component pipeline computing a portfolio of two independent zeta-modified
European options. Each option uses the zeta/alpha modifications to standard
Black-Scholes formulas.

## Input

`portfolio_request` — flat record with all fields for both options:
- `case_id`: benchmark case identifier
- Option A fields: `spot_a`, `strike_a`, `rate_a`, `vol_a`, `T_a`, `zeta_a`, `alpha_a`
- Option B fields: `spot_b`, `strike_b`, `rate_b`, `vol_b`, `T_b`, `zeta_b`, `alpha_b`

## Output

`portfolio_results` — complete Greek surfaces for both options plus portfolio-level Greeks.

## Key Formulas

For each option (A or B):

```
disc_alpha = exp(-(rate**alpha) * T)          # NOT exp(-rate*T)
d1_zeta = (log(S/K) + (rate + zeta*sigma^2/2)*T) / (sigma*sqrt(T))
d2_zeta = d1_zeta - zeta*sigma*sqrt(T)        # zeta scales the d1-d2 gap
dd1_dT  = (rate + zeta*sigma^2/2)/(sigma*sqrt(T)) - d1_zeta/(2*T)

call = S*N(d1_zeta) - K*disc_alpha*N(d2_zeta)
put  = K*disc_alpha*N(-d2_zeta) - S*N(-d1_zeta)

delta_call = zeta*N(d1_zeta)                  # NOT N(d1_zeta) alone
delta_put  = zeta*N(d1_zeta) - 1
gamma = zeta*N'(d1_zeta) / (S*sigma*sqrt(T))
vega  = S*N'(d1_zeta)*sqrt(T)*(zeta**0.5)     # NOT zeta alone
theta_call = -(S*N'(d1)*sigma*zeta)/(2*sqrt(T)) - (rate**alpha)*K*disc_alpha*N(d2)
theta_put  = -(S*N'(d1)*sigma*zeta)/(2*sqrt(T)) + (rate**alpha)*K*disc_alpha*N(-d2)
rho_call = alpha*K*T*(rate**(alpha-1))*disc_alpha*N(d2)
rho_put  = -alpha*K*T*(rate**(alpha-1))*disc_alpha*N(-d2)
vanna = -zeta*N'(d1)*d2/sigma
volga = vega*d1*d2/sigma
charm = zeta*N'(d1)*dd1_dT
veta  = S*(zeta**0.5)*N'(d1)*(1/(2*sqrt(T)) - d1*dd1_dT)
speed = -gamma*(1 + d1/(sigma*sqrt(T)))/S
zomma = gamma*(d1*d2 - 1)/sigma
color = -gamma*(d1*dd1_dT + 1/(2*T))
dual_delta_call = -disc_alpha*N(d2)
dual_delta_put  = disc_alpha*N(-d2)
ultima = -volga/sigma*(d1*d2*(1-d1*d2) + d1^2 + d2^2)
```

## Portfolio Greeks

```
portfolio_delta = delta_call_a + delta_call_b
portfolio_gamma = gamma_a + gamma_b
portfolio_vega  = vega_a + vega_b
portfolio_theta = theta_call_a + theta_call_b
portfolio_rho   = rho_call_a + rho_call_b
```

## Critical Differences from Standard Black-Scholes

1. `disc_alpha = exp(-r^alpha * T)` not `exp(-r*T)`
2. `delta_call = zeta * N(d1)` not `N(d1)`
3. `vega = S*N'(d1)*sqrt(T)*zeta^0.5` not `S*N'(d1)*sqrt(T)`
4. `rho_call = alpha*K*T*r^(alpha-1)*disc_alpha*N(d2)` not `K*T*exp(-rT)*N(d2)`

## Dependencies

- `scipy.stats.norm` for CDF (`norm.cdf`) and PDF (`norm.pdf`)
- `math` for `log`, `sqrt`, `exp`

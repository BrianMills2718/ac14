# Black-Scholes Option Pricing and Greeks

Implement a system that prices European call and put options using the Black-Scholes formula
and computes all five first-order Greeks (delta, gamma, theta, vega, rho).

## Input

A `bs_request` with fields: `case_id` (str), `spot` (float), `strike` (float),
`rate` (float), `volatility` (float), `time_to_expiry` (float).

## Output

A `bs_results` with all computed values (see workflow hints for field details).

## Components

The system decomposes into 10 pipeline components:

1. `compute_d_parameters` — compute d1, d2, and discount factor
2. `price_vanilla_call` — call price using S*N(d1) - K*e^(-rT)*N(d2)
3. `price_vanilla_put` — put price using K*e^(-rT)*N(-d2) - S*N(-d1)
4. `compute_delta` — delta for call (N(d1)) and put (N(d1) - 1)
5. `compute_gamma` — gamma = N'(d1) / (S*sigma*sqrt(T)), same for call and put
6. `compute_theta_call` — theta for call only
7. `compute_theta_put` — theta for put only (different formula from call)
8. `compute_vega` — vega = S*N'(d1)*sqrt(T), same for call and put
9. `compute_rho_call` — rho for call = K*T*e^(-rT)*N(d2)
10. `compute_rho_put` (terminal) — rho for put = -K*T*e^(-rT)*N(-d2), assembles final output

## Key Distinctions

- Theta call and theta put have different second terms (sign and N() argument differ)
- Rho call uses N(d2); rho put uses -N(-d2) (leading minus AND flipped N() argument)
- Delta put = N(d1) - 1, NOT -N(-d1) (though mathematically equal, use the d1-based form)
- Gamma and vega are identical for call and put
- All formulas depend on d1 and d2 computed in stage 1

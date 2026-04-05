# Prospect Theory Utility Suite — Benchmark Requirements

## Overview

Implement Tversky & Kahneman's (1992) cumulative prospect theory as a five-component
pipeline. Each component implements exactly one operation in the prospect evaluation
process. All computations use Python's standard `**` operator for exponentiation.

## Parameters

The following parameters are fixed for all computations and passed through the pipeline:

| Parameter | Symbol | Value | Role |
|-----------|--------|-------|------|
| alpha | α | 0.88 | Value function curvature (gains) |
| beta | β | 0.88 | Value function curvature (losses) |
| lambda_loss_aversion | λ | 2.25 | Loss aversion coefficient |
| gamma_gains | γ | 0.61 | Probability weighting curvature (gains) |
| delta_losses | δ | 0.69 | Probability weighting curvature (losses) |

Note: α and β happen to be equal in the standard parameterization, but they are
**distinct parameters** with distinct roles and must NOT be treated as the same value.

## Formulas

### 1. apply_reference_point

Subtract the `reference_point` from each outcome value. Classify each outcome as a
gain (net ≥ 0) or loss (net < 0).

```
net_value_i = outcome_value_i - reference_point
is_gain_i   = (net_value_i >= 0)
```

- `outcomes`: list of `{outcome_value, probability}` pairs
- `reference_point`: float (default 0.0)
- Result: list of `{net_value, probability, is_gain}` triples

### 2. compute_value_function

Apply the piecewise value function to each `net_value`:

```
v(x) = x^α                    if x >= 0   (gains)
v(x) = -λ * ((-x)^β)         if x < 0    (losses)
```

**Critical constraints:**
- For gains: `x^alpha` where `x >= 0`. When `x == 0`, `v(0) = 0` (gains branch gives 0^0.88 = 0 ✓).
- For losses: the argument to the exponent is `(-x)`, not `x`. Since `x < 0`, `(-x) > 0`.
  Do NOT compute `x^beta` when x is negative — use `((-x)**beta)`.
- The result for losses is **negative**: `-lambda_loss_aversion * ((-x)**beta)`.

Result: each adjusted outcome gains a `utility_value` field.

### 3. apply_probability_weighting

Apply the Tversky-Kahneman (1992) one-parameter weighting function. Gains and losses use
**different** parameter values.

For gain outcomes (`is_gain == True`), use `gamma_gains`:
```
w+(p) = p^γ / (p^γ + (1-p)^γ)^(1/γ)
```

For loss outcomes (`is_gain == False`), use `delta_losses`:
```
w-(p) = p^δ / (p^δ + (1-p)^δ)^(1/δ)
```

**Edge cases (handle explicitly):**
- `p == 0.0` → `w(0) = 0.0`
- `p == 1.0` → `w(1) = 1.0`

Result: each outcome gains a `decision_weight` field. The weighted utility
`weighted_utility = decision_weight * utility_value` is also computed here.

### 4. compute_prospect_utility

Sum all `weighted_utility` values to produce the overall prospect utility `V`:

```
V = Σ weighted_utility_i   (sum over all outcomes)
```

This is a simple summation. The complexity is in the upstream components.

Result: a single `prospect_utility` float.

### 5. compute_certainty_equivalent

Invert the prospect utility to a monetary certainty equivalent. The inversion is
**sign-dependent** on `V`:

```
if V >= 0:
    CE = V^(1/α) + reference_point

if V < 0:
    CE = -((-V / λ)^(1/β)) + reference_point
```

**Critical constraints:**
- For `V >= 0`: use `alpha` in the exponent.
- For `V < 0`: use `beta` in the exponent and `lambda_loss_aversion` to rescale.
  The argument `(-V / lambda_loss_aversion)` is positive since `V < 0`.
- Always **add `reference_point`** to the result. Forgetting this step gives the
  wrong CE whenever the reference point is non-zero.

Result: `certainty_equivalent` float.

## Pipeline Structure

```
prospect_theory_request
  → apply_reference_point          → reference_adjusted_output
  → compute_value_function         → valued_outcomes_output
  → apply_probability_weighting    → weighted_outcomes_output
  → compute_prospect_utility       → prospect_utility_output
  → compute_certainty_equivalent   → prospect_theory_results
```

## Test Cases

Parameters for all cases: α=0.88, β=0.88, λ=2.25, γ=0.61, δ=0.69

| case_id | outcomes | ref | prospect_utility | certainty_equivalent |
|---------|----------|-----|------------------|---------------------|
| mixed_lottery | [(100, 0.5), (-50, 0.5)] | 0.0 | -7.733639713710360 | -4.067427239812672 |
| all_gains | [(200, 0.3), (100, 0.7)] | 0.0 | 64.434060657731621 | 113.713773112445139 |
| all_losses | [(-100, 0.4), (-30, 0.6)] | 0.0 | -73.960652207898121 | -52.924536287148676 |
| with_reference | [(150, 0.6), (-20, 0.4)] | 50.0 | -9.781086307192847 | 44.688313077011543 |
| certain_gain | [(100, 1.0)] | 0.0 | 57.543993733715695 | 100.00000000000004 |

The `certain_gain` CE ≈ 100.0. Python floating-point arithmetic gives `100.00000000000004`
for `(100.0**0.88)**(1/0.88)` — a tiny rounding error from the two-step exponentiation.

Expected values are exact Python float results — no rounding or tolerance. Any correct
implementation using Python's `**` operator will produce these exact values.

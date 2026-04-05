# Plan #153: Theory Forge — Prospect Theory Benchmark

**Status:** In Progress
**Type:** implementation
**Priority:** High
**Blocked By:** 152
**Blocks:** 154

---

## Goal

Implement the second Theory Forge benchmark: Prospect Theory (Tversky & Kahneman 1992).
Five components, 5 runtime cases, all deterministic math with exact Python float outputs.

**Hypothesis:** The piecewise value function, dual probability weighting functions (w+ vs w-),
and sign-dependent CE inversion create enough context pressure that monolithic mishandles
at least one component while AC14 isolates each formula correctly.

The key traps that distinguish this from Information Theory:
1. Value function has DIFFERENT exponents for gains vs losses: `v(x) = x^α` vs `v(x) = -λ(-x)^β`
2. Two probability weighting functions with DIFFERENT parameters: w+ uses γ, w- uses δ
3. CE inversion is sign-dependent: `V≥0 → CE = V^(1/α) + ref` vs `V<0 → CE = -(|V|/λ)^(1/β) + ref`
4. Reference point must be subtracted BEFORE value function, then RE-ADDED to CE

---

## Parameters (Tversky & Kahneman 1992)

| Parameter | Value | Role |
|-----------|-------|------|
| α (alpha) | 0.88 | Value function curvature — gains |
| β (beta) | 0.88 | Value function curvature — losses |
| λ (lambda) | 2.25 | Loss aversion coefficient |
| γ (gamma) | 0.61 | Probability weighting curvature — gains |
| δ (delta) | 0.69 | Probability weighting curvature — losses |

Note: α = β in the standard parameterization, but they are SEPARATE parameters with
separate roles. Monolithic is likely to treat them as interchangeable.

---

## Formulas

### 1. apply_reference_point
Subtracts `reference_point` from each outcome value. Classifies each as gain (net ≥ 0) or loss (net < 0).

```
net_value_i = outcome_value_i - reference_point
is_gain_i = (net_value_i >= 0)
```

### 2. compute_value_function
Applies piecewise value function to each net outcome:
```
v(x) = x^α                    if x >= 0  (gains)
v(x) = -λ * ((-x)^β)         if x < 0   (losses)
```
**Critical:** 0 * anything = 0 (x=0 maps to v(0)=0 correctly via the gains branch).
**Critical:** Use `(-x)` not `x` inside the exponent for losses, since x < 0.

### 3. apply_probability_weighting
Applies Tversky-Kahneman (1992) weighting function separately for gains and losses:
```
w+(p) = p^γ / (p^γ + (1-p)^γ)^(1/γ)    for gains
w-(p) = p^δ / (p^δ + (1-p)^δ)^(1/δ)    for losses
```
**Critical:** Gains use γ, losses use δ. These are DIFFERENT parameters.
**Edge cases:** w(0) = 0, w(1) = 1 (handle explicitly to avoid 0^γ issues).

### 4. compute_prospect_utility
Sums all decision_weight × utility_value products:
```
V = Σ decision_weight_i × utility_value_i
```
This is a simple sum — the complexity is in the upstream components.

### 5. compute_certainty_equivalent
Inverts the prospect utility to a monetary value:
```
if V >= 0:
    CE = V^(1/α) + reference_point
if V < 0:
    CE = -((-V / λ)^(1/β)) + reference_point
```
**Critical:** The inverse depends on the SIGN of V. Use α for gains, β for losses, λ for rescaling losses.
**Critical:** Add `reference_point` back at the end.

---

## Pipeline Structure

```
prospect_theory_request
  → apply_reference_point          → reference_adjusted_output
  → compute_value_function         → valued_outcomes_output
  → apply_probability_weighting    → weighted_outcomes_output
  → compute_prospect_utility       → prospect_utility_output
  → compute_certainty_equivalent   → prospect_theory_results
```

Each stage passes accumulated values to the next. Final output `prospect_theory_results`
contains `prospect_utility` and `certainty_equivalent`.

---

## Runtime Test Cases

All values computed with Python `**` operator and standard float arithmetic.

| case_id | outcomes | ref | V | CE |
|---------|----------|-----|---|-----|
| `mixed_lottery` | [(100, 0.5), (-50, 0.5)] | 0.0 | -7.733639713710360 | -4.067427239812672 |
| `all_gains` | [(200, 0.3), (100, 0.7)] | 0.0 | 64.434060657731621 | 113.713773112445139 |
| `all_losses` | [(-100, 0.4), (-30, 0.6)] | 0.0 | -73.960652207898121 | -52.924536287148676 |
| `with_reference` | [(150, 0.6), (-20, 0.4)] | 50.0 | -9.781086307192847 | 44.688313077011543 |
| `certain_gain` | [(100, 1.0)] | 0.0 | 57.543993733715695 | 100.0 |

`certain_gain` CE is exactly 100.0 because v^{-1}(v(100)) = 100 (round-trips exactly).

---

## Key Traps Summary

| Component | Trap | Wrong approach | Right approach |
|-----------|------|---------------|---------------|
| apply_reference_point | Applying gains formula to net=0 | Crash or skip | v(0)=0 via gains branch |
| compute_value_function | Loss formula sign | `-λ * x^β` (wrong sign inside exp) | `-λ * (-x)^β` |
| apply_probability_weighting | Parameter confusion | w(p) = p^γ for all outcomes | w+(p) uses γ, w-(p) uses δ |
| compute_certainty_equivalent | CE inversion branch | One formula for all V | Different formula for V≥0 vs V<0 |
| compute_certainty_equivalent | Reference restoration | Forget to add reference_point | CE = inverse(V) + reference_point |

---

## Files to Create

```
benchmarks/prospect_theory_tk1992/
├── structured_spec_input.yaml      # Hand-authored AC14 spec
├── runtime_cases.json              # 5 golden test cases
├── expected_runtime_outputs.json   # Exact expected outputs
├── requirements.md                 # Human-readable spec with formulas
├── benchmark.yaml                  # StructuredSpecBenchmarkConfig
└── back_half/
    └── benchmark.yaml              # BenchmarkConfig (for runtime harness)
    └── blueprint/                  # 6-file blueprint bundle
        ├── metadata.yaml
        ├── schemas.yaml
        ├── components.yaml
        ├── architecture.yaml
        ├── validation.yaml
        └── fixtures.yaml
```

---

## Implementation Steps

1. Write `requirements.md` — formulas, parameters, pipeline description, test cases
2. Write `structured_spec_input.yaml` — 5 workflow hints with exact formula business rules
3. Write `runtime_cases.json` — 5 cases with all parameters
4. Write `expected_runtime_outputs.json` — exact Python float outputs
5. Write `benchmark.yaml` and `back_half/benchmark.yaml`
6. Write `back_half/blueprint/` — 6-file blueprint bundle
7. Smoke gate: `make front-half-first-smoke-gate BENCHMARK=benchmarks/prospect_theory_tk1992 OUTPUT=.ac14_out/pt_smoke_1 MAX_ATTEMPTS=3 MAX_BUDGET=1.50`
8. If `ready_for_full_trials`: `make front-half-first-full-trials BENCHMARK=benchmarks/prospect_theory_tk1992 OUTPUT=.ac14_out/pt_gate_1 TRIALS=5 MAX_ATTEMPTS=3 MAX_BUDGET=1.50`
9. Read verdict and write Plan #154

---

## Smoke-Gate Command

```bash
make front-half-first-smoke-gate \
  BENCHMARK=benchmarks/prospect_theory_tk1992 \
  OUTPUT=.ac14_out/pt_smoke_1 \
  MAX_ATTEMPTS=3 MAX_BUDGET=1.50
```

## Full Trial Command

```bash
make front-half-first-full-trials \
  BENCHMARK=benchmarks/prospect_theory_tk1992 \
  OUTPUT=.ac14_out/pt_gate_1 \
  TRIALS=5 MAX_ATTEMPTS=3 MAX_BUDGET=1.50
```

---

## Acceptance Criteria

- [ ] `requirements.md` written with all 5 formulas and exact parameter values
- [ ] `structured_spec_input.yaml` written with 5 workflow hints, explicit trap notes in business_rules
- [ ] `runtime_cases.json` has 5 cases with outcomes list and all parameters
- [ ] `expected_runtime_outputs.json` has exact Python float values
- [ ] `benchmark.yaml` and `back_half/benchmark.yaml` valid
- [ ] `back_half/blueprint/` has all 6 YAML files
- [ ] Smoke gate passes (`ready_for_full_trials`)
- [ ] Gate_1 full trial run complete with persisted verdict artifact
- [ ] Plan #154 written with verdict results

---

## References

- `docs/plans/152_it_gate_1_verdict.md` — motivation
- `benchmarks/information_theory_shannon/` — format reference for all files
- Tversky, A., & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297–323.

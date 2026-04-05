# Plan #161: Harder Benchmark Design — Portfolio Risk Decomposition (20 Components)

**Status**: Active  
**Started**: 2026-04-04

---

## Context

All Theory Forge benchmarks (IT, PT, BS) with both gpt-4.1 and Gemini flash show monolithic
competitive or winning. Root cause: known mathematical formulas are memorized in training data.
Neither 4, 5, nor 10 components stresses monolithic's context capacity.

**Hypothesis for this plan**: A 20-component benchmark with:
1. Matrix operations requiring shared intermediate results across components
2. Formulas that are less commonly implemented end-to-end (Cholesky, portfolio attribution, CVaR decomposition)
3. Cross-component data flow dependencies that stress monolithic coordination

**Target**: monolithic fails ≥1/5 with gpt-4.1 due to context coordination errors.

---

## Benchmark: Portfolio Risk Decomposition System

### Domain

Markowitz portfolio theory + risk decomposition. ~20 components that pipeline from raw returns
to attribution. Each component is mathematically well-defined but requires correct shared
intermediate values (covariance matrix, Cholesky factor, portfolio weights) flowing through.

### Design Rationale

- **Context stress**: The covariance matrix is a shared intermediate that must be consistent
  across 6+ downstream components. Monolithic code must maintain this coherence globally.
- **Formula complexity**: Cholesky decomposition, eigenvalue-based correlation, Cornish-Fisher
  CVaR expansion, marginal risk contribution — less commonly memorized as end-to-end pipelines.
- **Cross-component invariants**: Sum of risk contributions must equal total portfolio risk.
  If one component gets the Cholesky factor wrong, downstream attribution is silently wrong.
- **20 components**: Large enough to stress context capacity for Gemini flash.

### Components (20 total)

1. `compute_return_moments` — mean, variance from return series
2. `compute_covariance_matrix` — covariance from returns matrix (NxN)
3. `compute_cholesky_factor` — Cholesky L such that L@L.T = Sigma
4. `compute_correlation_matrix` — Corr from Cov and std devs
5. `compute_eigenvalues_eigenvectors` — EVD of correlation matrix
6. `compute_portfolio_variance` — w.T @ Sigma @ w
7. `compute_portfolio_volatility` — sqrt of portfolio variance
8. `compute_sharpe_ratio` — (return - rf) / volatility
9. `compute_var_parametric` — parametric VaR at confidence level
10. `compute_cvar_cornish_fisher` — CVaR with skewness/kurtosis correction via Cornish-Fisher expansion
11. `compute_marginal_risk_contribution` — dσ/dw_i = (Sigma @ w)_i / σ_portfolio
12. `compute_component_risk_contribution` — w_i * MRC_i (must sum to σ_portfolio)
13. `compute_risk_parity_weights` — equal risk contribution weights (iterative)
14. `compute_minimum_variance_weights` — min w.T @ Sigma @ w s.t. sum(w)=1
15. `compute_maximum_sharpe_weights` — tangency portfolio weights
16. `compute_diversification_ratio` — sum(w_i * σ_i) / σ_portfolio
17. `compute_effective_n` — 1 / sum(w_i^2) (portfolio concentration)
18. `compute_tracking_error` — volatility of (portfolio - benchmark) returns
19. `compute_information_ratio` — active return / tracking error
20. `compute_attribution_summary` — structured dict of all metrics for output

### Key Cross-Component Dependencies (stress points)

- `compute_cholesky_factor` → `compute_cvar_cornish_fisher`, `compute_component_risk_contribution`
- `compute_marginal_risk_contribution` → `compute_component_risk_contribution` (must use same Sigma@w)
- `compute_minimum_variance_weights` → needs Sigma; output must satisfy w.T@Sigma@w ≤ any other w
- Risk attribution invariant: sum(component_risk) == portfolio_volatility (up to float tol)

### Test Case Design

Use 4 assets (manageable but non-trivial matrix math):
- Assets: equity_growth, equity_value, bonds_ig, bonds_hy
- Covariance matrix: realistic but specified exactly in fixture
- Expected outputs: computed analytically and verified with scipy

---

## Acceptance Criteria

1. Blueprint bundle validates B1 with 0 errors
2. Runtime expected outputs match Python scipy/numpy reference implementation exactly
3. Gate runs 5 trials with gpt-4.1 — at least 1 monolithic failure expected
4. If monolithic passes 5/5, run Gemini flash gate next

---

## Implementation Steps

### Step 1: Reference Implementation (Python)
Write `benchmarks/portfolio_risk/reference_impl.py` — scipy/numpy ground truth.
Verify Cholesky, risk contribution, CVaR, attribution numerics.

### Step 2: Benchmark Bundle
Create `benchmarks/portfolio_risk/` with:
- `structured_spec.yaml` — 20-component spec with business rules for each
- `schemas/` — typed schemas for all intermediate ports
- `blueprints/architecture.yaml`, `components.yaml`, `schemas.yaml`, `fixtures.yaml`, `validation.yaml`, `scenarios.yaml`
- `expected_runtime_outputs.json` — full float precision from reference impl

### Step 3: Gate Execution
Run `make front-half-first-full-trials BENCHMARK=benchmarks/portfolio_risk MODEL=openai/gpt-4.1`
Write Plan #162 as the verdict.

---

## Files to Create

- `benchmarks/portfolio_risk/reference_impl.py`
- `benchmarks/portfolio_risk/structured_spec.yaml`
- `benchmarks/portfolio_risk/schemas/*.yaml`
- `benchmarks/portfolio_risk/blueprints/*.yaml`
- `benchmarks/portfolio_risk/expected_runtime_outputs.json`


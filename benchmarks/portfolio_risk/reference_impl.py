"""Reference implementation for Portfolio Risk Decomposition benchmark.

Computes all 20 components of the portfolio risk pipeline from raw returns
to full attribution. Used to generate expected_runtime_outputs.json.
"""

import json
import math
import numpy as np
from scipy.stats import norm


# --- Test inputs ---
# 4 assets: equity_growth, equity_value, bonds_ig, bonds_hy
ASSET_NAMES = ["equity_growth", "equity_value", "bonds_ig", "bonds_hy"]

# Annualized return series (simplified: these are the underlying stats)
# We'll use a pre-computed covariance matrix and means to avoid depending on
# a full return time series in the benchmark input.

ANNUAL_RETURNS = np.array([0.12, 0.10, 0.04, 0.07])  # expected annual returns
RISK_FREE_RATE = 0.02

# Annualized covariance matrix (realistic correlation structure)
# Constructed so that Cholesky decomposition is well-conditioned
ANNUAL_VOLS = np.array([0.20, 0.18, 0.05, 0.12])  # annual volatilities

# Correlation matrix
CORR = np.array([
    [1.00,  0.85,  0.10,  0.25],
    [0.85,  1.00,  0.08,  0.22],
    [0.10,  0.08,  1.00,  0.45],
    [0.25,  0.22,  0.45,  1.00],
])

# Cov = diag(vols) @ Corr @ diag(vols)
SIGMA = np.diag(ANNUAL_VOLS) @ CORR @ np.diag(ANNUAL_VOLS)

# Initial portfolio weights (equal weight)
WEIGHTS = np.array([0.25, 0.25, 0.25, 0.25])

# Benchmark weights for tracking error
BENCHMARK_WEIGHTS = np.array([0.30, 0.30, 0.20, 0.20])

CONFIDENCE_LEVEL = 0.95
N_ASSETS = 4


def compute_return_moments(returns_vector):
    """Mean and variance of a return series."""
    mean = float(np.mean(returns_vector))
    variance = float(np.var(returns_vector, ddof=1))
    return {"mean": mean, "variance": variance}


def compute_covariance_matrix(sigma):
    """Return covariance matrix as nested list."""
    return sigma.tolist()


def compute_cholesky_factor(sigma):
    """Cholesky L such that L @ L.T = Sigma."""
    L = np.linalg.cholesky(sigma)
    return L.tolist()


def compute_correlation_matrix(sigma):
    """Correlation matrix from covariance."""
    stds = np.sqrt(np.diag(sigma))
    corr = sigma / np.outer(stds, stds)
    return corr.tolist()


def compute_eigenvalues_eigenvectors(corr):
    """Eigenvalues and eigenvectors of correlation matrix."""
    corr_arr = np.array(corr)
    eigenvalues, eigenvectors = np.linalg.eigh(corr_arr)
    # Sort descending
    idx = np.argsort(eigenvalues)[::-1]
    return {
        "eigenvalues": eigenvalues[idx].tolist(),
        "eigenvectors": eigenvectors[:, idx].tolist(),
    }


def compute_portfolio_variance(weights, sigma):
    """w.T @ Sigma @ w"""
    w = np.array(weights)
    s = np.array(sigma)
    return float(w @ s @ w)


def compute_portfolio_volatility(portfolio_variance):
    """sqrt(portfolio_variance)"""
    return float(math.sqrt(portfolio_variance))


def compute_sharpe_ratio(portfolio_return, portfolio_volatility, risk_free_rate):
    """(return - rf) / vol"""
    return float((portfolio_return - risk_free_rate) / portfolio_volatility)


def compute_portfolio_return(weights, expected_returns):
    """w.T @ mu"""
    return float(np.array(weights) @ np.array(expected_returns))


def compute_var_parametric(portfolio_volatility, confidence_level):
    """Parametric VaR: z * sigma (positive = loss)"""
    z = norm.ppf(confidence_level)
    return float(z * portfolio_volatility)


def compute_cvar_cornish_fisher(portfolio_volatility, portfolio_skewness, portfolio_excess_kurtosis, confidence_level):
    """CVaR with Cornish-Fisher expansion for non-normality."""
    alpha = 1 - confidence_level
    z = norm.ppf(1 - alpha)
    # Cornish-Fisher adjusted z
    skew = portfolio_skewness
    kurt = portfolio_excess_kurtosis
    z_cf = (z
            + (z**2 - 1) * skew / 6
            + (z**3 - 3*z) * kurt / 24
            - (2*z**3 - 5*z) * skew**2 / 36)
    # CVaR via integration: E[loss | loss > VaR]
    # For CF expansion: CVaR ≈ -mu - sigma * z_cf (simplified; assume zero mean portfolio)
    cvar = float(portfolio_volatility * z_cf)
    return cvar


def compute_marginal_risk_contribution(weights, sigma, portfolio_volatility):
    """dσ/dw_i = (Sigma @ w)_i / σ_portfolio"""
    w = np.array(weights)
    s = np.array(sigma)
    sigma_w = s @ w
    mrc = sigma_w / portfolio_volatility
    return mrc.tolist()


def compute_component_risk_contribution(weights, marginal_risk_contributions):
    """CRC_i = w_i * MRC_i. Must sum to portfolio_volatility."""
    w = np.array(weights)
    mrc = np.array(marginal_risk_contributions)
    crc = w * mrc
    return {
        "contributions": crc.tolist(),
        "total": float(np.sum(crc)),
    }


def compute_risk_parity_weights(sigma, n_iter=1000, tol=1e-8):
    """Equal risk contribution weights via iterative algorithm."""
    s = np.array(sigma)
    n = len(s)
    w = np.ones(n) / n
    for _ in range(n_iter):
        sigma_w = s @ w
        port_vol = math.sqrt(float(w @ sigma_w))
        mrc = sigma_w / port_vol
        crc = w * mrc
        # Newton step
        grad = mrc - (1/n) * port_vol
        w_new = w - 0.01 * grad
        w_new = np.maximum(w_new, 1e-8)
        w_new = w_new / np.sum(w_new)
        if np.max(np.abs(w_new - w)) < tol:
            w = w_new
            break
        w = w_new
    return w.tolist()


def compute_minimum_variance_weights(sigma):
    """min w.T@Sigma@w s.t. sum(w)=1, w>=0 via analytical unconstrained solution."""
    s = np.array(sigma)
    inv_sigma = np.linalg.inv(s)
    ones = np.ones(len(s))
    w = inv_sigma @ ones / (ones @ inv_sigma @ ones)
    # Project to simplex (ensure non-negative)
    w = np.maximum(w, 0)
    w = w / np.sum(w)
    return w.tolist()


def compute_maximum_sharpe_weights(sigma, expected_returns, risk_free_rate):
    """Tangency portfolio (maximum Sharpe) weights."""
    s = np.array(sigma)
    mu = np.array(expected_returns) - risk_free_rate
    inv_sigma = np.linalg.inv(s)
    w = inv_sigma @ mu
    w = np.maximum(w, 0)
    if np.sum(w) < 1e-12:
        return np.ones(len(s)) / len(s)
    w = w / np.sum(w)
    return w.tolist()


def compute_diversification_ratio(weights, sigma):
    """sum(w_i * sigma_i) / sigma_portfolio"""
    w = np.array(weights)
    s = np.array(sigma)
    vols = np.sqrt(np.diag(s))
    weighted_vol = float(w @ vols)
    port_var = float(w @ s @ w)
    port_vol = math.sqrt(port_var)
    return float(weighted_vol / port_vol)


def compute_effective_n(weights):
    """1 / sum(w_i^2) — inverse Herfindahl index."""
    w = np.array(weights)
    return float(1.0 / np.sum(w**2))


def compute_tracking_error(weights, benchmark_weights, sigma):
    """Volatility of active return: sigma of (w - w_b)."""
    active = np.array(weights) - np.array(benchmark_weights)
    s = np.array(sigma)
    return float(math.sqrt(float(active @ s @ active)))


def compute_information_ratio(active_return, tracking_error):
    """active_return / tracking_error"""
    return float(active_return / tracking_error)


def compute_attribution_summary(
    portfolio_return,
    portfolio_volatility,
    portfolio_variance,
    sharpe_ratio,
    var_parametric,
    cvar_cornish_fisher,
    component_risk_contributions,
    diversification_ratio,
    effective_n,
    tracking_error,
    information_ratio,
):
    """Collect all metrics into a structured output dict."""
    return {
        "portfolio_return": portfolio_return,
        "portfolio_volatility": portfolio_volatility,
        "portfolio_variance": portfolio_variance,
        "sharpe_ratio": sharpe_ratio,
        "var_parametric": var_parametric,
        "cvar_cornish_fisher": cvar_cornish_fisher,
        "component_risk_contributions": component_risk_contributions["contributions"],
        "risk_contribution_total": component_risk_contributions["total"],
        "diversification_ratio": diversification_ratio,
        "effective_n": effective_n,
        "tracking_error": tracking_error,
        "information_ratio": information_ratio,
    }


if __name__ == "__main__":
    # Compute all intermediate values in pipeline order
    sigma = SIGMA
    weights = WEIGHTS
    bm_weights = BENCHMARK_WEIGHTS
    mu = ANNUAL_RETURNS
    rf = RISK_FREE_RATE
    cl = CONFIDENCE_LEVEL

    cov_matrix = compute_covariance_matrix(sigma)
    cholesky = compute_cholesky_factor(sigma)
    corr_matrix = compute_correlation_matrix(sigma)
    eig = compute_eigenvalues_eigenvectors(corr_matrix)
    port_var = compute_portfolio_variance(weights, cov_matrix)
    port_vol = compute_portfolio_volatility(port_var)
    port_ret = compute_portfolio_return(weights, mu)
    sharpe = compute_sharpe_ratio(port_ret, port_vol, rf)
    var_p = compute_var_parametric(port_vol, cl)

    # For CVaR: use approximate portfolio skewness/kurtosis (near-normal for equal weights)
    skewness = 0.0  # assume symmetric for initial test case
    excess_kurt = 0.0
    cvar_cf = compute_cvar_cornish_fisher(port_vol, skewness, excess_kurt, cl)

    mrc = compute_marginal_risk_contribution(weights, cov_matrix, port_vol)
    crc = compute_component_risk_contribution(weights, mrc)
    rp_weights = compute_risk_parity_weights(cov_matrix)
    mv_weights = compute_minimum_variance_weights(cov_matrix)
    ms_weights = compute_maximum_sharpe_weights(cov_matrix, mu, rf)
    div_ratio = compute_diversification_ratio(weights, cov_matrix)
    eff_n = compute_effective_n(weights)
    te = compute_tracking_error(weights, bm_weights, cov_matrix)
    active_ret = float(np.array(weights) @ mu - np.array(bm_weights) @ mu)
    ir = compute_information_ratio(active_ret, te)
    summary = compute_attribution_summary(
        port_ret, port_vol, port_var, sharpe, var_p, cvar_cf,
        crc, div_ratio, eff_n, te, ir
    )

    # Build the expected runtime outputs
    outputs = {
        "return_moments": {"mean": float(np.mean(mu)), "variance": float(np.var(mu, ddof=1))},
        "covariance_matrix": cov_matrix,
        "cholesky_factor": cholesky,
        "correlation_matrix": corr_matrix,
        "eigenvalues_eigenvectors": eig,
        "portfolio_variance": port_var,
        "portfolio_volatility": port_vol,
        "portfolio_return": port_ret,
        "sharpe_ratio": sharpe,
        "var_parametric": var_p,
        "cvar_cornish_fisher": cvar_cf,
        "marginal_risk_contributions": mrc,
        "component_risk_contributions": crc,
        "risk_parity_weights": rp_weights,
        "minimum_variance_weights": mv_weights,
        "maximum_sharpe_weights": ms_weights,
        "diversification_ratio": div_ratio,
        "effective_n": eff_n,
        "tracking_error": te,
        "information_ratio": ir,
        "attribution_summary": summary,
    }

    print(json.dumps(outputs, indent=2))

    # Verify the key invariant: sum of CRC == portfolio volatility
    crc_total = sum(crc["contributions"])
    assert abs(crc_total - port_vol) < 1e-10, f"CRC sum {crc_total} != port_vol {port_vol}"
    import sys
    print(f"\nInvariant check: CRC sum ({crc_total:.8f}) == port_vol ({port_vol:.8f}): OK", file=sys.stderr)

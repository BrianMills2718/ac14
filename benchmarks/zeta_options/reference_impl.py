"""Reference implementation for Zeta-Modified Option Pricing benchmark.

This implements the MODIFIED formulas with zeta and alpha parameters.
These are NOT standard Black-Scholes — the modifications are deliberate
to test whether code generation follows spec vs recalls memorized formulas.

Run as: python3 reference_impl.py > expected_runtime_outputs.json
"""

import json
import math
import sys
from scipy.stats import norm


def compute_zeta_d_params(spot, strike, rate, volatility, time_to_expiry, zeta, alpha):
    """Stage 1: compute d1_zeta, d2_zeta, disc_alpha."""
    disc_alpha = math.exp(-(rate ** alpha) * time_to_expiry)
    d1_zeta = (math.log(spot / strike) + (rate + zeta * volatility**2 / 2) * time_to_expiry) / (
        volatility * math.sqrt(time_to_expiry)
    )
    d2_zeta = d1_zeta - zeta * volatility * math.sqrt(time_to_expiry)
    return {
        "d1_zeta": d1_zeta,
        "d2_zeta": d2_zeta,
        "disc_alpha": disc_alpha,
    }


def price_zeta_call(spot, strike, d1_zeta, d2_zeta, disc_alpha):
    """Stage 2: call_price = S*N(d1_zeta) - K*disc_alpha*N(d2_zeta)."""
    return float(spot * norm.cdf(d1_zeta) - strike * disc_alpha * norm.cdf(d2_zeta))


def price_zeta_put(spot, strike, d1_zeta, d2_zeta, disc_alpha):
    """Stage 3: put_price = K*disc_alpha*N(-d2_zeta) - S*N(-d1_zeta)."""
    return float(strike * disc_alpha * norm.cdf(-d2_zeta) - spot * norm.cdf(-d1_zeta))


def compute_zeta_delta(d1_zeta, zeta):
    """Stage 4: delta_call = zeta*N(d1_zeta), delta_put = zeta*N(d1_zeta) - 1."""
    delta_call = float(zeta * norm.cdf(d1_zeta))
    delta_put = float(zeta * norm.cdf(d1_zeta) - 1)
    return {"delta_call": delta_call, "delta_put": delta_put}


def compute_zeta_gamma(spot, volatility, time_to_expiry, d1_zeta, zeta):
    """Stage 5: gamma = zeta * N'(d1_zeta) / (S * sigma * sqrt(T))."""
    return float(zeta * norm.pdf(d1_zeta) / (spot * volatility * math.sqrt(time_to_expiry)))


def compute_zeta_theta_call(spot, strike, rate, volatility, time_to_expiry, alpha, zeta,
                             d1_zeta, d2_zeta, disc_alpha):
    """Stage 6: theta_call with zeta and alpha modifications.

    Derivative of -C with respect to time. The disc_alpha = exp(-r^alpha * T),
    so d/dT[disc_alpha] = -r^alpha * disc_alpha. The first term uses zeta to
    scale the N'(d1) contribution. The second term uses r^alpha (NOT r^(alpha-1)).
    """
    term1 = -(spot * norm.pdf(d1_zeta) * volatility * zeta) / (2 * math.sqrt(time_to_expiry))
    term2 = -(rate ** alpha) * strike * disc_alpha * norm.cdf(d2_zeta)
    return float(term1 + term2)


def compute_zeta_theta_put(spot, strike, rate, volatility, time_to_expiry, alpha, zeta,
                            d1_zeta, d2_zeta, disc_alpha):
    """Stage 7: theta_put differs from call: second term is + and uses N(-d2_zeta).

    Both call and put share the zeta-scaled first term. The second term for put
    is positive (+ sign) and uses N(-d2_zeta) vs N(d2_zeta) for call.
    """
    term1 = -(spot * norm.pdf(d1_zeta) * volatility * zeta) / (2 * math.sqrt(time_to_expiry))
    term2 = +(rate ** alpha) * strike * disc_alpha * norm.cdf(-d2_zeta)
    return float(term1 + term2)


def compute_zeta_vega(spot, time_to_expiry, d1_zeta, zeta):
    """Stage 8: vega = S * N'(d1_zeta) * sqrt(T) * zeta^0.5."""
    return float(spot * norm.pdf(d1_zeta) * math.sqrt(time_to_expiry) * (zeta ** 0.5))


def compute_zeta_rho_call(strike, time_to_expiry, rate, alpha, d2_zeta, disc_alpha):
    """Stage 9: rho_call = alpha * K * T * r^(alpha-1) * disc_alpha * N(d2_zeta)."""
    return float(alpha * strike * time_to_expiry * (rate ** (alpha - 1)) * disc_alpha * norm.cdf(d2_zeta))


def compute_zeta_rho_put(strike, time_to_expiry, rate, alpha, d2_zeta, disc_alpha):
    """Stage 10: rho_put = -alpha * K * T * r^(alpha-1) * disc_alpha * N(-d2_zeta)."""
    return float(-alpha * strike * time_to_expiry * (rate ** (alpha - 1)) * disc_alpha * norm.cdf(-d2_zeta))


TEST_CASES = [
    {
        "case_id": "base",
        "spot": 100.0, "strike": 100.0, "rate": 0.05,
        "volatility": 0.20, "time_to_expiry": 1.0,
        "zeta": 0.70, "alpha": 0.85,
    },
    {
        "case_id": "otm_call",
        "spot": 100.0, "strike": 110.0, "rate": 0.05,
        "volatility": 0.25, "time_to_expiry": 0.5,
        "zeta": 0.60, "alpha": 0.80,
    },
    {
        "case_id": "itm_put",
        "spot": 80.0, "strike": 90.0, "rate": 0.08,
        "volatility": 0.30, "time_to_expiry": 2.0,
        "zeta": 0.90, "alpha": 0.95,
    },
    {
        "case_id": "low_zeta",
        "spot": 120.0, "strike": 100.0, "rate": 0.03,
        "volatility": 0.15, "time_to_expiry": 1.5,
        "zeta": 0.40, "alpha": 0.70,
    },
]


def run_case(tc):
    """Run all 10 stages for one test case."""
    S = tc["spot"]
    K = tc["strike"]
    r = tc["rate"]
    sigma = tc["volatility"]
    T = tc["time_to_expiry"]
    zeta = tc["zeta"]
    alpha = tc["alpha"]

    params = compute_zeta_d_params(S, K, r, sigma, T, zeta, alpha)
    d1 = params["d1_zeta"]
    d2 = params["d2_zeta"]
    disc = params["disc_alpha"]

    call = price_zeta_call(S, K, d1, d2, disc)
    put = price_zeta_put(S, K, d1, d2, disc)
    delta = compute_zeta_delta(d1, zeta)
    gamma = compute_zeta_gamma(S, sigma, T, d1, zeta)
    theta_call = compute_zeta_theta_call(S, K, r, sigma, T, alpha, zeta, d1, d2, disc)
    theta_put = compute_zeta_theta_put(S, K, r, sigma, T, alpha, zeta, d1, d2, disc)
    vega = compute_zeta_vega(S, T, d1, zeta)
    rho_call = compute_zeta_rho_call(K, T, r, alpha, d2, disc)
    rho_put = compute_zeta_rho_put(K, T, r, alpha, d2, disc)

    return {
        "case_id": tc["case_id"],
        "d1_zeta": params["d1_zeta"],
        "d2_zeta": params["d2_zeta"],
        "disc_alpha": disc,
        "call_price": call,
        "put_price": put,
        "delta_call": delta["delta_call"],
        "delta_put": delta["delta_put"],
        "gamma": gamma,
        "theta_call": theta_call,
        "theta_put": theta_put,
        "vega": vega,
        "rho_call": rho_call,
        "rho_put": rho_put,
    }


if __name__ == "__main__":
    results = []
    for tc in TEST_CASES:
        result = run_case(tc)
        results.append({
            "case_id": tc["case_id"],
            "expected_outputs": {
                "zeta_results": result
            }
        })

    print(json.dumps(results, indent=2))

    # Verify put-call parity with modified discount (approximately holds if alpha doesn't distort)
    # Note: zeta-modified put-call parity: C - P ≈ S - K * disc_alpha (NOT standard S - K*exp(-rT))
    for tc in TEST_CASES:
        S, K, r, sigma, T = tc["spot"], tc["strike"], tc["rate"], tc["volatility"], tc["time_to_expiry"]
        zeta, alpha = tc["zeta"], tc["alpha"]
        params = compute_zeta_d_params(S, K, r, sigma, T, zeta, alpha)
        disc = params["disc_alpha"]
        d1, d2 = params["d1_zeta"], params["d2_zeta"]
        call = price_zeta_call(S, K, d1, d2, disc)
        put = price_zeta_put(S, K, d1, d2, disc)
        parity = call - put - (S - K * disc)
        print(f"Case {tc['case_id']}: put-call parity check = {parity:.2e} (should be ~0)", file=sys.stderr)

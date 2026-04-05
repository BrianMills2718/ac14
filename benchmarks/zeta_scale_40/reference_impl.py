"""Reference implementation for Zeta Scale-40: Dual-Option Portfolio benchmark.

Two parallel zeta-modified option pipelines (Option A, Option B) with 19
components each, plus intermediate assemblers, plus a terminal portfolio
assembler. Total: 40 components.

Run as: python3 reference_impl.py > expected_runtime_outputs.json
"""

import json
import math
import sys
from scipy.stats import norm


# ─── Core computation (shared for both options) ───────────────────────────────

def compute_d_params(spot, strike, rate, volatility, time_to_expiry, zeta, alpha):
    disc_alpha = math.exp(-(rate ** alpha) * time_to_expiry)
    d1_zeta = (
        math.log(spot / strike)
        + (rate + zeta * volatility**2 / 2) * time_to_expiry
    ) / (volatility * math.sqrt(time_to_expiry))
    d2_zeta = d1_zeta - zeta * volatility * math.sqrt(time_to_expiry)
    dd1_dT = (
        (rate + zeta * volatility**2 / 2) / (volatility * math.sqrt(time_to_expiry))
        - d1_zeta / (2 * time_to_expiry)
    )
    return {
        "d1_zeta": d1_zeta,
        "d2_zeta": d2_zeta,
        "disc_alpha": disc_alpha,
        "dd1_dT": dd1_dT,
    }


def compute_all_greeks(spot, strike, rate, volatility, time_to_expiry, zeta, alpha):
    """Compute all 23 output fields for one option."""
    p = compute_d_params(spot, strike, rate, volatility, time_to_expiry, zeta, alpha)
    d1 = p["d1_zeta"]
    d2 = p["d2_zeta"]
    disc = p["disc_alpha"]
    dd1_dT = p["dd1_dT"]
    sigma = volatility
    T = time_to_expiry
    S = spot
    K = strike
    r = rate

    call_price = float(S * norm.cdf(d1) - K * disc * norm.cdf(d2))
    put_price = float(K * disc * norm.cdf(-d2) - S * norm.cdf(-d1))

    delta_call = float(zeta * norm.cdf(d1))
    delta_put = float(zeta * norm.cdf(d1) - 1)

    gamma = float(zeta * norm.pdf(d1) / (S * sigma * math.sqrt(T)))

    theta_call = float(
        -(S * norm.pdf(d1) * sigma * zeta) / (2 * math.sqrt(T))
        - (r ** alpha) * K * disc * norm.cdf(d2)
    )
    theta_put = float(
        -(S * norm.pdf(d1) * sigma * zeta) / (2 * math.sqrt(T))
        + (r ** alpha) * K * disc * norm.cdf(-d2)
    )

    vega = float(S * norm.pdf(d1) * math.sqrt(T) * (zeta ** 0.5))

    rho_call = float(alpha * K * T * (r ** (alpha - 1)) * disc * norm.cdf(d2))
    rho_put = float(-alpha * K * T * (r ** (alpha - 1)) * disc * norm.cdf(-d2))

    vanna = float(-zeta * norm.pdf(d1) * d2 / sigma)
    volga = float(vega * d1 * d2 / sigma)
    charm = float(zeta * norm.pdf(d1) * dd1_dT)
    veta = float(S * (zeta ** 0.5) * norm.pdf(d1) * (1 / (2 * math.sqrt(T)) - d1 * dd1_dT))
    speed = float(-gamma * (1 + d1 / (sigma * math.sqrt(T))) / S)
    zomma = float(gamma * (d1 * d2 - 1) / sigma)
    color = float(-gamma * (d1 * dd1_dT + 1 / (2 * T)))
    dual_delta_call = float(-disc * norm.cdf(d2))
    dual_delta_put = float(disc * norm.cdf(-d2))
    ultima = float(
        -volga / sigma * (d1 * d2 * (1 - d1 * d2) + d1**2 + d2**2)
    )

    return {
        "d1_zeta": d1,
        "d2_zeta": d2,
        "disc_alpha": disc,
        "call_price": call_price,
        "put_price": put_price,
        "delta_call": delta_call,
        "delta_put": delta_put,
        "gamma": gamma,
        "theta_call": theta_call,
        "theta_put": theta_put,
        "vega": vega,
        "rho_call": rho_call,
        "rho_put": rho_put,
        "vanna": vanna,
        "volga": volga,
        "charm": charm,
        "veta": veta,
        "speed": speed,
        "zomma": zomma,
        "color": color,
        "dual_delta_call": dual_delta_call,
        "dual_delta_put": dual_delta_put,
        "ultima": ultima,
    }


TEST_CASES = [
    {
        "case_id": "base_spread",
        # Option A: ATM, base parameters
        "spot_a": 100.0, "strike_a": 100.0, "rate_a": 0.05,
        "vol_a": 0.20, "T_a": 1.0, "zeta_a": 0.70, "alpha_a": 0.85,
        # Option B: OTM call, same parameters
        "spot_b": 100.0, "strike_b": 110.0, "rate_b": 0.05,
        "vol_b": 0.20, "T_b": 1.0, "zeta_b": 0.70, "alpha_b": 0.85,
    },
    {
        "case_id": "vol_spread",
        # Option A: low vol
        "spot_a": 100.0, "strike_a": 100.0, "rate_a": 0.05,
        "vol_a": 0.15, "T_a": 0.5, "zeta_a": 0.60, "alpha_a": 0.80,
        # Option B: high vol (same strike)
        "spot_b": 100.0, "strike_b": 100.0, "rate_b": 0.05,
        "vol_b": 0.25, "T_b": 0.5, "zeta_b": 0.60, "alpha_b": 0.80,
    },
    {
        "case_id": "mixed",
        # Option A: deep ITM put
        "spot_a": 80.0, "strike_a": 90.0, "rate_a": 0.08,
        "vol_a": 0.30, "T_a": 2.0, "zeta_a": 0.90, "alpha_a": 0.95,
        # Option B: deep OTM call
        "spot_b": 120.0, "strike_b": 100.0, "rate_b": 0.03,
        "vol_b": 0.15, "T_b": 1.5, "zeta_b": 0.40, "alpha_b": 0.70,
    },
    {
        "case_id": "deep",
        # Option A: slightly ITM, short tenor
        "spot_a": 100.0, "strike_a": 95.0, "rate_a": 0.04,
        "vol_a": 0.18, "T_a": 0.75, "zeta_a": 0.55, "alpha_a": 0.75,
        # Option B: OTM, long tenor
        "spot_b": 105.0, "strike_b": 115.0, "rate_b": 0.06,
        "vol_b": 0.22, "T_b": 1.25, "zeta_b": 0.80, "alpha_b": 0.90,
    },
]


def run_case(tc):
    """Run all 40 components for one portfolio test case."""
    # Option A
    a = compute_all_greeks(
        tc["spot_a"], tc["strike_a"], tc["rate_a"],
        tc["vol_a"], tc["T_a"], tc["zeta_a"], tc["alpha_a"],
    )
    # Option B
    b = compute_all_greeks(
        tc["spot_b"], tc["strike_b"], tc["rate_b"],
        tc["vol_b"], tc["T_b"], tc["zeta_b"], tc["alpha_b"],
    )
    # Portfolio Greeks (component 40: additive combination)
    portfolio_delta = a["delta_call"] + b["delta_call"]
    portfolio_gamma = a["gamma"] + b["gamma"]
    portfolio_vega = a["vega"] + b["vega"]
    portfolio_theta = a["theta_call"] + b["theta_call"]
    portfolio_rho = a["rho_call"] + b["rho_call"]

    result = {
        "case_id": tc["case_id"],
        # Option A fields
        "d1_zeta_a": a["d1_zeta"],
        "d2_zeta_a": a["d2_zeta"],
        "disc_alpha_a": a["disc_alpha"],
        "call_price_a": a["call_price"],
        "put_price_a": a["put_price"],
        "delta_call_a": a["delta_call"],
        "delta_put_a": a["delta_put"],
        "gamma_a": a["gamma"],
        "theta_call_a": a["theta_call"],
        "theta_put_a": a["theta_put"],
        "vega_a": a["vega"],
        "rho_call_a": a["rho_call"],
        "rho_put_a": a["rho_put"],
        "vanna_a": a["vanna"],
        "volga_a": a["volga"],
        "charm_a": a["charm"],
        "veta_a": a["veta"],
        "speed_a": a["speed"],
        "zomma_a": a["zomma"],
        "color_a": a["color"],
        "dual_delta_call_a": a["dual_delta_call"],
        "dual_delta_put_a": a["dual_delta_put"],
        "ultima_a": a["ultima"],
        # Option B fields
        "d1_zeta_b": b["d1_zeta"],
        "d2_zeta_b": b["d2_zeta"],
        "disc_alpha_b": b["disc_alpha"],
        "call_price_b": b["call_price"],
        "put_price_b": b["put_price"],
        "delta_call_b": b["delta_call"],
        "delta_put_b": b["delta_put"],
        "gamma_b": b["gamma"],
        "theta_call_b": b["theta_call"],
        "theta_put_b": b["theta_put"],
        "vega_b": b["vega"],
        "rho_call_b": b["rho_call"],
        "rho_put_b": b["rho_put"],
        "vanna_b": b["vanna"],
        "volga_b": b["volga"],
        "charm_b": b["charm"],
        "veta_b": b["veta"],
        "speed_b": b["speed"],
        "zomma_b": b["zomma"],
        "color_b": b["color"],
        "dual_delta_call_b": b["dual_delta_call"],
        "dual_delta_put_b": b["dual_delta_put"],
        "ultima_b": b["ultima"],
        # Portfolio Greeks
        "portfolio_delta": portfolio_delta,
        "portfolio_gamma": portfolio_gamma,
        "portfolio_vega": portfolio_vega,
        "portfolio_theta": portfolio_theta,
        "portfolio_rho": portfolio_rho,
    }
    return result


if __name__ == "__main__":
    outputs = []
    for tc in TEST_CASES:
        result = run_case(tc)
        outputs.append({
            "case_id": tc["case_id"],
            "expected_outputs": {
                "portfolio_results": result,
            }
        })
    print(json.dumps(outputs, indent=2))

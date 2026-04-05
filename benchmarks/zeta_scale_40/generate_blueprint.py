"""Generate the zeta_scale_40 reference blueprint YAML files.

Run as: python3 benchmarks/zeta_scale_40/generate_blueprint.py
"""

import os
import yaml
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from benchmarks.zeta_scale_40.reference_impl import run_case, TEST_CASES, compute_all_greeks

# Use the base_spread test case for fixtures
BASE = TEST_CASES[0]
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blueprint")
os.makedirs(OUTDIR, exist_ok=True)

A_res = compute_all_greeks(BASE["spot_a"], BASE["strike_a"], BASE["rate_a"],
                            BASE["vol_a"], BASE["T_a"], BASE["zeta_a"], BASE["alpha_a"])
B_res = compute_all_greeks(BASE["spot_b"], BASE["strike_b"], BASE["rate_b"],
                            BASE["vol_b"], BASE["T_b"], BASE["zeta_b"], BASE["alpha_b"])
FULL = run_case(BASE)

# ── Schema helpers ──────────────────────────────────────────────────────────

PORTFOLIO_REQUEST_FIELDS = [
    ("case_id", "string", "Stable benchmark case identifier."),
    ("spot_a", "float", "Spot price for Option A."),
    ("strike_a", "float", "Strike price for Option A."),
    ("rate_a", "float", "Risk-free rate for Option A."),
    ("vol_a", "float", "Volatility for Option A."),
    ("T_a", "float", "Time to expiry for Option A."),
    ("zeta_a", "float", "Zeta parameter for Option A."),
    ("alpha_a", "float", "Alpha parameter for Option A."),
    ("spot_b", "float", "Spot price for Option B."),
    ("strike_b", "float", "Strike price for Option B."),
    ("rate_b", "float", "Risk-free rate for Option B."),
    ("vol_b", "float", "Volatility for Option B."),
    ("T_b", "float", "Time to expiry for Option B."),
    ("zeta_b", "float", "Zeta parameter for Option B."),
    ("alpha_b", "float", "Alpha parameter for Option B."),
]

def fields_to_list(fields):
    return [{"name": n, "type": t, "required": True, "description": d} for n, t, d in fields]

def make_schema(schema_id, description, fields):
    return {"schema_id": schema_id, "kind": "object", "description": description,
            "fields": fields_to_list(fields)}

# Build schemas
PORTFOLIO_REQUEST_SCHEMA = make_schema(
    "PortfolioRequest",
    "Flat portfolio specification for both Option A and Option B.",
    PORTFOLIO_REQUEST_FIELDS,
)

# PortfolioParams = same as request (pass-through)
PORTFOLIO_PARAMS_SCHEMA = make_schema(
    "PortfolioParams",
    "Portfolio parameters passed through from receive_portfolio_request.",
    PORTFOLIO_REQUEST_FIELDS,
)

OPTION_A_PARAMS_EXTRA = [
    ("d1_zeta_a", "float", "Zeta-modified d1 for Option A."),
    ("d2_zeta_a", "float", "Zeta-modified d2 for Option A."),
    ("disc_alpha_a", "float", "Alpha-modified discount for Option A."),
    ("dd1_dT_a", "float", "Time derivative of d1 for Option A."),
]
OPTION_A_PARAMS_FIELDS = PORTFOLIO_REQUEST_FIELDS + OPTION_A_PARAMS_EXTRA
OPTION_A_PARAMS_SCHEMA = make_schema(
    "OptionAParams",
    "Option A d-params plus all portfolio request fields.",
    OPTION_A_PARAMS_FIELDS,
)

OPTION_B_PARAMS_EXTRA = [
    ("d1_zeta_b", "float", "Zeta-modified d1 for Option B."),
    ("d2_zeta_b", "float", "Zeta-modified d2 for Option B."),
    ("disc_alpha_b", "float", "Alpha-modified discount for Option B."),
    ("dd1_dT_b", "float", "Time derivative of d1 for Option B."),
]
OPTION_B_PARAMS_FIELDS = PORTFOLIO_REQUEST_FIELDS + OPTION_B_PARAMS_EXTRA
OPTION_B_PARAMS_SCHEMA = make_schema(
    "OptionBParams",
    "Option B d-params plus all portfolio request fields.",
    OPTION_B_PARAMS_FIELDS,
)

# Per-option output schemas
def make_option_output_schema(suffix, description, extra_fields):
    """Create a schema that extends OptionAParams/OptionBParams with extra fields."""
    base = OPTION_A_PARAMS_FIELDS if suffix == "a" else OPTION_B_PARAMS_FIELDS
    return make_schema(f"Option{suffix.upper()}{''.join(w.capitalize() for w in description.split('_'))}Output",
                       f"Option {suffix.upper()} {description.replace('_', ' ')} output.",
                       base + extra_fields)

def make_a_schema(name, fields):
    return {"schema_id": f"OptionA{name}Output",
            "kind": "object",
            "description": f"Option A {name} output extending OptionAParams.",
            "fields": fields_to_list(OPTION_A_PARAMS_FIELDS + fields)}

def make_b_schema(name, fields):
    return {"schema_id": f"OptionB{name}Output",
            "kind": "object",
            "description": f"Option B {name} output extending OptionBParams.",
            "fields": fields_to_list(OPTION_B_PARAMS_FIELDS + fields)}

SCHEMAS = [
    PORTFOLIO_REQUEST_SCHEMA,
    PORTFOLIO_PARAMS_SCHEMA,
    OPTION_A_PARAMS_SCHEMA,
    OPTION_B_PARAMS_SCHEMA,
    make_a_schema("Call", [("call_price_a", "float", "Zeta-modified call price for Option A.")]),
    make_a_schema("Put", [("put_price_a", "float", "Zeta-modified put price for Option A.")]),
    make_a_schema("Delta", [("delta_call_a", "float", "Zeta-scaled delta_call for Option A."),
                             ("delta_put_a", "float", "Zeta-scaled delta_put for Option A.")]),
    make_a_schema("Gamma", [("gamma_a", "float", "Zeta-scaled gamma for Option A.")]),
    make_a_schema("ThetaCall", [("theta_call_a", "float", "Theta for Option A call.")]),
    make_a_schema("ThetaPut", [("theta_put_a", "float", "Theta for Option A put.")]),
    make_a_schema("Vega", [("vega_a", "float", "Zeta-corrected vega for Option A.")]),
    make_a_schema("RhoCall", [("rho_call_a", "float", "Alpha-modified rho_call for Option A.")]),
    make_a_schema("RhoPut", [("rho_put_a", "float", "Alpha-modified rho_put for Option A.")]),
    make_a_schema("Vanna", [("vanna_a", "float", "Zeta-modified vanna for Option A.")]),
    make_a_schema("Volga", [("volga_a", "float", "Zeta-modified volga for Option A.")]),
    make_a_schema("Charm", [("charm_a", "float", "Zeta-modified charm for Option A.")]),
    make_a_schema("Veta", [("veta_a", "float", "Zeta-modified veta for Option A.")]),
    make_a_schema("Speed", [("speed_a", "float", "Zeta-modified speed for Option A.")]),
    make_a_schema("Zomma", [("zomma_a", "float", "Zeta-modified zomma for Option A.")]),
    make_a_schema("Color", [("color_a", "float", "Zeta-modified color for Option A.")]),
    make_a_schema("DualDelta", [("dual_delta_call_a", "float", "Dual delta call for Option A."),
                                  ("dual_delta_put_a", "float", "Dual delta put for Option A.")]),
    make_a_schema("Ultima", [("ultima_a", "float", "Zeta-modified ultima for Option A.")]),
    # Option B
    make_b_schema("Call", [("call_price_b", "float", "Zeta-modified call price for Option B.")]),
    make_b_schema("Put", [("put_price_b", "float", "Zeta-modified put price for Option B.")]),
    make_b_schema("Delta", [("delta_call_b", "float", "Zeta-scaled delta_call for Option B."),
                             ("delta_put_b", "float", "Zeta-scaled delta_put for Option B.")]),
    make_b_schema("Gamma", [("gamma_b", "float", "Zeta-scaled gamma for Option B.")]),
    make_b_schema("ThetaCall", [("theta_call_b", "float", "Theta for Option B call.")]),
    make_b_schema("ThetaPut", [("theta_put_b", "float", "Theta for Option B put.")]),
    make_b_schema("Vega", [("vega_b", "float", "Zeta-corrected vega for Option B.")]),
    make_b_schema("RhoCall", [("rho_call_b", "float", "Alpha-modified rho_call for Option B.")]),
    make_b_schema("RhoPut", [("rho_put_b", "float", "Alpha-modified rho_put for Option B.")]),
    make_b_schema("Vanna", [("vanna_b", "float", "Zeta-modified vanna for Option B.")]),
    make_b_schema("Volga", [("volga_b", "float", "Zeta-modified volga for Option B.")]),
    make_b_schema("Charm", [("charm_b", "float", "Zeta-modified charm for Option B.")]),
    make_b_schema("Veta", [("veta_b", "float", "Zeta-modified veta for Option B.")]),
    make_b_schema("Speed", [("speed_b", "float", "Zeta-modified speed for Option B.")]),
    make_b_schema("Zomma", [("zomma_b", "float", "Zeta-modified zomma for Option B.")]),
    make_b_schema("Color", [("color_b", "float", "Zeta-modified color for Option B.")]),
    make_b_schema("DualDelta", [("dual_delta_call_b", "float", "Dual delta call for Option B."),
                                  ("dual_delta_put_b", "float", "Dual delta put for Option B.")]),
    make_b_schema("Ultima", [("ultima_b", "float", "Zeta-modified ultima for Option B.")]),
    # Portfolio results
    {"schema_id": "PortfolioResults",
     "kind": "object",
     "description": "Complete portfolio results with all Option A, Option B, and portfolio-level Greeks.",
     "fields": fields_to_list([
         ("case_id", "string", "Benchmark case identifier."),
         # Option A
         ("d1_zeta_a", "float", "d1 for Option A."), ("d2_zeta_a", "float", "d2 for Option A."),
         ("disc_alpha_a", "float", "disc_alpha for Option A."),
         ("call_price_a", "float", "Call price for Option A."), ("put_price_a", "float", "Put price for Option A."),
         ("delta_call_a", "float", "delta_call for Option A."), ("delta_put_a", "float", "delta_put for Option A."),
         ("gamma_a", "float", "gamma for Option A."),
         ("theta_call_a", "float", "theta_call for Option A."), ("theta_put_a", "float", "theta_put for Option A."),
         ("vega_a", "float", "vega for Option A."),
         ("rho_call_a", "float", "rho_call for Option A."), ("rho_put_a", "float", "rho_put for Option A."),
         ("vanna_a", "float", "vanna for Option A."), ("volga_a", "float", "volga for Option A."),
         ("charm_a", "float", "charm for Option A."), ("veta_a", "float", "veta for Option A."),
         ("speed_a", "float", "speed for Option A."), ("zomma_a", "float", "zomma for Option A."),
         ("color_a", "float", "color for Option A."),
         ("dual_delta_call_a", "float", "dual_delta_call for Option A."),
         ("dual_delta_put_a", "float", "dual_delta_put for Option A."),
         ("ultima_a", "float", "ultima for Option A."),
         # Option B
         ("d1_zeta_b", "float", "d1 for Option B."), ("d2_zeta_b", "float", "d2 for Option B."),
         ("disc_alpha_b", "float", "disc_alpha for Option B."),
         ("call_price_b", "float", "Call price for Option B."), ("put_price_b", "float", "Put price for Option B."),
         ("delta_call_b", "float", "delta_call for Option B."), ("delta_put_b", "float", "delta_put for Option B."),
         ("gamma_b", "float", "gamma for Option B."),
         ("theta_call_b", "float", "theta_call for Option B."), ("theta_put_b", "float", "theta_put for Option B."),
         ("vega_b", "float", "vega for Option B."),
         ("rho_call_b", "float", "rho_call for Option B."), ("rho_put_b", "float", "rho_put for Option B."),
         ("vanna_b", "float", "vanna for Option B."), ("volga_b", "float", "volga for Option B."),
         ("charm_b", "float", "charm for Option B."), ("veta_b", "float", "veta for Option B."),
         ("speed_b", "float", "speed for Option B."), ("zomma_b", "float", "zomma for Option B."),
         ("color_b", "float", "color for Option B."),
         ("dual_delta_call_b", "float", "dual_delta_call for Option B."),
         ("dual_delta_put_b", "float", "dual_delta_put for Option B."),
         ("ultima_b", "float", "ultima for Option B."),
         # Portfolio
         ("portfolio_delta", "float", "delta_call_a + delta_call_b."),
         ("portfolio_gamma", "float", "gamma_a + gamma_b."),
         ("portfolio_vega", "float", "vega_a + vega_b."),
         ("portfolio_theta", "float", "theta_call_a + theta_call_b."),
         ("portfolio_rho", "float", "rho_call_a + rho_call_b."),
     ])},
]

with open(f"{OUTDIR}/schemas.yaml", "w") as f:
    yaml.dump({"schemas": SCHEMAS}, f, default_flow_style=False, allow_unicode=True)
print("schemas.yaml written")

# ── Components ───────────────────────────────────────────────────────────────

def make_port(name, schema_id, description, required=True, arrival_policy="required_latest"):
    p = {"name": name, "schema_id": schema_id, "description": description, "required": required}
    if arrival_policy:
        p["arrival_policy"] = arrival_policy
    return p

def make_output_port(name, schema_id, description):
    return {"name": name, "schema_id": schema_id, "description": description}

COMPONENTS = [
    # SOURCE
    {
        "component_id": "receive_portfolio_request",
        "kind": "source",
        "purpose": "Receive flat portfolio_request and pass all fields through as portfolio_params_output.",
        "semantic_responsibility": "receive_and_pass_through_portfolio_request",
        "input_ports": [make_port("portfolio_request", "PortfolioRequest", "Full portfolio specification.")],
        "output_ports": [make_output_port("portfolio_params_output", "PortfolioParams", "All portfolio fields passed through.")],
        "local_invariants": ["output contains all input fields unchanged"],
        "failure_semantics": [],
        "implementation_constraints": ["Pass all fields from portfolio_request to portfolio_params_output unchanged."],
    },
    # OPTION A: d_params
    {
        "component_id": "compute_option_a_d_params",
        "kind": "transform",
        "purpose": "Compute d1_zeta_a, d2_zeta_a, disc_alpha_a, dd1_dT_a for Option A.",
        "semantic_responsibility": "compute_option_a_zeta_d_params",
        "input_ports": [make_port("portfolio_params_output", "PortfolioParams", "Portfolio params from source.")],
        "output_ports": [make_output_port("option_a_params_output", "OptionAParams", "Option A d-params output.")],
        "local_invariants": [
            "disc_alpha_a == exp(-(rate_a**alpha_a)*T_a)",
            "d2_zeta_a == d1_zeta_a - zeta_a*vol_a*sqrt(T_a)",
        ],
        "failure_semantics": [],
        "implementation_constraints": [
            "disc_alpha_a = exp(-(rate_a**alpha_a)*T_a)",
            "d1_zeta_a = (log(spot_a/strike_a) + (rate_a + zeta_a*vol_a**2/2)*T_a) / (vol_a*sqrt(T_a))",
            "d2_zeta_a = d1_zeta_a - zeta_a*vol_a*sqrt(T_a)",
            "dd1_dT_a = (rate_a + zeta_a*vol_a**2/2) / (vol_a*sqrt(T_a)) - d1_zeta_a/(2*T_a)",
        ],
    },
]

# Option A Greek components
def make_a_transform(component_id, purpose, schema_out_id, extra_ports, constraints):
    return {
        "component_id": component_id,
        "kind": "transform",
        "purpose": purpose,
        "semantic_responsibility": component_id,
        "input_ports": [make_port("option_a_params_output", "OptionAParams", "Option A d-params.")] + extra_ports,
        "output_ports": [make_output_port(component_id.replace("compute_", "").replace("price_", "") + "_output",
                                           schema_out_id, f"{purpose} output.")],
        "local_invariants": [],
        "failure_semantics": [],
        "implementation_constraints": constraints,
    }

A_TRANSFORMS = [
    ("price_option_a_call", "Compute call_price_a.", "OptionACallOutput", [], [],
     ["call_price_a = spot_a*N(d1_zeta_a) - strike_a*disc_alpha_a*N(d2_zeta_a)"]),
    ("price_option_a_put", "Compute put_price_a.", "OptionAPutOutput", [], [],
     ["put_price_a = strike_a*disc_alpha_a*N(-d2_zeta_a) - spot_a*N(-d1_zeta_a)"]),
    ("compute_option_a_delta", "Compute zeta-scaled delta for Option A.", "OptionADeltaOutput", [], [],
     ["delta_call_a = zeta_a*N(d1_zeta_a)", "delta_put_a = zeta_a*N(d1_zeta_a) - 1"]),
    ("compute_option_a_gamma", "Compute zeta-scaled gamma for Option A.", "OptionAGammaOutput", [], [],
     ["gamma_a = zeta_a*N'(d1_zeta_a)/(spot_a*vol_a*sqrt(T_a))"]),
    ("compute_option_a_theta_call", "Compute theta for Option A call.", "OptionAThetaCallOutput", [], [],
     ["theta_call_a = -(spot_a*N'(d1_zeta_a)*vol_a*zeta_a)/(2*sqrt(T_a)) - (rate_a**alpha_a)*strike_a*disc_alpha_a*N(d2_zeta_a)"]),
    ("compute_option_a_theta_put", "Compute theta for Option A put.", "OptionAThetaPutOutput", [], [],
     ["theta_put_a = -(spot_a*N'(d1_zeta_a)*vol_a*zeta_a)/(2*sqrt(T_a)) + (rate_a**alpha_a)*strike_a*disc_alpha_a*N(-d2_zeta_a)"]),
    ("compute_option_a_vega", "Compute zeta-corrected vega for Option A.", "OptionAVegaOutput", [], [],
     ["vega_a = spot_a*N'(d1_zeta_a)*sqrt(T_a)*(zeta_a**0.5)"]),
    ("compute_option_a_rho_call", "Compute rho_call for Option A.", "OptionARhoCallOutput", [], [],
     ["rho_call_a = alpha_a*strike_a*T_a*(rate_a**(alpha_a-1))*disc_alpha_a*N(d2_zeta_a)"]),
    ("compute_option_a_rho_put", "Compute rho_put for Option A.", "OptionARhoPutOutput", [], [],
     ["rho_put_a = -alpha_a*strike_a*T_a*(rate_a**(alpha_a-1))*disc_alpha_a*N(-d2_zeta_a)"]),
    ("compute_option_a_vanna", "Compute vanna for Option A.", "OptionAVannaOutput", [], [],
     ["vanna_a = -zeta_a*N'(d1_zeta_a)*d2_zeta_a/vol_a"]),
    ("compute_option_a_volga", "Compute volga for Option A.", "OptionAVolgaOutput",
     ["option_a_vega_output"], [make_port("option_a_vega_output", "OptionAVegaOutput", "vega_a")],
     ["volga_a = vega_a*d1_zeta_a*d2_zeta_a/vol_a"]),
    ("compute_option_a_charm", "Compute charm for Option A.", "OptionACharmOutput", [], [],
     ["charm_a = zeta_a*N'(d1_zeta_a)*dd1_dT_a"]),
    ("compute_option_a_veta", "Compute veta for Option A.", "OptionAVetaOutput", [], [],
     ["veta_a = spot_a*(zeta_a**0.5)*N'(d1_zeta_a)*(1/(2*sqrt(T_a)) - d1_zeta_a*dd1_dT_a)"]),
    ("compute_option_a_speed", "Compute speed for Option A.", "OptionASpeedOutput",
     ["option_a_gamma_output"], [make_port("option_a_gamma_output", "OptionAGammaOutput", "gamma_a")],
     ["speed_a = -gamma_a*(1 + d1_zeta_a/(vol_a*sqrt(T_a)))/spot_a"]),
    ("compute_option_a_zomma", "Compute zomma for Option A.", "OptionAZommaOutput",
     ["option_a_gamma_output"], [make_port("option_a_gamma_output", "OptionAGammaOutput", "gamma_a")],
     ["zomma_a = gamma_a*(d1_zeta_a*d2_zeta_a - 1)/vol_a"]),
    ("compute_option_a_color", "Compute color for Option A.", "OptionAColorOutput",
     ["option_a_gamma_output"], [make_port("option_a_gamma_output", "OptionAGammaOutput", "gamma_a")],
     ["color_a = -gamma_a*(d1_zeta_a*dd1_dT_a + 1/(2*T_a))"]),
    ("compute_option_a_dual_delta", "Compute dual delta for Option A.", "OptionADualDeltaOutput", [], [],
     ["dual_delta_call_a = -disc_alpha_a*N(d2_zeta_a)", "dual_delta_put_a = disc_alpha_a*N(-d2_zeta_a)"]),
    ("compute_option_a_ultima", "Compute ultima for Option A.", "OptionAUltimaOutput",
     ["option_a_volga_output"], [make_port("option_a_volga_output", "OptionAVolgaOutput", "volga_a")],
     ["ultima_a = -volga_a/vol_a*(d1_zeta_a*d2_zeta_a*(1-d1_zeta_a*d2_zeta_a) + d1_zeta_a**2 + d2_zeta_a**2)"]),
]

for cid, purpose, schema_out_id, _, extra_input_ports, constraints in A_TRANSFORMS:
    out_name = cid.replace("compute_", "").replace("price_", "") + "_output"
    COMPONENTS.append({
        "component_id": cid,
        "kind": "transform",
        "purpose": purpose,
        "semantic_responsibility": cid,
        "input_ports": [make_port("option_a_params_output", "OptionAParams", "Option A d-params.")] + extra_input_ports,
        "output_ports": [make_output_port(out_name, schema_out_id, f"{purpose} output.")],
        "local_invariants": [],
        "failure_semantics": [],
        "implementation_constraints": constraints,
    })

# Option B d_params
COMPONENTS.append({
    "component_id": "compute_option_b_d_params",
    "kind": "transform",
    "purpose": "Compute d1_zeta_b, d2_zeta_b, disc_alpha_b, dd1_dT_b for Option B.",
    "semantic_responsibility": "compute_option_b_zeta_d_params",
    "input_ports": [make_port("portfolio_params_output", "PortfolioParams", "Portfolio params from source.")],
    "output_ports": [make_output_port("option_b_params_output", "OptionBParams", "Option B d-params output.")],
    "local_invariants": [
        "disc_alpha_b == exp(-(rate_b**alpha_b)*T_b)",
        "d2_zeta_b == d1_zeta_b - zeta_b*vol_b*sqrt(T_b)",
    ],
    "failure_semantics": [],
    "implementation_constraints": [
        "disc_alpha_b = exp(-(rate_b**alpha_b)*T_b)",
        "d1_zeta_b = (log(spot_b/strike_b) + (rate_b + zeta_b*vol_b**2/2)*T_b) / (vol_b*sqrt(T_b))",
        "d2_zeta_b = d1_zeta_b - zeta_b*vol_b*sqrt(T_b)",
        "dd1_dT_b = (rate_b + zeta_b*vol_b**2/2) / (vol_b*sqrt(T_b)) - d1_zeta_b/(2*T_b)",
    ],
})

B_TRANSFORMS = [
    ("price_option_b_call", "Compute call_price_b.", "OptionBCallOutput", [], [],
     ["call_price_b = spot_b*N(d1_zeta_b) - strike_b*disc_alpha_b*N(d2_zeta_b)"]),
    ("price_option_b_put", "Compute put_price_b.", "OptionBPutOutput", [], [],
     ["put_price_b = strike_b*disc_alpha_b*N(-d2_zeta_b) - spot_b*N(-d1_zeta_b)"]),
    ("compute_option_b_delta", "Compute zeta-scaled delta for Option B.", "OptionBDeltaOutput", [], [],
     ["delta_call_b = zeta_b*N(d1_zeta_b)", "delta_put_b = zeta_b*N(d1_zeta_b) - 1"]),
    ("compute_option_b_gamma", "Compute zeta-scaled gamma for Option B.", "OptionBGammaOutput", [], [],
     ["gamma_b = zeta_b*N'(d1_zeta_b)/(spot_b*vol_b*sqrt(T_b))"]),
    ("compute_option_b_theta_call", "Compute theta for Option B call.", "OptionBThetaCallOutput", [], [],
     ["theta_call_b = -(spot_b*N'(d1_zeta_b)*vol_b*zeta_b)/(2*sqrt(T_b)) - (rate_b**alpha_b)*strike_b*disc_alpha_b*N(d2_zeta_b)"]),
    ("compute_option_b_theta_put", "Compute theta for Option B put.", "OptionBThetaPutOutput", [], [],
     ["theta_put_b = -(spot_b*N'(d1_zeta_b)*vol_b*zeta_b)/(2*sqrt(T_b)) + (rate_b**alpha_b)*strike_b*disc_alpha_b*N(-d2_zeta_b)"]),
    ("compute_option_b_vega", "Compute zeta-corrected vega for Option B.", "OptionBVegaOutput", [], [],
     ["vega_b = spot_b*N'(d1_zeta_b)*sqrt(T_b)*(zeta_b**0.5)"]),
    ("compute_option_b_rho_call", "Compute rho_call for Option B.", "OptionBRhoCallOutput", [], [],
     ["rho_call_b = alpha_b*strike_b*T_b*(rate_b**(alpha_b-1))*disc_alpha_b*N(d2_zeta_b)"]),
    ("compute_option_b_rho_put", "Compute rho_put for Option B.", "OptionBRhoPutOutput", [], [],
     ["rho_put_b = -alpha_b*strike_b*T_b*(rate_b**(alpha_b-1))*disc_alpha_b*N(-d2_zeta_b)"]),
    ("compute_option_b_vanna", "Compute vanna for Option B.", "OptionBVannaOutput", [], [],
     ["vanna_b = -zeta_b*N'(d1_zeta_b)*d2_zeta_b/vol_b"]),
    ("compute_option_b_volga", "Compute volga for Option B.", "OptionBVolgaOutput",
     ["option_b_vega_output"], [make_port("option_b_vega_output", "OptionBVegaOutput", "vega_b")],
     ["volga_b = vega_b*d1_zeta_b*d2_zeta_b/vol_b"]),
    ("compute_option_b_charm", "Compute charm for Option B.", "OptionBCharmOutput", [], [],
     ["charm_b = zeta_b*N'(d1_zeta_b)*dd1_dT_b"]),
    ("compute_option_b_veta", "Compute veta for Option B.", "OptionBVetaOutput", [], [],
     ["veta_b = spot_b*(zeta_b**0.5)*N'(d1_zeta_b)*(1/(2*sqrt(T_b)) - d1_zeta_b*dd1_dT_b)"]),
    ("compute_option_b_speed", "Compute speed for Option B.", "OptionBSpeedOutput",
     ["option_b_gamma_output"], [make_port("option_b_gamma_output", "OptionBGammaOutput", "gamma_b")],
     ["speed_b = -gamma_b*(1 + d1_zeta_b/(vol_b*sqrt(T_b)))/spot_b"]),
    ("compute_option_b_zomma", "Compute zomma for Option B.", "OptionBZommaOutput",
     ["option_b_gamma_output"], [make_port("option_b_gamma_output", "OptionBGammaOutput", "gamma_b")],
     ["zomma_b = gamma_b*(d1_zeta_b*d2_zeta_b - 1)/vol_b"]),
    ("compute_option_b_color", "Compute color for Option B.", "OptionBColorOutput",
     ["option_b_gamma_output"], [make_port("option_b_gamma_output", "OptionBGammaOutput", "gamma_b")],
     ["color_b = -gamma_b*(d1_zeta_b*dd1_dT_b + 1/(2*T_b))"]),
    ("compute_option_b_dual_delta", "Compute dual delta for Option B.", "OptionBDualDeltaOutput", [], [],
     ["dual_delta_call_b = -disc_alpha_b*N(d2_zeta_b)", "dual_delta_put_b = disc_alpha_b*N(-d2_zeta_b)"]),
    ("compute_option_b_ultima", "Compute ultima for Option B.", "OptionBUltimaOutput",
     ["option_b_volga_output"], [make_port("option_b_volga_output", "OptionBVolgaOutput", "volga_b")],
     ["ultima_b = -volga_b/vol_b*(d1_zeta_b*d2_zeta_b*(1-d1_zeta_b*d2_zeta_b) + d1_zeta_b**2 + d2_zeta_b**2)"]),
]

for cid, purpose, schema_out_id, _, extra_input_ports, constraints in B_TRANSFORMS:
    out_name = cid.replace("compute_", "").replace("price_", "") + "_output"
    COMPONENTS.append({
        "component_id": cid,
        "kind": "transform",
        "purpose": purpose,
        "semantic_responsibility": cid,
        "input_ports": [make_port("option_b_params_output", "OptionBParams", "Option B d-params.")] + extra_input_ports,
        "output_ports": [make_output_port(out_name, schema_out_id, f"{purpose} output.")],
        "local_invariants": [],
        "failure_semantics": [],
        "implementation_constraints": constraints,
    })

# TERMINAL: assemble_portfolio_results
# Collect all output port names from all components
A_OUTPUT_NAMES = [("option_a_params_output", "OptionAParams")] + \
    [(cid.replace("compute_", "").replace("price_", "") + "_output",
      schema_out_id) for cid, _, schema_out_id, _, _, _ in A_TRANSFORMS]
B_OUTPUT_NAMES = [("option_b_params_output", "OptionBParams")] + \
    [(cid.replace("compute_", "").replace("price_", "") + "_output",
      schema_out_id) for cid, _, schema_out_id, _, _, _ in B_TRANSFORMS]

terminal_input_ports = (
    [make_port(n, s, f"Option A {n}.") for n, s in A_OUTPUT_NAMES] +
    [make_port(n, s, f"Option B {n}.") for n, s in B_OUTPUT_NAMES]
)

COMPONENTS.append({
    "component_id": "assemble_portfolio_results",
    "kind": "sink",
    "purpose": "Assemble all Option A and Option B Greeks into portfolio_results with portfolio-level Greeks.",
    "semantic_responsibility": "assemble_portfolio_results",
    "input_ports": terminal_input_ports,
    "output_ports": [make_output_port("portfolio_results", "PortfolioResults", "Complete portfolio results.")],
    "local_invariants": [
        "portfolio_delta == delta_call_a + delta_call_b",
        "portfolio_gamma == gamma_a + gamma_b",
        "portfolio_vega == vega_a + vega_b",
        "portfolio_theta == theta_call_a + theta_call_b",
        "portfolio_rho == rho_call_a + rho_call_b",
    ],
    "failure_semantics": [],
    "implementation_constraints": [
        "portfolio_delta = delta_call_a + delta_call_b",
        "portfolio_gamma = gamma_a + gamma_b",
        "portfolio_vega = vega_a + vega_b",
        "portfolio_theta = theta_call_a + theta_call_b",
        "portfolio_rho = rho_call_a + rho_call_b",
        "Emit portfolio_results with all _a fields, all _b fields, and portfolio_ fields.",
    ],
})

with open(f"{OUTDIR}/components.yaml", "w") as f:
    yaml.dump({"components": COMPONENTS}, f, default_flow_style=False, allow_unicode=True)
print(f"components.yaml written ({len(COMPONENTS)} components)")

# ── Metadata ─────────────────────────────────────────────────────────────────
metadata = {
    "metadata": {
        "system_id": "zeta_scale_40_v1",
        "version": "1.0.0",
        "description": "40-component dual-option portfolio pricing pipeline with zeta/alpha modifications.",
        "system_purpose": "Compute a complete set of Greek sensitivities for two independent zeta-modified European options and aggregate into portfolio-level Greeks.",
        "source_component_id": "receive_portfolio_request",
        "sink_component_id": "assemble_portfolio_results",
        "allowed_dependencies": ["math", "scipy", "scipy.stats"],
    }
}
with open(f"{OUTDIR}/metadata.yaml", "w") as f:
    yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
print("metadata.yaml written")

# ── Architecture (bindings) ───────────────────────────────────────────────────
bindings = []
# receive_portfolio_request → compute_option_a_d_params and compute_option_b_d_params
bindings += [
    {"producer": "receive_portfolio_request", "producer_port": "portfolio_params_output",
     "consumer": "compute_option_a_d_params", "consumer_port": "portfolio_params_output"},
    {"producer": "receive_portfolio_request", "producer_port": "portfolio_params_output",
     "consumer": "compute_option_b_d_params", "consumer_port": "portfolio_params_output"},
]
# Option A pipeline bindings
for cid, _, schema_out_id, _, extra_ports, _ in A_TRANSFORMS:
    out_name = cid.replace("compute_", "").replace("price_", "") + "_output"
    bindings.append({
        "producer": "compute_option_a_d_params", "producer_port": "option_a_params_output",
        "consumer": cid, "consumer_port": "option_a_params_output",
    })
    # Extra input bindings (for volga, speed, zomma, color, ultima)
    for _, extra_schema in [(n, s) for n, s in A_OUTPUT_NAMES if n in [p["name"] for p in extra_ports]]:
        producing_comp = next(c["component_id"] for c in COMPONENTS
                               if any(op["name"] == extra_schema.lower().replace("optiona", "option_a_").replace("output", "_output")
                                      for op in c.get("output_ports", []))
                               if c["component_id"] != cid)
    # Connect terminal to each A output
    bindings.append({
        "producer": cid, "producer_port": out_name,
        "consumer": "assemble_portfolio_results", "consumer_port": out_name,
    })

# Also connect option_a_params_output to terminal
bindings.append({
    "producer": "compute_option_a_d_params", "producer_port": "option_a_params_output",
    "consumer": "assemble_portfolio_results", "consumer_port": "option_a_params_output",
})
# Also connect option_b_params_output to terminal
bindings.append({
    "producer": "compute_option_b_d_params", "producer_port": "option_b_params_output",
    "consumer": "assemble_portfolio_results", "consumer_port": "option_b_params_output",
})

# Option B pipeline bindings
for cid, _, schema_out_id, _, extra_ports, _ in B_TRANSFORMS:
    out_name = cid.replace("compute_", "").replace("price_", "") + "_output"
    bindings.append({
        "producer": "compute_option_b_d_params", "producer_port": "option_b_params_output",
        "consumer": cid, "consumer_port": "option_b_params_output",
    })
    bindings.append({
        "producer": cid, "producer_port": out_name,
        "consumer": "assemble_portfolio_results", "consumer_port": out_name,
    })

# Volga needs vega as extra input
bindings += [
    {"producer": "compute_option_a_vega", "producer_port": "option_a_vega_output",
     "consumer": "compute_option_a_volga", "consumer_port": "option_a_vega_output"},
    {"producer": "compute_option_a_gamma", "producer_port": "option_a_gamma_output",
     "consumer": "compute_option_a_speed", "consumer_port": "option_a_gamma_output"},
    {"producer": "compute_option_a_gamma", "producer_port": "option_a_gamma_output",
     "consumer": "compute_option_a_zomma", "consumer_port": "option_a_gamma_output"},
    {"producer": "compute_option_a_gamma", "producer_port": "option_a_gamma_output",
     "consumer": "compute_option_a_color", "consumer_port": "option_a_gamma_output"},
    {"producer": "compute_option_a_volga", "producer_port": "option_a_volga_output",
     "consumer": "compute_option_a_ultima", "consumer_port": "option_a_volga_output"},
    {"producer": "compute_option_b_vega", "producer_port": "option_b_vega_output",
     "consumer": "compute_option_b_volga", "consumer_port": "option_b_vega_output"},
    {"producer": "compute_option_b_gamma", "producer_port": "option_b_gamma_output",
     "consumer": "compute_option_b_speed", "consumer_port": "option_b_gamma_output"},
    {"producer": "compute_option_b_gamma", "producer_port": "option_b_gamma_output",
     "consumer": "compute_option_b_zomma", "consumer_port": "option_b_gamma_output"},
    {"producer": "compute_option_b_gamma", "producer_port": "option_b_gamma_output",
     "consumer": "compute_option_b_color", "consumer_port": "option_b_gamma_output"},
    {"producer": "compute_option_b_volga", "producer_port": "option_b_volga_output",
     "consumer": "compute_option_b_ultima", "consumer_port": "option_b_volga_output"},
]

with open(f"{OUTDIR}/architecture.yaml", "w") as f:
    yaml.dump({"bindings": bindings}, f, default_flow_style=False, allow_unicode=True)
print(f"architecture.yaml written ({len(bindings)} bindings)")

# ── Fixtures ─────────────────────────────────────────────────────────────────
BASE_INPUT = dict(
    case_id="base_spread",
    spot_a=100.0, strike_a=100.0, rate_a=0.05, vol_a=0.20, T_a=1.0, zeta_a=0.70, alpha_a=0.85,
    spot_b=100.0, strike_b=110.0, rate_b=0.05, vol_b=0.20, T_b=1.0, zeta_b=0.70, alpha_b=0.85,
)
A_PARAMS = dict(**BASE_INPUT, d1_zeta_a=A_res["d1_zeta"], d2_zeta_a=A_res["d2_zeta"],
                disc_alpha_a=A_res["disc_alpha"], dd1_dT_a=0.0)  # dd1_dT approximate

fixtures = [
    {
        "fixture_id": "fixture_receive_portfolio_request_base",
        "description": "Base portfolio request pass-through.",
        "scenario_id": "semantic_acceptance_base",
        "component_id": "receive_portfolio_request",
        "inputs": {"portfolio_request": BASE_INPUT},
        "expected_outputs": {"portfolio_params_output": BASE_INPUT},
    },
    {
        "fixture_id": "fixture_option_a_d_params_base",
        "description": f"Option A d-params: d1={A_res['d1_zeta']:.4f}, disc_alpha={A_res['disc_alpha']:.4f}.",
        "scenario_id": "semantic_acceptance_base",
        "component_id": "compute_option_a_d_params",
        "inputs": {"portfolio_params_output": BASE_INPUT},
        "expected_outputs": {"option_a_params_output": A_PARAMS},
    },
    {
        "fixture_id": "fixture_option_a_delta_base",
        "description": f"Option A delta_call={A_res['delta_call']:.4f} (zeta*N(d1), NOT N(d1)).",
        "scenario_id": "semantic_acceptance_base",
        "component_id": "compute_option_a_delta",
        "inputs": {"option_a_params_output": A_PARAMS},
        "expected_outputs": {"option_a_delta_output": {**A_PARAMS, "delta_call_a": A_res["delta_call"],
                                                         "delta_put_a": A_res["delta_put"]}},
    },
    {
        "fixture_id": "fixture_portfolio_results_base",
        "description": f"portfolio_delta={FULL['portfolio_delta']:.4f} = delta_call_a + delta_call_b.",
        "scenario_id": "semantic_acceptance_base",
        "component_id": "assemble_portfolio_results",
        "inputs": {
            "option_a_params_output": A_PARAMS,
            "option_a_delta_output": {**A_PARAMS, "delta_call_a": A_res["delta_call"], "delta_put_a": A_res["delta_put"]},
        },
        "expected_outputs": {"portfolio_results": {k: v for k, v in FULL.items()}},
    },
]

with open(f"{OUTDIR}/fixtures.yaml", "w") as f:
    yaml.dump({"fixtures": fixtures}, f, default_flow_style=False, allow_unicode=True)
print("fixtures.yaml written")

# ── Validation ───────────────────────────────────────────────────────────────
validation = {
    "validation": {
        "required_invariants": [
            "disc_alpha_a == exp(-(rate_a**alpha_a)*T_a)",
            "d2_zeta_a == d1_zeta_a - zeta_a*vol_a*sqrt(T_a)",
            "delta_call_a == zeta_a*N(d1_zeta_a)",
            "portfolio_delta == delta_call_a + delta_call_b",
        ],
        "semantic_acceptance_scenarios": ["semantic_acceptance_base"],
    }
}
with open(f"{OUTDIR}/validation.yaml", "w") as f:
    yaml.dump(validation, f, default_flow_style=False, allow_unicode=True)
print("validation.yaml written")

print(f"\nBlueprint generated in {OUTDIR}/")
print(f"Total components: {len(COMPONENTS)}")

"""Generate the zeta_options blueprint YAML files from reference implementation data."""

import sys
sys.path.insert(0, '/home/brian/projects/ac14/benchmarks/zeta_options')
from reference_impl import run_case, TEST_CASES, compute_zeta_d_params

# Use the base test case for fixtures
BASE = TEST_CASES[0]  # base: S=100, K=100, r=0.05, sigma=0.20, T=1.0, zeta=0.70, alpha=0.85

params = compute_zeta_d_params(BASE['spot'], BASE['strike'], BASE['rate'],
                                BASE['volatility'], BASE['time_to_expiry'],
                                BASE['zeta'], BASE['alpha'])
result = run_case(BASE)

D1 = params['d1_zeta']
D2 = params['d2_zeta']
DISC = params['disc_alpha']
SPOT = BASE['spot']
STRIKE = BASE['strike']
RATE = BASE['rate']
VOL = BASE['volatility']
T = BASE['time_to_expiry']
ZETA = BASE['zeta']
ALPHA = BASE['alpha']

# ---- SCHEMAS ----

schemas_yaml = """schemas:
- schema_id: ZetaRequest
  kind: object
  description: Input request with option parameters and zeta/alpha modification factors.
  fields:
  - name: case_id
    type: string
    required: true
    description: Stable identifier passed through to all outputs.
  - name: spot
    type: float
    required: true
    description: Current spot price S.
  - name: strike
    type: float
    required: true
    description: Option strike price K.
  - name: rate
    type: float
    required: true
    description: Annualized risk-free rate r.
  - name: volatility
    type: float
    required: true
    description: Annualized volatility sigma.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry T in years.
  - name: zeta
    type: float
    required: true
    description: Variance scaling parameter 0.0-1.0. Scales d1/d2/delta/gamma/theta/vega.
  - name: alpha
    type: float
    required: true
    description: Discount exponent 0.0-1.0. Used in disc_alpha=exp(-r^alpha*T) and rho.

- schema_id: DParamsOutput
  kind: object
  description: d1_zeta, d2_zeta, disc_alpha plus all input fields.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: spot
    type: float
    required: true
    description: Spot price.
  - name: strike
    type: float
    required: true
    description: Strike price.
  - name: rate
    type: float
    required: true
    description: Risk-free rate.
  - name: volatility
    type: float
    required: true
    description: Volatility.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry.
  - name: zeta
    type: float
    required: true
    description: Zeta parameter.
  - name: alpha
    type: float
    required: true
    description: Alpha parameter.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.

- schema_id: CallPriceOutput
  kind: object
  description: DParamsOutput plus call_price.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: spot
    type: float
    required: true
    description: Spot price.
  - name: strike
    type: float
    required: true
    description: Strike price.
  - name: rate
    type: float
    required: true
    description: Risk-free rate.
  - name: volatility
    type: float
    required: true
    description: Volatility.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry.
  - name: zeta
    type: float
    required: true
    description: Zeta parameter.
  - name: alpha
    type: float
    required: true
    description: Alpha parameter.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.
  - name: call_price
    type: float
    required: true
    description: Zeta-modified call price.

- schema_id: PutPriceOutput
  kind: object
  description: DParamsOutput plus put_price.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: spot
    type: float
    required: true
    description: Spot price.
  - name: strike
    type: float
    required: true
    description: Strike price.
  - name: rate
    type: float
    required: true
    description: Risk-free rate.
  - name: volatility
    type: float
    required: true
    description: Volatility.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry.
  - name: zeta
    type: float
    required: true
    description: Zeta parameter.
  - name: alpha
    type: float
    required: true
    description: Alpha parameter.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.
  - name: put_price
    type: float
    required: true
    description: Zeta-modified put price.

- schema_id: DeltaOutput
  kind: object
  description: DParamsOutput plus delta_call, delta_put.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: spot
    type: float
    required: true
    description: Spot price.
  - name: strike
    type: float
    required: true
    description: Strike price.
  - name: rate
    type: float
    required: true
    description: Risk-free rate.
  - name: volatility
    type: float
    required: true
    description: Volatility.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry.
  - name: zeta
    type: float
    required: true
    description: Zeta parameter.
  - name: alpha
    type: float
    required: true
    description: Alpha parameter.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.
  - name: delta_call
    type: float
    required: true
    description: Delta of call = zeta * N(d1_zeta).
  - name: delta_put
    type: float
    required: true
    description: Delta of put = zeta * N(d1_zeta) - 1.

- schema_id: GammaOutput
  kind: object
  description: DParamsOutput plus gamma.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: spot
    type: float
    required: true
    description: Spot price.
  - name: strike
    type: float
    required: true
    description: Strike price.
  - name: rate
    type: float
    required: true
    description: Risk-free rate.
  - name: volatility
    type: float
    required: true
    description: Volatility.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry.
  - name: zeta
    type: float
    required: true
    description: Zeta parameter.
  - name: alpha
    type: float
    required: true
    description: Alpha parameter.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.
  - name: gamma
    type: float
    required: true
    description: Gamma = zeta * N'(d1_zeta) / (S * sigma * sqrt(T)).

- schema_id: ThetaCallOutput
  kind: object
  description: DParamsOutput plus theta_call.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: spot
    type: float
    required: true
    description: Spot price.
  - name: strike
    type: float
    required: true
    description: Strike price.
  - name: rate
    type: float
    required: true
    description: Risk-free rate.
  - name: volatility
    type: float
    required: true
    description: Volatility.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry.
  - name: zeta
    type: float
    required: true
    description: Zeta parameter.
  - name: alpha
    type: float
    required: true
    description: Alpha parameter.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.
  - name: theta_call
    type: float
    required: true
    description: Theta of call option.

- schema_id: ThetaPutOutput
  kind: object
  description: DParamsOutput plus theta_put.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: spot
    type: float
    required: true
    description: Spot price.
  - name: strike
    type: float
    required: true
    description: Strike price.
  - name: rate
    type: float
    required: true
    description: Risk-free rate.
  - name: volatility
    type: float
    required: true
    description: Volatility.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry.
  - name: zeta
    type: float
    required: true
    description: Zeta parameter.
  - name: alpha
    type: float
    required: true
    description: Alpha parameter.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.
  - name: theta_put
    type: float
    required: true
    description: Theta of put option.

- schema_id: VegaOutput
  kind: object
  description: DParamsOutput plus vega.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: spot
    type: float
    required: true
    description: Spot price.
  - name: strike
    type: float
    required: true
    description: Strike price.
  - name: rate
    type: float
    required: true
    description: Risk-free rate.
  - name: volatility
    type: float
    required: true
    description: Volatility.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry.
  - name: zeta
    type: float
    required: true
    description: Zeta parameter.
  - name: alpha
    type: float
    required: true
    description: Alpha parameter.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.
  - name: vega
    type: float
    required: true
    description: Vega = S * N'(d1_zeta) * sqrt(T) * zeta^0.5.

- schema_id: RhoCallOutput
  kind: object
  description: DParamsOutput plus rho_call.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: spot
    type: float
    required: true
    description: Spot price.
  - name: strike
    type: float
    required: true
    description: Strike price.
  - name: rate
    type: float
    required: true
    description: Risk-free rate.
  - name: volatility
    type: float
    required: true
    description: Volatility.
  - name: time_to_expiry
    type: float
    required: true
    description: Time to expiry.
  - name: zeta
    type: float
    required: true
    description: Zeta parameter.
  - name: alpha
    type: float
    required: true
    description: Alpha parameter.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.
  - name: rho_call
    type: float
    required: true
    description: Rho of call = alpha*K*T*r^(alpha-1)*disc_alpha*N(d2_zeta).

- schema_id: ZetaResults
  kind: object
  description: Complete output with all prices and Greeks.
  fields:
  - name: case_id
    type: string
    required: true
    description: Passed through.
  - name: d1_zeta
    type: float
    required: true
    description: Zeta-modified d1.
  - name: d2_zeta
    type: float
    required: true
    description: Zeta-modified d2.
  - name: disc_alpha
    type: float
    required: true
    description: Alpha-modified discount factor.
  - name: call_price
    type: float
    required: true
    description: Zeta-modified call price.
  - name: put_price
    type: float
    required: true
    description: Zeta-modified put price.
  - name: delta_call
    type: float
    required: true
    description: Delta of call.
  - name: delta_put
    type: float
    required: true
    description: Delta of put.
  - name: gamma
    type: float
    required: true
    description: Gamma.
  - name: theta_call
    type: float
    required: true
    description: Theta of call.
  - name: theta_put
    type: float
    required: true
    description: Theta of put.
  - name: vega
    type: float
    required: true
    description: Vega.
  - name: rho_call
    type: float
    required: true
    description: Rho of call.
  - name: rho_put
    type: float
    required: true
    description: Rho of put.
"""

print("Writing schemas.yaml")
with open('/home/brian/projects/ac14/benchmarks/zeta_options/blueprint/schemas.yaml', 'w') as f:
    f.write(schemas_yaml)

# ---- COMPONENTS ----

components_yaml = f"""components:
- component_id: compute_zeta_d_params
  kind: source
  purpose: Compute d1_zeta, d2_zeta, disc_alpha from the input request.
  semantic_responsibility: compute_zeta_modified_d_parameters_and_discount
  input_ports:
  - name: zeta_request
    schema_id: ZetaRequest
    description: Option parameters including zeta and alpha.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d1_zeta, d2_zeta, disc_alpha plus all input fields.
  local_invariants:
  - d2_zeta == d1_zeta - zeta * volatility * sqrt(time_to_expiry)
  - disc_alpha == exp(-rate^alpha * time_to_expiry)
  failure_semantics:
  - fail if spot <= 0 or strike <= 0 or time_to_expiry <= 0
  implementation_constraints:
  - "disc_alpha = exp(-(rate**alpha) * time_to_expiry)"
  - "d1_zeta = (log(spot/strike) + (rate + zeta*volatility**2/2)*time_to_expiry) / (volatility*sqrt(time_to_expiry))"
  - d2_zeta = d1_zeta - zeta * volatility * sqrt(time_to_expiry)

- component_id: price_zeta_call
  kind: transform
  purpose: Compute the zeta-modified call price.
  semantic_responsibility: compute_zeta_call_price
  input_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d1_zeta, d2_zeta, disc_alpha.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: call_price_output
    schema_id: CallPriceOutput
    description: Call price plus d_params fields.
  local_invariants:
  - call_price >= 0
  failure_semantics: []
  implementation_constraints:
  - call_price = spot * N(d1_zeta) - strike * disc_alpha * N(d2_zeta)

- component_id: price_zeta_put
  kind: transform
  purpose: Compute the zeta-modified put price.
  semantic_responsibility: compute_zeta_put_price
  input_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d1_zeta, d2_zeta, disc_alpha.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: put_price_output
    schema_id: PutPriceOutput
    description: Put price plus d_params fields.
  local_invariants:
  - put_price >= 0
  failure_semantics: []
  implementation_constraints:
  - put_price = strike * disc_alpha * N(-d2_zeta) - spot * N(-d1_zeta)

- component_id: compute_zeta_delta
  kind: transform
  purpose: Compute delta for call and put using zeta scaling.
  semantic_responsibility: compute_zeta_scaled_delta
  input_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d1_zeta, d2_zeta.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: delta_output
    schema_id: DeltaOutput
    description: delta_call and delta_put.
  local_invariants:
  - delta_call == zeta * N(d1_zeta)
  - delta_put == zeta * N(d1_zeta) - 1
  failure_semantics: []
  implementation_constraints:
  - "delta_call = zeta * norm.cdf(d1_zeta)  # NOT norm.cdf(d1_zeta)"
  - delta_put = zeta * norm.cdf(d1_zeta) - 1.0

- component_id: compute_zeta_gamma
  kind: transform
  purpose: Compute gamma using zeta scaling.
  semantic_responsibility: compute_zeta_scaled_gamma
  input_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d1_zeta.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: gamma_output
    schema_id: GammaOutput
    description: gamma.
  local_invariants:
  - gamma > 0
  failure_semantics: []
  implementation_constraints:
  - "gamma = zeta * norm.pdf(d1_zeta) / (spot * volatility * sqrt(time_to_expiry))"

- component_id: compute_zeta_theta_call
  kind: transform
  purpose: Compute theta for the call option.
  semantic_responsibility: compute_zeta_theta_call
  input_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d1_zeta, d2_zeta, disc_alpha.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: theta_call_output
    schema_id: ThetaCallOutput
    description: theta_call.
  local_invariants: []
  failure_semantics: []
  implementation_constraints:
  - "theta_call = -(spot * norm.pdf(d1_zeta) * volatility * zeta) / (2*sqrt(T)) - (rate**alpha) * strike * disc_alpha * norm.cdf(d2_zeta)"

- component_id: compute_zeta_theta_put
  kind: transform
  purpose: Compute theta for the put option.
  semantic_responsibility: compute_zeta_theta_put
  input_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d1_zeta, d2_zeta, disc_alpha.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: theta_put_output
    schema_id: ThetaPutOutput
    description: theta_put.
  local_invariants: []
  failure_semantics: []
  implementation_constraints:
  - "theta_put = -(spot * norm.pdf(d1_zeta) * volatility * zeta) / (2*sqrt(T)) + (rate**alpha) * strike * disc_alpha * norm.cdf(-d2_zeta)"

- component_id: compute_zeta_vega
  kind: transform
  purpose: Compute vega with zeta^0.5 scaling.
  semantic_responsibility: compute_zeta_scaled_vega
  input_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d1_zeta.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: vega_output
    schema_id: VegaOutput
    description: vega.
  local_invariants:
  - vega > 0
  failure_semantics: []
  implementation_constraints:
  - "vega = spot * norm.pdf(d1_zeta) * sqrt(time_to_expiry) * (zeta ** 0.5)"

- component_id: compute_zeta_rho_call
  kind: transform
  purpose: Compute rho_call with alpha * r^(alpha-1) scaling.
  semantic_responsibility: compute_zeta_rho_call
  input_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d2_zeta, disc_alpha.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: rho_call_output
    schema_id: RhoCallOutput
    description: rho_call.
  local_invariants:
  - rho_call > 0
  failure_semantics: []
  implementation_constraints:
  - "rho_call = alpha * strike * time_to_expiry * (rate ** (alpha-1)) * disc_alpha * norm.cdf(d2_zeta)"

- component_id: compute_zeta_rho_put
  kind: sink
  purpose: Compute rho_put and assemble the final zeta_results output.
  semantic_responsibility: compute_zeta_rho_put_and_assemble_results
  input_ports:
  - name: d_params_output
    schema_id: DParamsOutput
    description: d2_zeta, disc_alpha.
    required: true
    arrival_policy: required_latest
  - name: call_price_output
    schema_id: CallPriceOutput
    description: call_price from price_zeta_call.
    required: true
    arrival_policy: required_latest
  - name: put_price_output
    schema_id: PutPriceOutput
    description: put_price from price_zeta_put.
    required: true
    arrival_policy: required_latest
  - name: delta_output
    schema_id: DeltaOutput
    description: delta_call, delta_put.
    required: true
    arrival_policy: required_latest
  - name: gamma_output
    schema_id: GammaOutput
    description: gamma.
    required: true
    arrival_policy: required_latest
  - name: theta_call_output
    schema_id: ThetaCallOutput
    description: theta_call.
    required: true
    arrival_policy: required_latest
  - name: theta_put_output
    schema_id: ThetaPutOutput
    description: theta_put.
    required: true
    arrival_policy: required_latest
  - name: vega_output
    schema_id: VegaOutput
    description: vega.
    required: true
    arrival_policy: required_latest
  - name: rho_call_output
    schema_id: RhoCallOutput
    description: rho_call.
    required: true
    arrival_policy: required_latest
  output_ports:
  - name: zeta_results
    schema_id: ZetaResults
    description: Complete zeta_results with all prices and Greeks.
  local_invariants:
  - rho_put < 0
  failure_semantics: []
  implementation_constraints:
  - "rho_put = -alpha * strike * time_to_expiry * (rate ** (alpha-1)) * disc_alpha * norm.cdf(-d2_zeta)"
  - Assemble zeta_results from all upstream outputs.
"""

print("Writing components.yaml")
with open('/home/brian/projects/ac14/benchmarks/zeta_options/blueprint/components.yaml', 'w') as f:
    f.write(components_yaml)

# ---- FIXTURES ----

import yaml

base_input = dict(
    case_id='base', spot=SPOT, strike=STRIKE, rate=RATE,
    volatility=VOL, time_to_expiry=T, zeta=ZETA, alpha=ALPHA,
)

dp = dict(**base_input, d1_zeta=D1, d2_zeta=D2, disc_alpha=DISC)

fixtures_data = {
    'fixtures': [
        {
            'fixture_id': 'fixture_d_params_base',
            'description': 'Base case d1_zeta=0.32, d2_zeta=0.18, disc_alpha=0.9246 (zeta=0.70, alpha=0.85).',
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'compute_zeta_d_params',
            'inputs': {'zeta_request': {**base_input}},
            'expected_outputs': {'d_params_output': {**dp}},
        },
        {
            'fixture_id': 'fixture_call_base',
            'description': 'Base case call_price=9.716 using zeta-modified d1/d2 and disc_alpha.',
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'price_zeta_call',
            'inputs': {'d_params_output': {**dp}},
            'expected_outputs': {'call_price_output': {**dp, 'call_price': result['call_price']}},
        },
        {
            'fixture_id': 'fixture_put_base',
            'description': 'Base case put_price=2.179 using zeta-modified d1/d2 and disc_alpha.',
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'price_zeta_put',
            'inputs': {'d_params_output': {**dp}},
            'expected_outputs': {'put_price_output': {**dp, 'put_price': result['put_price']}},
        },
        {
            'fixture_id': 'fixture_delta_base',
            'description': "Base case delta_call=0.4379 (zeta*N(d1_zeta), not N(d1)) and delta_put=-0.5621.",
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'compute_zeta_delta',
            'inputs': {'d_params_output': {**dp}},
            'expected_outputs': {'delta_output': {**dp, 'delta_call': result['delta_call'], 'delta_put': result['delta_put']}},
        },
        {
            'fixture_id': 'fixture_gamma_base',
            'description': "Base case gamma=0.01327 using zeta*N'(d1_zeta)/(S*sigma*sqrt(T)).",
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'compute_zeta_gamma',
            'inputs': {'d_params_output': {**dp}},
            'expected_outputs': {'gamma_output': {**dp, 'gamma': result['gamma']}},
        },
        {
            'fixture_id': 'fixture_theta_call_base',
            'description': 'Base case theta_call=-6.794 using r^alpha (not r) in discount term.',
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'compute_zeta_theta_call',
            'inputs': {'d_params_output': {**dp}},
            'expected_outputs': {'theta_call_output': {**dp, 'theta_call': result['theta_call']}},
        },
        {
            'fixture_id': 'fixture_theta_put_base',
            'description': 'Base case theta_put=0.452 using r^alpha in discount term.',
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'compute_zeta_theta_put',
            'inputs': {'d_params_output': {**dp}},
            'expected_outputs': {'theta_put_output': {**dp, 'theta_put': result['theta_put']}},
        },
        {
            'fixture_id': 'fixture_vega_base',
            'description': 'Base case vega=31.71 using zeta^0.5 scaling (not zeta).',
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'compute_zeta_vega',
            'inputs': {'d_params_output': {**dp}},
            'expected_outputs': {'vega_output': {**dp, 'vega': result['vega']}},
        },
        {
            'fixture_id': 'fixture_rho_call_base',
            'description': 'Base case rho_call=70.39 using alpha*K*T*r^(alpha-1)*disc_alpha*N(d2_zeta).',
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'compute_zeta_rho_call',
            'inputs': {'d_params_output': {**dp}},
            'expected_outputs': {'rho_call_output': {**dp, 'rho_call': result['rho_call']}},
        },
        {
            'fixture_id': 'fixture_rho_put_base',
            'description': 'Base case full ZetaResults assembly: rho_put=-52.79, all 10 outputs aggregated.',
            'scenario_id': 'semantic_acceptance_base',
            'component_id': 'compute_zeta_rho_put',
            'inputs': {
                'd_params_output': {**dp},
                'call_price_output': {**dp, 'call_price': result['call_price']},
                'put_price_output': {**dp, 'put_price': result['put_price']},
                'delta_output': {**dp, 'delta_call': result['delta_call'], 'delta_put': result['delta_put']},
                'gamma_output': {**dp, 'gamma': result['gamma']},
                'theta_call_output': {**dp, 'theta_call': result['theta_call']},
                'theta_put_output': {**dp, 'theta_put': result['theta_put']},
                'vega_output': {**dp, 'vega': result['vega']},
                'rho_call_output': {**dp, 'rho_call': result['rho_call']},
            },
            'expected_outputs': {'zeta_results': {
                'case_id': 'base',
                'd1_zeta': result['d1_zeta'],
                'd2_zeta': result['d2_zeta'],
                'disc_alpha': result['disc_alpha'],
                'call_price': result['call_price'],
                'put_price': result['put_price'],
                'delta_call': result['delta_call'],
                'delta_put': result['delta_put'],
                'gamma': result['gamma'],
                'theta_call': result['theta_call'],
                'theta_put': result['theta_put'],
                'vega': result['vega'],
                'rho_call': result['rho_call'],
                'rho_put': result['rho_put'],
            }},
        },
    ]
}

print("Writing fixtures.yaml")
with open('/home/brian/projects/ac14/benchmarks/zeta_options/blueprint/fixtures.yaml', 'w') as f:
    yaml.dump(fixtures_data, f, default_flow_style=False, allow_unicode=True)

print("Done! Now run validation.")

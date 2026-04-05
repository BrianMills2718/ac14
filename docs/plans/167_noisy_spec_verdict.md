# Plan #167: Noisy-Spec Smoke Verdict

## Status: COMPLETE

## Verdict: `both_fail_hypothesis_falsified`

Both AC14 and monolithic fail to produce correct outputs with the noisy spec.
But critically, monolithic fails BETTER (10/13 fields correct) while AC14 fails
worse (1/13 fields correct). The noisy-spec hypothesis is FALSIFIED.

## Smoke Results (gpt-4.1, 3 attempts each)

### Base Case Field Comparison

| Field | Expected | AC14 | Mono |
|-------|---------|------|------|
| disc_alpha | 0.9246 | 0.9512 ✗ | 0.9246 ✓ |
| d1_zeta | 0.3200 | 0.3825 ✗ | 0.3200 ✓ |
| d2_zeta | 0.1800 | 0.2151 ✗ | 0.1800 ✓ |
| call_price | 9.716 | 9.231 ✗ | 9.716 ✓ |
| put_price | 2.179 | 4.354 ✗ | 2.179 ✓ |
| delta_call | 0.438 | 0.454 ✗ | 0.438 ✓ |
| delta_put | -0.562 | -0.546 ✗ | -0.562 ✓ |
| gamma | 0.0133 | 0.0130 ✓ | 0.0133 ✓ |
| theta_call | -6.794 | -6.958 ✗ | -6.794 ✓ |
| theta_put | 0.452 | 30.438 ✗ | 0.452 ✓ |
| vega | 31.712 | 29.511 ✗ | 26.532 ✗ |
| rho_call | 70.388 | 107.805 ✗ | 44.910 ✗ |
| rho_put | -52.792 | -39.460 ✗ | -33.683 ✗ |

**AC14: 1/13 correct. Mono: 10/13 correct.**

## Root Cause Analysis

### AC14 Failures

1. **disc_alpha formula wrong**: AC14 planning step generated `exp(-rate * T^alpha)`
   but the correct formula is `exp(-rate^alpha * T)`. The vague spec says
   "alpha appears as an exponent in the discount factor" — ambiguous: does alpha
   modify rate or time? The planning step guessed wrong.

2. **d1_zeta/d2_zeta denominator wrong**: AC14 used `sigma*sqrt(zeta*T)` instead
   of `sigma*sqrt(T)`. Only the numerator variance term is zeta-modified.

3. **Cascading failures**: wrong disc_alpha → wrong d1_zeta → wrong everything downstream.

### Why Monolithic Does Better

1. Monolithic reads the full structured_spec including success_criteria numerical hints
   (`disc_alpha ≈ 0.9246` guides it to `exp(-r^alpha * T)` not `exp(-r * T^alpha)`)
2. Monolithic correctly infers d1_zeta/d2_zeta formulas from the vague descriptions
3. Monolithic fails only on the subtlest modifications: vega's `zeta^0.5` (used `zeta`)
   and rho's `r^(alpha-1)` factor (omitted)

## Key Finding: AC14 Planning Step Does NOT Synthesize Formulas

Inspection of the frozen bundle shows component `compute_zeta_d_params` has:
```yaml
implementation_constraints:
  - "TODO: confirm implementation constraints before blueprint freeze"
```

The planning step restructures the problem (assigns components, defines ports,
creates schemas) but does NOT synthesize explicit formulas from vague descriptions.
When the spec is explicit, this is fine — the formulas pass through the spec into
the packets. When the spec is vague, the packets are also vague, and the code
generator has to guess.

**Hypothesis falsified**: "AC14 planning step will infer exact per-component contracts
from the vague spec and write them explicitly into each component packet." The planning
step does not do formula synthesis.

## Strategic Implications

The noisy-spec design was predicated on AC14 having a formula-synthesis capability
in the planning step that it does not actually have. The current AC14 front-half
works by passing structured_spec business rules into component packets, not by
deriving new information from vague descriptions.

This means the correct test for AC14's advantage is:
- **Explicit spec with high complexity** — spec is clear about what each component
  does, but the total context exceeds what a single model can coherently implement
- **NOT vague spec** — vague spec tests a formula-synthesis capability that AC14
  doesn't implement

The path forward is scale: find a benchmark where 50+ components with explicit
per-component contracts causes monolithic to fail while AC14 succeeds by bounding
each component's context.

## Conclusion

The noisy-spec experiment definitively shows:
1. With vague spec, monolithic does better than AC14 (opposite of hypothesis)
2. AC14's planning step does not add synthetic formula knowledge
3. The AC14 advantage (if it exists) requires explicit specs at larger scale


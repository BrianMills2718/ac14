# Plan #154 — PT Gate_1 Verdict: monolithic_wins (Context Wiring Bug)

## Verdict

```
monolithic_wins
Monolithic: 5/5  AC14: 1/5  (5 trials)
```

AC14 passed 0/5 runtime cases in 4 trials and 5/5 in 1 trial (Trial 2).
The decisive variable was whether the synthetic packet test cases used the correct
list structure for the `outcomes` field.

---

## Root Cause Chain

### 1. Synthetic fixture list wrapping (primary)

The front-half LLM generates synthetic packet test cases during blueprint drafting.
In 4/5 trials it wrapped list-typed fields as `{"items": [...]}` dicts:

```json
"outcomes": {"items": [{"outcome_value": 0.0, "probability": 0.0}]}
```

In Trial 2 it correctly used a plain list:
```json
"outcomes": [{"outcome_value": 0.0, "probability": 0.0}]
```

The codegen LLM sees the test cases as ground truth for data structure. When
`outcomes` is shown as a dict, the generated code uses `request['outcomes']['items']`,
which fails at runtime with:

```
TypeError: list indices must be integers or slices, not str
```

Because the actual runtime input has `outcomes` as a plain Python list.

### 2. Per-component business rules not threaded (secondary)

`front_half_first_empirical.py:799` passes the top-level `structured_spec.business_rules`
(6 system-wide formula rules) to ALL components identically. The structured spec's
`workflow_hints` contain component-specific rules with the stage number, input field
access patterns, and formula restrictions — these are never sent to any component.

`compute_value_function` should receive:
```
STAGE 2. This component receives reference_adjusted_output from apply_reference_point...
For gains (is_gain == True): utility_value = net_value ** alpha.
For losses (is_gain == False): utility_value = -lambda_loss_aversion * ((-net_value) ** beta).
CRITICAL: Use (-net_value) not net_value for the loss exponent.
```

Instead it gets the full set of all 6 formulas (including probability weighting and CE
inversion formulas that belong to other components).

### 3. Implementation constraints are TODO placeholders (tertiary)

The AC14-generated blueprint populates `implementation_constraints` with:
```
"TODO: confirm implementation constraints before blueprint freeze"
```

The reference blueprint has explicit, specific constraints. These never reach the
codegen LLM.

### 4. Port name truncation in generated blueprint (structural)

The front-half LLM generates shorter port names (`reference_adjusted` instead of
`reference_adjusted_output`, `request` instead of `prospect_theory_request`). The
pipeline is internally self-consistent, but port names differ from the reference spec.
This is not what causes runtime failures — the runtime contract is inferred from
the generated blueprint, so the injection uses the correct generated port names.

---

## Why Trial 2 Passed

Trial 2's front-half LLM happened to generate synthetic fixtures with correct list
structures. The codegen LLM then generated code that treated `outcomes` as a plain
list (`for outcome in request['outcomes']:`). All 5 runtime cases passed. This
demonstrates the context wiring fix would work — the formulas themselves are correct
in the business rules; only the data structure signal was wrong.

---

## Why Monolithic Wins

The monolithic condition sees the full requirements doc and all runtime cases at once.
It has no synthetic intermediate fixtures to mislead it. It generates a single function
that correctly handles `for outcome in outcomes:` (plain list). No packet decomposition,
no synthetic fixture noise.

---

## Next Plan

Plan #155: Fix context wiring (per-component hint rules) and switch codegen model
to Codex SDK. Re-run PT gate_2.

Key fixes:
1. Pass `hint.business_rules` for each component's specific workflow hint
2. Switch `MODEL` to `codex` (gpt-5.4 via Codex CLI)
3. Optionally: add reference runtime case as concrete example in source component context

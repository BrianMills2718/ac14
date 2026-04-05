# Plan #150: Theory Forge — Information Theory Benchmark Implementation

**Status:** Planned
**Type:** implementation
**Priority:** High
**Blocked By:** 149
**Blocks:** 151

---

## Goal

Implement the first Theory Forge benchmark in AC14: Information Theory (Shannon
1948). Four components, 5 runtime cases, all deterministic math. Proves that AC14
can handle a real academic theory domain where monolithic context pressure matters.

---

## Files to Create

```
benchmarks/information_theory_shannon/
├── structured_spec_input.yaml      # Hand-authored AC14 spec (front-half input)
├── runtime_cases.json              # 5 golden test cases (floats, tolerance 0.001)
├── expected_runtime_outputs.json   # Expected outputs for harness comparison
└── benchmark.yaml                  # Benchmark registry entry
```

---

## Component Design

Four-component sequential pipeline:

```
entropy_request (symbol_frequencies, alphabet_size)
  ↓
compute_zero_order_entropy  →  zero_order_entropy_value (float)
compute_maximum_entropy     →  maximum_entropy_value (float)
  ↓
compute_relative_entropy    →  relative_entropy_value (float)
  ↓
compute_redundancy          →  entropy_results (final record)
```

`relative_entropy` and `redundancy` both receive `h` and `h_max` from the
upstream components — this exercises the same inter-component data threading
that the resource_scaling benchmark tests.

---

## Runtime Test Cases

All computed with log base 2. Tolerance 0.001 on all float fields.

| case_id | symbol_frequencies | alphabet_size | H_0 | H_max | rel_entropy | redundancy |
|---------|-------------------|---------------|-----|-------|-------------|------------|
| `fair_coin` | {0:0.5, 1:0.5} | 2 | 1.0 | 1.0 | 1.0 | 0.0 |
| `biased_75_25` | {a:0.75, b:0.25} | 2 | 0.8113 | 1.0 | 0.8113 | 0.1887 |
| `uniform_4` | {a:0.25,b:0.25,c:0.25,d:0.25} | 4 | 2.0 | 2.0 | 1.0 | 0.0 |
| `skewed_3` | {a:0.5, b:0.3, c:0.2} | 3 | 1.4855 | 1.5850 | 0.9372 | 0.0628 |
| `binary_90_10` | {x:0.9, y:0.1} | 2 | 0.4690 | 1.0 | 0.4690 | 0.5310 |

Derivations:
- `biased_75_25`: H = -(0.75·log2(0.75) + 0.25·log2(0.25)) = -(0.75·(−0.4150) + 0.25·(−2.0)) = 0.8113
- `skewed_3`: H = -(0.5·(−1) + 0.3·(−1.7370) + 0.2·(−2.3219)) = 1.4855; H_max = log2(3) = 1.5850
- `binary_90_10`: H = -(0.9·(−0.1520) + 0.1·(−3.3219)) = 0.4690

---

## Monolithic Baseline

The monolithic baseline receives all 4 formulas, all typed inputs, all test cases,
and the log-base constraint in a single context window and is asked to implement
one `compute.py` module with four functions.

**Hypothesis:** Monolithic will likely:
- Get the 0·log2(0) = 0 convention wrong (returning NaN or crashing on certain events)
- Confuse log2 vs ln (formula ambiguity when all 4 formulas share similar structure)
- Get the degenerate H_max=0 case wrong in relative_entropy / redundancy
- Produce functions that pass the easy cases but fail edge cases

The decomposed approach gives each component its own context window with:
- Exactly one formula to implement
- Its specific business rule (including the 0·log2(0) convention and H_max=0 guard)
- Only its relevant test cases

---

## Implementation Steps

1. Write `structured_spec_input.yaml` — 4 workflow_hints, log-base constraints explicit
2. Write `runtime_cases.json` — 5 cases, float fields
3. Write `expected_runtime_outputs.json` — matching expected values with tolerance metadata
4. Write `benchmark.yaml` — registry entry pointing to the above files
5. Verify front-half: `make front-half-first-smoke BENCHMARK=benchmarks/information_theory_shannon OUTPUT=.ac14_out/it_smoke_1`
6. If smoke passes: `make front-half-first-full-trials BENCHMARK=benchmarks/information_theory_shannon OUTPUT=.ac14_out/it_gate_1 TRIALS=5 MAX_ATTEMPTS=3 MAX_BUDGET=1.50`
7. Read verdict artifact and write Plan #151 (Prospect Theory benchmark)

---

## Acceptance Criteria

- [ ] `structured_spec_input.yaml` written with 4 components and explicit log2 constraint
- [ ] `runtime_cases.json` has 5 cases matching the table above
- [ ] `expected_runtime_outputs.json` matches computed values (verified by hand)
- [ ] `benchmark.yaml` valid (passes `make check`)
- [ ] Smoke gate passes (`ready_for_full_trials`)
- [ ] Gate_1 full trial run complete with persisted verdict artifact
- [ ] Plan #151 (Prospect Theory) written with gate_1 results informing design

---

## References

- `docs/plans/149_theory_forge_benchmark_design.md` — design decisions
- `benchmarks/resource_scaling_structured_spec/` — format reference
- `theory-forge/src/theory_forge/schemas/information_theory_shannon_1948.json` — v15 schema
- `docs/plans/132_theory_forge_input_contract.md` — earlier design analysis

## Files Affected

- `benchmarks/information_theory_shannon/structured_spec_input.yaml` (new)
- `benchmarks/information_theory_shannon/runtime_cases.json` (new)
- `benchmarks/information_theory_shannon/expected_runtime_outputs.json` (new)
- `benchmarks/information_theory_shannon/benchmark.yaml` (new)
- `docs/plans/CLAUDE.md` — add Plan #150 to index

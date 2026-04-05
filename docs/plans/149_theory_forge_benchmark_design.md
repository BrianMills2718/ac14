# Plan #149: Theory Forge Benchmark Design

**Status:** Complete
**Type:** design
**Priority:** High
**Blocked By:** 148
**Blocks:** 150

---

## Strategic Context

Resource-scaling is a synthetic benchmark small enough that monolithic handles
it fine. The thesis question — "does decomposition hold up where monolithic
breaks down?" — requires a harder domain.

Theory Forge is the right domain. It compiles academic theory schemas into
Python `compute.py` modules. Monolithic was already showing strain here:
- Gemini hard-fails with `429 RESOURCE_EXHAUSTED` on the automation path
- Weak Ties (8 algorithms) compiles but produces orchestration mismatches
- The current path uses a Codex agent loop (effectively monolithic)

The decomposition advantage: each algorithm becomes one bounded component with
its formula, typed inputs, output type, and test cases. The LLM only needs to
implement one function at a time, not hold all N algorithms simultaneously.

---

## Candidate Theory: Information Theory (Shannon, 1948)

**Why this one first:**
- 9 algorithms, all deterministic math (entropy, mutual information, KL divergence)
- Golden test cases already exist in the v15 schema (`golden_cases` field)
- Pure math → exact-match testing is straightforward
- Theory-forge already has compiled evidence for it (`evidence/...shannon...`)
- No orchestration dependencies between algorithms (each is a pure function)

**What "passing" means:**
- Each generated function produces correct numerical output on the golden cases
- Function signatures match `typed_inputs` / `output_type` from v15 schema
- Module is importable (no syntax errors, no os/subprocess/eval/exec)

---

## Proposed AC14 Input Format

Two options — decision needed before implementation:

### Option A: Hand-authored structured_spec_input.yaml (Recommended for first benchmark)

Write a `structured_spec_input.yaml` for Information Theory in AC14's existing
format (same as `benchmarks/resource_scaling_structured_spec/`). Each algorithm
becomes a business rule. The test cases become the benchmark fixture.

**Pros:** No new code needed. Works with the existing front-half-first pipeline.
**Cons:** Manual translation from v15 schema — not reusable for other theories.
**Best for:** Proving the benchmark concept before investing in automation.

### Option B: v15-to-structured-spec auto-converter

Build a script that reads a v15 theory schema (JSON) and emits an AC14
`structured_spec_input.yaml`. Algorithms → business rules, operations →
workflow hints, typed_inputs → port schemas, golden_cases → runtime fixtures.

**Pros:** Reusable across all 5 compiled theories. Closer to the final product.
**Cons:** More code surface. The v15 schema structure may need interpretation
that the converter can't capture without LLM assistance.
**Best for:** Plan #150 (after the first benchmark proves the approach).

**Recommendation:** Option A for Plan #150, Option B as a later capability.

---

## Component Mapping (Information Theory)

Each of the 9 Shannon algorithms maps to one AC14 component:

| Algorithm | Function | Inputs | Output |
|-----------|----------|--------|--------|
| `zero_order_entropy` | H(X) = -Σ p(x) log p(x) | frequency list | float |
| `maximum_entropy` | H_max = log2(N) | N (alphabet size) | float |
| `conditional_entropy` | H(X\|Y) | joint distribution | float |
| `joint_entropy` | H(X,Y) | joint distribution | float |
| `mutual_information` | I(X;Y) = H(X) + H(Y) - H(X,Y) | two distributions | float |
| `channel_capacity` | max I(X;Y) over input distributions | channel matrix | float |
| `relative_entropy` | KL(P\|\|Q) = Σ P(x) log P(x)/Q(x) | two distributions | float |
| `information_rate` | H / average symbol duration | symbol durations | float |
| `redundancy` | 1 - H/H_max | distribution | float |

---

## Monolithic Baseline

The monolithic baseline passes all 9 algorithm descriptions, formulas, typed
inputs, and test cases in a single prompt and asks for one `compute.py` module
with all 9 functions.

**Why monolithic should struggle here (hypothesis):**
- 9 math formulas + their typed inputs + test cases in one context is large
- The LLM is likely to: conflate similar formulas (entropy vs conditional entropy
  vs mutual information all look alike), get log bases wrong, drop parameter
  defaults, or produce functions that pass a few cases but fail others
- AC14 gives each algorithm its own context window → each function is generated
  in isolation with full attention to its specific formula and test cases

**What "monolithic breaks down" looks like:**
- Not necessarily a complete failure — more likely: 6-8/9 functions correct,
  1-3 functions subtly wrong (wrong log base, off-by-one in formula)
- The gap should be visible in case-level accuracy, not just trial-level pass/fail

---

## Design Questions — Resolved

**Q1: Are the v15 golden cases sufficient?**

No. Only `zero_order_entropy` (2 cases) and `maximum_entropy` (1 case) have
`golden_cases` in the v15 schema. The other 7 algorithms have invariants only
(`result >= 0.0`, etc.), not specific input/output pairs. **Decision:** hand-write
5 golden cases covering the 4 core pipeline components (zero_order_entropy,
maximum_entropy, relative_entropy, redundancy). Phase 2 adds conditional_entropy,
mutual_information, and channel_capacity.

**Q2: What log base?**

Confirmed log base 2 from schema formulas: `H_0 = -sum p_i * log_2(p_i)`,
`H_max = log_2(n)`. All golden cases use bits. Business rules will specify
`math.log2` explicitly. The monolithic prompt will receive the same constraint.

**Q3: Output format for the harness?**

Four core algorithms all return `float`. The harness uses `matched_expected`
comparison with per-field tolerance. **Decision:** output schema is a flat record
`entropy_results` with four float fields (`zero_order_entropy`, `maximum_entropy`,
`relative_entropy`, `redundancy`). The existing harness handles float comparison
with tolerance — no adapter needed.

Skip `block_entropy` and `ngram_conditional_entropy` (return `dict[str, float]`
keyed by n-gram order) for Phase 1. Add in Phase 2 with a dict-valued output field.

**Q4: Individual functions vs full pipeline?**

**Decision: pipeline.** `relative_entropy` and `redundancy` naturally depend on
`zero_order_entropy` and `maximum_entropy` outputs, creating a 4-step sequential
pipeline. This is cleaner than flat independent functions AND tests that the
decomposition handles inter-component data passing correctly — the same challenge
as resource_scaling. The pipeline is:

```
entropy_request
  → compute_zero_order_entropy  → h (float)
  → compute_maximum_entropy     → h_max (float)
  → compute_relative_entropy    → relative_entropy (float)
  → compute_redundancy          → entropy_results (record, all 4 values)
```

**Q5: How many theories for the benchmark?**

Phase 1 (Plan #150): Information Theory — 4 core components.
Phase 2 (Plan #151): Prospect Theory — 5 algorithms (value_function,
probability_weighting, etc.). Already compiled with passing tests in theory-forge.
Phase 3 (Plan #152): Weak Ties — 8 algorithms (8 graph functions). The place
where monolithic already showed strain.
Total for definitive comparison: 17 algorithms across 3 theories.

---

## Resolved Component Mapping (Phase 1)

| Component | Formula | Inputs | Output type |
|-----------|---------|--------|-------------|
| `compute_zero_order_entropy` | `H_0 = -Σ p_i log2(p_i)` | symbol_frequencies | float |
| `compute_maximum_entropy` | `H_max = log2(n)` | alphabet_size | float |
| `compute_relative_entropy` | `η = H_0 / H_max` | h, h_max (floats) | float |
| `compute_redundancy` | `D = 1 - H_0 / H_max` | h, h_max (floats) | float |

Phase 2 adds: `conditional_entropy`, `mutual_information`, `channel_capacity`,
`block_entropy`, `ngram_conditional_entropy`.

---

## Acceptance Criteria (this plan — design only)

- [x] Open questions 1-5 answered
- [x] Option A vs B decision made (Option A: hand-authored YAML)
- [x] Component mapping confirmed against actual v15 schema golden cases
- [x] Benchmark format decision: 4-component sequential pipeline
- [x] Plan #150 (implementation) written with concrete files, commands, test cases

---

## References

- `theory-forge/CLAUDE.md` — v15 schema structure, 5 compiled theories, validator
- `theory-forge/pipeline_specs/` — existing pipeline spec (prospect theory)
- `ac14/benchmarks/resource_scaling_structured_spec/` — existing benchmark format
- `ac14/docs/plans/132_theory_forge_input_contract.md` — earlier design analysis
- `theory-forge/docs/plans/08_ac14_codegen_integration.md` — theory-forge side

## Files That Will Be Affected (Plan #150, not this plan)

- `ac14/benchmarks/information_theory_shannon/` — new benchmark directory
  - `structured_spec_input.yaml` — theory as AC14 structured spec
  - `runtime_cases.json` — golden test cases from v15 schema
- `ac14/docs/plans/150_theory_forge_information_theory_benchmark.md` — impl plan

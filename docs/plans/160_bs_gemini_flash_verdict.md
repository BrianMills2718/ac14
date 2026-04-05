# Plan #160: Black-Scholes Gemini Flash Gate Verdict — Inconclusive (4/5 vs 5/5)

**Status**: Complete  
**Started**: 2026-04-04  
**Completed**: 2026-04-04

---

## Gate Results

Output: `.ac14_out/bs_gate_gemini_flash/`  
Model: `gemini/gemini-2.5-flash-lite`  
Benchmark: `black_scholes_greeks_structured_spec_v1` (10 components)

| Metric | AC14 | Monolithic |
|--------|------|------------|
| Successes | 4/5 | 5/5 |
| Front-half successes | 5/5 | N/A |
| Avg repair loops | 1.4 | 0.0 |
| Avg semantic score | 1.67 | 2.0 |
| Total cost | $0.448 | $0.067 |

**Verdict**: `inconclusive` — success gap is ≤1 trial, mixed secondary metrics.

---

## Failure Analysis

### Trial 3 (AC14 failed)
- Front-half passed on all 3 attempts
- Packet tests failed: `disc` field = 1.0 (expected 0.0), `rho_put` formula wrong
- Runtime outputs failed on all 3 attempts — `rho_put` errors persisted
- Failure: Gemini flash generated wrong rho_put formula variant and wrong disc value

### Trials 1, 2, 5 (AC14 passed via repair)
- Front-half passed on attempt 1
- Packet tests failed on all attempts (recomposition_passed=False consistently)
- Runtime outputs failed on attempts 1-2, passed on final attempt
- Pattern: 2-3 repair loops needed to get runtime correct

### Trial 4 (AC14 passed first attempt)
- Front-half passed, runtime passed on attempt 1
- Still no recomposition pass (packet-level tests harder than runtime)

---

## Key Finding: Packet Tests Always Fail

In every trial, `recomposition_passed=False`. AC14 only "passes" when runtime outputs
eventually succeed. This means:

1. The packet-level tests are correctly catching real formula bugs
2. Repair loops use runtime feedback to fix code, not packet test feedback  
3. The benchmark's packet fixtures expose subtle formula variants (theta sign, rho sign, disc handling) that LLMs get wrong under decomposition

**AC14's packet tests are a stricter gate than monolithic's runtime test** — which is
actually the design intent. But they're causing more repair loops with weaker models.

---

## Benchmark Series Summary (Through BS Gemini Flash)

| Gate | Model | AC14 | Mono | Verdict |
|------|-------|------|------|---------|
| IT gate_1 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| PT gate_2d | gpt-4.1 | 5/5 | 5/5 | monolithic_wins (efficiency) |
| PT Gemini flash | gemini-2.5-flash-lite | 2/5 | 5/5 | monolithic_wins |
| BS gate_1 | gpt-4.1 | 5/5 | 5/5 | inconclusive |
| BS Gemini flash | gemini-2.5-flash-lite | 4/5 | 5/5 | inconclusive |

---

## Interpretation

### What the data shows:
1. With gpt-4.1 (strong model), both approaches perform equally on all tried benchmarks — known math formulas are memorized; decomposition adds cost without benefit
2. With Gemini flash (weaker model), monolithic is more robust for PT (5 components) and slightly better for BS (10 components) — the weaker model handles decomposition less gracefully
3. AC14's front-half (blueprint generation) succeeds reliably — the weakness is code generation quality with weaker models
4. AC14 cost overhead vs monolithic: 4-8x for these benchmarks

### Thesis status:
The AC14 thesis requires finding tasks where decomposition provides measurable advantage.
All current benchmarks use well-known mathematical formulas that LLMs can implement
monolithically even at 10+ components. The model capability hypothesis is partially
falsified — even Gemini flash handles BS monolithically (5/5).

**The untested dimension**: specifications that are TOO LARGE for effective single-context
reasoning. Current benchmarks are 4-10 components with well-known formulas. The thesis
may require either:
1. Novel/obscure formulas not memorized in training data
2. Very large specifications (20-50 components) that stress context limits
3. Specification-level ambiguity that benefits from component-level clarification

---

## Next Plan: Design Harder Benchmark

**Plan #161**: Design a benchmark that specifically targets one of:
1. **Large specification** (20+ components) — tests context capacity
2. **Novel formulas** (obscure domain, made-up physics) — tests generalization
3. **Cross-component invariants** (conservation laws, consistency constraints) — tests decomposition-mediated constraint satisfaction

Acceptance criteria for next benchmark: mono should fail ≥1/5 trials with gpt-4.1,
demonstrating a genuinely hard task.


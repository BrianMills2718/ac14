# Plan #157: Theory Forge Model-Capability Comparison

**Status:** Planned
**Type:** experiment
**Priority:** High
**Blocked By:** 156
**Blocks:** 158

---

## Goal

Test the AC14 thesis directly: does decomposition help when the **model is weaker**?

The PT gate_2d result shows gpt-4.1 passes 5/5 monolithic WITH 0 repair loops.
The thesis is not "AC14 helps strong models on easy problems" — it is "AC14 helps
when context pressure exceeds a model's capacity."

We need to test: does AC14 decomposition enable a weaker model to pass PT when
monolithic cannot?

---

## Experimental Design

### Benchmark
`benchmarks/prospect_theory_tk1992` — same 5-component piecewise math benchmark.
Already verified: gpt-4.1 passes 5/5 monolithic.

### Hypothesis
On a weaker model (gemini-2.5-flash-lite), monolithic will fail some PT trials
while AC14 will pass more. The piecewise parameter-confusion traps in PT are
designed for exactly this test.

### Conditions
- **Model A (weak)**: `gemini/gemini-2.5-flash-lite` — fast, cheap, known to struggle
  on complex math pipelines (gate_1 showed 5/5 mono vs 1/5 AC14 on this model;
  gate_1 AC14 failure was harness bugs, not model capability)
- **Model B (medium)**: `openai/gpt-4.1-mini` — cheaper than gpt-4.1, test midpoint
- **Comparison**: run 5-trial front-half-first gate on BOTH models; compare AC14 vs mono

### If hypothesis holds:
- gemini-flash: mono fails (say 2/5), AC14 passes (say 4/5) → `ac14_wins`
- This validates the thesis: decomposition helps on the exact benchmark where
  a weaker model breaks down

### If hypothesis fails:
- gemini-flash: both fail similarly (both 0-1/5) → AC14 doesn't recover failures
- This means the bottleneck is not context pressure but raw model capability
- Then we need a harder benchmark (Direction A from Plan #156)

---

## Implementation Steps

### Step 1: Run PT gate on gemini-flash (5 trials)

```bash
make front-half-first-full-trials \
  BENCHMARK=benchmarks/prospect_theory_tk1992 \
  OUTPUT=.ac14_out/pt_gate_gemini_flash \
  TRIALS=5 MAX_ATTEMPTS=3 \
  MODEL=gemini/gemini-2.5-flash-lite \
  MAX_BUDGET=0.50
```

Note: The structured_spec front-half uses the same MODEL for both front-half and codegen.
This tests whether gemini-flash can both generate blueprints AND correct code.

### Step 2: Read verdict

If `monolithic_wins` (mono passes, AC14 fails): confirms thesis, gemini-flash benefits from decomposition.
If `inconclusive` or `ac14_wins`: record and move to IT benchmark comparison.

### Step 3 (optional): Run IT gate on gemini-flash (5 trials)

Information Theory is simpler (4 components, explicit log2 requirement).
If gemini-flash passes both IT and PT with AC14 but fails without, that maps
the capability-decomposition boundary.

```bash
make front-half-first-full-trials \
  BENCHMARK=benchmarks/information_theory_shannon \
  OUTPUT=.ac14_out/it_gate_gemini_flash \
  TRIALS=5 MAX_ATTEMPTS=3 \
  MODEL=gemini/gemini-2.5-flash-lite \
  MAX_BUDGET=0.50
```

---

## Expected Outcomes

| Scenario | AC14 (gemini) | Mono (gemini) | Meaning |
|----------|---------------|---------------|---------|
| Thesis confirms | 4-5/5 | 1-2/5 | Decomposition bridges model gap |
| Partial support | 3/5 | 1/5 | AC14 helps but not decisively |
| Thesis fails | 0-1/5 | 0-1/5 | Raw model capability is floor |
| Surprising win | 5/5 | 5/5 | gemini-flash is also tractable |

---

## What We're NOT Doing

- **Not building a new benchmark** (Plan #156 recommended Direction B first)
- **Not changing the evaluation infrastructure** (it works)
- **Not running gpt-4.1-mini yet** (test gemini-flash first for maximum contrast)

---

## Acceptance Criteria

- [ ] PT gate on gemini-flash (5 trials) with `front-half-first-full-trials` complete
- [ ] Verdict read and interpreted
- [ ] If `monolithic_wins` and gemini-flash AC14 passes more: thesis validated
- [ ] Plan #158 written based on verdict

---

## References

- `docs/plans/156_pt_gate_2d_verdict.md` — gpt-4.1 gate_2d verdict
- `docs/plans/153_prospect_theory_benchmark.md` — PT benchmark design
- `.ac14_out/pt_gate_2d/front_half_first_decision.json` — gpt-4.1 baseline

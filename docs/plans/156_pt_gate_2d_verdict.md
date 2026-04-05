# Plan #156: PT Gate_2d Verdict Interpretation

**Status:** Complete
**Type:** verdict
**Priority:** High
**Blocked By:** 155
**Blocks:** 157

---

## Gate_2d Result

**Command run:**
```
python3 -m ac14 front-half-first-full-trials benchmarks/prospect_theory_tk1992 \
  --output-dir .ac14_out/pt_gate_2d --trials 5 --max-attempts 3 \
  --model openai/gpt-4.1 --max-budget 1.50
```

**Verdict: `monolithic_wins`** — both conditions passed 5/5 trials; monolithic won on secondary metrics.

| Metric | AC14 | Monolithic |
|--------|------|-----------|
| Successes | 5/5 | 5/5 |
| Front-half successes | 5/5 | 0/5 |
| Avg repair loops | 0.4 | **0.0** |
| Avg semantic score | 1.0 | 1.0 |
| Total cost | $0.18 | **$0.10** |
| Avg duration | 92s | **13s** |

Rationale: "The conditions tied on success, but the monolithic condition matched
semantic quality and used fewer repair loops."

---

## Full Gate_2 History

| Gate | Model | AC14 | Mono | Verdict | Root cause of AC14 failures |
|------|-------|------|------|---------|----------------------------|
| gate_1 | gemini-2.5-flash | 1/5 | 5/5 | monolithic_wins | Context wiring: no hint rules, wrong fixture format |
| gate_2 | gpt-4.1 | 1/5 | 2/5 | inconclusive | Partial codegen (only last component generated) |
| gate_2b | gpt-4.1 | 0/5 | 1/5 | inconclusive | Front-half blocked on list type + partial codegen |
| gate_2c | gpt-4.1 | 1/5 | 5/5 | monolithic_wins | E-B1-SCHEMA-FIELD-REF-MISSING (list schema) |
| **gate_2d** | **gpt-4.1** | **5/5** | **5/5** | **monolithic_wins** | **Tied on correctness; mono wins on repair loops** |

---

## Interpretation

### Primary finding: Prospect Theory is tractable for gpt-4.1 monolithic

Both conditions pass 5/5 runtime correctness tests. The PT benchmark — piecewise
value function with different exponents, two distinct probability weighting functions,
sign-dependent certainty equivalent inversion — does NOT create context pressure that
overwhelms a capable single-context model (gpt-4.1).

This is consistent with the prior benchmark arc:

| Gate | Benchmark | AC14 | Mono | Verdict |
|------|-----------|------|------|---------|
| gate_5 | resource_scaling (10 trials) | 10/10 | 10/10 | inconclusive |
| it_gate_1 | information_theory | 5/5 | 5/5 | inconclusive |
| **pt_gate_2d** | **prospect_theory** | **5/5** | **5/5** | **monolithic_wins** |

**Pattern:** The capabilities of gpt-4.1 are sufficient for all benchmarks tried so far.
The thesis requires a benchmark where the model fails WITHOUT decomposition.

### Secondary finding: AC14 adds overhead but not correctness on tractable benchmarks

On the hardest tractable benchmark so far (PT), monolithic achieved 0 repair loops
while AC14 needed 0.4 average. This means 2/5 AC14 trials needed a repair attempt
that monolithic didn't. AC14 is 1.8× more expensive and 7× slower.

On the flip side: **AC14 still achieves 5/5** — decomposition does not impede
correctness. It adds structured reasoning overhead that paid off on less capable
models (gatess 1-3 on resource_scaling with gemini-flash) but gpt-4.1 doesn't need it.

### Thesis implication

The AC14 thesis is specifically about benchmarks "where monolithic breaks down." We
have not yet found a benchmark where this happens with gpt-4.1. Options:

1. **Model regression testing** — verify AC14 still helps weaker models (gemini-flash)
   on the same benchmarks where it helped before
2. **Harder benchmark** — need a pipeline with more simultaneous interdependencies
   than a 5-component math pipeline
3. **Adversarial spec** — a requirements doc that is intentionally ambiguous in ways
   that require component isolation to resolve correctly

### What makes Prospect Theory still "easy" for monolithic?

1. Only 5 components — easily fits in a single window
2. Exact formula in `requirements.md` + `structured_spec` — no ambiguity left
3. Python `**` operator maps directly to the math — minimal translation error
4. Well-known algorithm — gpt-4.1 likely trained on PT implementations

---

## Progress Arc

| Gate | Benchmark | AC14 | Mono | Verdict |
|------|-----------|------|------|---------|
| gate_2 (3 trials) | resource_scaling | 2/3 | 3/3 | inconclusive |
| gate_3 (5 trials) | resource_scaling | 4/5 | 5/5 | inconclusive |
| gate_4 (5 trials) | resource_scaling | 4/5 | 5/5 | inconclusive |
| gate_5 (10 trials) | resource_scaling | 10/10 | 10/10 | inconclusive |
| it_gate_1 (5 trials) | info_theory | 5/5 | 5/5 | inconclusive |
| pt_gate_1 (5 trials) | prospect_theory | 1/5 | 5/5 | monolithic_wins (infra bug) |
| **pt_gate_2d (5 trials)** | **prospect_theory** | **5/5** | **5/5** | **monolithic_wins (secondary)** |

The pattern is clear: with gpt-4.1, both systems converge on the same correctness.
The interesting signal is that AC14 needed 0.4 repair loops on PT while mono needed 0.

---

## Next Step

**Plan #157: Theory Forge harder benchmark OR model-budget comparison.**

Two candidate directions:

### Direction A: Harder benchmark
Design a benchmark where the number of interacting formulas or the cross-component
invariant complexity genuinely exceeds what a single context window can hold cleanly.
Candidate: **Stochastic Dominance** or **Expected Utility with multiple risk orderings**
(10+ components, mutually referential invariants).

### Direction B: Model comparison across capability tiers
Use the PT benchmark to test whether AC14 helps on WEAKER models. If gemini-flash
fails PT monolithic but passes PT with AC14 decomposition, that validates the thesis
on a real benchmark.

**Recommended: Direction B first** — it uses existing benchmarks and tests the
specific thesis claim directly. Direction A risks building more benchmarks before
understanding why the thesis claim needs stronger evidence.

---

## Acceptance Criteria

- [x] Gate_2d full 5-trial run complete
- [x] Verdict read from `front_half_first_decision.json`: `monolithic_wins`
- [x] Both conditions: 5/5 successes (primary metric tied)
- [x] Secondary metrics analyzed: mono wins on repair loops (0.0 vs 0.4)
- [x] Progress arc updated with pt_gate_2d result
- [x] Thesis implication stated clearly
- [x] Next plan direction documented

---

## References

- `.ac14_out/pt_gate_2d/front_half_first_decision.json` — verdict artifact
- `.ac14_out/pt_gate_2d_smoke/smoke_readiness_report.json` — smoke passed
- `docs/plans/155_pt_gate_2_repair_and_rerun.md` — repairs
- `docs/plans/154_pt_gate_1_verdict.md` — gate_1 root cause (infra bugs)
- `docs/plans/152_it_gate_1_verdict.md` — IT gate context

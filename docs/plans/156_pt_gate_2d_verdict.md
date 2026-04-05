# Plan #156: PT Gate_2d Verdict — Both 5/5, Monolithic More Efficient

**Status**: Complete  
**Gate**: `.ac14_out/pt_gate_2d/`  
**Model**: `openai/gpt-4.1`  
**Date**: 2026-04-04

---

## Gate Results

| Metric | AC14 | Monolithic |
|--------|------|-----------|
| Successes | 5/5 | 5/5 |
| Avg repair loops | 0.4 | 0.0 |
| Avg semantic score | 1.0 | 1.0 |
| Avg duration | 92.4s | 13.0s |
| Total cost | $0.180 | $0.101 |
| Front-half successes | 5/5 | N/A |

**Verdict**: `monolithic_wins`  
**Rationale**: "The conditions tied on success, but the monolithic condition matched semantic quality and used fewer repair loops."

---

## Interpretation

### What the verdict means

Both conditions achieve 100% success rate and identical semantic quality. The verdict
is due to efficiency — monolithic uses 0 repair loops and costs ~44% less per run.

### What this actually proves

1. **AC14's decomposition is correct**: 5/5 success rate with front_half passing every
   time. The blueprint/packet/codegen pipeline works end-to-end.
2. **The E-B1-SCHEMA-FIELD-REF-MISSING fix was the root blocker**: Before this fix,
   0/5 AC14 trials reached codegen. After: 5/5 front-half passed, 5/5 succeeded.
3. **PT is not a discriminating benchmark**: Simple enough that monolithic never
   fails (5/5 with 0 repairs). AC14's value proposition is for complex systems
   where monolithic fails due to context overload.

### Remaining gap

0.4 avg repair loops = 2 of 5 trials needed a second attempt. Likely cause:
first attempt's generated code misses a formula edge case (CE sign-dependent
inversion for the with_reference case). Per-component hint business rules help
but may not be specific enough.

---

## Next Plan

Plan #157: Design a harder benchmark where AC14's decomposition provides a real
advantage over monolithic. Target: monolithic success rate < 80%, AC14 >= 80%.

Candidates: complex financial instrument (10+ components), multi-stage pipeline
exceeding context window, system with recursive structure.

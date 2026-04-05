# Plan #148: Gate_5 — Ten-Trial Statistical Confirmation

**Status:** Planned
**Type:** evaluation
**Priority:** High
**Blocked By:** None
**Blocks:** 149

---

## Gap

**Current:** gate_4 produced `inconclusive` (4/5 AC14, 5/5 mono). The single AC14
failure (trial_4) exhausted all 3 retries — syntax error on attempt_3. 5 trials
is too few to distinguish generation variance from a systematic 20% gap.

**Target:** Run 10 trials to get a cleaner statistical read before moving on to
Theory Forge. Context traces from Plan #147 mean any failure is immediately
diagnosable without a new plan.

---

## Acceptance Criteria

- [ ] gate_5 run at `.ac14_out/front_half_first_full_gate_5/` TRIALS=10 MAX_BUDGET=1.50
- [ ] Decision artifact persisted
- [ ] `make context-audit OUTPUT=.ac14_out/front_half_first_full_gate_5` run on any failures
- [ ] Verdict interpreted per branch matrix below

---

## Command

```bash
make front-half-first-full-trials \
  BENCHMARK=benchmarks/resource_scaling_structured_spec \
  OUTPUT=.ac14_out/front_half_first_full_gate_5 \
  TRIALS=10 MAX_ATTEMPTS=3 MAX_BUDGET=1.50
```

---

## Branch Matrix

| AC14 successes | Interpretation | Next |
|----------------|---------------|------|
| 9-10/10 | Variance confirmed — near-parity is real | Proceed to Plan #149 (Theory Forge) |
| 7-8/10 | Systematic 15-20% gap — run `context-audit` on failures, diagnose with traces | Plan #150: targeted fix based on audit |
| ≤6/10 | Regression — something is wrong with the pipeline | Plan #150: regression diagnosis |

Monolithic 10/10 is expected. If monolithic drops below 9/10, investigate spec
issues first (this benchmark should be deterministic for monolithic).

---

## Notes

Plan #147 context traces apply. Every generated component will have
`{component_id}.context.json` and `{component_id}.prompt.json` in `generated/`.
Any AC14 failure: run `make diagnose-attempt OUTPUT=... TRIAL=N ATTEMPT=M` before
writing a diagnosis plan.

---

## Files Affected

- None (evaluation only)

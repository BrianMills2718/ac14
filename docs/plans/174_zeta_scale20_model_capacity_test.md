# Plan #174: Zeta Scale-20 — Model Capacity Test

**Status:** PLANNED
**Type:** empirical
**Priority:** High
**Blocked By:** Plan #173 (verdict complete)
**Blocks:** Plan #175 (pivot decision)

---

## Gap

**Current:** Both AC14 and monolithic pass 10/10 on zeta_scale_20 with Gemini flash.
No hard-harness discrimination at 20 components with this model.

**Target:** Test whether model capacity (not scale) is the discriminating factor.
Run zeta_scale_20 with `claude-haiku-4-5-20251001` — a weaker model that may fail
monolithically at 20 components while AC14 succeeds component-by-component.

**Why:** Plan #173 verdict showed scale_20 + Gemini flash = both pass. If haiku fails
monolithically but AC14 succeeds, that confirms the discrimination mechanism is
model-capacity dependent, not just scale. This determines whether to build scale_50
(expensive, several days) or to find a weaker model (cheap, uses existing benchmark).

---

## Hypothesis

H1 (capacity hypothesis): Haiku fails monolithic at 20 components due to context/
capacity pressure. AC14 succeeds because each component packet is within haiku's capacity.

H2 (null): Haiku also passes both, discrimination requires scale >> 20.

---

## Execution

### Smoke Gate

```bash
make front-half-first-smoke-gate \
  BENCHMARK=benchmarks/zeta_scale_20 \
  OUTPUT=.ac14_out/zeta_scale20_haiku_smoke \
  MODEL=claude-haiku-4-5-20251001 \
  MAX_BUDGET=2.00 \
  MAX_ATTEMPTS=3
```

Accept `ready_for_full_trials` or diagnose blocker.

### Full Gate (if smoke clears)

```bash
make front-half-first-full-trials \
  BENCHMARK=benchmarks/zeta_scale_20 \
  OUTPUT=.ac14_out/zeta_scale20_haiku_gate \
  MODEL=claude-haiku-4-5-20251001 \
  TRIALS=5 \
  MAX_BUDGET=2.00 \
  MAX_ATTEMPTS=3
```

5 trials sufficient for initial signal.

---

## Verdict Branches

| Verdict | Interpretation | Next Plan |
|---------|---------------|-----------|
| `ac14_wins` | Capacity hypothesis confirmed at 20 components | Plan #175: Document threshold finding, consider series complete |
| `monolithic_wins` | Haiku fails mono at 20 components, AC14 wins | Plan #175: Document — threshold is model-capacity + scale interaction |
| `inconclusive` | Both pass or both fail equally | Plan #175: Scale_50 is the next test, or declare series complete |

---

## Acceptance Criteria

1. Smoke artifact at `.ac14_out/zeta_scale20_haiku_smoke/smoke_readiness_report.json`
2. If smoke clears: full gate artifact at `.ac14_out/zeta_scale20_haiku_gate/`
3. Plan #175 created with next direction

---

## Cost Estimate

- Haiku is significantly cheaper than Gemini flash
- 5-trial gate: estimated $0.10-0.30 total
- Risk: haiku may refuse to generate code in the expected format

---

## Circuit Breaker

If haiku smoke gate fails with infrastructure errors (not runtime mismatches), do NOT
spend the 5-trial budget. File as `blocked_on_model_capability` and proceed to:
- Either build scale_50 (Option A from Plan #173)
- Or declare Theory Forge series complete (Option C from Plan #173)

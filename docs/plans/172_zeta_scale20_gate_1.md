# Plan #172: Zeta Scale-20 Gate_1 — Smoke + Full Trial

**Status:** ACTIVE
**Type:** empirical
**Priority:** High
**Blocked By:** None (zeta_scale_20 benchmark B1 passes)
**Blocks:** Plan #173 (verdict interpretation)

---

## Gap

**Current:** `benchmarks/zeta_scale_20/` blueprint passes B1 validation. No empirical
comparison run yet. Gate_3 (10-trial Gemini flash, zeta_options 10-component) confirmed
`monolithic_wins` (9/10 vs 6/10).

**Target:** First empirical comparison on the 20-component benchmark with Gemini flash,
to test whether scale_20 is enough to discriminate.

**Why:** Theory Forge evidence (Plans #149-#170) shows monolithic wins consistently at
10-component scale. The central question is: what scale threshold causes context pressure
to hurt monolithic generation? Scale_20 is the first test.

---

## Gate_3 Summary (Context)

| Metric | AC14 | Monolithic |
|--------|------|------------|
| Successes | 6/10 | 9/10 |
| Front-half successes | 10/10 | 0/10 |
| Cost | $1.45 | $0.36 |
| Verdict | LOSES | WINS |

Pattern: AC14 front-half (blueprint comprehension) is perfect. Runtime codegen still
under-performs. Consistent with Plans #162-#163.

---

## Smoke Phase (Gate_1a)

Run 1 trial with each condition on zeta_scale_20. Accept `ready_for_full_trials` only
if at least 1 AC14 runtime success, otherwise diagnose.

```bash
make front-half-first-smoke-gate \
  BENCHMARK=benchmarks/zeta_scale_20 \
  OUTPUT=.ac14_out/zeta_scale20_smoke_1 \
  MODEL=google/gemini-2.0-flash-001 \
  MAX_BUDGET=2.00 \
  MAX_ATTEMPTS=3
```

Expected: ~$0.50-$1.50 per trial (20 components vs 10).

### Smoke Verdict Branches

| Smoke verdict | Next action |
|--------------|-------------|
| `ready_for_full_trials` | Run 10-trial gate (Gate_1b) |
| `blocked_on_harness` | Diagnose and fix harness (Plan #173a) |
| `inconclusive` | Run 3-trial quick gate |

---

## Full Trial Phase (Gate_1b — if smoke clears)

```bash
make front-half-first-full-gate \
  BENCHMARK=benchmarks/zeta_scale_20 \
  OUTPUT=.ac14_out/zeta_scale20_gate_1 \
  MODEL=google/gemini-2.0-flash-001 \
  TRIALS=10 \
  MAX_BUDGET=3.00 \
  MAX_ATTEMPTS=3
```

### Expected Results

Given Theory Forge evidence, most likely:
- **`monolithic_wins`** (7-10/10 mono, 3-7/10 AC14): Scale-20 still within context capacity
- **`inconclusive`** (within 2 trials): Scale-20 marginal — need scale-50
- **`ac14_wins`** (unlikely): Scale-20 actually discriminates

### Pre-Defined Branches

| Verdict | Next plan |
|---------|-----------|
| `ac14_wins` | Plan #173: Write `ac14_wins` verdict, analyze what caused discrimination |
| `inconclusive` | Plan #173: Write verdict, recommend scale-50 or domain complexity |
| `monolithic_wins` | Plan #173: Write verdict, confirm scale-50+ threshold |

---

## Acceptance Criteria

1. Smoke artifact exists at `.ac14_out/zeta_scale20_smoke_1/smoke_readiness_report.json`
2. If smoke clears: full gate artifact at `.ac14_out/zeta_scale20_gate_1/front_half_first_decision.json`
3. Verdict doc written as Plan #173

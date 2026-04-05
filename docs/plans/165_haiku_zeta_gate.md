# Plan #165 — Zeta Options with Claude Haiku (Weakest Model Test)

## Status: ACTIVE

## Objective

Test whether claude-haiku-4-5 (the weakest available model) can still pass the
zeta options benchmark monolithically. If haiku fails monolithically but AC14
succeeds, we find the first `ac14_wins` verdict.

## Hypothesis

- haiku is weaker than Gemini flash
- Novel zeta/alpha formulas may overwhelm haiku's ability to track 10 components
- AC14 per-component packets (with local CRITICAL DIFFERENCE callouts) may help haiku
- Expected: haiku mono 2-3/5, AC14 3-4/5 → `ac14_wins`

## Command

```bash
make front-half-first-full-trials \
  BENCHMARK=benchmarks/zeta_options \
  OUTPUT=.ac14_out/zeta_haiku_gate_1 \
  MODEL=claude-haiku-4-5-20251001 \
  MAX_BUDGET=0.80 \
  TRIALS=5 \
  MAX_ATTEMPTS=3
```

Note: MAX_BUDGET=0.80 ensures AC14 planning step gets $0.40+ (needs $0.46 for Gemini flash;
haiku may cost less but using same budget for safety).

## Verdict Branch Tree

| Gate Verdict | Next Plan |
|-------------|-----------|
| ac14_wins | Write ADR + Plan #166 confirmation |
| inconclusive | Run 10-trial gate |
| monolithic_wins | Scale test design (50+ component benchmark) |


# Plan #163 — Zeta Options Gate with Gemini Flash

## Status: ACTIVE

## Objective

Run the zeta options benchmark with Gemini flash (not gpt-4.1) to test whether a weaker
model that failed PT can fail zeta options monolithically while AC14 succeeds.

## Hypothesis

- Gemini flash failed PT at 2/5 monolithic (Plan #158)
- Zeta options has harder formulas (novel zeta/alpha modifications to every formula)
- Monolithic Gemini flash may revert to standard BS formulas when not given per-component hints
- AC14 explicitly calls out each modification in component-level implementation_constraints
- If mono < AC14 on Gemini flash → first `ac14_wins` verdict

## Command

```bash
make front-half-first-full-trials \
  BENCHMARK=benchmarks/zeta_options \
  OUTPUT=.ac14_out/zeta_gemini_gate_1 \
  MODEL=gemini/gemini-2.5-flash \
  MAX_BUDGET=0.30 \
  TRIALS=5 \
  MAX_ATTEMPTS=3
```

## Acceptance Criteria

- `ac14_wins`: AC14 successes > mono by ≥2 → thesis validated for weak-model regime
- `inconclusive`: gap ≤1 → run 10-trial gate
- `monolithic_wins`: diagnose failure, consider even weaker model or larger system

## Verdict Branch Tree

| Smoke Verdict | Action |
|--------------|--------|
| blocked_on_front_half | Increase budget, re-run smoke |
| ready_for_full_trials | Run full 5-trial gate |

| Gate Verdict | Next Plan |
|-------------|-----------|
| ac14_wins | Write ADR, update CLAUDE.md, write Plan #164 confirmation |
| inconclusive | Run 10-trial gate, write Plan #164 verdict |
| monolithic_wins | Diagnose, consider haiku or larger system |


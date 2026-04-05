# Plan #156: PT Gate_2d Verdict Interpretation

**Status:** In Progress
**Type:** verdict
**Priority:** High
**Blocked By:** 155
**Blocks:** 157

---

## Gate_2d Setup

**Command run:**
```
python3 -m ac14 front-half-first-full-trials benchmarks/prospect_theory_tk1992 \
  --output-dir .ac14_out/pt_gate_2d --trials 5 --max-attempts 3 \
  --model openai/gpt-4.1 --max-budget 1.50
```

Gate_2d is the definitive gate after Plan #155 repairs:
1. `list`/`array` primitive types accepted by blueprint validator (validation.py)
2. Bare `list`/`array` draft values produce `[]` instead of `"draft_fieldname"` (draft_authoring.py)
3. Per-component hint business rules threaded to codegen LLM (generated_codegen.py)
4. Codex SDK `additionalProperties: false` fix (llm_codegen.py)
5. Model: `openai/gpt-4.1` (Codex credits exhausted)

---

## Gate_2d Progress (interim — gate still running)

| Trial | AC14 passed | Mono passed | AC14 attempts |
|-------|-------------|-------------|---------------|
| 1     | True        | True        | 1             |
| 2     | True        | True        | 2             |
| 3     | True        | True        | 1             |
| 4     | TBD         | TBD         | TBD           |
| 5     | TBD         | TBD         | TBD           |

---

## Full Gate_2 History (all variants)

| Gate | Model | AC14 | Mono | Verdict | Root cause of AC14 failures |
|------|-------|------|------|---------|----------------------------|
| gate_1 | gemini-2.5-flash | 1/5 | 5/5 | monolithic_wins | Context wiring: no hint rules, wrong fixture format |
| gate_2 | gpt-4.1 (?) | 1/5 | 2/5 | inconclusive | Partial codegen: only compute_certainty_equivalent generated |
| gate_2b | gpt-4.1 | 0/5 | 1/5 | inconclusive | Front-half blocked (list type) + partial codegen |
| gate_2c | gpt-4.1 | 1/5 | 5/5 | monolithic_wins | E-B1-SCHEMA-FIELD-REF-MISSING in front-half (list schema) |
| **gate_2d** | gpt-4.1 | **?/5** | **?/5** | **TBD** | Post all repairs |

---

## Verdict (TBD — fill in after gate completes)

```
<VERDICT PLACEHOLDER>
Monolithic: ?/5  AC14: ?/5  (5 trials)
```

---

## Interpretation (template — complete after verdict)

### If `ac14_wins`:

This would be the first decisive AC14 win on the Theory Forge benchmark series.
Root cause of monolithic failures: the piecewise value function with different
exponents for gains vs losses (α for gains, β for losses) plus two distinct
probability weighting functions (w+ with γ, w- with δ) created enough context
pressure that monolithic confused parameters or branches.

Next: Write ADR documenting the first AC14 win. Continue with a harder benchmark
(e.g., Cumulative Prospect Theory with rank-ordering, or a multi-agent contract).

### If `inconclusive`:

The gap is ≤1 trial. This is the strongest result yet but not decisive. The
secondary metrics (repair loops, semantic score) become the differentiator.

Next: Run a 10-trial statistical confirmation gate (same setup). Or tighten the
benchmark with more edge-case runtime tests.

### If `monolithic_wins`:

The Plan #155 repairs improved AC14 (3/3 completed trials all passed) but some
AC14 failure pattern remains. Diagnose the failing trials.

Likely remaining issues:
- Front-half LLM still generates structurally-incomplete blueprints on some runs
- Codegen produces mathematically-incorrect component code
- Monolithic context window adequate for 5-component PT pipeline

Next: Freeze a targeted repair boundary from the failing trial artifacts.

---

## Acceptance Criteria

- [x] Gate_2d smoke: `ready_for_full_trials` (confirmed — pt_gate_2d_smoke)
- [ ] Gate_2d full 5-trial run complete
- [ ] Verdict read from `front_half_first_decision.json`
- [ ] Secondary metrics analyzed (cost, repair loops, semantic score)
- [ ] Next plan written based on verdict branch

---

## References

- `.ac14_out/pt_gate_2d/front_half_first_decision.json` — verdict artifact
- `.ac14_out/pt_gate_2d_smoke/smoke_readiness_report.json` — smoke passed
- `docs/plans/155_pt_gate_2_repair_and_rerun.md` — repairs that enabled gate_2d
- `docs/plans/154_pt_gate_1_verdict.md` — gate_1 verdict (root cause analysis)
- `docs/plans/153_prospect_theory_benchmark.md` — benchmark design

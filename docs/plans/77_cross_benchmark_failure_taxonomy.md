# Plan #77: Cross-Benchmark Failure Taxonomy

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 76
**Blocks:** None

---

## Gap

**Current:** AC14 now has one `inconclusive` empirical gate, one decisive
`monolithic_wins` gate, and one non-winning post-loss smoke repair. The repo
states that another `resource_scaling_v1` micro-repair is not justified, but it
does not yet classify which failure surfaces are benchmark-local versus
generalizable.

**Target:** Build one explicit taxonomy across the current empirical evidence
that separates:

1. infrastructure/provider noise
2. generation-stability failures
3. packet-context insufficiency
4. semantic-coupling / business-rule grounding weakness
5. benchmark-local expectation quirks

Then freeze one next lane that targets only the reusable category that the
evidence actually supports.

**Why:** Without a cross-benchmark taxonomy, the project may oscillate between
benchmark-local tuning and vague strategic pivots. The next move should target
either a reusable weakness or an explicit claim-boundary adjustment, not habit.

---

## References Reviewed

- `.ac14_out/full_trials_gate_1/experiment_decision.json`
- `.ac14_out/full_trials_gate_2/experiment_decision.json`
- `.ac14_out/full_trials_gate_2_smoke_grounding1/smoke_readiness_report.json`
- `investigations/ac14/2026-04-02-resource-scaling-second-gate-diagnosis.md`
- `investigations/ac14/2026-04-02-resource-scaling-packet-context-diagnosis.md`
- `docs/plans/44_verdict_interpretation_and_next_horizon.md`
- `docs/plans/62_inconclusive_comparison_diagnosis.md`
- `docs/plans/76_second_gate_repair_boundary.md`

---

## Open Questions

### Q1: Which observed failure classes are genuinely reusable AC14 weaknesses?
**Status:** Open
**Why it matters:** The next lane should improve the system, not just the
current benchmark.

### Q2: Does the evidence support a reusable implementation repair, a claim-boundary adjustment, or a front-half-first pivot?
**Status:** Open
**Why it matters:** The next lane should respond to the actual empirical story.

---

## Files Affected

- `docs/plans/77_cross_benchmark_failure_taxonomy.md` (create)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Compare the first empirical gate, the second empirical gate, and the
   post-loss grounding smoke artifact.
2. Classify which failure surfaces are benchmark-local versus reusable AC14
   weaknesses.
3. Freeze one explicit next lane from that taxonomy and keep benchmark-local
   tuning frozen unless the taxonomy says otherwise.

---

## Required Tests

This is an evaluation/strategy lane. No code should land unless the taxonomy
explicitly justifies one reusable repair lane.

---

## Acceptance Criteria

- [ ] The repo has one explicit cross-benchmark failure taxonomy grounded in the
      current empirical artifacts.
- [ ] The repo states whether the next move is a reusable implementation repair,
      a claim-boundary adjustment, or a different empirical design.
- [ ] `resource_scaling_v1` benchmark-local micro-repairs remain frozen unless
      this plan produces explicit new evidence to reopen them.

---

## Notes

This plan exists to stop the project from drifting from "another local tweak"
to "another local tweak" after already recording a decisive harder-benchmark
loss.

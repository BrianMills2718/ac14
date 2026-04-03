# Plan #77: Cross-Benchmark Failure Taxonomy

**Status:** Complete
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
**Status:** Resolved
**Why it matters:** The next lane should improve the system, not just the
current benchmark.
**Resolution:** The reusable weakness is weak first-class rule grounding for
semantically coupled business logic inside bounded packets. The evidence does
not support packet-size insufficiency as the leading diagnosis, and it no
longer supports packet-level semantic review as the dominant blocker.

### Q2: Does the evidence support a reusable implementation repair, a claim-boundary adjustment, or a front-half-first pivot?
**Status:** Resolved
**Why it matters:** The next lane should respond to the actual empirical story.
**Resolution:** The next move should be one reusable implementation repair:
strengthen benchmark-agnostic rule grounding inside the packet/codegen surface,
then spend one bounded smoke rerun. If that still does not produce an AC14
hard-harness success, the next branch should be a strategic pivot or claim
boundary adjustment rather than more local tuning.

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

- [x] The repo has one explicit cross-benchmark failure taxonomy grounded in the
      current empirical artifacts.
- [x] The repo states whether the next move is a reusable implementation repair,
      a claim-boundary adjustment, or a different empirical design.
- [x] `resource_scaling_v1` benchmark-local micro-repairs remain frozen unless
      this plan produces explicit new evidence to reopen them.

---

## Notes

This plan exists to stop the project from drifting from "another local tweak"
to "another local tweak" after already recording a decisive harder-benchmark
loss.

## Implementation Summary (2026-04-02)

### Cross-Benchmark Taxonomy

1. **Infrastructure/provider noise**
   - real but secondary
   - affected some earlier live attempts and time/cost interpretation
   - not the dominant reason for the completed second-gate loss

2. **Generation-stability failures**
   - present in both conditions across the two gates
   - important observability and contract issue
   - not the dominant differentiator after the repair chain

3. **Packet-context insufficiency**
   - not the leading diagnosis on the harder second gate
   - packet-context review plus the bounded grounding repair indicate the
     failing packets already contain strong local schemas, fixtures,
     constraints, and neighboring summaries

4. **Semantic-coupling / business-rule grounding weakness**
   - the strongest reusable AC14 weakness
   - gate 1 surfaced shared business-rule mismatches before the runtime-first
     contract demoted packet-level noise
   - gate 2 surfaced repeated AC14 runtime misses in a tightly coupled business
     logic subgraph even after packet-context sufficiency was judged strong
   - the bounded post-loss grounding repair changed the failure surface, which
     is evidence that rule salience is the right repair family

5. **Benchmark-local expectation quirks**
   - real in both benchmarks
   - still present, but no longer the best next target after the boundary
     decision because the project now needs a reusable response

### Decision

- keep `resource_scaling_v1` benchmark-local micro-repairs frozen
- pursue one reusable implementation repair aimed at packet-local rule
  grounding
- use one bounded smoke rerun to determine whether that reusable repair earns
  another full-gate attempt
- if the smoke rerun still yields no AC14 hard-harness success, do not continue
  with more local repairs by default

### Frozen Next Chain

1. [Plan #78: Reusable Packet Rule Grounding](/home/brian/projects/ac14/docs/plans/78_reusable_packet_rule_grounding.md)
2. [Plan #79: Post-Grounding Smoke Rerun](/home/brian/projects/ac14/docs/plans/79_post_grounding_smoke_rerun.md)
3. if Plan #79 shows AC14 hard-harness success and no infrastructure
   contamination -> [Plan #80: Second-Gate Full Rerun](/home/brian/projects/ac14/docs/plans/80_second_gate_full_rerun.md)
4. otherwise -> [Plan #81: Post-Grounding Strategic Pivot](/home/brian/projects/ac14/docs/plans/81_post_grounding_strategic_pivot.md)

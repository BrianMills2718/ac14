# Plan #62: Inconclusive Comparison Diagnosis

**Status:** Complete
**Type:** evaluation + planning
**Priority:** Critical
**Blocked By:** None
**Blocks:** 63, 37

---

## Gap

**Current:** The first five-trial monolithic-vs-AC14 comparison finished with
an `inconclusive` verdict. The project has no explicit diagnosis of why the
benchmark failed to separate the conditions or what the next empirical horizon
should be.

**Target:** Diagnose the tie using the persisted full-trial artifacts, separate
shared benchmark-local failures from condition-specific strengths and weaknesses,
and freeze the next empirical direction clearly enough that AC14 does not drift
back into endless micro-repair loops.

**Why:** An inconclusive result is real evidence, but it only helps if the next
move is grounded in that evidence rather than in optimism or inertia.

---

## References Reviewed

- `docs/plans/38_empirical_comparison_gate.md`
- `docs/plans/39_monolithic_vs_ac14_comparison_execution.md`
- `docs/plans/43_full_trial_gate.md`
- `docs/plans/44_verdict_interpretation_and_next_horizon.md`
- `.ac14_out/full_trials_gate_1/experiment_decision.json`
- `.ac14_out/full_trials_gate_1/trial_*/paired_trial_report.json`
- `docs/AC14_ROADMAP.md`
- `docs/AC14_IMPLEMENTATION_STATUS.md`
- `docs/UNCERTAINTIES.md`

---

## Open Questions

### Q1: Should `inconclusive` be treated as a soft AC14 win because monolithic was not clearly better?
**Status:** Resolved
**Decision:** No. The result must stay `inconclusive` unless the frozen decision rule says otherwise.

### Q2: Should the next lane continue repairing the current benchmark until AC14 wins?
**Status:** Resolved
**Decision:** No. The current benchmark is now one completed data point. The next lane should diagnose what the benchmark is actually measuring and freeze a sharper next comparison direction rather than spending more time squeezing small local repairs out of the same benchmark by default.

### Q3: Should notebook remediation be folded into this diagnosis plan?
**Status:** Resolved
**Decision:** No. Notebook remediation remains a separate post-verdict documentation/process lane in Plan #61.

---

## Files Affected

- `docs/AC14_ROADMAP.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)
- `docs/plans/62_inconclusive_comparison_diagnosis.md` (modify)

---

## Plan

### Steps

1. Summarize the five-trial result from the decision artifact and paired-trial artifacts.
2. Separate shared failure patterns from AC14-specific and monolithic-specific failures.
3. State plainly what the current benchmark did and did not prove about the thesis.
4. Freeze the next empirical direction in the active docs.
5. Keep unrelated blocked propagation plans blocked.

---

## Required Tests

No new unit tests. The acceptance surface is the persisted full-trial artifact
plus truthful documentation updates.

---

## Acceptance Criteria

- [x] The docs state clearly that the first empirical gate was inconclusive.
- [x] The docs distinguish shared benchmark-local failure patterns from
  condition-specific ones.
- [x] The next empirical horizon is explicit and does not default to more local
  benchmark tuning by inertia.
- [x] Blocked propagation lanes remain subordinate to the empirical follow-up.

---

## Implementation Summary (2026-04-02)

### Five-Trial Result

- AC14: 2/5 successful trials
- monolithic: 2/5 successful trials
- average repair loops: 1.6 (both conditions identical)
- average semantic score: 2.0 (both conditions identical)
- monolithic was faster and cheaper on this benchmark

### Diagnosis

**Dominant failure mode: packet-test failures in both conditions.**

Packet tests failed at similar rates for both conditions for two distinct
reasons:

1. **Categorical mismatches** (shared, not condition-specific):
   - `inventory_risk_evaluator` produces `inventory_risk_band='moderate'` when
     `'low'` is expected for the shipping-delay case (no shortage present)
   - `factor_correlator` produces `escalation_required=True` when `False` is
     expected for standard shipping-delay routing
   - These are generation quality issues that surface in both conditions and
     are not caused by the decomposition architecture per se

2. **LLM packet-eval over-strictness** (evaluator noise, not generation
   quality):
   - The packet-level LLM judge rejected semantically correct but
     differently-phrased `reason` text (e.g., "shortage requires partial
     fulfillment or back-order" rejected when gold standard says "shortage is
     large enough to threaten the order promise")
   - This adds non-deterministic noise that swamps decomposition signal

**Runtime outputs pass in virtually all attempts.** All three cases (ORX-100,
ORX-101, ORX-102) produced correct final system outputs in nearly every
attempt, including attempts where packet tests failed.

**The success criterion masked the real signal.** Because trial success
required ALL of packet tests + recomposition + runtime outputs + semantic
review to pass, packet-level failures blocked what were otherwise correct
end-to-end runs. The metric that matters for the decomposition thesis — does
the generated system produce correct final outputs — was almost uniformly
passing for both conditions.

**The benchmark did not test decomposition quality cleanly.** Both conditions
tied not because they performed equally, but because packet-level intermediate
test failures dominated the signal and affected both conditions at similar
rates. Those failures are a mix of generation quality issues and evaluator
noise, not a clean test of whether decomposition outperforms monolithic context
management.

### What This Benchmark Did and Did Not Prove

Did prove:
- The harness infrastructure works end-to-end for five paired trials
- Both conditions can produce correct final outputs for all three runtime cases
- The benchmark is real and reviewable, not just instrumentation

Did not prove:
- That decomposition beats monolithic context management at runtime correctness
- That decomposition loses
- That the current packet-level LLM eval is a reliable signal about generation
  quality rather than a source of noise

### Next Empirical Direction

The next empirical direction is Plan #63: redesign the trial success criterion
so that runtime output correctness is the primary gate, and packet-level tests
are demoted to secondary diagnostic evidence only.

This gives a cleaner answer to the actual thesis question: does
blueprint-driven decomposition produce systems with more correct final outputs?
Packet-level intermediate test failures are useful diagnostic artifacts, but
they should not block the primary verdict when final system outputs are correct.

Plan #63 should:

1. Redefine trial success as: generation succeeds AND final runtime outputs
   match expected outputs (using LLM semantic eval for free-form fields in the
   final outputs only, not intermediate component outputs)
2. Retain packet tests as a logged diagnostic artifact, not a mandatory gate
3. Rerun the five-trial gate with this cleaner criterion
4. Record the new verdict

---

## Notes

The point of this plan is not to reopen the verdict. The point is to decide
what the project should learn from the verdict.

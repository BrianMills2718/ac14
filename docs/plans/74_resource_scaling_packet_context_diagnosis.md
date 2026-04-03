# Plan #74: Resource Scaling Packet-Context Diagnosis

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 73
**Blocks:** 75

---

## Gap

**Current:** The second-gate diagnosis shows that AC14 lost primarily on a
small cluster of semantically coupled components, but the repo still does not
know whether those misses came from insufficient packet-local context or from
poor use of already sufficient context.

**Target:** Produce one explicit diagnosis artifact for the failing component
cluster (`trend_evaluator`, `deploy_risk_evaluator`,
`recommendation_generator`, `decision_recorder`) that says whether packet
projection itself is insufficient for the benchmark rules.

**Why:** The next code lane should differ depending on the answer. If packets
are insufficient, AC14 needs context/packet work. If packets are sufficient,
the next lane should target prompt/schema grounding instead.

---

## References Reviewed

- `investigations/ac14/2026-04-02-resource-scaling-second-gate-diagnosis.md`
- `.ac14_out/full_trials_gate_2/trial_*/paired_trial_report.json`
- `benchmarks/resource_scaling/benchmark.yaml`
- `benchmarks/resource_scaling/blueprint/components.yaml`
- `benchmarks/resource_scaling/blueprint/validation.yaml`
- `ac14/packets.py`
- `ac14/codegen_context.py`

---

## Open Questions

### Q1: Does each failing component packet include the benchmark-local rules needed to succeed?
**Status:** Open
**Why it matters:** Missing rules in packet-local context would mean the current
decomposition projection is weaker than the benchmark requires.

### Q2: Are the failing rules present but not salient enough in schema/prompt surfaces?
**Status:** Open
**Why it matters:** If the rules are present, the next move is grounding or
generation repair rather than packet redesign.

---

## Files Affected

- `investigations/ac14/2026-04-02-resource-scaling-packet-context-diagnosis.md` (create)
- `docs/plans/74_resource_scaling_packet_context_diagnosis.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)

---

## Plan

### Steps

1. Inspect the frozen packets and codegen contexts for the failing component cluster.
2. Compare packet-local context against the benchmark rules and repeated mismatch lines.
3. Decide whether the next lane should be packet/context repair or prompt/schema grounding.

---

## Required Tests

This is an investigation lane. No new code is required unless the diagnosis
itself surfaces a bounded implementation fix that should be landed separately.

---

## Acceptance Criteria

- [x] One persisted packet-context diagnosis artifact exists for the failing component cluster.
- [x] The next recommended response is explicit: packet/context repair or prompt/schema grounding.

---

## Notes

This plan exists to stop the project from treating every benchmark failure as
just another prompt-tuning problem.

## Implementation Summary (2026-04-02)

The packet-context diagnosis artifact now exists at:

- `investigations/ac14/2026-04-02-resource-scaling-packet-context-diagnosis.md`

Conclusion:

- the failing packets are structurally sufficient for the benchmark cases
- the dominant weakness is uneven local rule salience, especially for
  `trend_evaluator` and `deploy_risk_evaluator`
- the next repair should target prompt/schema grounding, not packet redesign

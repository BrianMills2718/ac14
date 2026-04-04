# Plan #142: Front-Half-First Runtime Code Quality Boundary

**Status:** Planned
**Type:** investigation
**Priority:** Critical
**Blocked By:** 141
**Blocks:** 143

---

## Gap

**Current:** gate_2 shows AC14 generates correct blueprint structure (front_half_successes: 5/5)
but wrong component implementations (successes: 0/5). The generated code misapplies
business rules: wrong tier mappings, wrong actions, wrong strategy/cooldown.

**Target:** Diagnose the specific gap between what the packet context provides and
what the generated code produces. Freeze a concrete repair target.

---

## Acceptance Criteria

- [ ] The packet context content for evaluate_thresholds_and_policy is examined
- [ ] The specific rules that are being misapplied are enumerated
- [ ] The hypothesis for why the generated code gets them wrong is concrete
- [ ] A bounded repair target is explicit for Plan #143

---

## Execution Contract

1. Read the generated code for evaluate_thresholds_and_policy from a gate_2 trial
   (e.g., `.ac14_out/front_half_first_full_gate_2/trial_1/ac14/attempt_1/`)
2. Read the packet context YAML that was passed to generate that component
3. Identify which business rules are present in the context vs. which were missed
4. Note the specific misapplied rules (tier mapping, action selection, strategy/cooldown)
5. Enumerate the repair hypothesis: is this a context gap, a prompt gap, or a
   model capability gap?
6. Freeze as a concrete repair for Plan #143

---

## Files Affected

None — this is a read-only investigation.

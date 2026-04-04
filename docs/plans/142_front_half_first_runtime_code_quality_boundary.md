# Plan #142: Front-Half-First Runtime Code Quality Boundary

**Status:** Complete
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

- [x] The packet context content for evaluate_thresholds_and_policy is examined
- [x] The specific rules that are being misapplied are enumerated
- [x] The hypothesis for why the generated code gets them wrong is concrete
- [x] A bounded repair target is explicit for Plan #143

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

## Findings

### Root Cause: Structured Spec Business Rules Never Reach the Code Generator

**Primary cause: context gap.** The structured spec's `business_rules` list is never
passed to the code generator. Trace:

1. `structured_spec_artifact.json` contains the full 15-rule business rules list
   (THRESHOLD, ACTION, URGENCY, TIER MAPPING, DEPLOY RISK, TARGET ADJUSTMENT,
   MIN HEALTHY, AUTO SCALE ENABLED, REQUIRES APPROVAL, APPROVAL TIER, STRATEGY
   AND COOLDOWN, ALERT TIER, COMPLIANCE CONFLICT, AUTHORIZATION MODE, FINAL ACTION).

2. The frozen bundle `components.yaml` has `local_invariants: ["TODO: confirm local
   invariants before blueprint freeze"]` for ALL four components. The blueprint
   planner generated placeholder invariants — it was not instructed to translate
   business rules into per-component invariants.

3. `build_codegen_context()` (codegen_context.py:55) builds `CodegenContext` from
   the component packet. It copies `component.local_invariants` directly — meaning
   the context only sees the TODO placeholders.

4. `emit_generated_package()` (generated_codegen.py:79) calls `build_codegen_context(
   packet, packet_cases, repair_guidance)`. It takes no `structured_spec_business_rules`
   parameter. There is no path for structured spec rules to enter the codegen context.

5. `generate_component.yaml` prompt renders `local_invariants`, `packet_test_cases`,
   and `rule_grounding_summaries`. With TODO invariants and placeholder expected
   outputs (`draft_action`, `draft_alert_tier`, etc.), the LLM has no real
   business rule grounding and generates simplified placeholder logic.

6. Packet test cases compound the gap: `packet_test_report.json` shows expected
   values like `scaling_decision.action expected='draft_action'` — the fixture
   generator produced placeholder expected values. The `rule_grounding_summaries`
   built from these say "expect action='draft_action'" — zero signal.

### Misapplied Rules Enumerated

From trial_1/attempt_1 runtime failures:

- **RSC-100**: action=`scale_up` (correct) but approval_tier=`manager` (expected `auto`);
  authorization_mode=`manual` (expected `auto`); cooldown=`10` (expected `5`);
  min_healthy=`2` (expected `3`); requires_approval=`True` (expected `False`)
- **RSC-101**: alert_tier=`critical` (expected `info`); cooldown=`30` (expected `10`);
  scale_tier=`premium` (expected `budget` — bronze→budget mapping hardcoded wrong);
  strategy=`emergency_scale` (expected `deferred` — not a valid schema value);
  urgency=`high` (expected `medium`)

The code explicitly comments "In a real scenario, this would involve complex rule
evaluation" and hardcodes `scale_tier = 'premium'` regardless of service_tier.
The bronze→budget, silver/gold→standard, platinum→premium tier mapping was not
applied at all.

### Hypothesis: Context Gap (Not Model Capability Gap)

This is a **context gap**, not a model capability gap. Evidence:

- The monolithic generator receives `structured_spec_input.yaml` business rules
  directly in its prompt (`generate_monolithic_runtime_system_from_structured_spec.yaml`).
  It succeeds 5/5 trials with the same model (gemini-2.5-flash-lite).
- AC14's code generator receives identical schemas but NO business rules — only
  TODO invariants and placeholder expected values.
- The LLM explicitly acknowledges the placeholder logic with comments — it knows
  it doesn't have the information needed.

---

## Repair Target for Plan #143

**Minimal bounded repair: inject structured spec business rules into the codegen context.**

Changes:
1. `ac14/codegen_context.py`: Add
   `structured_spec_business_rules: list[str] = Field(default_factory=list)`
   to `CodegenContext`. Add optional `structured_spec_business_rules: list[str] | None`
   to `build_codegen_context()`.
2. `ac14/generated_codegen.py`: Add optional
   `structured_spec_business_rules: list[str] | None = None` to both
   `emit_generated_package()` and `aemit_generated_package()`. Pass to
   `build_codegen_context()`.
3. `ac14/front_half_first_empirical.py`: Pass
   `structured_spec_business_rules=structured_bundle.structured_spec.business_rules`
   to `emit_generated_package()`.
4. `prompts/generate_component.yaml`: Add a section that renders
   `structured_spec_business_rules` as a "Business rules (from structured spec)"
   block before local invariants, with explicit instruction to implement all rules.

This is a pure context addition — no logic changes, no schema changes, no new
infrastructure. The structured spec rules already exist; they just need to flow
into the generation prompt.

---

## Files Affected

Read-only investigation — no changes. Plan #143 implements the repair.

# Plan #143: Front-Half-First Packet Grounding Repair And Gate Rerun

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 142
**Blocks:** None

---

## Gap

**Current:** gate_2 verdict monolithic_wins (0/5 AC14 successes) because generated
component code misapplies business rules despite correct blueprint structure.

**Target:** Apply the repair identified in Plan #142, run gate_3, and get a
budget-neutral verdict that measures whether the repair closes the gap.

---

## Acceptance Criteria

- [x] Repair applied (as specified by Plan #142 boundary)
- [x] Gate_3 run at `.ac14_out/front_half_first_full_gate_3/` TRIALS=5 MAX_BUDGET=1.50
- [x] Decision artifact persisted
- [x] Verdict is `monolithic_wins` (0/5 AC14, 4/5 monolithic)
- [x] Repair-boundary plan frozen: Plan #145 (spec contract fix + gate_4)

---

## Repair Applied

**Files changed:**

- `ac14/codegen_context.py`: Added `structured_spec_business_rules: list[str]` field to
  `CodegenContext`. Added `structured_spec_business_rules: list[str] | None` parameter
  to `build_codegen_context()`.

- `ac14/generated_codegen.py`: Added `structured_spec_business_rules: list[str] | None = None`
  to `emit_generated_package()` and `aemit_generated_package()`. Passed through to
  `build_codegen_context()`.

- `ac14/front_half_first_empirical.py`: Pass
  `structured_spec_business_rules=list(structured_bundle.structured_spec.business_rules)`
  to `emit_generated_package()`.

- `prompts/generate_component.yaml` (v1.1): Added a "Business rules (from structured spec)"
  block rendered before local_invariants. When non-empty, renders all 15 rules with explicit
  instruction to "implement ALL rules exactly" and not use placeholder logic.

**Tests:** 303 pass, 1 skipped. All existing tests green.

---

## Gate_3 Run

- Output dir: `.ac14_out/front_half_first_full_gate_3/`
- TRIALS=5, MAX_ATTEMPTS=3, MAX_BUDGET=1.50
- Command: `make front-half-first-full-trials BENCHMARK=benchmarks/resource_scaling_structured_spec OUTPUT=.ac14_out/front_half_first_full_gate_3 TRIALS=5 MAX_ATTEMPTS=3 MAX_BUDGET=1.50`
- Status: complete — verdict `monolithic_wins` (0/5 AC14, 4/5 monolithic)
- Decision artifact: `.ac14_out/front_half_first_full_gate_3/front_half_first_decision.json`
- Key finding: repair moved case accuracy from 0% → 75%; RSC-102 fails due to spec ambiguity

---

## Branch Matrix

| Verdict | Next plan |
|---------|-----------|
| `ac14_wins` | Plan #144: Final verdict interpretation + thesis claim |
| `inconclusive` | Plan #144: Inconclusive interpretation + secondary metrics analysis |
| `monolithic_wins` | Repair-boundary freeze: cross-benchmark analysis + strategic pivot |

---

## Files Affected

- `ac14/codegen_context.py` — added structured_spec_business_rules field
- `ac14/generated_codegen.py` — thread business_rules through emit_generated_package
- `ac14/front_half_first_empirical.py` — pass business_rules at codegen call site
- `prompts/generate_component.yaml` — render business rules in code generation prompt

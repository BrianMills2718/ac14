# Plan #45: Schema-Aware Empirical Repair

**Status:** Complete
**Type:** evaluation + implementation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 46

---

## Gap

**Current:** Plan #42 hardened the benchmark harness and prompt surface, but the
latest smoke artifacts still show two avoidable failure classes:

1. the AC14 component prompt does not render packet-local schema definitions,
   so components can miss optionality and valid categorical values even though
   that information exists in the packet context
2. the empirical repair loop still feeds the same broad failure summary back to
   every AC14 component, so unrelated components receive noisy repair guidance
   while benchmark-local rules such as 24h shipping materiality, compound
   exceptions, and optional override handling are not reinforced precisely

**Target:** The AC14 empirical lane should provide schema-aware component
prompts plus benchmark-local repair guidance that is targeted by condition and,
for AC14, by component.

**Why:** The empirical smoke gate is now blocked by benchmark-fidelity misses,
not by missing infrastructure. The next honest lane is to remove prompt/context
blindness before spending another smoke attempt.

---

## References Reviewed

- `CLAUDE.md` - active empirical execution rules
- `docs/AC14_ROADMAP.md` - empirical gate priority
- `docs/plans/42_empirical_benchmark_fidelity_repair.md` - previous repair lane
- `.ac14_out/empirical_smoke_v2/trial_1/ac14/attempt_3/attempt_report.json` - latest AC14 failure snapshot
- `.ac14_out/empirical_smoke_v2/trial_1/monolithic/attempt_3/attempt_report.json` - latest monolithic failure snapshot
- `.ac14_out/empirical_smoke_v2/trial_1/ac14/attempt_3/generated/factor_correlator.py` - optional override misuse
- `.ac14_out/empirical_smoke_v2/trial_1/ac14/attempt_3/generated/resolution_assembler.py` - optional override misuse
- `benchmarks/order_exception_resolution/requirements.md` - benchmark business rules
- `benchmarks/order_exception_resolution/blueprint/schemas.yaml` - optional fields and valid values
- `prompts/generate_component.yaml` - current AC14 component prompt
- `prompts/generate_monolithic_system.yaml` - current monolithic prompt
- `ac14/empirical_comparison.py` - current repair-loop wiring
- `ac14/codegen_context.py` - packet-local prompt surface
- `tests/test_empirical_comparison.py` - current empirical runner tests
- `tests/test_llm_codegen.py` - LLM codegen contract tests

---

## Open Questions

### Q1: Should packet-local schema definitions be added to the general AC14 component prompt?
**Status:** Resolved
**Why it matters:** The component generator already has the schema data in the
codegen context. Omitting it from the prompt makes the packet weaker than the
actual packet contract.
**Decision:** Yes. Render packet-local schema definitions in the component
prompt.

### Q2: Should benchmark-local repair guidance stay benchmark-local or become a general AC14 policy layer?
**Status:** Resolved
**Why it matters:** The failures are specific to the empirical benchmark and
should not silently redefine AC14 globally.
**Decision:** Keep the additional repair guidance benchmark-local inside the
empirical comparison runner.

### Q3: Should this plan add a hidden second-pass syntax auto-repair loop?
**Status:** Resolved
**Why it matters:** Syntax-only retries would change the fairness contract.
**Decision:** No. Improve prompt/context quality and repair guidance, but keep
attempt counting unchanged.

---

## Files Affected

- `prompts/generate_component.yaml` (modify)
- `prompts/generate_monolithic_system.yaml` (modify)
- `ac14/empirical_comparison.py` (modify)
- `tests/test_empirical_comparison.py` (modify)
- `tests/test_llm_codegen.py` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Render packet-local schema definitions explicitly in the AC14 component prompt.
2. Add benchmark-local repair-guidance helpers for `order_exception_resolution`.
3. Feed AC14 component-specific repair guidance instead of copying the same
   summary to every component; keep monolithic guidance benchmark-local but
   whole-system.
4. Lock the docs and prepare the next smoke rerun plan.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_llm_codegen.py` | `test_component_prompt_includes_local_schema_definitions` | The AC14 component prompt now exposes packet-local schema details |
| `tests/test_empirical_comparison.py` | `test_benchmark_repair_guidance_targets_override_and_shipping_rules` | Benchmark-local repair guidance includes the real blocker rules |
| `tests/test_empirical_comparison.py` | `test_component_specific_repair_guidance_targets_resolution_assembler` | AC14 repair guidance can target component-specific fixes |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Keep the empirical lane type-clean |
| `python -m ruff check ac14 tests` | Keep the empirical lane lint-clean |

---

## Acceptance Criteria

- [ ] The component prompt renders packet-local schema definitions.
- [ ] Benchmark-local repair guidance names the shipping-delay 24h rule,
      compound-exception rule, and optional override handling.
- [ ] AC14 component generation receives component-specific repair guidance for
      the empirical lane instead of the same undifferentiated summary for every
      component.
- [ ] Full local verification passes.
- [ ] The active control docs clearly point to the next smoke rerun lane.

---

## Implementation Summary (2026-04-02)

- The AC14 component prompt now renders packet-local schema definitions,
  including field optionality and absence meaning.
- The empirical runner now injects benchmark-local repair guidance for the
  `order_exception_resolution_v1` benchmark.
- AC14 no longer copies the same broad repair summary to every component in the
  empirical lane; it now combines benchmark-local component guidance with
  bounded prior-attempt guidance targeted by component.
- The monolithic lane also receives benchmark-local repair guidance, but it
  remains whole-system rather than componentized.
- Verification passed with the targeted empirical/codegen tests plus full repo
  verification.

## Notes

This plan intentionally improves the empirical lane's context quality without
changing the attempt-count fairness contract.

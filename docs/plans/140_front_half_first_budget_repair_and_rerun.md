# Plan #140: Front-Half-First Budget Repair And Rerun

**Status:** Planned
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 139
**Blocks:** None

---

## Gap

**Current:** full_gate_1 verdict is `monolithic_wins` because the $0.50/attempt
budget cap cuts off AC14 before it can complete the front-half pipeline.

**Target:** Increase the per-attempt budget to $1.50 and run full_gate_2 to get
a budget-neutral verdict that measures capability, not cost cap.

---

## Acceptance Criteria

- [ ] Makefile default MAX_BUDGET for front-half-first-full-trials updated to 1.50
- [ ] Full gate rerun at `.ac14_out/front_half_first_full_gate_2/` with TRIALS=5 MAX_BUDGET=1.50
- [ ] Decision artifact persisted at `.ac14_out/front_half_first_full_gate_2/front_half_first_decision.json`
- [ ] Verdict is explicitly one of: ac14_wins, monolithic_wins, inconclusive
- [ ] Next plan is frozen from the verdict

---

## Execution Contract

1. Update Makefile: change `MAX_BUDGET ?= 0.50` to `MAX_BUDGET ?= 1.50`
   (or add a separate front-half-first default since the existing default is
   used by other targets — prefer a comment noting the front-half-first gate
   needs $1.50 per attempt)
2. Run:
   ```
   make front-half-first-full-trials \
     BENCHMARK=benchmarks/resource_scaling_structured_spec \
     OUTPUT=.ac14_out/front_half_first_full_gate_2 \
     TRIALS=5 MAX_BUDGET=1.50
   ```
3. Read the verdict artifact
4. Update Plan #140 acceptance criteria from the artifact
5. Commit and merge
6. Freeze the next numbered plan from the verdict

## Branch Matrix

| Verdict | Next plan |
|---------|-----------|
| `ac14_wins` | Plan #141: Verdict interpretation + thesis claim |
| `monolithic_wins` | Plan #141: Verdict interpretation + identify remaining gap |
| `inconclusive` | Plan #141: Verdict interpretation + secondary metrics diagnosis |

---

## Files Affected

- `Makefile` — update MAX_BUDGET default or add note

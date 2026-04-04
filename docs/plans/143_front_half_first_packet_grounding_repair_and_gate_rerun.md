# Plan #143: Front-Half-First Packet Grounding Repair And Gate Rerun

**Status:** Planned
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

- [ ] Repair applied (as specified by Plan #142 boundary)
- [ ] Gate_3 run at `.ac14_out/front_half_first_full_gate_3/` TRIALS=5 MAX_BUDGET=1.50
- [ ] Decision artifact persisted
- [ ] Verdict is one of: ac14_wins, monolithic_wins, inconclusive
- [ ] If still monolithic_wins: freeze a repair-boundary plan per CLAUDE.md policy
- [ ] If ac14_wins or inconclusive: interpret and plan next horizon

---

## Branch Matrix

| Verdict | Next plan |
|---------|-----------|
| `ac14_wins` | Plan #144: Final verdict interpretation + thesis claim |
| `inconclusive` | Plan #144: Inconclusive interpretation + secondary metrics analysis |
| `monolithic_wins` | Repair-boundary freeze: cross-benchmark analysis + strategic pivot |

---

## Files Affected

TBD based on Plan #142 diagnosis. Likely:
- `ac14/generated_codegen.py` or packet context generation
- Possibly structured spec business rules

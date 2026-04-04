# Plan #88: Front-Half-First Full Trial Gate

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 87
**Blocks:** None

---

## Gap

**Current:** The repo can reach a bounded front-half-first smoke verdict, but
that alone is not the actual empirical comparison. The repo also does not yet
have a dedicated front-half-first full-trial runner surface comparable to the
older back-half gate.

**Target:** If Plan #87 says `ready_for_full_trials`, spend the bounded
front-half-first full-trial budget and persist the verdict artifact.

**Why:** This is the next honest thesis-facing gate once the smoke artifact says
the benchmark is worth spending.

---

## Acceptance Criteria

- [x] Full trial runner surface added: run_front_half_first_full_trials(), CLI command front-half-first-full-trials, Makefile target
- [x] A full front-half-first trial artifact set exists (5 trials) at .ac14_out/front_half_first_full_gate_1/
- [x] The final empirical verdict is persisted: monolithic_wins (5/5 vs 0/5)
- [x] The repo updates its story surfaces from that verdict: Plan #100 interpretation + Plans #139/#140 frozen

---

## Execution Contract

If and only if Plan #96 says `ready_for_full_trials`, this plan must:

1. add the missing front-half-first full-trial runner surface if it does not
   already exist
2. expose that runner through typed Python entrypoints plus CLI/Make parity
3. run the five-trial front-half-first gate with explicit
   `MODEL=gpt-5-mini`
4. persist the decision artifact before any narrative doc update
5. hand off immediately to Plan #100 for verdict interpretation with no pause

---

## Notes

This plan is conditional. It only activates if the latest smoke rerun produces
`ready_for_full_trials`, and it is not complete until the verdict artifact
exists and Plan #100 is unlocked explicitly.

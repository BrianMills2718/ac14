# Plan #114: Front-Half Runtime-Harness Boundary IV

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 113
**Blocks:** 115

---

## Gap

**Current:** Smoke_10 still says `blocked_on_harness`. The structured-spec
benchmark fidelity repair landed, but runtime inference still expects each
structured-spec output name to appear as the literal emitted component port
name.

**Target:** Freeze the exact post-smoke_10 blocker from the fresh artifact:
generated drafts emit semantically correct final schemas under renamed output
ports such as `final_decision`, `final_decision_out`, or `decision_out`, and the
runtime contract currently fails before evaluation because it only looks for
literal ports named `scaling_decision_entry`.

**Why:** The front-half-first lane only stays empirically honest if each smoke
artifact names one explicit blocker class and one bounded next repair.

---

## Acceptance Criteria

- [x] One explicit blocker-boundary artifact exists because smoke_10 returned
      `blocked_on_harness`.
- [x] The dominant remaining blocker class is named precisely enough for one
      bounded repair lane.
- [x] The next move is explicit as Plan #115.

---

## Continuation Contract

If this boundary plan activates, the next required move is
[Plan #115: Front-Half Runtime-Harness Repair IV And Smoke Rerun IX](115_front_half_runtime_harness_repair_iv_and_smoke_rerun_ix.md).

---

## Frozen Smoke_10 Boundary

- Canonical artifact:
  - `.ac14_out/front_half_first_smoke_10/smoke_readiness_report.json`
- Verdict: `blocked_on_harness`
- AC14 front half: `true`
- Infrastructure failure detected: `false`
- Dominant AC14 failure class: `generation`
- Dominant blocker detail:
  - `unable to infer one unique final component from structured spec output 'scaling_decision_entry': []`
- Interpretation:
  - the old input/source boundary is no longer dominant
  - the next bounded repair must make runtime output binding schema-aware without
    weakening ambiguity detection

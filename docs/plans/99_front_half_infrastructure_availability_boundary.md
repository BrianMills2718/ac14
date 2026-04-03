# Plan #99: Front-Half Infrastructure Boundary For Hidden Default Model Paths

**Status:** Complete
**Type:** investigation
**Priority:** Critical
**Blocked By:** 96
**Blocks:** 106

---

## Gap

**Current:** Plan #96 reran the smoke gate with explicit `MODEL=gpt-5-mini`,
but AC14 still blocked on Gemini quota before the front-half acceptance report
was written.

**Target:** Freeze the actual infrastructure boundary from smoke_5 without
misreporting it as generic provider noise.

**Why:** The rerun already ruled out one false explanation: the top-level smoke
runner itself is no longer the Gemini-default problem.

---

## Acceptance Criteria

- [x] One explicit infrastructure boundary artifact exists for the smoke_5 rerun.
- [x] The next move is explicit and bounded to the hidden default-model path.
- [x] The full-trial budget remains closed unless a later rerun says otherwise.

---

## Implementation Summary (2026-04-02)

Evidence from `.ac14_out/front_half_first_smoke_5/`:

- monolithic attempts all reached real `runtime_outputs` evaluation
- AC14 attempts all persisted:
  - `structured_spec/structured_spec_artifact.json`
  - `front_half/draft_plan/draft_blueprint_plan.json`
  - `front_half/draft_bundle/freeze_readiness_report.json`
  - `front_half/freeze_decision/freeze_remediation_plan.json`
- AC14 never persisted:
  - `front_half/structured_spec_front_half_acceptance_report.json`
  - `front_half/freeze_decision/freeze_decision.json`

Boundary decision:

- the dominant blocker is not the smoke-runner `MODEL` parameter anymore
- the dominant blocker is AC14 front-half subcalls that still fall back to
  hidden Gemini defaults, most concretely freeze semantic review and refreshed
  freeze inside retry paths
- the next lane must repair explicit model propagation through those subcalls
  and then rerun one bounded smoke trial immediately

---

## Continuation Contract

If this boundary plan activates, the next required move is
[Plan #106: Front-Half Model Propagation Repair And Smoke Rerun IV](106_front_half_provider_fallback_and_smoke_rerun_iv.md).

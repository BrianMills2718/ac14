# Plan #141: Front-Half-First Full-Gate-2 Verdict Interpretation

**Status:** Complete
**Type:** evaluation + planning
**Priority:** Critical
**Blocked By:** 140
**Blocks:** None

---

## Gap

**Current:** full_gate_2 verdict is persisted at
`.ac14_out/front_half_first_full_gate_2/front_half_first_decision.json`.

**Target:** Interpret the verdict honestly, identify the root cause of AC14's
runtime failures, and freeze the next numbered plan.

---

## Acceptance Criteria

- [x] The gate_2 verdict is stated plainly
- [x] The root cause of AC14's 0/5 runtime successes is identified
- [x] The gap between front-half success and runtime failure is characterized
- [x] The next horizon is frozen as a numbered plan

---

## Verdict: monolithic_wins (5/5 vs 0/5) — Genuine Capability Gap

**Decision artifact:** `.ac14_out/front_half_first_full_gate_2/front_half_first_decision.json`

**AC14:** 0 successes / 5 trials, 5/5 front_half_successes, $0.597 total cost, 96s avg, semantic_score=0.2
**Monolithic:** 5 successes / 5 trials, $0.316 total cost, 16s avg, semantic_score=1.0

### Key Contrast vs gate_1

Gate_1 was budget overflow (AC14 couldn't complete the pipeline).
Gate_2 at $1.50 budget: AC14 completed the pipeline in all 5 trials — front-half
approval earned in every trial — but still failed at runtime for all 5.

### Root Cause: Component Code Generation Produces Wrong Business Logic

Despite generating approved blueprints (front_half_passed=True in every trial),
the generated component code fails runtime evaluation for all 4 cases.

Sample failures from trial_1:
- RSC-100: action expected `scale_out` actual `scale_up`; approval_tier expected `auto` actual `manager`; authorization_mode expected `auto` actual `manual`; cooldown expected `5` actual `10`; min_healthy expected `3` actual `2`; requires_approval expected `False` actual `True`
- RSC-101: alert_tier expected `info` actual `critical`; cooldown expected `30` actual `10`; **scale_tier expected `budget` actual `premium`** (bronze→budget mapping wrong); strategy expected `deferred` actual `emergency_scale`; urgency expected `medium` actual `high`

The packet-level test failures also show placeholder expected values (`expected='draft_action'`) in the packet contracts — the blueprint is generated with placeholder examples rather than real expected values computed from the business rules.

### Characterization of the Gap

The front-half-first architecture correctly separates:
1. **Blueprint design** — AC14 passes this (5/5 approved blueprints)
2. **Component implementation** — AC14 fails this (wrong values in all cases)

The generated component code gets multi-field logic wrong even though:
- The structured spec explicitly spells out THRESHOLD, ACTION, URGENCY, TIER MAPPING, etc.
- The business rules are passed in the packet context

This pattern matches the known "packet-local rule grounding" weakness from Plans
#73-#78 (the second-gate diagnosis). The packet context exists but the LLM still
implements business rules incorrectly at the component level.

### Thesis Impact

The monolithic_wins verdict at gate_2 is honest evidence of a real capability gap:
the AC14 decomposed approach generates structurally valid blueprints but produces
lower-quality component implementations than the monolithic approach for complex
multi-rule business logic.

The front-half-first lane has now yielded two clean signals:
1. AC14 CAN produce approved blueprints (structured spec → blueprint → front-half review)
2. The generated component implementations do not correctly apply complex business rules

### Next Plan

Per CLAUDE.md: "after a decisive harder-benchmark loss, allow at most one bounded
post-loss benchmark-local repair before freezing a repair-boundary plan."

Gate_1 was a budget artifact (not a real loss). Gate_2 is the FIRST genuine loss.
One bounded repair is permitted before a repair-boundary freeze.

The most targeted repair: improve the packet-level code generation context to better
ground the business rules in the generated component code. This mirrors Plan #78
(reusable packet rule grounding) but applied to the structured spec / front-half-first lane.

- [Plan #142: Front-Half-First Runtime Code Quality Boundary](142_front_half_first_runtime_code_quality_boundary.md) — diagnose the specific component implementation gap
- [Plan #143: Front-Half-First Packet Grounding Repair And Gate Rerun](143_front_half_first_packet_grounding_repair_and_gate_rerun.md) — one bounded repair + gate_3

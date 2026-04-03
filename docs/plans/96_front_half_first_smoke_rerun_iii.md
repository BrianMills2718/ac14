# Plan #96: Front-Half-First Smoke Rerun III

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 88, 97, 98, 99

---

## Gap

**Current:** The latest rerun was blocked by Gemini quota exhaustion before the
front half could be judged, and the Makefile default model still points at that
Gemini path.

**Target:** Rerun one bounded front-half-first smoke trial with an explicit
OpenAI-routed model: `gpt-5-mini`.

**Why:** The next smoke artifact must test the repaired front half, not default
model availability.

---

## Acceptance Criteria

- [ ] One fresh smoke artifact exists after Plan #95.
- [ ] The rerun uses `MODEL=gpt-5-mini` explicitly rather than the Makefile default.
- [ ] The next branch is explicit:
      - Plan #88 if `ready_for_full_trials`
      - Plan #97 if `blocked_on_front_half`
      - Plan #98 if `blocked_on_harness`
      - Plan #99 if `blocked_on_infrastructure`

---

## Execution Contract

Run:

```bash
make front-half-first-smoke-gate \
  OUTPUT=.ac14_out/front_half_first_smoke_5 \
  BENCHMARK=benchmarks/resource_scaling_structured_spec \
  MAX_ATTEMPTS=3 \
  MODEL=gpt-5-mini
```

This plan is only complete once the persisted smoke verdict exists and the next
branch is locked in the control docs.

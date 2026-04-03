# Plan #96: Front-Half-First Smoke Rerun III

**Status:** Complete
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

- [x] One fresh smoke artifact exists after Plan #95.
- [x] The rerun uses `MODEL=gpt-5-mini` explicitly rather than the Makefile default.
- [x] The next branch is explicit:
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

---

## Implementation Summary (2026-04-02)

Smoke artifact: `.ac14_out/front_half_first_smoke_5/smoke_readiness_report.json`

Verdict: `blocked_on_infrastructure`

What changed relative to smoke_4:

- the rerun did honor explicit `MODEL=gpt-5-mini` at the top-level smoke runner
- monolithic no longer died on Gemini quota and instead produced real
  `runtime_outputs` failures across all bounded attempts
- AC14 still failed all bounded attempts as `infrastructure_provider`

Why the verdict stayed infrastructure-blocked:

- AC14 got far enough to persist the structured-spec artifact, draft plan,
  draft bundle, and freeze remediation plan on every attempt
- it never persisted the final structured-spec front-half acceptance report
- the remaining hidden Gemini-default step was inside AC14's front-half model
  plumbing rather than at the smoke-runner entrypoint

Next branch:

- [Plan #99: Front-Half Infrastructure Availability Boundary](99_front_half_infrastructure_availability_boundary.md)

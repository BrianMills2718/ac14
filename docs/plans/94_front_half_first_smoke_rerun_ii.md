# Plan #94: Front-Half-First Smoke Rerun II

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 88, 95

---

## Gap

**Current:** The second smoke artifact is blocked on the repaired front half,
but the next repair lane has not yet been tested.

**Target:** Rerun one bounded front-half-first smoke trial after Plan #93.

**Why:** The repo needs one fresh persisted verdict after the async-safe
front-half repair, not reasoning by analogy from smoke2.

---

## Acceptance Criteria

- [x] One fresh smoke artifact exists after Plan #93.
- [x] The verdict is explicit and persisted.
- [x] The next branch is explicit:
      - Plan #88 if `ready_for_full_trials`
      - Plan #95 if still `blocked_*`

---

## Notes

This plan only executes after Plan #93 is fully verified.

## Implementation Summary

Plan #94 ran the front-half-first smoke gate at `.ac14_out/front_half_first_smoke_4/` using
`benchmarks/resource_scaling_structured_spec` with `MAX_ATTEMPTS=3`.

Verdict: `blocked_on_infrastructure`

All 6 attempts (3 monolithic + 3 AC14) failed with Gemini 429 rate limit errors
(`litellm.RateLimitError: GeminiException - {"error": {"code": 429}}`). The 429
classification fix from this session correctly detected these as
`infrastructure_provider` failures and returned `blocked_on_infrastructure`
rather than a false `blocked_on_front_half`.

The Plan #93 async-safe fix was NOT empirically tested — the provider quota was
exhausted before any attempt reached the front-half execution stage.

Next branch: Plan #95 (blocked_* condition). Plan #95 should document that the
dominant blocker is infrastructure (Gemini quota), not freeze fidelity. The next
actionable step is to retry the smoke gate after rate limits clear or with an
alternate model.

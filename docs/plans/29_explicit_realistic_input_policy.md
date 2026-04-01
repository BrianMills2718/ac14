# Plan #29: Explicit Realistic-Input Policy

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** 28
**Blocks:** 30

---

## Gap

**Current:** AC14 can execute realistic-input acceptance on both clean and
messy structured inputs, but shipped-example input choice is still implicit.
`acceptance.py` now uses structured candidate precedence while
`front_half_acceptance.py` still defaults to `.json` only.

**Target:** AC14 should have an explicit per-example realistic-input policy
artifact with a named default and named alternate profiles, plus one shared
resolver that fails loud when the policy is invalid.

**Why:** The proof surface should not silently depend on file-extension
precedence or let front-half and final-gate defaults drift apart once one
example ships both a clean JSON asset and a messy CSV asset.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and explicit next-chain policy
- `docs/AC14_ROADMAP.md` - Horizon 1 proof discipline and Horizon 2 realism strengthening
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current realistic-input state and remaining ambiguity
- `docs/plans/28_messy_input_llm_comparison.md` - just-completed bounded messy-input `llm` lane
- `ac14/examples.py` - shipped-example discovery surface
- `ac14/acceptance.py` - current structured-candidate default discovery
- `ac14/front_half_acceptance.py` - current JSON-only default discovery

---

## Open Questions

### Q1: Should AC14 rely on optional manifests with fallback precedence?
**Status:** Resolved
**Why it matters:** Hidden fallback precedence would preserve the same ambiguity this plan is meant to remove.
**Decision:** No for shipped examples. Add explicit manifests to shipped examples and make the resolver fail loud on invalid manifests.

### Q2: What should the first policy shape be?
**Status:** Resolved
**Why it matters:** The policy should stay simple enough to review and reuse across surfaces.
**Decision:** One manifest per example input directory with an explicit `default_profile` and named profiles mapping to input filenames.

---

## Files Affected

- `ac14/examples.py` (modify)
- `tests/test_examples.py` (modify)
- `examples/support_ticket_digest/input/realistic_inputs.json` (create)
- `examples/support_ticket_digest_auth_mix/input/realistic_inputs.json` (create)
- `examples/incident_alert_digest/input/realistic_inputs.json` (create)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)

---

## Plan

### Steps

1. Define a small per-example realistic-input manifest and add it to the shipped examples.
2. Extend shipped-example discovery with a shared resolver for the default profile and named alternate profiles.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_examples.py` | `test_discover_shipped_blueprints_reads_realistic_input_policy` | Shipped example discovery exposes explicit default and named realistic-input profiles |
| `tests/test_examples.py` | `test_resolve_realistic_input_path_fails_loud_on_unknown_profile` | The shared resolver fails loud on invalid profile selection |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] Shipped examples declare explicit realistic-input profiles with a named default.
- [x] AC14 has one shared realistic-input resolver instead of hidden extension precedence for shipped examples.
- [x] Invalid profile references fail loud.
- [x] Full local verification passes and the docs match the lane.

## Verification

- Targeted realistic-input policy verification passed:
  - `python -m pytest -q tests/test_examples.py tests/test_acceptance.py::test_build_realistic_suite_acceptance_report_supports_realistic_inputs tests/test_acceptance.py::test_discover_realistic_input_path_supports_structured_non_json_inputs tests/test_front_half_acceptance.py::test_build_front_half_acceptance_suite_report_runs_for_shipped_examples`
  - `python -m mypy ac14/examples.py ac14/structured_inputs.py ac14/acceptance.py ac14/front_half_acceptance.py tests/test_examples.py tests/test_acceptance.py tests/test_front_half_acceptance.py`
  - `python -m ruff check ac14/examples.py ac14/structured_inputs.py ac14/acceptance.py ac14/front_half_acceptance.py tests/test_examples.py tests/test_acceptance.py tests/test_front_half_acceptance.py`

## Outcome

AC14 now gives every shipped example an explicit realistic-input manifest with
named profiles and a named default. The shared resolver is now the source of
truth for default realistic-input selection, and both acceptance surfaces use
it for shipped examples instead of relying on hidden file precedence.

---

## Notes

This plan is about explicit selection policy, not yet about changing every
consumer surface. Consumer parity lands in the next plan.

# Plan #86: Front-Half-First Smoke Gate Contract And Runner

**Status:** In Progress
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 85
**Blocks:** 87

---

## Gap

**Current:** The repo has the front-half-first empirical direction, a bounded
structured-spec input contract, a full AC14 structured-spec front-half lane,
and a benchmark-ready bundle. It still does not have an explicit smoke-gate
runner or a pre-made definition of what that smoke gate judges.

**Target:** Run one bounded smoke paired trial comparing:

1. AC14 from structured-spec input through front half and generated system
2. a monolithic baseline from the same structured-spec input and requirements

**Why:** The project needs a cheap stop/go artifact before it spends another
full empirical budget, and that artifact must measure the new front-half-first
surface honestly instead of quietly reverting to a back-half-only gate.

---

## Acceptance Criteria

- [ ] One bounded front-half-first smoke runner exists and persists a smoke
      artifact.
- [ ] The smoke contract is explicit: AC14 front-half acceptance is a required
      precondition, and runtime success stays the hard end-to-end success
      surface.
- [ ] The next branch is explicit from the verdict: full trial or blocker
      diagnosis.

---

## Open Questions

### Q1: What should the first front-half-first smoke gate treat as success?
**Status:** Resolved
**Why it matters:** The existing empirical runner judges generated systems
against runtime outputs from a frozen blueprint benchmark. The new bundle adds a
front-half input surface, so the smoke gate must decide whether success means:

1. strong front-half artifacts only
2. strong front-half artifacts plus final generated runtime outputs
3. a staged combination of both

**Resolution:** Use a staged combination of both.

- AC14 must first produce a structured-spec front-half artifact that ends in
  `final_freeze_approved = true`.
- The smoke gate still judges end-to-end success from runtime outputs plus the
  existing semantic/runtime policy.
- The overall smoke verdict is:
  - `blocked_on_infrastructure` if provider or transport instability appears
  - `blocked_on_front_half` if AC14 cannot produce an approved front-half
    artifact
  - `blocked_on_harness` if front-half succeeds but neither condition achieves
    a runtime hard-harness success
  - `ready_for_full_trials` if AC14 front-half succeeds and at least one
    condition achieves a runtime hard-harness success without infrastructure
    contamination

### Q2: Should monolithic generation be forced into a fake front-half artifact?
**Status:** Resolved
**Why it matters:** Forcing a fake front-half stage into the monolithic
baseline would create symmetry theater instead of a truthful benchmark.
**Resolution:** No. The monolithic baseline remains direct structured-spec +
requirements -> generation -> runtime evaluation. The front-half artifact is
the differentiating AC14 surface, so only AC14 carries that additional gate.

---

## Files Affected

- `docs/plans/86_front_half_first_smoke_gate.md` (update)
- `ac14/front_half_first_empirical.py` (create)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_front_half_first_empirical.py` (create)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `CLAUDE.md` (modify)

---

## Plan

### Steps

1. Add a dedicated front-half-first smoke runner that consumes the structured-spec
   benchmark bundle.
2. Reuse the existing structured-spec front-half acceptance path for the AC14
   condition.
3. Reuse the existing runtime benchmark assets for both conditions.
4. Persist one smoke artifact that separates:
   - AC14 front-half status
   - runtime hard-harness success
   - infrastructure contamination
   - next-branch verdict
5. Verify the runner with targeted tests before spending the smoke budget.

---

## Required Tests

| Command | Why |
|---------|-----|
| `python -m pytest -q tests/test_front_half_first_empirical.py tests/test_cli.py tests/test_make_targets.py` | Proves the new runner, CLI, and Make surfaces |
| `python -m mypy ac14 tests` | Keeps the new empirical surface typed and reviewable |
| `python -m ruff check ac14 tests` | Keeps the new lane lint-clean |

---

## Notes

This plan does not spend the smoke budget itself. It freezes and implements the
truthful runner contract so Plan #87 can spend one bounded smoke trial without
reopening the old ambiguity.

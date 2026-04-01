# Plan #19: Controlled Dependency Remediation

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 can plan dependencies, probe them, carry blocked results into
freeze readiness, and stop freeze explicitly when required libraries remain
unavailable.

**Target:** AC14 should provide one narrow, reviewable remediation lane for
dependency blockers so approved dependency actions can be executed and persisted
without collapsing into broad silent environment mutation.

**Why:** The project vision includes being able to install and use libraries.
Right now AC14 is strong at diagnosing missing dependencies and weak at
bridging that diagnosis into a controlled action lane.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 emphasis on stronger environment/tool execution
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current remaining dependency gap
- `docs/AC14_ANTI_DRIFT_DOCTRINE.md` - hierarchy of truth
- `docs/plans/03_meta_process_dependency_probe_policy.md` - shared policy background
- `docs/plans/18_messy_input_front_half_proof.md` - just-completed front-half realism lane
- `ac14/dependency_execution.py` - current probe execution artifact
- `ac14/draft_authoring.py` - current freeze-readiness blocking behavior
- `ac14/freeze_decision.py` - current remediation-plan surface

---

## Open Questions

### Q1: What is the narrowest safe remediation scope?
**Status:** Resolved
**Why it matters:** The first remediation lane should stay explicit and
reviewable rather than becoming broad automatic environment mutation.
**Resolution:** The remediation lane is a narrow rerun/delta artifact built on
top of the existing dependency execution artifact. It reruns previously blocked
install probes with explicit mutation intent instead of introducing a second
dependency system.

### Q2: How should remediation outcomes feed back into freeze/readiness?
**Status:** Resolved
**Why it matters:** A remediation lane only matters if later phases can consume
its result without guesswork.
**Resolution:** The remediation artifact now points to a fresh remediated
dependency execution artifact. That path becomes the explicit hand-off back
into draft planning and later front-half phases.

---

## Files Affected

- `ac14/dependency_execution.py` (modify)
- `ac14/draft_authoring.py` (modify if remediation results change readiness)
- `ac14/freeze_decision.py` (modify if remediation artifacts should be linked)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_dependency_execution.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Pre-make the remediation scope and outcome contract.
2. Implement one explicit remediation artifact/command and wire its result back into the front-half chain.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_dependency_execution.py` | `test_build_dependency_remediation_artifact_runs_approved_actions` | Remediation stays explicit and persists before/after state |
| `tests/test_cli.py` | `test_cli_remediate_dependencies_runs_end_to_end` | CLI remediation surface persists the remediation artifact |
| `tests/test_make_targets.py` | `test_make_remediate_dependencies_runs_end_to_end` | Make remediation surface persists the remediation artifact |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] AC14 provides one explicit, reviewable dependency-remediation lane.
- [x] Remediation does not silently mutate the environment without an explicit artifact and operator-visible intent.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

This lane should stay narrow. It is about controlled remediation of known
dependency blockers, not about general package management or hidden automatic
fallbacks.

# Plan #2: Dependency Probe Integration

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 can persist dependency execution probes, but the resulting
artifact is still mostly a side surface. Draft planning, draft authoring, and
freeze decisions do not yet treat confirmed probes and blocked probes as part of
the same front-half contract.

**Target:** AC14 carries dependency execution evidence into draft planning and
uses blocked probe results as explicit freeze-readiness blockers while
preserving confirmed probe results as reusable planning context.

**Why:** Probe evidence only helps the decomposition thesis if it changes what
the front half is allowed to freeze. Otherwise AC14 still asks for dependency
evidence without actually enforcing it at the freeze boundary.

---

## References Reviewed

- `CLAUDE.md` - project execution rules and active proof-expansion rule
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis on stronger front-half evidence
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current statement that front-half work is still earlier than the back half
- `docs/AC14_ANTI_DRIFT_DOCTRINE.md` - hierarchy of truth and thesis boundary
- `docs/TODO.md` - current active control surface
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that needs to stop lagging the real lane
- `docs/UNCERTAINTIES.md` - dedicated uncertainty tracker
- `docs/plans/01_dependency_execution_probing.md` - completed prerequisite lane
- `ac14/blueprint_planning.py` - draft planning artifact and planning handoff
- `ac14/draft_authoring.py` - draft bundle materialization and readiness findings
- `ac14/freeze_decision.py` - explicit freeze decision and remediation buckets
- `ac14/dependency_execution.py` - persisted dependency execution-probe artifact
- `ac14/__main__.py` - current operator surface

---

## Open Questions

### Q1: Should blocked dependency probes be warnings or freeze blockers?
**Status:** Resolved
**Why it matters:** If blocked probes only become warnings, probe evidence still
does not materially constrain freeze decisions.
**Resolution:** Blocked dependency probes are explicit freeze blockers until the
dependency plan changes or the probe result changes.

### Q2: Should dependency execution artifacts replace dependency plans?
**Status:** Resolved
**Why it matters:** The execution artifact is narrower than the planning
artifact and should not erase earlier planning evidence.
**Resolution:** Dependency execution artifacts augment dependency plans; they do
not replace them.

### Q3: Where should confirmed probe evidence live downstream?
**Status:** Resolved
**Why it matters:** AC14 should stop re-asking already confirmed dependency
questions in later planning phases.
**Resolution:** The draft planning artifact carries confirmed probe summaries
and blocked probe summaries as explicit fields.

---

## Files Affected

- `ac14/blueprint_planning.py` (modify)
- `ac14/draft_authoring.py` (modify)
- `ac14/freeze_decision.py` (modify)
- `ac14/__main__.py` (modify)
- `tests/test_blueprint_planning.py` (modify)
- `tests/test_draft_authoring.py` (modify)
- `tests/test_freeze_decision.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Extend draft planning so it can ingest dependency execution artifacts and
   persist confirmed and blocked probe summaries.
2. Extend draft authoring readiness findings so blocked dependency probes become
   explicit freeze blockers.
3. Ensure freeze remediation groups dependency blockers into actionable tasks.
4. Thread the new artifact path through CLI and operator surfaces.
5. Run targeted tests, full verification, and then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_blueprint_planning.py` | `test_build_draft_blueprint_plan_carries_dependency_execution_artifact` | Draft planning persists confirmed and blocked probe summaries |
| `tests/test_draft_authoring.py` | `test_materialize_draft_blueprint_bundle_blocks_on_dependency_probe_results` | Blocked probes become explicit readiness blockers |
| `tests/test_freeze_decision.py` | `test_build_freeze_decision_groups_dependency_probe_blockers` | Freeze remediation groups dependency blockers into actionable work |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `tests/test_cli.py` | CLI surface stays coherent |
| `tests/test_make_targets.py` | Make targets remain usable |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [x] Dependency execution evidence is visible in persisted draft planning artifacts.
- [x] Blocked probe results become explicit freeze-readiness blockers.
- [x] Freeze remediation turns blocked dependency probes into actionable tasks.
- [x] CLI and operator docs expose the integrated lane honestly.
- [x] Full local verification passes.

---

## Notes

- This lane is still narrower than full automatic dependency remediation.
- Confirmed probe evidence should reduce repeated uncertainty, not hide the
  earlier dependency-planning artifact.
- If integrating blocked probe results exposes a broader bundle/regeneration
  design problem, log it explicitly rather than adding silent bypasses.

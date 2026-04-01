# Plan #1: Dependency Execution Probing

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 can inspect the environment, retrieve docs and repos, plan
dependencies, and carry those recommendations into draft planning, but it does
not yet probe whether recommended reuse or install actions actually work in the
current environment.

**Target:** AC14 can persist explicit dependency execution-probe artifacts that
test approved recommendations in a reviewable, fail-loud way and expose those
probes through its CLI and Make surfaces.

**Why:** The front half of AC14 is still too advisory around environment and
dependency decisions. This lane makes those decisions more evidence-backed
without turning AC14 into a silent package-management side channel.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and current proof-expansion rule
- `docs/AC14_ROADMAP.md` - Horizon 1 and Horizon 4 emphasis on dependency execution
- `docs/AC14_IMPLEMENTATION_STATUS.md` - explicit statement that dependency execution/install verification is still missing
- `docs/AC14_ANTI_DRIFT_DOCTRINE.md` - front-half scope and validation philosophy
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary of the current lane
- `docs/UNCERTAINTIES.md` - dedicated uncertainty tracker
- `docs/TODO.md` - active checklist and known uncertainties
- `ac14/dependency_planning.py` - current advisory dependency planning artifact
- `ac14/blueprint_planning.py` - current dependency-aware planning handoff
- `ac14/__main__.py` - current operator surface
- `Makefile` - current Make surface

---

## Open Questions

### Q1: What should the probe result state model be?
**Status:** Resolved
**Why it matters:** The artifact needs explicit reviewable states such as
`confirmed`, `blocked`, or `skipped` rather than implicit shell success/failure.
**Resolution:** The persisted probe artifact now uses `confirmed`, `blocked`,
and `skipped` as explicit result states.

### Q2: How much environment mutation is acceptable in the first lane?
**Status:** Resolved
**Why it matters:** AC14 should probe recommendations without quietly turning
into a broad automatic installer.
**Resolution:** The default execution mode is `check_only`; install actions are
blocked unless the operator explicitly enables `--allow-install`.

### Q3: What post-probe environment observations should be persisted?
**Status:** Resolved
**Why it matters:** The follow-on planning and freeze surfaces need explicit
environment deltas, not just command output.
**Resolution:** Each result persists before/after snapshots, command exit code,
compact observations, and cross-cutting environment observations.

---

## Files Affected

- `ac14/dependency_execution.py` (create)
- `ac14/dependency_planning.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_dependency_execution.py` (create)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Define the dependency execution-probe artifact and state model.
2. Implement a fail-loud probing bridge for reuse/install recommendations.
3. Thread the probe surface through CLI and Make.
4. Add deterministic tests for artifact persistence and failure behavior.
5. Run full verification and update the tactical/docs surface.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_dependency_execution.py` | `test_probe_artifact_persists_reviewable_state` | Probe results are explicit and persisted |
| `tests/test_dependency_execution.py` | `test_probe_failure_is_fail_loud` | Failed probes do not silently pass |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `tests/test_dependency_planning.py` | Dependency-plan compatibility remains intact |
| `tests/test_cli.py` | CLI surface stays coherent |
| `tests/test_make_targets.py` | Make targets remain usable |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [x] AC14 can persist a dependency execution-probe artifact with explicit result states.
- [x] Probe behavior is reviewable and fail loud.
- [x] CLI and Make expose the probing lane without manual glue code.
- [x] Full local verification passes.
- [x] Tactical docs reflect the implemented state honestly.

---

## Notes

- This lane is intentionally narrower than full dependency installation
  automation.
- AC14 should probe explicit approved recommendations, not broadly mutate the
  environment by default.
- If the first probe path reveals a larger environment-management design
  problem, log it explicitly rather than hiding it behind fallback behavior.

# Plan #125: Front-Half Structured-Dependency Repair And Smoke Rerun XIV

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 124
**Blocks:** None

---

## Gap

**Current:** Smoke_13 failed before front-half approval or runtime on both
conditions because the repo-local `.venv` could not import `instructor`. AC14's
declared dependency contract is too weak for the structured generation path it
actually exercises.

**Target:** Repair the repo-local structured dependency contract, verify that
the local environment can execute the structured path honestly, then spend one
fresh bounded smoke rerun immediately.

**Why:** Future agents need the repo-local install flow and the bounded smoke
lane to work without relying on undeclared system Python packages.

---

## Acceptance Criteria

- [x] AC14 declares the structured `llm_client` dependency it actually uses for
      front-half and monolithic structured generation.
- [x] The repo-local `.venv` install flow can import `instructor` without
      relying on system-site packages.
- [x] Targeted verification proves the dependency repair did not regress the
      repaired Plan #119 lane.
- [x] One fresh smoke artifact exists after the repair at
      `.ac14_out/front_half_first_smoke_14/`.
- [x] The next branch is explicit from the new artifact as Plan #88 + #100,
      Plan #120 + #121, Plan #122 + #123, Plan #126 + #127, or
      Plan #128 + #129.

---

## Execution Contract

This plan must stay bounded:

1. repair only the repo-local structured dependency contract exposed by
   smoke_13
2. verify the repair with a repo-local import probe plus targeted tests,
   `mypy`, and `ruff`
3. rerun one bounded smoke trial immediately after the repair
4. if the rerun returns `ready_for_full_trials`, immediately continue into
   Plan #88 then Plan #100
5. if the rerun returns `blocked_on_runtime_outputs`, immediately continue into
   Plan #120 then Plan #121
6. if the rerun returns `blocked_on_harness`, immediately continue into
   Plan #122 then Plan #123
7. if the rerun still returns `blocked_on_front_half`, immediately continue
   into Plan #126 then Plan #127
8. if the rerun returns `blocked_on_infrastructure`, immediately continue into
   Plan #128 then Plan #129

## Result

The dependency repair landed truthfully:

1. `pyproject.toml` now declares `llm_client[structured]`
2. the repo-local `.venv` editable install imports `instructor` without relying
   on hidden system packages
3. targeted regression tests, `mypy`, and `ruff` all passed

Smoke_14 then reran cleanly at `.ac14_out/front_half_first_smoke_14/`. The
dependency blocker is gone, but the gate still ended `blocked_on_harness`
because AC14 attempts 1 and 3 failed on repeated ambiguous final-output
inference for `scaling_decision_entry`. That closed Plan #125 and activated the
bounded harness branch in Plans #122 and #123.

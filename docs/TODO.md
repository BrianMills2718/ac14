# AC14 TODO

Status: Active control surface
Last updated: 2026-03-31

## Short-Term Active Lane

- [x] Phase 1: freeze the dependency execution-probing lane
  - [x] update `CLAUDE.md` to make dependency execution probing the active proof-expansion rule
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md` with dependency execution-probing phases and success criteria
  - [x] keep this TODO as the running control surface during implementation
  - Success criteria: the active lane is documented honestly and can run without stop-and-ask interpretation

- [ ] Phase 2: add dependency execution probes
  - [ ] define a persisted dependency execution-probe artifact
  - [ ] keep probe results explicit with states such as confirmed, blocked, or skipped
  - [ ] record post-probe environment observations rather than only shell output
  - Success criteria: AC14 can test dependency recommendations without hiding side effects

- [ ] Phase 3: connect dependency execution into operator surfaces
  - [ ] expose the probing bridge through CLI and Make
  - [ ] add deterministic tests for artifact persistence and fail-loud probe behavior
  - Success criteria: operators can run dependency probes without manual glue code and the behavior is tested

- [ ] Phase 4: verify and lock the lane
  - [ ] run full `pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update TODO, plan, README, and KNOWLEDGE to reflect actual final state
  - Success criteria: local verification passes and the control docs match the implemented lane

## Logged Uncertainties

- the generated component logic is still semantic-responsibility-specific rather than general synthesis
- realistic-input acceptance will still be synthetic-but-plausible until the pre-freeze discovery layer exists
- proof breadth is broader than one workflow slice now, but it is still narrow overall
- live LLM acceptance may be too expensive for the default gate and may remain optional outside targeted runs
- discovery will start with local input inspection and environment/dependency planning before broader doc/repo retrieval is implemented
- the next bridge will produce draft planning artifacts, not claim that blueprint freeze is solved
- the next bridge will materialize draft bundles and readiness reports, not claim those drafts are frozen
- the next bridge will decide and promote only when approval is explicit; it still does not broaden proof breadth
- the new remediation loop will guide direct draft-bundle editing first; automated rewrite loops are still deferred
- proof breadth will still be approximate because the current metric is based on workflow signatures rather than a richer benchmark taxonomy
- the next bridge will start with local project docs and will not yet claim GitHub/web/context-server retrieval
- the next bridge after local project docs should persist external retrieval artifacts rather than hiding them inside prompts
- the next bridge after shared retrieval should recommend dependency actions without pretending package installation is already automated
- the next bridge after dependency planning should feed those decisions into draft planning rather than leaving them as disconnected advisory artifacts
- the next bridge after dependency-aware planning should probe explicit recommendations without becoming a broad automatic package manager
- the current biggest risk is planning-artifact drift: the implementation has moved farther than the original bootstrap notebook

## Latest Verified Results

- detailed implementation reality and broader risk framing now live in [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md)
- planning-artifact resynchronization verification passed:
  - notebook JSON parsed successfully for `notebooks/01_ac14_execution_status_journey.ipynb`
  - notebook registry YAML parsed successfully for `notebooks/notebook_registry.yaml`
  - AC14-native canonical notebook and implementation-status doc now exist
- dependency-aware planning lane verification passed:
  - `pytest -q` passed with `93 passed`
  - `python -m mypy ac14 tests` passed on 54 source files
  - `python -m ruff check ac14 tests` passed
- targeted dependency-aware planning verification passed:
  - `pytest -q tests/test_blueprint_planning.py tests/test_draft_authoring.py tests/test_cli.py tests/test_make_targets.py -x` passed with `42 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- dependency-planning lane verification passed:
  - `pytest -q` passed with `91 passed`
  - `python -m mypy ac14 tests` passed on 54 source files
  - `python -m ruff check ac14 tests` passed
- targeted dependency-planning verification passed:
  - `pytest -q tests/test_dependency_planning.py tests/test_cli.py tests/test_make_targets.py -x` passed with `40 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- shared-retrieval lane verification passed:
  - `pytest -q` passed with `86 passed`
  - `python -m mypy ac14 tests` passed on 52 source files
  - `python -m ruff check ac14 tests` passed
- targeted shared-retrieval verification passed:
  - `pytest -q tests/test_retrieval.py tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py -x` passed with `43 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`

## Longer-Term Next Steps

- [ ] connect broader proof breadth to less hard-coded deterministic generation
- [ ] connect remediation tasks to automated draft-refinement loops when the current manual bundle-edit loop is proven
- [ ] feed dependency planning into draft planning and freeze readiness so library decisions stay explicit
- [ ] connect dependency planning to installation execution only after the advisory layer is proven
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

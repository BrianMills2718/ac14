# AC14 TODO

Status: Active control surface
Last updated: 2026-03-30

## Short-Term Active Lane

- [x] Phase 1: freeze the remediation lane
  - [x] update `CLAUDE.md` to make freeze remediation the active proof-expansion rule
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md` with remediation phases and success criteria
  - [x] keep this TODO as the running control surface during implementation
  - Success criteria: the active lane is documented honestly and can run without stop-and-ask interpretation

- [ ] Phase 2: add the freeze remediation artifact
  - [ ] persist remediation tasks alongside each freeze decision
  - [ ] group findings into actionable authoring buckets
  - [ ] point tasks at bundle files or upstream planning artifacts
  - [ ] include an explicit rerun path for freeze after edits
  - Success criteria: a blocked freeze decision becomes a usable authoring worklist instead of a flat finding dump

- [ ] Phase 3: wire remediation through CLI, Make, and tests
  - [ ] expose remediation-path details through `decide-freeze`
  - [ ] keep the Make surface aligned with the CLI behavior
  - [ ] add deterministic tests for blocked-remediation and approved-no-work paths
  - Success criteria: the remediation loop is discoverable and verified from operator surfaces

- [ ] Phase 4: verify and lock the lane
  - [ ] run full `pytest -q`
  - [ ] run full `python -m mypy ac14 tests`
  - [ ] run full `python -m ruff check ac14 tests`
  - [ ] update TODO, plan, README, and KNOWLEDGE to reflect actual final state
  - Success criteria: local verification passes and the control docs match the implemented lane

## Logged Uncertainties

- the generated component logic is still semantic-responsibility-specific rather than general synthesis
- realistic-input acceptance will still be synthetic-but-plausible until the pre-freeze discovery layer exists
- proof breadth is still narrow even though the suite now has multiple blueprints
- live LLM acceptance may be too expensive for the default gate and may remain optional outside targeted runs
- discovery will start with local input inspection and environment/dependency planning before broader doc/repo retrieval is implemented
- the next bridge will produce draft planning artifacts, not claim that blueprint freeze is solved
- the next bridge will materialize draft bundles and readiness reports, not claim those drafts are frozen
- the next bridge will decide and promote only when approval is explicit; it still does not broaden proof breadth
- the new remediation loop will guide direct draft-bundle editing first; automated rewrite loops are still deferred

## Latest Verified Results

- freeze-decision lane verification passed:
  - `pytest -q` passed with `78 passed`
  - `python -m mypy ac14 tests` passed on 50 source files
  - `python -m ruff check ac14 tests` passed
- targeted freeze-decision verification passed:
  - `pytest -q tests/test_freeze_decision.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- draft-authoring lane verification passed:
  - `pytest -q` passed with `73 passed`
  - `python -m mypy ac14 tests` passed on 48 source files
  - `python -m ruff check ac14 tests` passed
- targeted draft-authoring verification passed:
  - `pytest -q tests/test_draft_authoring.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- discovery-to-plan lane verification passed:
  - `pytest -q` passed with `69 passed`
  - `python -m mypy ac14 tests` passed on 46 source files
  - `python -m ruff check ac14 tests` passed
- targeted planning verification passed:
  - `pytest -q tests/test_blueprint_planning.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- discovery lane verification passed:
  - `pytest -q` passed with `66 passed`
  - `python -m mypy ac14 tests` passed on 44 source files
  - `python -m ruff check ac14 tests` passed
- targeted discovery verification passed:
  - `pytest -q tests/test_discovery.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- full lane verification passed:
  - `pytest -q` passed with `57 passed`
  - `python -m mypy ac14 tests` passed on 42 source files
  - `python -m ruff check ac14 tests` passed
- targeted lane verification passed:
  - `pytest -q tests/test_validation.py tests/test_acceptance.py tests/test_cli.py tests/test_make_targets.py`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- `pytest -q` passed
- `python -m mypy ac14 tests` passed
- `python -m ruff check ac14 tests` passed
- live unit smoke for `tests/test_live_llm_codegen.py` passed
- live CLI generation with `python -m ac14 generate-components ... --generator llm` passed
- targeted recomposition-proof tests passed after removing example-specific proof assumptions
- targeted suite discovery, suite proof, suite comparison, CLI, and Make tests passed
- `pytest -q` passed with `43 passed`
- `python -m mypy ac14 tests` passed on 35 source files
- `python -m ruff check ac14 tests` passed
- targeted reference, semantic comparison, recommendation, CLI, and Make tests passed
- `pytest -q` passed with `50 passed`
- `python -m mypy ac14 tests` passed on 40 source files
- `python -m ruff check ac14 tests` passed

## Longer-Term Next Steps

- [ ] widen proof breadth beyond the current ticket-digest slice
- [ ] connect remediation tasks to automated draft-refinement loops when the current manual bundle-edit loop is proven
- [ ] extend discovery beyond local files into shared doc/repo/dependency retrieval surfaces
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

# AC14 TODO

Status: Active control surface
Last updated: 2026-03-30

## Short-Term Active Lane

- [x] Phase 1: freeze the proof-breadth lane
  - [x] update `CLAUDE.md` to make proof breadth expansion the active proof-expansion rule
  - [x] refresh `docs/AC14_NEXT_24_HOURS.md` with proof-breadth phases and success criteria
  - [x] keep this TODO as the running control surface during implementation
  - Success criteria: the active lane is documented honestly and can run without stop-and-ask interpretation

- [x] Phase 2: broaden the shipped proof suite
  - [x] add one non-ticket workflow bundle with a distinct semantic-responsibility signature
  - [x] support that bundle in the reference runtime
  - [x] support that bundle in the deterministic generator
  - Success criteria: the suite has at least two distinct workflow signatures and the new example passes the same proof surfaces as the old one

- [x] Phase 3: replace narrow proof-breadth wording
  - [x] rename `semantic family` metrics and messages to `proof breadth`
  - [x] update recommendation and related tests to use the broader suite honestly
  - [x] keep anti-drift docs aligned with the implementation wording
  - Success criteria: evaluation heuristics stop reading like project ontology

- [x] Phase 4: verify and lock the lane
  - [x] run full `pytest -q`
  - [x] run full `python -m mypy ac14 tests`
  - [x] run full `python -m ruff check ac14 tests`
  - [x] update TODO, plan, README, and KNOWLEDGE to reflect actual final state
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

## Latest Verified Results

- proof-breadth lane verification passed:
  - `pytest -q` passed with `78 passed`
  - `python -m mypy ac14 tests` passed on 50 source files
  - `python -m ruff check ac14 tests` passed
- targeted proof-breadth verification passed:
  - `pytest -q tests/test_examples.py tests/test_reference_runtime.py tests/test_recommendation.py tests/test_generated_evidence.py tests/test_semantic_comparison.py tests/test_acceptance.py` passed with `11 passed`
  - `pytest -q tests/test_suite.py tests/test_make_targets.py tests/test_cli.py` passed with `33 passed`
  - `python -m ac14 list-examples --examples-root examples` returned three shipped examples including `incident_alert_digest`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
- freeze-remediation lane verification passed:
  - `pytest -q` passed with `78 passed`
  - `python -m mypy ac14 tests` passed on 50 source files
  - `python -m ruff check ac14 tests` passed
- targeted freeze-remediation verification passed:
  - `pytest -q tests/test_freeze_decision.py tests/test_cli.py tests/test_make_targets.py` passed with `33 passed`
  - `python -m mypy ac14 tests`
  - `python -m ruff check ac14 tests`
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

- [ ] connect broader proof breadth to less hard-coded deterministic generation
- [ ] connect remediation tasks to automated draft-refinement loops when the current manual bundle-edit loop is proven
- [ ] extend discovery beyond local files into shared doc/repo/dependency retrieval surfaces
- [ ] connect shared retrieval and dependency-install surfaces without coupling AC14 to agent-only MCP runtime assumptions

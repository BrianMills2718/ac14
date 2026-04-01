# AC14

AC14 is a clean implementation of the decomposition-first coding-agent thesis.

The first proof slice is intentionally narrow:

- frozen six-file blueprint bundle
- canonical in-memory blueprint model
- B1 blueprint validation
- packet compilation and B2 packet validation

AC14 is not trying to solve enterprise deployment, full autonomy, or broad
tool/runtime integration in the first pass.

## Local Setup

```bash
bash scripts/setup_hooks.sh
```

This enables the tracked `hooks/commit-msg` hook so local commits follow the
repo's light plan-prefix discipline.

The repo also reads shared process policy from [meta-process.yaml](/home/brian/projects/ac14/meta-process.yaml).
Dependency-probe behavior is currently governed by:

- `strict` = blocked probes block freeze
- `warn` = blocked probes stay visible but non-blocking
- `ignore` = probe results are recorded but omitted from freeze blocking

## Core Docs

- [Roadmap](/home/brian/projects/ac14/docs/AC14_ROADMAP.md)
- [Anti-Drift Doctrine](/home/brian/projects/ac14/docs/AC14_ANTI_DRIFT_DOCTRINE.md)
- [Uncertainties](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)
- [Implementation Status](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md)
- [Next 24 Hours](/home/brian/projects/ac14/docs/AC14_NEXT_24_HOURS.md)
- [TODO](/home/brian/projects/ac14/docs/TODO.md)
- [Plans Index](/home/brian/projects/ac14/docs/plans/CLAUDE.md)
- [Meta-Process Adoption Plan](/home/brian/projects/ac14/docs/AC14_META_PROCESS_ADOPTION_PLAN.md)
- [Execution Notebook](/home/brian/projects/ac14/notebooks/01_ac14_execution_status_journey.ipynb)

## What Works Today

AC14 now supports:

- keeping an AC14-native execution/alignment notebook and status surface so the story artifact can stay synchronized with the implementation
- loading and validating the six-file blueprint bundle
- inspecting local inputs before blueprint freeze and persisting discovery artifacts with inferred field summaries and open concerns
- recording environment and dependency inventory before generation begins
- recording local project-document context before blueprint freeze so README, CLAUDE, and docs become explicit planning inputs
- retrieving and persisting reviewable external documentation and repository-search artifacts before blueprint freeze
- building an evidence-backed advisory dependency and library plan before blueprint freeze
- probing dependency-plan recommendations through an explicit persisted execution artifact with narrow default mutation rules
- turning a persisted discovery artifact plus explicit requirements into an LLM-backed draft blueprint planning artifact
- carrying dependency-plan provenance, confirmed probe evidence, blocked probe evidence, and unresolved dependency questions into draft planning and freeze readiness
- consuming shared `meta-process` dependency-probe policy instead of hard-coding freeze behavior
- materializing a six-file draft bundle plus a freeze-readiness report from that planning artifact
- making an explicit approve/block freeze decision and promoting only approved bundles
- turning blocked freeze decisions into persisted remediation worklists with bundle-edit retry paths
- running a persisted realistic-input front-half acceptance lane from discovery through freeze decision plus a structured semantic review
- running a persisted realistic-input full-system acceptance lane in `reference` mode with actual outputs plus a final semantic review
- enforcing explicit scenario kinds, evaluator definitions, component fixture coverage, and realistic-input semantic-acceptance coverage
- discovering a shipped suite of blueprint examples with more than one workflow slice
- compiling bounded component packets
- emitting standalone generated Python components from packet/codegen contexts
- running packet-local tests and recomposition proof on generated code
- writing persisted evidence bundles and repeated fresh-run summaries
- comparing deterministic and LLM-backed generators
- building suite-level proof and comparison artifacts across shipped examples
- building semantic comparison artifacts across reference and generated modes
- building requirements-aware semantic-acceptance artifacts against actual system outputs
- producing an evidence-backed default-generator recommendation that reasons about proof breadth

## What Is Still Missing

AC14 is still incomplete on:

- broader proof breadth across many workflow shapes
- stronger messy-input blueprint derivation
- broad automatic dependency execution/install remediation
- richer first-class semantic/business-logic review at every major gate
- realistic-input full-system acceptance outside `reference` mode
- realistic-input full-system acceptance as the default gate instead of only a front-half gate
- first-class tool/runtime nodes in the blueprint model

The blunt state-of-project summary is in [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md).

## Quickstart

```bash
make test
make verify-blueprint
make discover-input INPUT=path/to/input.json OUTPUT=.ac14_out/discovery PACKAGES="pydantic"
make inspect-environment OUTPUT=.ac14_out/environment PACKAGES="pydantic"
make inspect-project-context OUTPUT=.ac14_out/project_context
make retrieve-context OUTPUT=.ac14_out/retrieval WEB_QUERY="incident response playbook" REPO_QUERY="packet compiler" REPOS="example/ac14"
make plan-dependencies DISCOVERY=.ac14_out/discovery/discovery_artifact.json OUTPUT=.ac14_out/dependency_plan REQUIREMENTS="preserve typed schema contracts avoid unnecessary dependencies"
make probe-dependencies DEPENDENCY_PLAN=.ac14_out/dependency_plan/dependency_plan.json OUTPUT=.ac14_out/dependency_probe
make draft-blueprint-plan DISCOVERY=.ac14_out/discovery/discovery_artifact.json DEPENDENCY_PLAN=.ac14_out/dependency_plan/dependency_plan.json DEPENDENCY_EXECUTION=.ac14_out/dependency_probe/dependency_execution_artifact.json OUTPUT=.ac14_out/draft_plan REQUIREMENTS="bounded decomposition preserve semantics"
make materialize-draft-bundle PLAN=.ac14_out/draft_plan/draft_blueprint_plan.json OUTPUT=.ac14_out/draft_bundle
make decide-freeze INPUT=.ac14_out/draft_bundle OUTPUT=.ac14_out/freeze READINESS=.ac14_out/draft_bundle/freeze_readiness_report.json
make front-half-acceptance REALISTIC_INPUT=examples/support_ticket_digest/input/realistic_ticket_batch.json OUTPUT=.ac14_out/front_half REQUIREMENTS="preserve support ticket meaning keep packets bounded" PACKAGES="pydantic"
make acceptance-review INPUT=examples/support_ticket_digest/blueprint OUTPUT=.ac14_out/acceptance_realistic GENERATOR=reference REALISTIC_INPUT=examples/support_ticket_digest/input/realistic_ticket_batch.json RECORD_INDEX=0
make list-examples
make generate-components OUTPUT=.ac14_out/generated
make prove-example OUTPUT=.ac14_out/proof TRIALS=3
make fresh-runs OUTPUT=.ac14_out/fresh TRIALS=3
make acceptance-review INPUT=examples/support_ticket_digest/blueprint OUTPUT=.ac14_out/acceptance GENERATOR=deterministic
make prove-suite OUTPUT=.ac14_out/suite TRIALS=1
make compare-suite OUTPUT=.ac14_out/suite_compare TRIALS=1 GENERATORS=deterministic
make semantic-compare-suite OUTPUT=.ac14_out/suite_semantic MODES="reference deterministic"
make acceptance-review-suite OUTPUT=.ac14_out/suite_acceptance GENERATOR=deterministic
make recommend-default-generator OUTPUT=.ac14_out/recommend GENERATORS=deterministic TRIALS=1
```

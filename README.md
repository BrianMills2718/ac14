# AC14

AC14 is a clean implementation of the decomposition-first coding-agent thesis.

The first proof slice is intentionally narrow:

- frozen six-file blueprint bundle
- canonical in-memory blueprint model
- B1 blueprint validation
- packet compilation and B2 packet validation

AC14 is not trying to solve enterprise deployment, full autonomy, or broad
tool/runtime integration in the first pass.

## Current Proof Surface

AC14 now supports:

- loading and validating the six-file blueprint bundle
- inspecting local inputs before blueprint freeze and persisting discovery artifacts with inferred field summaries and open concerns
- recording environment and dependency inventory before generation begins
- recording local project-document context before blueprint freeze so README, CLAUDE, and docs become explicit planning inputs
- turning a persisted discovery artifact plus explicit requirements into an LLM-backed draft blueprint planning artifact
- materializing a six-file draft bundle plus a freeze-readiness report from that planning artifact
- making an explicit approve/block freeze decision and promoting only approved bundles
- turning blocked freeze decisions into persisted remediation worklists with bundle-edit retry paths
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

## Quickstart

```bash
make test
make verify-blueprint
make discover-input INPUT=path/to/input.json OUTPUT=.ac14_out/discovery PACKAGES="pydantic"
make inspect-environment OUTPUT=.ac14_out/environment PACKAGES="pydantic"
make inspect-project-context OUTPUT=.ac14_out/project_context
make draft-blueprint-plan DISCOVERY=.ac14_out/discovery/discovery_artifact.json OUTPUT=.ac14_out/draft_plan REQUIREMENTS="bounded decomposition preserve semantics"
make materialize-draft-bundle PLAN=.ac14_out/draft_plan/draft_blueprint_plan.json OUTPUT=.ac14_out/draft_bundle
make decide-freeze INPUT=.ac14_out/draft_bundle OUTPUT=.ac14_out/freeze READINESS=.ac14_out/draft_bundle/freeze_readiness_report.json
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

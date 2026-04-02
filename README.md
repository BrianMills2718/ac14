# AC14

AC14 is a clean implementation of the decomposition-first coding-agent thesis.

The first proof slice is intentionally narrow:

- frozen six-file blueprint bundle
- canonical in-memory blueprint model
- B1 blueprint validation
- packet compilation and B2 packet validation

AC14 is not trying to solve enterprise deployment, full autonomy, or broad
tool/runtime integration in the first pass.

The current empirical comparison surface is also intentionally narrower than
the full end-to-end thesis: the active benchmark compares packetized local
generation against whole-package generation over a fixed decomposition.

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
- accepting one bounded input directory as a reviewable discovery surface, inventorying explicit structured candidates plus supporting local context files, and persisting one deterministic primary structured candidate plus explicit alternatives
- persisting bounded summaries for alternate structured candidates and supporting local context files in that same directory-discovery surface while keeping one explicit primary structured planning input
- proving that those new directory summaries survive the full front-half discovery-through-freeze chain instead of remaining only a raw discovery feature
- surfacing explicit bounded schema-divergence concerns when alternate structured candidates expose fields that differ from the primary structured planning input
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
- attaching a persisted semantic review artifact directly to draft/freeze quality whenever `decide-freeze` evaluates a draft bundle with readiness evidence
- running a persisted realistic-input front-half acceptance lane from discovery through freeze decision plus a structured semantic review
- proving that the same front-half acceptance lane can start from a bounded directory input bundle while preserving the directory input path plus explicit primary and alternate structured candidates
- running a persisted suite-level front-half acceptance lane across shipped realistic-input examples, with separate review-vs-freeze aggregates and explicit freeze-semantic review paths
- proving one explicit messy-input front-half lane on a reviewable CSV asset without changing the blueprint/runtime model
- rerunning previously blocked install probes through one explicit dependency-remediation artifact that points to a fresh dependency execution artifact for downstream reuse
- feeding a dependency-remediation artifact directly back into draft planning while keeping both the remediation path and the chosen dependency execution path explicit
- refining a blocked draft planning artifact directly from the freeze decision plus remediation plan while preserving the full retry provenance
- running one explicit retry chain that refines a blocked plan, rematerializes the bundle, reruns freeze, and persists every intermediate path
- optionally carrying that retry-chain evidence into realistic-input front-half acceptance while preserving the initial blocked freeze record
- optionally carrying that retry-aware front-half evidence across the shipped suite while preserving per-example retry artifact paths
- proving the same retry-aware front-half story on the shipped messy CSV asset without inventing a new artifact type
- sharing structured-input loading between discovery and realistic-input acceptance so the final gate now supports record-bearing `json`, `jsonl`, `csv`, and `yaml` inputs
- defining explicit realistic-input manifests for shipped examples so the clean default and alternate profiles are named instead of implied by file precedence
- exposing explicit realistic-input profile selection on suite/operator surfaces while preserving the clean default path when no profile is specified
- proving one explicit suite-level `messy` profile lane across `reference`, `deterministic`, and bounded fixture-backed `llm`, with explicit `missing_profile` states for the other shipped examples
- running a persisted realistic-input full-system acceptance lane in `reference` and `deterministic` modes with actual outputs plus a final semantic review
- proving the shipped support-ticket messy CSV asset through that same final gate in `reference` and `deterministic` modes, plus the non-LLM realistic mode-comparison surface
- persisting one suite-level realistic-input acceptance artifact across shipped examples for the currently supported non-LLM modes
- running one bounded realistic-input full-system acceptance lane in `llm` mode with persisted outputs plus final semantic review
- proving the shipped support-ticket messy CSV asset through that same bounded `llm` final gate plus the matching realistic mode-comparison surface
- persisting one per-blueprint realistic-input comparison artifact across `reference`, `deterministic`, and `llm`
- persisting one fixture-backed suite-level realistic-input acceptance artifact in `llm` mode across shipped examples
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
- persisting an explicit live-readiness artifact for realistic-input `llm` acceptance that stays separate from fixture-backed breadth and requires `AC14_ENABLE_LIVE_LLM_READINESS=1` before a real live attempt
- persisting a structural packet-sufficiency artifact so packet existence and packet sufficiency are not conflated
- carrying realistic-input full-system acceptance into the default deterministic proof/evidence bundle for shipped examples, while keeping missing realistic-input artifacts explicit
- carrying realistic-input full-system acceptance into the default suite proof/evidence story for shipped examples, while keeping missing and unsupported suite gate states explicit
- making default-generator recommendation consume suite-level realistic-input default-gate evidence instead of reasoning only from structural suite comparison and semantic comparison
- persisting a suite-level live-readiness artifact for realistic-input `llm` acceptance with explicit per-example and aggregate `ready`, `blocked`, and `skipped` results
- making default-generator recommendation consume both the bounded one-example live-readiness artifact and the broader suite-level live-readiness artifact

## What Is Still Missing

AC14 is still incomplete on:

- one explicit empirical comparison showing whether AC14 materially beats a fair monolithic baseline
- broader proof breadth across many workflow shapes
- stronger messy-input blueprint derivation
- explicit front-half proof that the new directory schema-divergence concerns survive the discovery-through-freeze chain
- broader refinement and retry loops after blocked freeze
- broad automatic dependency execution/install remediation
- richer first-class semantic/business-logic review at every major gate
- first-class tool/runtime nodes in the blueprint model

The blunt state-of-project summary is in [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md).

The next strategic gate is
[Plan #42: Empirical Benchmark Fidelity Repair](/home/brian/projects/ac14/docs/plans/42_empirical_benchmark_fidelity_repair.md),
which follows completed smoke stabilization and first harness-repair work. The
goal now is to make the next bounded smoke rerun benchmark-fidelity-focused
enough to justify spending the full five-trial budget in
[Plan #39: Monolithic Vs AC14 Comparison Execution](/home/brian/projects/ac14/docs/plans/39_monolithic_vs_ac14_comparison_execution.md).

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
make acceptance-review-realistic-suite OUTPUT=.ac14_out/realistic_suite_acceptance MODES="reference deterministic" RECORD_INDEX=0
make acceptance-review-realistic-compare INPUT=examples/support_ticket_digest/blueprint REALISTIC_INPUT=examples/support_ticket_digest/input/realistic_ticket_batch.json OUTPUT=.ac14_out/realistic_compare MODES="reference deterministic llm" RECORD_INDEX=0
AC14_ENABLE_LIVE_LLM_READINESS=1 make live-llm-readiness OUTPUT=.ac14_out/live_llm_readiness
AC14_ENABLE_LIVE_LLM_READINESS=1 make live-llm-readiness-suite OUTPUT=.ac14_out/live_llm_readiness_suite
make packet-sufficiency INPUT=examples/support_ticket_digest/blueprint OUTPUT=.ac14_out/packet_sufficiency
make recommend-default-generator OUTPUT=.ac14_out/recommend GENERATORS=deterministic TRIALS=1
make empirical-smoke-gate BENCHMARK=benchmarks/order_exception_resolution OUTPUT=.ac14_out/empirical_smoke MAX_ATTEMPTS=1
```

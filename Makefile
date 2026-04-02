# AC14 Makefile

SHELL := /bin/bash
.DEFAULT_GOAL := help
PROJECT := $(notdir $(CURDIR))
PYTHON := python3
INPUT ?= examples/support_ticket_digest/blueprint
REALISTIC_INPUT ?= examples/support_ticket_digest/input/realistic_ticket_batch.json
EXAMPLES_ROOT ?= examples
OUTPUT ?= .ac14_out
TRIALS ?= 3
MAX_ATTEMPTS ?= 3
GENERATOR ?= deterministic
GENERATORS ?= deterministic llm
MODES ?= reference deterministic
MODEL ?= gemini/gemini-2.5-flash-lite
MAX_BUDGET ?= 0.50
RETRY_MODEL ?= gemini/gemini-2.5-flash-lite
RETRY_MAX_BUDGET ?= 0.75
RECORD_INDEX ?= 0
REALISTIC_INPUT_PROFILE ?=
PACKAGES ?=
WEB_QUERY ?=
REPO_QUERY ?=
REPOS ?=
RETRIEVAL_ARTIFACTS ?=
DISCOVERY ?= .ac14_out/discovery/discovery_artifact.json
PLAN ?= .ac14_out/draft_plan/draft_blueprint_plan.json
DEPENDENCY_PLAN ?=
DEPENDENCY_EXECUTION ?=
DEPENDENCY_REMEDIATION ?=
ALLOW_INSTALL ?= 0
RETRY_BLOCKED_FREEZE ?= 0
REQUIREMENTS ?= clarify input schema preserve bounded packets
READINESS ?=
BENCHMARK ?= benchmarks/order_exception_resolution

.PHONY: help test test-quick check status verify-blueprint packet-sufficiency discover-input inspect-environment inspect-project-context retrieve-context plan-dependencies probe-dependencies remediate-dependencies draft-blueprint-plan refine-draft-blueprint-plan retry-freeze materialize-draft-bundle decide-freeze front-half-acceptance front-half-acceptance-suite generate-components prove-example fresh-runs compare-generators acceptance-review semantic-compare list-examples prove-suite compare-suite semantic-compare-suite acceptance-review-suite acceptance-review-realistic-suite acceptance-review-realistic-compare recommend-default-generator live-llm-readiness live-llm-readiness-suite empirical-compare empirical-smoke-gate

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: ## Run full test suite
	$(PYTHON) -m pytest -q

test-quick: ## Run tests with fail-fast
	$(PYTHON) -m pytest -x -q

check: ## Run tests, lint, and type-checking
	$(PYTHON) -m pytest -q
	$(PYTHON) -m ruff check ac14 tests
	$(PYTHON) -m mypy ac14 tests

status: ## Show git status
	@git status --short --branch

verify-blueprint: ## Validate a blueprint bundle (INPUT=examples/.../blueprint)
	$(PYTHON) -m ac14 verify-blueprint "$(INPUT)"

packet-sufficiency: ## Build a persisted structural packet-sufficiency artifact (INPUT=examples/.../blueprint OUTPUT=.ac14_out/packet_sufficiency)
	$(PYTHON) -m ac14 packet-sufficiency "$(INPUT)" --output-dir "$(OUTPUT)"

discover-input: ## Inspect a local input and persist a pre-freeze discovery artifact (INPUT=data.json OUTPUT=.ac14_out/discovery PACKAGES="pandas requests")
	$(PYTHON) -m ac14 discover-input "$(INPUT)" --output-dir "$(OUTPUT)" --project-root "$(CURDIR)" --packages $(PACKAGES) $(foreach artifact,$(RETRIEVAL_ARTIFACTS),--retrieval-artifact "$(artifact)")

inspect-environment: ## Persist the current discovery environment inventory (OUTPUT=.ac14_out/environment PACKAGES="pandas requests")
	$(PYTHON) -m ac14 inspect-environment --output-dir "$(OUTPUT)" --project-root "$(CURDIR)" --packages $(PACKAGES)

inspect-project-context: ## Persist local project-document context (OUTPUT=.ac14_out/project_context)
	$(PYTHON) -m ac14 inspect-project-context --output-dir "$(OUTPUT)" --project-root "$(CURDIR)"

retrieve-context: ## Persist reviewable external documentation/repository retrieval artifacts (OUTPUT=.ac14_out/retrieval WEB_QUERY="..." REPO_QUERY="..." REPOS="owner/repo")
	$(PYTHON) -m ac14 retrieve-context --output-dir "$(OUTPUT)" $(if $(WEB_QUERY),--web-query "$(WEB_QUERY)",) $(if $(REPO_QUERY),--repo-query "$(REPO_QUERY)",) $(foreach repo,$(REPOS),--repo "$(repo)")

plan-dependencies: ## Build an evidence-backed dependency plan (DISCOVERY=.ac14_out/discovery/discovery_artifact.json OUTPUT=.ac14_out/dependency_plan REQUIREMENTS="...")
	$(PYTHON) -m ac14 plan-dependencies "$(DISCOVERY)" --output-dir "$(OUTPUT)" --requirements $(REQUIREMENTS) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

probe-dependencies: ## Probe dependency recommendations (DEPENDENCY_PLAN=.ac14_out/dependency_plan/dependency_plan.json OUTPUT=.ac14_out/dependency_probe ALLOW_INSTALL=1 to permit installs)
	$(PYTHON) -m ac14 probe-dependencies "$(DEPENDENCY_PLAN)" --output-dir "$(OUTPUT)" --project-root "$(CURDIR)" $(if $(filter 1 true yes,$(ALLOW_INSTALL)),--allow-install,)

remediate-dependencies: ## Rerun blocked install probes from an execution artifact (INPUT=.ac14_out/dependency_probe/dependency_execution_artifact.json OUTPUT=.ac14_out/dependency_remediation)
	$(PYTHON) -m ac14 remediate-dependencies "$(INPUT)" --output-dir "$(OUTPUT)" --project-root "$(CURDIR)"

draft-blueprint-plan: ## Build an LLM-backed draft blueprint plan (DISCOVERY=.ac14_out/discovery/discovery_artifact.json OUTPUT=.ac14_out/draft_plan REQUIREMENTS="..." DEPENDENCY_PLAN=optional.json DEPENDENCY_EXECUTION=optional.json DEPENDENCY_REMEDIATION=optional.json)
	$(PYTHON) -m ac14 draft-blueprint-plan "$(DISCOVERY)" --output-dir "$(OUTPUT)" --requirements $(REQUIREMENTS) $(if $(DEPENDENCY_PLAN),--dependency-plan "$(DEPENDENCY_PLAN)",) $(if $(DEPENDENCY_EXECUTION),--dependency-execution "$(DEPENDENCY_EXECUTION)",) $(if $(DEPENDENCY_REMEDIATION),--dependency-remediation "$(DEPENDENCY_REMEDIATION)",) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

refine-draft-blueprint-plan: ## Refine a blocked draft plan from a freeze decision (PLAN=.ac14_out/draft_plan/draft_blueprint_plan.json INPUT=.ac14_out/freeze_decision/freeze_decision.json OUTPUT=.ac14_out/refined_draft_plan)
	$(PYTHON) -m ac14 refine-draft-blueprint-plan "$(PLAN)" --freeze-decision "$(INPUT)" --output-dir "$(OUTPUT)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

retry-freeze: ## Run refine -> materialize -> refreeze as one explicit retry chain (PLAN=.ac14_out/draft_plan/draft_blueprint_plan.json INPUT=.ac14_out/freeze_decision/freeze_decision.json OUTPUT=.ac14_out/freeze_retry)
	$(PYTHON) -m ac14 retry-freeze "$(PLAN)" --freeze-decision "$(INPUT)" --output-dir "$(OUTPUT)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

materialize-draft-bundle: ## Materialize a six-file draft bundle and readiness report (PLAN=.ac14_out/draft_plan/draft_blueprint_plan.json OUTPUT=.ac14_out/draft_bundle)
	$(PYTHON) -m ac14 materialize-draft-bundle "$(PLAN)" --output-dir "$(OUTPUT)"

decide-freeze: ## Build a freeze decision and promote only when approved (INPUT=bundle_dir OUTPUT=.ac14_out/freeze READINESS=optional_report.json)
	$(PYTHON) -m ac14 decide-freeze "$(INPUT)" --output-dir "$(OUTPUT)" $(if $(READINESS),--readiness-report "$(READINESS)",)

front-half-acceptance: ## Run realistic-input discovery through freeze decision and review the front half (REALISTIC_INPUT=... OUTPUT=.ac14_out/front_half REQUIREMENTS="..." PACKAGES="pydantic" RETRY_BLOCKED_FREEZE=1)
	$(PYTHON) -m ac14 front-half-acceptance "$(REALISTIC_INPUT)" --output-dir "$(OUTPUT)" --requirements $(REQUIREMENTS) --project-root "$(CURDIR)" --packages $(PACKAGES) $(foreach artifact,$(RETRIEVAL_ARTIFACTS),--retrieval-artifact "$(artifact)") $(if $(filter 1 true yes,$(ALLOW_INSTALL)),--allow-install,) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)" $(if $(filter 1 true yes,$(RETRY_BLOCKED_FREEZE)),--retry-blocked-freeze,) --retry-model "$(RETRY_MODEL)" --retry-max-budget "$(RETRY_MAX_BUDGET)"

front-half-acceptance-suite: ## Run realistic-input front-half acceptance across shipped examples (OUTPUT=.ac14_out/front_half_suite EXAMPLES_ROOT=examples REALISTIC_INPUT_PROFILE=messy RETRY_BLOCKED_FREEZE=1)
	$(PYTHON) -m ac14 front-half-acceptance-suite --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" $(if $(REALISTIC_INPUT_PROFILE),--realistic-input-profile "$(REALISTIC_INPUT_PROFILE)",) $(if $(filter 1 true yes,$(ALLOW_INSTALL)),--allow-install,) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)" $(if $(filter 1 true yes,$(RETRY_BLOCKED_FREEZE)),--retry-blocked-freeze,) --retry-model "$(RETRY_MODEL)" --retry-max-budget "$(RETRY_MAX_BUDGET)"

generate-components: ## Emit generated components (INPUT=... OUTPUT=.ac14_out/generated GENERATOR=deterministic|llm)
	$(PYTHON) -m ac14 generate-components "$(INPUT)" --output-dir "$(OUTPUT)" --generator "$(GENERATOR)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

prove-example: ## Build a persisted proof bundle (INPUT=... OUTPUT=.ac14_out/proof TRIALS=3 GENERATOR=deterministic|llm)
	$(PYTHON) -m ac14 prove-example "$(INPUT)" --output-dir "$(OUTPUT)" --fresh-run-trials "$(TRIALS)" --generator "$(GENERATOR)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

fresh-runs: ## Run repeated fresh generation trials (INPUT=... OUTPUT=.ac14_out/fresh TRIALS=3 GENERATOR=deterministic|llm)
	$(PYTHON) -m ac14 fresh-runs "$(INPUT)" --output-dir "$(OUTPUT)" --trials "$(TRIALS)" --generator "$(GENERATOR)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

compare-generators: ## Compare generator modes (INPUT=... OUTPUT=.ac14_out/compare GENERATORS="deterministic llm")
	$(PYTHON) -m ac14 compare-generators "$(INPUT)" --output-dir "$(OUTPUT)" --fresh-run-trials "$(TRIALS)" --generators $(GENERATORS) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

acceptance-review: ## Run requirements-aware acceptance review for one blueprint (INPUT=... OUTPUT=.ac14_out/acceptance GENERATOR=reference|deterministic|llm REALISTIC_INPUT=optional.json RECORD_INDEX=0)
	$(PYTHON) -m ac14 acceptance-review "$(INPUT)" --output-dir "$(OUTPUT)" --mode "$(GENERATOR)" $(if $(REALISTIC_INPUT),--realistic-input "$(REALISTIC_INPUT)",) --record-index "$(RECORD_INDEX)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

semantic-compare: ## Compare semantic outputs for one blueprint (INPUT=... OUTPUT=.ac14_out/semantic MODES="reference deterministic")
	$(PYTHON) -m ac14 semantic-compare "$(INPUT)" --output-dir "$(OUTPUT)" --modes $(MODES) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

list-examples: ## List shipped blueprint examples (EXAMPLES_ROOT=examples)
	$(PYTHON) -m ac14 list-examples --examples-root "$(EXAMPLES_ROOT)"

prove-suite: ## Build persisted proof bundles across shipped examples (OUTPUT=.ac14_out/suite TRIALS=2 GENERATOR=deterministic|llm)
	$(PYTHON) -m ac14 prove-suite --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" --fresh-run-trials "$(TRIALS)" --generator "$(GENERATOR)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

compare-suite: ## Compare generator modes across shipped examples (OUTPUT=.ac14_out/suite_compare GENERATORS="deterministic llm")
	$(PYTHON) -m ac14 compare-suite --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" --fresh-run-trials "$(TRIALS)" --generators $(GENERATORS) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

semantic-compare-suite: ## Compare semantic outputs across shipped examples (OUTPUT=.ac14_out/suite_semantic MODES="reference deterministic")
	$(PYTHON) -m ac14 semantic-compare-suite --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" --modes $(MODES) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

acceptance-review-suite: ## Run requirements-aware acceptance review across shipped examples (OUTPUT=.ac14_out/suite_acceptance GENERATOR=reference|deterministic|llm)
	$(PYTHON) -m ac14 acceptance-review-suite --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" --mode "$(GENERATOR)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

acceptance-review-realistic-suite: ## Run realistic-input acceptance review across shipped examples (OUTPUT=.ac14_out/realistic_suite_acceptance MODES="reference deterministic" REALISTIC_INPUT_PROFILE=messy RECORD_INDEX=0)
	$(PYTHON) -m ac14 acceptance-review-realistic-suite --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" --modes $(MODES) $(if $(REALISTIC_INPUT_PROFILE),--realistic-input-profile "$(REALISTIC_INPUT_PROFILE)",) --record-index "$(RECORD_INDEX)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

acceptance-review-realistic-compare: ## Compare realistic-input acceptance across modes for one blueprint (INPUT=... REALISTIC_INPUT=... OUTPUT=.ac14_out/realistic_compare MODES="reference deterministic llm" RECORD_INDEX=0)
	$(PYTHON) -m ac14 acceptance-review-realistic-compare "$(INPUT)" --output-dir "$(OUTPUT)" --realistic-input "$(REALISTIC_INPUT)" --modes $(MODES) --record-index "$(RECORD_INDEX)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

recommend-default-generator: ## Recommend the current default generator (OUTPUT=.ac14_out/recommend GENERATORS="deterministic")
	$(PYTHON) -m ac14 recommend-default-generator --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" --generators $(GENERATORS) --fresh-run-trials "$(TRIALS)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

live-llm-readiness: ## Build one persisted realistic-input live-readiness artifact for the LLM lane (OUTPUT=.ac14_out/live_llm_readiness)
	$(PYTHON) -m ac14 live-llm-readiness --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

live-llm-readiness-suite: ## Build one persisted realistic-input suite live-readiness artifact for the LLM lane (OUTPUT=.ac14_out/live_llm_readiness_suite)
	$(PYTHON) -m ac14 live-llm-readiness-suite --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

empirical-compare: ## Run the frozen monolithic-vs-AC14 empirical comparison benchmark (BENCHMARK=benchmarks/order_exception_resolution OUTPUT=.ac14_out/empirical_compare TRIALS=5 MAX_ATTEMPTS=3)
	$(PYTHON) -m ac14 empirical-compare "$(BENCHMARK)" --output-dir "$(OUTPUT)" --trials "$(TRIALS)" --max-attempts "$(MAX_ATTEMPTS)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

empirical-smoke-gate: ## Run one bounded paired smoke trial and persist a readiness verdict (BENCHMARK=... OUTPUT=.ac14_out/empirical_smoke MAX_ATTEMPTS=3)
	$(PYTHON) -m ac14 empirical-smoke-gate "$(BENCHMARK)" --output-dir "$(OUTPUT)" --max-attempts "$(MAX_ATTEMPTS)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

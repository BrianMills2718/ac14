# AC14 Makefile

SHELL := /bin/bash
.DEFAULT_GOAL := help
PROJECT := $(notdir $(CURDIR))
PYTHON := python3
INPUT ?= examples/support_ticket_digest/blueprint
EXAMPLES_ROOT ?= examples
OUTPUT ?= .ac14_out
TRIALS ?= 3
GENERATOR ?= deterministic
GENERATORS ?= deterministic llm
MODES ?= reference deterministic
MODEL ?= gemini/gemini-2.5-flash-lite
MAX_BUDGET ?= 0.50
PACKAGES ?=

.PHONY: help test test-quick check status verify-blueprint discover-input inspect-environment generate-components prove-example fresh-runs compare-generators acceptance-review semantic-compare list-examples prove-suite compare-suite semantic-compare-suite acceptance-review-suite recommend-default-generator

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

discover-input: ## Inspect a local input and persist a pre-freeze discovery artifact (INPUT=data.json OUTPUT=.ac14_out/discovery PACKAGES="pandas requests")
	$(PYTHON) -m ac14 discover-input "$(INPUT)" --output-dir "$(OUTPUT)" --project-root "$(CURDIR)" --packages $(PACKAGES)

inspect-environment: ## Persist the current discovery environment inventory (OUTPUT=.ac14_out/environment PACKAGES="pandas requests")
	$(PYTHON) -m ac14 inspect-environment --output-dir "$(OUTPUT)" --project-root "$(CURDIR)" --packages $(PACKAGES)

generate-components: ## Emit generated components (INPUT=... OUTPUT=.ac14_out/generated GENERATOR=deterministic|llm)
	$(PYTHON) -m ac14 generate-components "$(INPUT)" --output-dir "$(OUTPUT)" --generator "$(GENERATOR)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

prove-example: ## Build a persisted proof bundle (INPUT=... OUTPUT=.ac14_out/proof TRIALS=3 GENERATOR=deterministic|llm)
	$(PYTHON) -m ac14 prove-example "$(INPUT)" --output-dir "$(OUTPUT)" --fresh-run-trials "$(TRIALS)" --generator "$(GENERATOR)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

fresh-runs: ## Run repeated fresh generation trials (INPUT=... OUTPUT=.ac14_out/fresh TRIALS=3 GENERATOR=deterministic|llm)
	$(PYTHON) -m ac14 fresh-runs "$(INPUT)" --output-dir "$(OUTPUT)" --trials "$(TRIALS)" --generator "$(GENERATOR)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

compare-generators: ## Compare generator modes (INPUT=... OUTPUT=.ac14_out/compare GENERATORS="deterministic llm")
	$(PYTHON) -m ac14 compare-generators "$(INPUT)" --output-dir "$(OUTPUT)" --fresh-run-trials "$(TRIALS)" --generators $(GENERATORS) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

acceptance-review: ## Run requirements-aware acceptance review for one blueprint (INPUT=... OUTPUT=.ac14_out/acceptance GENERATOR=reference|deterministic|llm)
	$(PYTHON) -m ac14 acceptance-review "$(INPUT)" --output-dir "$(OUTPUT)" --mode "$(GENERATOR)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

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

recommend-default-generator: ## Recommend the current default generator (OUTPUT=.ac14_out/recommend GENERATORS="deterministic")
	$(PYTHON) -m ac14 recommend-default-generator --output-dir "$(OUTPUT)" --examples-root "$(EXAMPLES_ROOT)" --generators $(GENERATORS) --fresh-run-trials "$(TRIALS)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

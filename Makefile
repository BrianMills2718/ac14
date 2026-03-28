# AC14 Makefile

SHELL := /bin/bash
.DEFAULT_GOAL := help
PROJECT := $(notdir $(CURDIR))
PYTHON := python3
INPUT ?= examples/support_ticket_digest/blueprint
OUTPUT ?= .ac14_out
TRIALS ?= 3

.PHONY: help test test-quick check status verify-blueprint generate-components prove-example fresh-runs

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

generate-components: ## Emit generated components (INPUT=... OUTPUT=.ac14_out/generated)
	$(PYTHON) -m ac14 generate-components "$(INPUT)" --output-dir "$(OUTPUT)"

prove-example: ## Build a persisted proof bundle (INPUT=... OUTPUT=.ac14_out/proof TRIALS=3)
	$(PYTHON) -m ac14 prove-example "$(INPUT)" --output-dir "$(OUTPUT)" --fresh-run-trials "$(TRIALS)"

fresh-runs: ## Run repeated fresh generation trials (INPUT=... OUTPUT=.ac14_out/fresh TRIALS=3)
	$(PYTHON) -m ac14 fresh-runs "$(INPUT)" --output-dir "$(OUTPUT)" --trials "$(TRIALS)"

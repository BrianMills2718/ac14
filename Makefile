# AC14 Makefile

SHELL := /bin/bash
.DEFAULT_GOAL := help
PROJECT := $(notdir $(CURDIR))
PYTHON := python3

.PHONY: help test test-quick check status

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

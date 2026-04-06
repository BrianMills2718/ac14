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
MODEL ?= codex
MAX_BUDGET ?= 0.50
RETRY_MODEL ?= codex
RETRY_MAX_BUDGET ?= 0.75
RECORD_INDEX ?= 0
REALISTIC_INPUT_PROFILE ?=
PACKAGES ?=
WEB_QUERY ?=
REPO_QUERY ?=
REPOS ?=
RETRIEVAL_ARTIFACTS ?=
DISCOVERY ?= .ac14_out/discovery/discovery_artifact.json
STRUCTURED_SPEC ?= .ac14_out/structured_spec/structured_spec_artifact.json
PLAN ?= .ac14_out/draft_plan/draft_blueprint_plan.json
DEPENDENCY_PLAN ?=
DEPENDENCY_EXECUTION ?=
DEPENDENCY_REMEDIATION ?=
ALLOW_INSTALL ?= 0
RETRY_BLOCKED_FREEZE ?= 0
REQUIREMENTS ?= clarify input schema preserve bounded packets
READINESS ?=
BENCHMARK ?= benchmarks/order_exception_resolution

TRIAL ?= 1
ATTEMPT ?= 1

.PHONY: help test test-quick check status verify-blueprint packet-sufficiency discover-input prepare-structured-spec inspect-environment inspect-project-context retrieve-context plan-dependencies probe-dependencies remediate-dependencies draft-blueprint-plan draft-blueprint-plan-from-structured-spec refine-draft-blueprint-plan retry-freeze materialize-draft-bundle decide-freeze front-half-acceptance structured-spec-front-half-acceptance front-half-acceptance-suite generate-components prove-example fresh-runs compare-generators acceptance-review semantic-compare list-examples prove-suite compare-suite semantic-compare-suite acceptance-review-suite acceptance-review-realistic-suite acceptance-review-realistic-compare recommend-default-generator live-llm-readiness live-llm-readiness-suite empirical-compare empirical-smoke-gate front-half-first-smoke-gate front-half-first-full-trials context-audit diagnose-attempt trace-eval-check trace-eval

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
	@! grep -rn "max_tokens\s*=" ac14/ tests/ --include="*.py" | grep -v "model_max\|max_tokens.*#.*allowed\|_apply_max_tokens\|max_completion_tokens" \
		|| (echo "ERROR: max_tokens set on LLM call. CLAUDE.md forbids this." && exit 1)

status: ## Show git status
	@git status --short --branch

trial-status: ## Live progress of a running trial (OUTPUT=.ac14_out/my_run TRIAL=1)
	@dir="$(OUTPUT)/trial_$(TRIAL)/ac14"; \
	attempt=$$(for d in $$(ls -d $$dir/attempt_* 2>/dev/null | sort -V); do echo "$$(ls $$d/generated/*.codex_exit.txt 2>/dev/null | wc -l) $$d"; done | sort -rn | head -1 | awk '{print $$2}'); \
	if [ -z "$$attempt" ]; then attempt=$$(ls -d $$dir/attempt_* 2>/dev/null | sort -V | tail -1); fi; \
	if [ -z "$$attempt" ]; then echo "No attempt dirs found under $$dir"; exit 1; fi; \
	gen="$$attempt/generated"; \
	total=$$(ls $$gen/*.context.json 2>/dev/null | wc -l | tr -d ' '); \
	done=$$(ls $$gen/*.codex_exit.txt 2>/dev/null | wc -l | tr -d ' '); \
	failed=$$(grep -l "^1$$" $$gen/*.codex_exit.txt 2>/dev/null | wc -l | tr -d ' '); \
	echo "Trial $(TRIAL) — $$(basename $$attempt): $$done/$$total components done, $$failed failures"; \
	if [ -f "$$gen/progress.jsonl" ]; then \
		echo "Recent:"; \
		tail -5 $$gen/progress.jsonl | python3 -c "import sys,json; [print(f\"  [{r['status'].upper()}] {r['component_id']} ({r.get('elapsed_s','?')}s)\" + (f\" t={r['tokens']:,}\" if 'tokens' in r else '')) for r in (json.loads(l) for l in sys.stdin)]"; \
	else \
		echo "Latest:"; ls -t $$gen/*.codex_exit.txt 2>/dev/null | head -5 | while read f; do echo "  exit=$$(cat $$f) $$(basename $$f .codex_exit.txt)"; done; \
	fi; \
	python3 $(CURDIR)/scripts/codex_token_summary.py $$gen 2>/dev/null || true; \
	if [ -f "$$attempt/attempt_report.json" ]; then \
		echo "--- ATTEMPT COMPLETE ---"; \
		python3 -c "import json; r=json.load(open('$$attempt/attempt_report.json')); print(f\"passed={r.get('passed')} rt_cases={len(r.get('runtime_cases',[]))}\")"; \
	fi

verify-blueprint: ## Validate a blueprint bundle (INPUT=examples/.../blueprint)
	$(PYTHON) -m ac14 verify-blueprint "$(INPUT)"

packet-sufficiency: ## Build a persisted structural packet-sufficiency artifact (INPUT=examples/.../blueprint OUTPUT=.ac14_out/packet_sufficiency)
	$(PYTHON) -m ac14 packet-sufficiency "$(INPUT)" --output-dir "$(OUTPUT)"

discover-input: ## Inspect a local input and persist a pre-freeze discovery artifact (INPUT=data.json OUTPUT=.ac14_out/discovery PACKAGES="pandas requests")
	$(PYTHON) -m ac14 discover-input "$(INPUT)" --output-dir "$(OUTPUT)" --project-root "$(CURDIR)" --packages $(PACKAGES) $(foreach artifact,$(RETRIEVAL_ARTIFACTS),--retrieval-artifact "$(artifact)")

prepare-structured-spec: ## Validate a bounded structured spec and persist an artifact (INPUT=spec.yaml OUTPUT=.ac14_out/structured_spec)
	$(PYTHON) -m ac14 prepare-structured-spec "$(INPUT)" --output-dir "$(OUTPUT)"

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

draft-blueprint-plan-from-structured-spec: ## Build an LLM-backed draft blueprint plan from a structured-spec artifact (STRUCTURED_SPEC=.ac14_out/structured_spec/structured_spec_artifact.json OUTPUT=.ac14_out/structured_spec_plan)
	$(PYTHON) -m ac14 draft-blueprint-plan-from-structured-spec "$(STRUCTURED_SPEC)" --output-dir "$(OUTPUT)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

refine-draft-blueprint-plan: ## Refine a blocked draft plan from a freeze decision (PLAN=.ac14_out/draft_plan/draft_blueprint_plan.json INPUT=.ac14_out/freeze_decision/freeze_decision.json OUTPUT=.ac14_out/refined_draft_plan)
	$(PYTHON) -m ac14 refine-draft-blueprint-plan "$(PLAN)" --freeze-decision "$(INPUT)" --output-dir "$(OUTPUT)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

retry-freeze: ## Run refine -> materialize -> refreeze as one explicit retry chain (PLAN=.ac14_out/draft_plan/draft_blueprint_plan.json INPUT=.ac14_out/freeze_decision/freeze_decision.json OUTPUT=.ac14_out/freeze_retry)
	$(PYTHON) -m ac14 retry-freeze "$(PLAN)" --freeze-decision "$(INPUT)" --output-dir "$(OUTPUT)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

materialize-draft-bundle: ## Materialize a six-file draft bundle and readiness report (PLAN=.ac14_out/draft_plan/draft_blueprint_plan.json OUTPUT=.ac14_out/draft_bundle)
	$(PYTHON) -m ac14 materialize-draft-bundle "$(PLAN)" --output-dir "$(OUTPUT)"

decide-freeze: ## Build a freeze decision and promote only when approved (INPUT=bundle_dir OUTPUT=.ac14_out/freeze READINESS=optional_report.json)
	$(PYTHON) -m ac14 decide-freeze "$(INPUT)" --output-dir "$(OUTPUT)" $(if $(READINESS),--readiness-report "$(READINESS)",) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

front-half-acceptance: ## Run realistic-input discovery through freeze decision and review the front half (REALISTIC_INPUT=... OUTPUT=.ac14_out/front_half REQUIREMENTS="..." PACKAGES="pydantic" RETRY_BLOCKED_FREEZE=1)
	$(PYTHON) -m ac14 front-half-acceptance "$(REALISTIC_INPUT)" --output-dir "$(OUTPUT)" --requirements $(REQUIREMENTS) --project-root "$(CURDIR)" --packages $(PACKAGES) $(foreach artifact,$(RETRIEVAL_ARTIFACTS),--retrieval-artifact "$(artifact)") $(if $(filter 1 true yes,$(ALLOW_INSTALL)),--allow-install,) --model "$(MODEL)" --max-budget "$(MAX_BUDGET)" $(if $(filter 1 true yes,$(RETRY_BLOCKED_FREEZE)),--retry-blocked-freeze,) --retry-model "$(RETRY_MODEL)" --retry-max-budget "$(RETRY_MAX_BUDGET)"

structured-spec-front-half-acceptance: ## Run structured-spec draft planning through freeze decision and review the front half (STRUCTURED_SPEC=.ac14_out/structured_spec/structured_spec_artifact.json OUTPUT=.ac14_out/structured_spec_front_half RETRY_BLOCKED_FREEZE=1)
	$(PYTHON) -m ac14 structured-spec-front-half-acceptance "$(STRUCTURED_SPEC)" --output-dir "$(OUTPUT)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)" $(if $(filter 1 true yes,$(RETRY_BLOCKED_FREEZE)),--retry-blocked-freeze,) --retry-model "$(RETRY_MODEL)" --retry-max-budget "$(RETRY_MAX_BUDGET)"

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

front-half-first-smoke-gate: ## Run one bounded front-half-first smoke trial from a structured-spec benchmark bundle (BENCHMARK=benchmarks/resource_scaling_structured_spec OUTPUT=.ac14_out/front_half_first_smoke MAX_ATTEMPTS=3)
	$(PYTHON) -m ac14 front-half-first-smoke-gate "$(BENCHMARK)" --output-dir "$(OUTPUT)" --max-attempts "$(MAX_ATTEMPTS)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

front-half-first-full-trials: ## Run the full front-half-first five-trial gate (BENCHMARK=benchmarks/resource_scaling_structured_spec OUTPUT=.ac14_out/front_half_first_full TRIALS=5 MAX_ATTEMPTS=3)
	$(PYTHON) -m ac14 front-half-first-full-trials "$(BENCHMARK)" --output-dir "$(OUTPUT)" --trials "$(TRIALS)" --max-attempts "$(MAX_ATTEMPTS)" --model "$(MODEL)" --max-budget "$(MAX_BUDGET)"

context-audit: ## Scan codegen context traces for missing/placeholder fields (OUTPUT=.ac14_out/gate_4)
	$(PYTHON) scripts/context_audit.py "$(OUTPUT)"

run-one: ## Run one paired trial and print clean diagnosis (BENCHMARK=back_half_dir OUTPUT=dir TRIAL=1 MODEL=gemini/gemini-2.5-flash-lite)
	$(PYTHON) -m ac14.trial_runner --benchmark "$(BENCHMARK)" --output "$(OUTPUT)" --trial $(or $(TRIAL),1) --model "$(or $(MODEL),$(DEFAULT_MODEL))"

diagnose-attempt: ## Show codegen context + runtime mismatches for one attempt (OUTPUT=.ac14_out/gate_4 TRIAL=N ATTEMPT=M [COMPONENT=name])
	$(PYTHON) scripts/diagnose_attempt.py "$(OUTPUT)" $(TRIAL) $(ATTEMPT) $(if $(COMPONENT),--show-prompt $(COMPONENT),)

TRACE_EVAL_CASE ?= tests/fixtures/cases/ac14_zeta_options/full_pipeline.yaml
TRACE_EVAL_ATTEMPT ?=

trace-eval-check: ## Validate the default trace_eval PipelineCase YAML (TRACE_EVAL_CASE=path)
	$(PYTHON) -m trace_eval.cli check --case "$(TRACE_EVAL_CASE)"

trace-eval: ## Run trace_eval against an AC14 attempt artifact (OUTPUT=.ac14_out/gate TRIAL=N ATTEMPT=M [TRACE_EVAL_CASE=path])
	$(PYTHON) scripts/run_trace_eval.py "$(OUTPUT)" $(TRIAL) $(ATTEMPT) --case "$(TRACE_EVAL_CASE)"

# >>> META-PROCESS WORKTREE TARGETS >>>
WORKTREE_CREATE_SCRIPT := scripts/meta/worktree-coordination/create_worktree.py
WORKTREE_REMOVE_SCRIPT := scripts/meta/worktree-coordination/safe_worktree_remove.py
WORKTREE_CLAIMS_SCRIPT := scripts/meta/worktree-coordination/../check_coordination_claims.py
WORKTREE_SESSION_START_SCRIPT := scripts/meta/worktree-coordination/../session_start.py
WORKTREE_SESSION_HEARTBEAT_SCRIPT := scripts/meta/worktree-coordination/../session_heartbeat.py
WORKTREE_SESSION_STATUS_SCRIPT := scripts/meta/worktree-coordination/../session_status.py
WORKTREE_SESSION_FINISH_SCRIPT := scripts/meta/worktree-coordination/../session_finish.py
WORKTREE_SESSION_CLOSE_SCRIPT := scripts/meta/worktree-coordination/../session_close.py
WORKTREE_DIR ?= $(shell python "$(WORKTREE_CREATE_SCRIPT)" --repo-root . --print-default-worktree-dir)
WORKTREE_START_POINT ?= HEAD
WORKTREE_PROJECT ?= $(notdir $(CURDIR))
WORKTREE_AGENT ?= $(shell if [ -n "$$CODEX_THREAD_ID" ]; then printf codex; elif [ -n "$$CLAUDE_SESSION_ID" ] || [ -n "$$CLAUDE_CODE_SSE_PORT" ]; then printf claude-code; elif [ -n "$$OPENCLAW_SESSION_ID" ] || [ -n "$$OPENCLAW_RUN_ID" ]; then printf openclaw; fi)
SESSION_GOAL ?=
SESSION_PHASE ?=
SESSION_NEXT ?=
SESSION_DEPENDS ?=
SESSION_STOP_CONDITIONS ?=
SESSION_NOTE ?=

.PHONY: worktree worktree-list worktree-remove session-start session-heartbeat session-status session-finish session-close

worktree:  ## Create claimed worktree (BRANCH=name TASK="..." [PLAN=N] [AGENT=name])
ifndef BRANCH
	$(error BRANCH is required. Usage: make worktree BRANCH=plan-42-feature TASK="Describe the task")
endif
ifndef TASK
	$(error TASK is required. Usage: make worktree BRANCH=plan-42-feature TASK="Describe the task")
endif
ifndef SESSION_GOAL
	$(error SESSION_GOAL is required. Name the broader objective, not the local branch)
endif
ifndef SESSION_PHASE
	$(error SESSION_PHASE is required. Describe the current execution phase)
endif
ifndef WORKTREE_AGENT
	$(error Unable to infer agent runtime. Set AGENT via WORKTREE_AGENT=codex|claude-code|openclaw)
endif
	@if [ ! -f "$(WORKTREE_CREATE_SCRIPT)" ]; then \
		echo "Missing worktree coordination module: $(WORKTREE_CREATE_SCRIPT)"; \
		echo "Install or sync the sanctioned worktree-coordination module before using make worktree."; \
		exit 1; \
	fi
	@if [ ! -f "$(WORKTREE_CLAIMS_SCRIPT)" ]; then \
		echo "Missing worktree coordination module: $(WORKTREE_CLAIMS_SCRIPT)"; \
		echo "Install or sync the sanctioned worktree-coordination module before using make worktree."; \
		exit 1; \
	fi
	@if [ ! -f "$(WORKTREE_SESSION_START_SCRIPT)" ]; then \
		echo "Missing session lifecycle module: $(WORKTREE_SESSION_START_SCRIPT)"; \
		echo "Install or sync the sanctioned session lifecycle module before using make worktree."; \
		exit 1; \
	fi
	@python "$(WORKTREE_CLAIMS_SCRIPT)" --claim \
		--agent "$(WORKTREE_AGENT)" \
		--project "$(WORKTREE_PROJECT)" \
		--scope "$(BRANCH)" \
		--intent "$(TASK)" \
		--claim-type program \
		--branch "$(BRANCH)" \
		--worktree-path "$(WORKTREE_DIR)/$(BRANCH)" \
		$(if $(PLAN),--plan "Plan #$(PLAN)",)
	@mkdir -p "$(WORKTREE_DIR)"
	@if ! python "$(WORKTREE_CREATE_SCRIPT)" --repo-root . --path "$(WORKTREE_DIR)/$(BRANCH)" --branch "$(BRANCH)" --start-point "$(WORKTREE_START_POINT)"; then \
		python "$(WORKTREE_CLAIMS_SCRIPT)" --release --agent "$(WORKTREE_AGENT)" --project "$(WORKTREE_PROJECT)" --scope "$(BRANCH)" >/dev/null 2>&1 || true; \
		exit 1; \
	fi
	@if ! python "$(WORKTREE_SESSION_START_SCRIPT)" \
		--agent "$(WORKTREE_AGENT)" \
		--project "$(WORKTREE_PROJECT)" \
		--scope "$(BRANCH)" \
		--intent "$(TASK)" \
		--repo-root "$(CURDIR)" \
		--worktree-path "$(WORKTREE_DIR)/$(BRANCH)" \
		--branch "$(BRANCH)" \
		--broader-goal "$(SESSION_GOAL)" \
		--current-phase "$(SESSION_PHASE)" \
		$(if $(PLAN),--plan "Plan #$(PLAN)",) \
		$(if $(SESSION_NEXT),--next-phase "$(SESSION_NEXT)",) \
		$(if $(SESSION_DEPENDS),--depends-on "$(SESSION_DEPENDS)",) \
		$(if $(SESSION_STOP_CONDITIONS),--stop-condition "$(SESSION_STOP_CONDITIONS)",) \
		$(if $(SESSION_NOTE),--notes "$(SESSION_NOTE)",); then \
		git worktree remove --force "$(WORKTREE_DIR)/$(BRANCH)" >/dev/null 2>&1 || true; \
		git branch -D "$(BRANCH)" >/dev/null 2>&1 || true; \
		python "$(WORKTREE_CLAIMS_SCRIPT)" --release --agent "$(WORKTREE_AGENT)" --project "$(WORKTREE_PROJECT)" --scope "$(BRANCH)" >/dev/null 2>&1 || true; \
		exit 1; \
	fi
	@echo ""
	@echo "Worktree created at $(WORKTREE_DIR)/$(BRANCH)"
	@echo "Claim created for branch $(BRANCH)"
	@echo "Session contract started for $(SESSION_GOAL)"

session-start:  ## Create or refresh the active session contract for BRANCH=name
ifndef BRANCH
	$(error BRANCH is required. Usage: make session-start BRANCH=plan-42-feature TASK="..." SESSION_GOAL="..." SESSION_PHASE="...")
endif
ifndef TASK
	$(error TASK is required. Usage: make session-start BRANCH=plan-42-feature TASK="...")
endif
ifndef SESSION_GOAL
	$(error SESSION_GOAL is required. Name the broader objective, not the local branch)
endif
ifndef SESSION_PHASE
	$(error SESSION_PHASE is required. Describe the current execution phase)
endif
ifndef WORKTREE_AGENT
	$(error Unable to infer agent runtime. Set AGENT via WORKTREE_AGENT=codex|claude-code|openclaw)
endif
	@python "$(WORKTREE_SESSION_START_SCRIPT)" \
		--agent "$(WORKTREE_AGENT)" \
		--project "$(WORKTREE_PROJECT)" \
		--scope "$(BRANCH)" \
		--intent "$(TASK)" \
		--repo-root "$(CURDIR)" \
		--worktree-path "$(WORKTREE_DIR)/$(BRANCH)" \
		--branch "$(BRANCH)" \
		--broader-goal "$(SESSION_GOAL)" \
		--current-phase "$(SESSION_PHASE)" \
		$(if $(PLAN),--plan "Plan #$(PLAN)",) \
		$(if $(SESSION_NEXT),--next-phase "$(SESSION_NEXT)",) \
		$(if $(SESSION_DEPENDS),--depends-on "$(SESSION_DEPENDS)",) \
		$(if $(SESSION_STOP_CONDITIONS),--stop-condition "$(SESSION_STOP_CONDITIONS)",) \
		$(if $(SESSION_NOTE),--notes "$(SESSION_NOTE)",)

session-heartbeat:  ## Refresh heartbeat and optional phase for BRANCH=name
ifndef BRANCH
	$(error BRANCH is required. Usage: make session-heartbeat BRANCH=plan-42-feature)
endif
ifndef WORKTREE_AGENT
	$(error Unable to infer agent runtime. Set AGENT via WORKTREE_AGENT=codex|claude-code|openclaw)
endif
	@python "$(WORKTREE_SESSION_HEARTBEAT_SCRIPT)" \
		--agent "$(WORKTREE_AGENT)" \
		--project "$(WORKTREE_PROJECT)" \
		--scope "$(BRANCH)" \
		--branch "$(BRANCH)" \
		$(if $(SESSION_PHASE),--current-phase "$(SESSION_PHASE)",)

session-status:  ## Show live session summaries for this repo
	@python "$(WORKTREE_SESSION_STATUS_SCRIPT)" --project "$(WORKTREE_PROJECT)"

session-finish:  ## Finish the session for BRANCH=name; blocks if the worktree is dirty
ifndef BRANCH
	$(error BRANCH is required. Usage: make session-finish BRANCH=plan-42-feature)
endif
ifndef WORKTREE_AGENT
	$(error Unable to infer agent runtime. Set AGENT via WORKTREE_AGENT=codex|claude-code|openclaw)
endif
	@python "$(WORKTREE_SESSION_FINISH_SCRIPT)" \
		--agent "$(WORKTREE_AGENT)" \
		--project "$(WORKTREE_PROJECT)" \
		--scope "$(BRANCH)" \
		--worktree-path "$(WORKTREE_DIR)/$(BRANCH)" \
		$(if $(SESSION_NOTE),--note "$(SESSION_NOTE)",)

session-close:  ## Close the claimed lane for BRANCH=name: cleanup worktree + branch + claim together
ifndef BRANCH
	$(error BRANCH is required. Usage: make session-close BRANCH=plan-42-feature)
endif
ifndef WORKTREE_AGENT
	$(error Unable to infer agent runtime. Set AGENT via WORKTREE_AGENT=codex|claude-code|openclaw)
endif
	@python "$(WORKTREE_SESSION_CLOSE_SCRIPT)" \
		--agent "$(WORKTREE_AGENT)" \
		--project "$(WORKTREE_PROJECT)" \
		--scope "$(BRANCH)" \
		--worktree-path "$(WORKTREE_DIR)/$(BRANCH)" \
		--branch "$(BRANCH)" \
		$(if $(SESSION_NOTE),--note "$(SESSION_NOTE)",)

worktree-list:  ## Show claimed worktree coordination status
	@if [ ! -f "$(WORKTREE_CLAIMS_SCRIPT)" ]; then \
		echo "Missing worktree coordination module: $(WORKTREE_CLAIMS_SCRIPT)"; \
		echo "Install or sync the sanctioned worktree-coordination module before using make worktree-list."; \
		exit 1; \
	fi
	@python "$(WORKTREE_CLAIMS_SCRIPT)" --list

worktree-remove:  ## Safely remove worktree for BRANCH=name
ifndef BRANCH
	$(error BRANCH is required. Usage: make worktree-remove BRANCH=plan-42-feature)
endif
	@if [ ! -f "$(WORKTREE_SESSION_CLOSE_SCRIPT)" ]; then \
		echo "Missing session lifecycle module: $(WORKTREE_SESSION_CLOSE_SCRIPT)"; \
		echo "Install or sync the sanctioned session lifecycle module before using make worktree-remove."; \
		exit 1; \
	fi
	@$(MAKE) session-close BRANCH="$(BRANCH)" $(if $(SESSION_NOTE),SESSION_NOTE="$(SESSION_NOTE)",)
# <<< META-PROCESS WORKTREE TARGETS <<<

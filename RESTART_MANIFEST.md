# Restart Manifest: AC14 → AC15

## Previous Version
- Repo: `~/projects/ac14`
- Last active: 2026-04-05 (Plan #175, Theory Forge series closed)
- Lineage doc: `~/projects/project-meta/docs/repo_versioning_notes/AUTOCODER_LINEAGE.md`
- Canonical vision: `~/projects/ac12/docs/AC14_GENERAL_CODING_AGENT_VISION.md`
- Tier model: `~/projects/ac12/CLAUDE.md` (T1–T7 with coupled validator-healer pairs)

## Why Restarting

AC14 implemented the front half of the thesis (blueprint, packets, front-half pipeline) well but never implemented the core robustness mechanism: per-component validation with coupled healing loops (T2/T3/T4). The empirical harness measured system-level pass/fail on single-pass generation, not per-component convergence. Ten benchmarks across three domains produced no `ac14_wins` verdict — but those benchmarks were not testing the actual thesis. They were testing a deliberately incomplete implementation against a baseline that also had an information asymmetry advantage. The accumulated documentation (175+ plans, 27KB CLAUDE.md, stale roadmap, frozen decision docs) obscures the thesis more than it clarifies it. AC15 starts clean with the correct architecture.

## What Worked (carry forward)

- **Blueprint model**: `models.py`, `loader.py`, `validation.py` — B1 structural validation is correct and solid. The six-file bundle schema (schemas, components, architecture, config, deployment) is the right SSOT structure.
- **Packet compiler**: `packets.py`, `packet_sufficiency.py` — correctly compiles blueprint into bounded local packets with informational closure. The concept and implementation are sound.
- **Front-half pipeline**: discovery, dependency planning, blueprint planning, draft authoring, freeze decision, freeze retry — all working. Front-half healing (freeze retry) exists and works. This is real, accumulated work.
- **Structured inputs**: `structured_inputs.py`, `structured_spec.py` — handles json/jsonl/csv/yaml inputs correctly.
- **trace_eval adapter**: `trace_eval_adapter.py` — maps AC attempt artifacts to trace_eval stage_outputs format. Integration groundwork done.
- **Shipped examples**: `examples/` — support_ticket_digest, incident_alert_digest, auth_mix blueprints are real validated artifacts.
- **Benchmarks**: `benchmarks/` — order_exception_resolution, resource_scaling, theory_forge series are real benchmark specifications.
- **Test infrastructure**: most of the 307 tests for blueprint loading, validation, packet compilation, discovery, front-half pipeline are valid and should be carried forward.
- **Codex codegen path**: `codex_codegen.py` — this IS the right design (per-component packet test loop). It's the model for how the LLM path should work.
- **Categorical scoring** for LLM evaluation: pass/partial/fail is correct, not continuous floats.
- **`pyproject.toml` dependencies**: pydantic>=2.0, pyyaml>=6.0, llm_client, open-web-retrieval.

## What Failed (avoid repeating)

- **System-level retry instead of per-component healing**: `empirical_comparison.py` retries all N components when any one fails, injecting failure hints into all component contexts. This is the wrong architecture. The correct model is: each component has its own bounded healing loop (generate → validate → inject test failure → retry), and only failing components are retried. The 39 passing components never get touched again.

- **Missing B3/T2/T3/T4 tier in LLM path**: `llm_codegen.py` is a single-pass LLM call with no coupled validator-healer. The Codex path (`codex_codegen.py`) has the right design — generate, run tests, fix, repeat. The LLM path must have the same structure. Without it, geometric failure accumulation at scale is unavoidable.

- **Measuring the thesis without its robustness mechanism**: All 10 Theory Forge benchmarks measured AC14 without per-component healing and concluded the thesis fails. This is invalid measurement. A thesis that requires per-component convergence cannot be measured with single-pass generation.

- **Benchmark information asymmetry**: The monolithic baseline received `success_criteria` numerical hints in `structured_spec_input.yaml` that AC14's codegen context did not. Every `monolithic_wins` verdict is potentially tainted by this. Fix: strip hints from monolithic input or inject equivalent context into AC14 packets.

- **Documentation accumulation drift**: 175+ numbered plans, 27KB CLAUDE.md, stale ROADMAP, frozen decision docs, duplicate AGENTS.md. The execution contract obscured the thesis. In AC15: one clean CLAUDE.md ≤ 5KB, plans start at #001, no stale status docs.

- **T6 Ship confused with T5 Runtime**: T5 is per-execution validation (schema, no crash). T6 is the meta-level benchmark of the generator itself (does AC15 reliably produce passing code across N fresh runs). These are different levels of abstraction and should not be conflated in the tier ladder.

- **Treating idempotency as a validation criterion**: Many generated systems call LLMs or have probabilistic outputs. Idempotency is wrong as a T5 criterion. T5 should validate: output schema conforms, execution succeeds, no crashes. Not same-value-twice.

- **trace_eval not wired into B4 healing**: The adapter exists but B4 recomposition failures don't drive targeted per-component retry. Without attribution, B4 failures force a full system retry (same problem as B3).

- **Front-half-first empirical as substitute for implementing B3**: The project spent ~60 plans (81–138) on smoke gate variations of front-half-first empirical instead of implementing the missing tier. This was scope drift.

## Domain Model

**Blueprint**: The frozen SSOT. Five YAML files: schemas (type definitions), components (logic contracts, test seeds, policies), architecture (DAG bindings), config (validation budgets, healing config), deployment (operational contracts). Only T1.Healer can write to the blueprint.

**Packet**: Bounded local context compiled from the blueprint for one component. Contains: component contract, direct neighbors, schemas, invariants, scenarios, local tests, write boundaries. The packet is the context boundary for the component coder — the model should not need the whole system to write one correct component.

**Component**: A generated Python module satisfying its packet contract. Ephemeral — regenerated from blueprint each run. Not persisted as SSOT.

**Tier**: A (Validator, Healer, Attempt Policy) triple. Runs in sequence: T1→T2→T3→T4→T5→T6→T7. Each tier must pass before the next begins. Backtracking ladder: T4 fails → back to T2; T2 fails → back to T1; T1 fails → STOP.

**Healing**: Per-component, per-tier. Bounded by attempt budget (T2: 2, T3: 2, T4: 2, T5: 1). Patches are ephemeral — next regeneration starts fresh. Healing proves the system can self-correct, not that the patch is permanent.

**Recomposition**: First-class architectural concern, not just a final integration test. Must explicitly prove: interface compat, schema compat, scenario success, global invariants, fan-in/fan-out correctness.

## Consumer Contracts

No external consumers in `PROJECT_GRAPH.json`. AC15 has no interface obligations to preserve.

## Golden Test Cases

1. **Blueprint loads and validates**: Load `examples/support_ticket_digest/blueprint/` → B1 passes, 4 components, all bindings valid.
2. **Packet compiles with informational closure**: Compile any component's packet → packet contains component contract + neighbor schemas + local fixtures + write boundaries.
3. **Freeze decision produces artifact**: Run freeze decision on a valid draft bundle → explicit binary freeze artifact with pass/fail and rationale.
4. **Component heals from test failure**: Generate a deliberately broken component → run T4 → inject test failure as repair context → retry → component passes T4. (This is the golden test for B3 healing — currently not tested.)
5. **Recomposition catches binding violation**: Introduce a schema mismatch at one binding → B4 catches it and attributes to the correct component.

## Configuration Baseline

```yaml
# Models
blueprint_plan_model: gemini/gemini-2.5-flash-lite       # front-half planning
codegen_model: gemini/gemini-2.5-flash-lite              # component generation
judge_model: gemini/gemini-2.5-flash-lite                # T7 rubric

# Healing budgets (per component per tier)
t2_syntax_budget: 2
t3_semantic_budget: 2
t4_logic_budget: 2
t5_runtime_budget: 1

# Empirical
trials_per_condition: 5
max_workers: 1    # parallel component generation off by default
```

## Architecture Guidance for Next Version

**The thesis in one sentence**: Software generation scales by explicit decomposition into bounded component problems, not by trying to hold the whole system in one model context.

**The critical missing piece**: B3/T2+T3+T4 per-component healing loop in the LLM codegen path. Model this on `codex_codegen.py`, which already has the right structure. The LLM path must: generate → validate (syntax + packet tests + schema) → on failure, extract test output → inject as repair context → retry, bounded by tier budget.

**trace_eval at B4**: Wire trace_eval's cascade attribution into B4 failure handling. When recomposition fails, trace_eval identifies the root-cause component. Retry only that component at B3, not the full system. This makes B4 healing targeted rather than system-level.

**Benchmark design**: Before running any new empirical gate, verify informational parity — monolithic and AC15 should receive equivalent context. Strip `success_criteria` hints from monolithic input or inject equivalent into AC15 packets.

**T6 is not a validation tier on generated code**: T6 is the meta-level benchmark measuring AC15 as a generator (fresh-run pass rate, no healing dependence for headline metrics). It belongs in the empirical harness, not the per-component tier ladder.

**Healing is not the core product**: Decomposition + bounded local generation + validated recomposition is the thesis. Healing is what makes it robust at scale. Don't let the healing loop become the identity of AC15.

**Keep CLAUDE.md under 5KB**: The vision is in `ac12/docs/AC14_GENERAL_CODING_AGENT_VISION.md`. The tier model is in `ac12/CLAUDE.md`. AC15's CLAUDE.md should be an execution contract that references these, not a duplicate of everything.

## Out of Scope for Next Version

- Front-half-first empirical as a standalone gate (subsumed by full tier ladder)
- Semantic comparison as a primary acceptance mechanism (T4 logic + T7 judge cover this)
- Multiple generator kinds in the empirical harness (pick one, prove it, don't split measurement)
- Broader benchmark domains before B3 healing is proven on existing benchmarks

## References

- Thesis: `~/projects/ac12/docs/AC14_GENERAL_CODING_AGENT_VISION.md`
- Tier model: `~/projects/ac12/CLAUDE.md` (T1–T7, healing loops, backtracking ladder)
- Blueprint spec: `~/projects/ac12/docs/AC14_BLUEPRINT_SPEC.md` (B1–B5 simplified model)
- Lineage: `~/projects/project-meta/docs/repo_versioning_notes/AUTOCODER_LINEAGE.md`
- trace_eval: `~/projects/trace_eval/` (stage-level failure attribution, cascade detection)
- Theory Forge results: `~/projects/ac14/docs/theory_forge/series_conclusion.md`
- Benchmark asymmetry finding: `~/projects/ac14/docs/theory_forge/zeta_scale40_verdict.md`

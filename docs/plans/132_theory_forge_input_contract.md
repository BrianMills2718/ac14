# Plan #132: Theory-Forge Input Contract

**Status:** Planned
**Priority:** High
**Type:** design + integration
**Blocked By:** Front-half-first empirical gate (Plans #123/88) — do not implement until smoke_15 resolves and the front-half-first full trial verdict exists
**Consumer:** `theory-forge/docs/plans/08_ac14_codegen_integration.md` (status: Blocked on this work)

---

## Gap

AC14's current front-half pipeline accepts structured data files (JSON records,
CSV rows, YAML event logs) and produces a blueprint whose components model the
processing pipeline for that data. That path is the wrong path for theory-forge.

Theory-forge needs AC14 to accept a **v15 theory schema** — a JSON document
describing algorithms, operations, constructs, and parameters — and produce a
blueprint whose components implement the theory's compute operations. The input
is a specification of what to build, not a corpus of data to process.

Theory-forge Plan #8 (`08_ac14_codegen_integration.md`) is blocked on this
capability existing. It was explicitly ruled out of AC14's current structured
data discovery path because that path does field/type inference on records, not
semantic interpretation of algorithm specs.

This plan defines the design contract that must be settled before implementation
begins. It does not implement the capability; it answers the design questions
that will make implementation straightforward.

---

## What Theory-Forge Provides

| Input | Description |
|-------|-------------|
| `v15_schema` (JSON) | Full v15 theory schema — 11 sections. Contains `algorithms` (math formulas, graph ops), `parameters` (named values with defaults), `constructs` (extraction types), `operations` (ordered compute pipeline), `representation` (graph/table/matrix/vector). This IS the spec of what to compile. |
| `analysis_goal` (str) | Natural-language context: "analyze news articles for framing devices", "compute graph metrics on social network edge lists". Tells AC14 what the generated code will run on. |
| `paper_text` (optional, str) | Raw text of the academic paper. Provides richer semantic context for AC14's front-half drafting. |

## What Theory-Forge Expects Back

AC14 produces a single Python module (`compute.py`) with functions implementing
the theory's compute operations. Specifically:

- Functions implementing each entry in v15 `algorithms` and `computation`-phase `operations`
- Function signatures matching the operation names and `typed_inputs` from the schema
- Code that passes theory-forge's AST structural validator (`validator.py`) and test suite (`test_properties.py`)
- No imports of os/subprocess/eval/exec (theory-forge SafeExecutor allowlist)

Theory-forge **keeps ownership of**:
- `extract.py` (Pydantic extraction model — owned by theory-forge's spec_codegen)
- `orchestrate.yaml` (declarative stage mapping — owned by theory-forge's schema_to_spec)
- `prompts/stage_*.yaml` (qualitative analysis prompts — owned by theory-forge)
- `manifest.yaml` (pipeline manifest — owned by theory-forge)

AC14 does **not** need to understand or generate those files.

---

## The Core Design Question

AC14's front half currently does:

```
structured data file → field/type discovery → draft blueprint → freeze
```

What theory-forge needs:

```
v15 theory schema → algorithm/operation interpretation → draft blueprint → freeze
```

The question is not whether AC14's packet model can represent math formulas or
theory-specific concepts — it can, because the packet is a general bounded-context
document and any description the generator needs is just text in that context.

The real question is whether AC14's discovery/blueprint-planning prompts correctly
interpret a v15 schema — specifically, whether they understand that `operations` +
`algorithms` describe functions to generate, not data fields to model. That is a
prompting and context-delivery question.

### Option A: Context Delivery (Recommended)

Pass the v15 schema + paper text + analysis goal as the input bundle. Include the
v15 meta-schema definition (`meta_schema_v15.json`) as a planning context document
alongside the input — the same way AC14 already accepts local context files (README,
CLAUDE.md, docs) in a directory input bundle (Plans #32–#36).

With that context in the discovery/planning prompt, the LLM knows what each v15
section means and can derive a correct blueprint without any new pipeline code.

**Advantage:** No new pipeline path. Works within the existing directory-bundle
input contract. The v15 meta-schema is the "vocabulary" that makes the prompts
semantically aware.
**Risk:** Prompt quality — the planning prompt needs to correctly separate
"generate these compute functions" from "these extraction types belong to
theory-forge, not AC14." This is testable on one theory before committing.

### Option B: New Theory-Schema Input Type

Treat v15 as a distinct input type with its own discovery path — separate from
structured data file discovery. Branch after input type detection.

**Advantage:** Clean separation.
**Risk:** More code surface. Likely unnecessary if Option A works.

### Recommended Direction

Option A. The v15 meta-schema as a context document is the prompting hook.
Pilot against Information Theory (pure deterministic math, 9 algorithms) — if
AC14's planning prompt correctly maps those 9 algorithms to 9 blueprint components
given the meta-schema context, the integration path is proven and Option B is
unnecessary.

Theory-forge's original Plan #8 framing ("AC14's NL disambiguation loop") was
describing a capability AC14 doesn't need to build specially — it's just good
context delivery to the existing front-half prompts.

---

## Blueprint Component Mapping

For a v15 schema, AC14's blueprint should map as follows:

| v15 Section | Blueprint Concept |
|-------------|------------------|
| `operations` (phase=computation) | One component per operation |
| `algorithms` | Implementation logic in the corresponding component's packet |
| `parameters` | Per-component packet constants / defaults |
| `representation` | Data type flowing between components (port types) |
| `constructs` / `categories` | Input port types (owned by theory-forge extraction) |
| `validation` | Recomposition acceptance criteria |

The `extract.py` / `extract` operation is explicitly **not** a blueprint
component — theory-forge owns that stage. AC14's blueprint should only cover
the compute pipeline.

---

## Open Questions (must be answered before implementation)

1. **How many components per theory?** Information Theory has 9 algorithms. Does
   each become one component, or are they grouped into one `compute` component?
   Grouping is simpler but loses packet isolation. One-per-algorithm is cleaner
   but may produce very thin components.

2. **What does a math algorithm packet look like?** A packet for
   `zero_order_entropy` needs: the formula, typed inputs (frequency list),
   output type (float), parameter defaults (log base). A formula is just text —
   the packet model's natural-language description field is sufficient, and the
   LLM generator will produce correct Python from it. The real question is
   whether AC14's blueprint-planning step correctly extracts that content from
   `algorithms[].formula` + `typed_inputs` rather than treating them as data
   schema fields to model.

3. **Can AC14's discovery prompts distinguish v15 schema sections from data
   schemas?** The discovery prompt currently infers field types from JSON
   records. A v15 schema has `algorithms[].formula` which looks nothing like a
   data field. A prompt rewrite may be needed.

4. **What is the packet → generator path for compute.py?** AC14's existing
   generators (deterministic, LLM) produce code from component specs. For
   theory-forge, the generator needs to produce a Python function that
   implements a math formula. Does the existing LLM generator handle this if
   given the right packet context, or does a theory-specific generator lane
   need to be defined?

5. **Validation surface**: AC14's B1/B2 validation is structural (graph,
   port refs). Theory-forge adds its own AST validator and pytest suite. What
   is the right handoff point — does AC14 run its own validation and then emit
   `compute.py` for theory-forge to validate, or does theory-forge's validator
   become a post-generation acceptance gate within AC14's pipeline?

6. **Input bundling**: Does theory-forge pass the v15 schema as a single JSON
   file, or as a directory bundle (schema + optional paper text + analysis goal)?
   The existing structured-spec input path expects a directory input. Aligning
   on a bundle format now avoids adapter churn later.

---

## Acceptance Criteria (for this plan — design phase only)

- [ ] Open questions 1–6 answered in a written design decision record
- [ ] Option A vs B decision made and justified
- [ ] Blueprint component mapping documented for at least one theory
   (recommend: Information Theory as the pure-math reference case)
- [ ] A named follow-on implementation plan created (Plan #133 or next available)
   with concrete files affected, required tests, and step-by-step phases
- [ ] `theory-forge/docs/plans/08_ac14_codegen_integration.md` updated to
   reflect AC14's chosen design direction and the new implementation plan number

---

## References Reviewed

- `theory-forge/docs/plans/08_ac14_codegen_integration.md` — integration design, blocker diagnosis, why existing structured-data path was ruled out
- `theory-forge/CLAUDE.md` — v15 meta-schema (11 sections), compiled module structure, TheoryCompiler pipeline
- `ac14/docs/plans/83_structured_spec_input_contract.md` — existing structured-spec input path design
- `ac14/docs/plans/84_structured_spec_front_half_acceptance.md` — structured-spec front-half acceptance proof
- `ac14/docs/AC14_ROADMAP.md` — Horizon 2 (Strengthen The Front Half) as the original planned home for this work
- `ac14/KNOWLEDGE.md` lines ~498–529 — theory-forge consumer requirements entry

## Files That Will Be Affected (implementation plan, not this plan)

- `ac14/ac14/discovery.py` — input type detection, v15-aware field interpretation
- `ac14/ac14/blueprint_planning.py` — operation-to-component mapping logic
- `ac14/examples/` — a new `theory_schema_compute/` example bundle
- `ac14/benchmarks/` — possibly a theory-schema benchmark for empirical validation
- `theory-forge/docs/plans/08_ac14_codegen_integration.md` — unblock after implementation

## Required Tests (implementation plan, not this plan)

- Discovery correctly identifies v14 sections (algorithms, operations, parameters)
- Blueprint components map to compute-phase operations, not extraction operations
- Packet for a math algorithm contains formula, typed inputs, output type, defaults
- Generated `compute.py` passes theory-forge's own validator and pytest suite on
  at least one reference theory (Information Theory recommended as first target)

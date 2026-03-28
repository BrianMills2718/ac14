# AC14 Next 24 Hours

Status: Active
Last updated: 2026-03-28

## Purpose

This plan defines the next continuous implementation lane inside `ac14`.

The first honest slice is already in place:

1. six-file blueprint bundle
2. canonical models and loader
3. B1 validation
4. packet compilation and B2 validation
5. manual recomposition proof
6. packet-local test materialization
7. packet-to-codegen-context projection

The previous lane exposed the proof surface as an executable workflow. The
current lane is to add the first true `llm_client`-backed generator that
consumes `CodegenContext` and can be selected through the operator surface.

## Progress Update

Completed:

1. deterministic generated-component flow
2. executable proof surface
3. evidence bundle packaging
4. CLI and Make surfaces for proof execution
5. `llm_client`-backed generator with prompt YAML and structured output
6. live LLM smoke and live CLI generation on the shipped example
7. persisted comparison artifacts across generator modes
8. comparison CLI and Make surfaces

Next:

1. broaden proof coverage beyond the shipped example
2. richer semantic comparison between deterministic, LLM, and reference outputs
3. decide whether to promote the LLM generator from optional to default for any lane

## Execution Rule

Do not stop because of uncertainty that can be documented.

If something is underspecified:

1. record it here
2. choose the smallest thesis-preserving option
3. continue

Only stop if the next step would clearly contradict the frozen AC14 spec.

## Phases

### Phase 1: Generator Comparison Contract

Deliverables:

- comparison artifact schema
- deterministic vs LLM comparison policy
- persisted summary format

Acceptance criteria:

- comparison output is explicit about which generator passed which checks
- artifact is machine-readable and stable

### Phase 2: Comparison Implementation

Deliverables:

- comparison runner across generator modes
- persisted comparison artifact
- fail-loud handling for partially successful runs

Acceptance criteria:

- deterministic and LLM runs can both be summarized in one artifact
- artifact records pass/fail by generator and check type

### Phase 3: Operator Surface Integration

Deliverables:

- CLI support for comparison report generation
- Make support for comparison execution

Acceptance criteria:

- operator can generate a comparison artifact without importing Python modules manually
- deterministic path remains the default stable path

### Phase 4: Verification

Deliverables:

- deterministic unit tests for comparison artifacts
- optional live comparison smoke when available
- clean `pytest`, `mypy`, and `ruff` lanes

Acceptance criteria:

- local verification passes
- uncertainties are documented without blocking progress

## Known Uncertainties

1. generated code is allowed to be proof-slice-specific for the shipped example
2. the first generator does not need LLM integration yet if packet-to-code flow
   is honest and explicit
3. evidence bundle schema may expand once more than one example exists
4. live LLM execution may not be stable enough to be a required default gate
5. full live comparison may be more expensive than the minimal smoke lane

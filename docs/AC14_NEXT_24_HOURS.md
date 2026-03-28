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

The next lane is to close the gap between packet contexts and actual generated
components.

## Progress Update

Completed:

1. Phase 1: Generated Component Emission
2. Phase 2: Generated Packet Test Execution
3. Phase 3: Generated Recomposition Proof
4. Phase 4: Repeated Fresh-Run Evidence

Next:

1. widen evidence packaging beyond the shipped example
2. decide how the first true LLM-backed generator should consume codegen contexts

## Execution Rule

Do not stop because of uncertainty that can be documented.

If something is underspecified:

1. record it here
2. choose the smallest thesis-preserving option
3. continue

Only stop if the next step would clearly contradict the frozen AC14 spec.

## Phases

### Phase 1: Generated Component Emission

Deliverables:

- packet-to-generated-module compiler
- standalone emitted Python modules for the shipped example
- deterministic support for the current proof slice

Acceptance criteria:

- modules are emitted from codegen contexts, not hand-authored files
- emitted code imports cleanly
- generation fails loud for unsupported semantic responsibilities

### Phase 2: Generated Packet Test Execution

Deliverables:

- loader for emitted components
- packet-local test runner against emitted code

Acceptance criteria:

- generated components pass packet-local tests on the shipped example
- failures point back to component id and fixture id

### Phase 3: Generated Recomposition Proof

Deliverables:

- full generated-component recomposition on the shipped example
- comparison against expected digest outputs

Acceptance criteria:

- happy path passes
- missing optional customer context path passes

### Phase 4: Repeated Fresh-Run Evidence

Deliverables:

- repeated fresh generation runs
- summary artifact for pass/fail counts

Acceptance criteria:

- multiple clean runs from scratch pass consistently
- summary artifact is written to disk

## Known Uncertainties

1. generated code is allowed to be proof-slice-specific for the shipped example
2. the first generator does not need LLM integration yet if packet-to-code flow
   is honest and explicit
3. repeated-run evidence can be deterministic in this slice; stochastic
   generation comes later

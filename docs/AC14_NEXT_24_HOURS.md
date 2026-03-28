# AC14 Next 24 Hours

Status: Completed
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

The previous lane closed the gap between packet contexts and actual generated
components. The current lane is to expose that proof surface as an executable,
operator-facing workflow with evidence artifacts.

## Progress Update

Completed:

1. Phase 1: Generated Component Emission
2. Phase 2: Generated Packet Test Execution
3. Phase 3: Generated Recomposition Proof
4. Phase 4: Repeated Fresh-Run Evidence

Next:

1. first LLM-backed generator using the existing codegen contexts
2. broaden proof coverage beyond the shipped example
3. richer evidence comparison between reference and generated implementations

## Execution Rule

Do not stop because of uncertainty that can be documented.

If something is underspecified:

1. record it here
2. choose the smallest thesis-preserving option
3. continue

Only stop if the next step would clearly contradict the frozen AC14 spec.

## Phases

### Phase 1: Evidence Bundle Packaging

Deliverables:

- one bundle writer that packages blueprint path, generated package manifest,
  packet-test report, recomposition result, and fresh-run summary
- persisted artifacts under an output directory

Acceptance criteria:

- bundle contents are sufficient to inspect a proof run without rerunning it
- bundle writing is covered by tests

### Phase 2: CLI Surface

Deliverables:

- `python -m ac14 verify-blueprint`
- `python -m ac14 generate-components`
- `python -m ac14 prove-example`
- `python -m ac14 fresh-runs`

Acceptance criteria:

- commands succeed against the shipped example
- commands write their expected artifacts
- command failures are explicit and actionable

### Phase 3: Make-Driven Proof Lane

Deliverables:

- make targets that wrap the proof commands
- one smoke-tested local workflow for operators

Acceptance criteria:

- `make help` exposes the proof targets
- the shipped example can be proven without importing Python modules manually

### Phase 4: Verification And Evidence

Deliverables:

- clean test, mypy, and ruff lanes
- TODO and plan artifacts updated to reflect actual progress

Acceptance criteria:

- verification passes after the new executable surface is added
- TODO states show which phases are complete

## Known Uncertainties

1. generated code is allowed to be proof-slice-specific for the shipped example
2. the first generator does not need LLM integration yet if packet-to-code flow
   is honest and explicit
3. evidence bundle schema may expand once more than one example exists

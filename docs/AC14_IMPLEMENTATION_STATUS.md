# AC14 Implementation Status

Last updated: 2026-03-31
Status: Canonical implementation-reality document

## Purpose

This document states, bluntly, what AC14 currently implements, what remains
missing, where the main risks are, and what would make this attempt fail.

Use it to keep the implementation aligned with:

1. the long-term vision
2. the frozen proof slice
3. the current code

If this document and the code disagree, the document should be updated or the
code should change. Silent drift is not acceptable.

Related roadmap:

- [AC14_ROADMAP.md](/home/brian/projects/ac14/docs/AC14_ROADMAP.md)

## Thesis Check

AC14 is still aligned with the project thesis.

The current implementation is still centered on:

1. blueprint-driven decomposition
2. bounded local packets
3. explicit recomposition
4. combined programmatic and LLM-backed validation
5. stronger pre-freeze context gathering instead of monolithic context stuffing

AC14 is not yet the full long-term general coding agent, but it is not off in a
different direction.

## What Is Implemented

### Frozen Blueprint Spine

Implemented:

1. six-file blueprint bundle
2. canonical in-memory models
3. blueprint loading
4. structural validation
5. packet compilation
6. recomposition proof surfaces

This is the strongest and most thesis-central part of the repo.

### Code Generation And Proof

Implemented:

1. deterministic generated-component path
2. optional LLM-backed generated-component path
3. packet-local proof
4. recomposition proof
5. fresh-run evidence
6. suite proof and comparison
7. semantic comparison and acceptance surfaces

This means the back half of the proof slice is real, not just planned.

### Pre-Freeze Front Half

Implemented:

1. local input inspection
2. environment and dependency inventory
3. local project-document inventory
4. persisted external documentation and repository retrieval artifacts
5. advisory dependency and library planning
6. dependency-aware draft blueprint planning
7. draft bundle materialization
8. freeze readiness
9. explicit freeze decision and remediation planning

This is no longer just a back-half compiler. AC14 now has meaningful pre-freeze
infrastructure, though it is still early.

## What Is Only Partially Implemented

### Discovery

Discovery exists, but it is still narrow.

It is good at:

1. reading local structured inputs
2. summarizing local docs
3. recording environment state
4. preserving external retrieval context

It is not yet strong at:

1. messy multi-artifact synthesis
2. deeper schema inference from realistic corpora
3. broad source-code understanding outside retrieved snippets

### Semantic Validation

Semantic validation exists, but not yet uniformly at every important gate.

Implemented:

1. semantic comparison artifacts
2. requirements-aware acceptance artifacts
3. optional LLM-backed generation comparison

Still weaker than desired:

1. business-logic review as a first-class artifact everywhere
2. final realistic-input acceptance as the default gate
3. strategy/value review during draft and freeze phases

### Generality

AC14 is broader than one toy slice, but still narrow overall.

Implemented:

1. more than one shipped workflow slice
2. proof breadth as an explicit evaluation concern

Still missing:

1. broad domain diversity
2. strong evidence that the decomposition discipline generalizes beyond current examples

## What Is Not Implemented Yet

1. automatic dependency installation and post-install verification as a normal lane
2. real shared-tool execution inside blueprinted components
3. first-class runtime tool nodes or retrieval nodes in the blueprint model
4. broad automatic NL-to-blueprint derivation from messy real inputs
5. strong notebook-driven execution parity inside the AC14 repo itself until this resynchronization

## Current Risks

### 1. Planning Artifact Drift

This was the biggest real risk as of 2026-03-31.

The original canonical notebook lived in `ac12` and stopped at bootstrap. The
implementation in `ac14` moved much farther. That created a gap between:

1. vision
2. notebook/story artifact
3. actual implementation

This document and the AC14-native notebook exist to close that gap.

### 2. Proof Machinery Outpacing Breadth

AC14 has strong artifact discipline, but still limited breadth.

That means the system may look rigorous while still being overfit to a narrow
set of workflow patterns.

### 3. Front Half Still Weaker Than Back Half

The repo is now much better at discovery and draft preparation than it was at
the start, but recomposition/proof is still stronger than real-world blueprint
derivation from messy inputs.

### 4. Generator Generality

The deterministic lane is still more of a controlled proof mechanism than a
general synthesis engine. That is acceptable for the proof slice, but it is not
the long-term end state.

## Current Percent Complete

These are rough but honest estimates:

1. first proof slice: 80-85%
2. long-term general coding agent vision: 30-35%

The remaining work is not mainly “more code.” It is:

1. keeping the planning artifacts synchronized
2. broadening proof breadth
3. making the front half stronger
4. proving library/tool execution in a reviewable way

## Why This Might Still Become “Attempt 14 Failing”

This attempt still fails if any of the following happen:

1. the notebook/story artifacts fall behind the implementation again
2. the project keeps adding proof machinery without broader evidence
3. decomposition packets still rely on too much hidden context in real use
4. the front half never becomes strong enough to derive good blueprints from realistic inputs
5. the operational overhead ends up larger than the decomposition benefit

## Why This Attempt Is Better Than Prior Restarts

This attempt is materially stronger because:

1. the thesis is explicit
2. the anti-drift hierarchy exists
3. the proof slice is narrower and more honest
4. inter-phase artifacts are persisted instead of implied
5. verification discipline is strong
6. the repo is being kept in clean committed increments

That does not guarantee success. It does mean failure is less likely to come
from vague architecture and more likely to come from real evidence.

## Immediate Recommendation

Before more major implementation lanes:

1. keep the AC14-native notebook current
2. keep this implementation-status document current
3. continue only when the next lane clearly strengthens the decomposition thesis
4. do not let side artifacts become disconnected from freeze, packets, and proof

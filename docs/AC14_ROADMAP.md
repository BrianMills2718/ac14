# AC14 Roadmap

Last updated: 2026-03-31
Status: Active roadmap

## Purpose

This document is the compendious roadmap from AC14's current proof slice to the
long-term general coding-agent vision.

It exists because the project currently has:

1. a clear long-term vision
2. a clear frozen proof contract
3. clear next-24-hours plans

but not yet one compact long-term roadmap connecting those layers.

## Canonical Sources

Interpret AC14 in this order:

1. [AC14_GENERAL_CODING_AGENT_VISION.md](/home/brian/projects/ac12/docs/AC14_GENERAL_CODING_AGENT_VISION.md)
2. [AC14_BLUEPRINT_SPEC.md](/home/brian/projects/ac12/docs/AC14_BLUEPRINT_SPEC.md)
3. [AC14_ANTI_DRIFT_DOCTRINE.md](/home/brian/projects/ac14/docs/AC14_ANTI_DRIFT_DOCTRINE.md)
4. `docs/plans/CLAUDE.md`
5. active numbered plan in `docs/plans/`
6. [UNCERTAINTIES.md](/home/brian/projects/ac14/docs/UNCERTAINTIES.md)
7. [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md)
8. [AC14_NEXT_24_HOURS.md](/home/brian/projects/ac14/docs/AC14_NEXT_24_HOURS.md)
9. [TODO.md](/home/brian/projects/ac14/docs/TODO.md)

The AC12 bootstrap artifacts remain historically important, but AC14-native
control docs plus numbered plans are the active execution surface.

## Current State

AC14 today has:

1. a real frozen blueprint spine
2. packet compilation and recomposition proof
3. deterministic and optional LLM generation lanes
4. pre-freeze discovery, retrieval, dependency planning, draft planning, and freeze decision artifacts
5. an AC14-native notebook and implementation-status document

AC14 does not yet have:

1. broad proof breadth
2. strong messy-input blueprint derivation
3. explicit dependency execution/install verification
4. first-class tool/runtime nodes in the blueprint model
5. a completed long-term front half

## Horizon 1: Finish The Proof Slice

Goal:

Prove that blueprint-driven decomposition is real, not just well-instrumented.

Remaining emphasis:

1. realistic-input full-system acceptance through one honest `llm` slice after closing the `reference` and `deterministic` lanes
2. cleaner packet sufficiency and recomposition evidence
3. slightly broader proof breadth
4. realistic-input final gates that combine programmatic and LLM review

Exit criteria:

1. the frozen blueprint spine is stable
2. dependency and environment assumptions can be checked explicitly
3. realistic-input acceptance exists as persisted artifacts across controlled modes
4. the proof slice is documented with clear pass/fail criteria

Failure signs:

1. artifact machinery keeps growing without stronger evidence
2. packet sufficiency still depends on hidden global context
3. recomposition only works on narrow repeated examples

## Horizon 2: Strengthen The Front Half

Goal:

Make blueprint derivation from realistic inputs materially stronger.

Focus areas:

1. richer multi-artifact discovery
2. schema inference from realistic corpora
3. stronger project/doc/repo/library understanding
4. business-logic and semantic review earlier in the pipeline

Exit criteria:

1. discovery handles more than small structured inputs cleanly
2. draft blueprint quality improves because front-half context is materially better
3. dependency/tool decisions are evidence-backed and testable

Failure signs:

1. front-half artifacts remain shallow while proof machinery keeps deepening
2. draft blueprints still rely heavily on manual cleanup

## Horizon 3: Broaden Generality

Goal:

Show that the decomposition discipline generalizes beyond the current narrow
workflow set.

Focus areas:

1. broader proof breadth across workflow shapes and responsibility sets
2. less responsibility-specific generation logic
3. richer semantic validation and business-logic review
4. more evidence that decomposition beats monolithic context stuffing

Exit criteria:

1. proof breadth is no longer narrow overall
2. claims of generality are evidence-backed rather than aspirational
3. the system still preserves bounded local packet discipline as breadth grows

Failure signs:

1. every new domain requires bespoke one-off machinery
2. the deterministic proof lane does not translate into broader synthesis reliability

## Horizon 4: Shared Tool And Runtime Expansion

Goal:

Extend the blueprint discipline to systems that involve tool usage, library
execution, retrieval, and hybrid nodes.

Focus areas:

1. dependency execution/install verification
2. shared-tool execution surfaces
3. possible future first-class tool/retrieval/runtime node types
4. stronger integration with shared infra such as `llm_client`, `prompt_eval`, and shared tool libraries

Exit criteria:

1. tool/library/runtime execution is explicit and reviewable
2. the blueprint model still stays disciplined rather than turning into vague orchestration prose
3. semantic validation and programmatic validation remain complementary

Failure signs:

1. tool integration bypasses the blueprint and packet model
2. hidden side channels reappear

## Immediate Priorities

In order:

1. keep the notebook/story artifacts synchronized with implementation
2. finish the remaining proof-slice infrastructure, especially one honest realistic-input `llm` final gate
3. strengthen the front half before making stronger generality claims
4. broaden proof breadth before expanding scope claims

## Working Rule

The next implementation lane is valuable only if it strengthens at least one of
these:

1. decomposition fidelity
2. packet sufficiency
3. recomposition confidence
4. pre-freeze context quality
5. breadth of evidence

If a lane strengthens none of those, it is probably side machinery.

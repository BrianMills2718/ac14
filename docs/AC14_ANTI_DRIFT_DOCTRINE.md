# AC14 Anti-Drift Doctrine

Last updated: 2026-03-30
Status: Canonical hierarchy-of-truth document

## Purpose

This document exists to stop local implementation details from being mistaken
for the AC14 vision.

AC14 has already accumulated:

1. a long-term vision
2. a deliberately narrow first proof slice
3. concrete implementation shortcuts and heuristics

Those are not the same thing.

When they are blurred together, drift follows.

## Hierarchy Of Truth

When there is tension between different descriptions of AC14, interpret the
project in this order:

1. long-term vision
2. frozen proof contract
3. current implementation
4. local evaluation heuristics

Lower layers must never silently redefine higher layers.

## Long-Term Vision

The long-term vision is:

AC14 is a general coding agent built around decomposition, bounded local coding
contexts, recomposition, and validation.

The core product idea is:

1. inspect the task and relevant artifacts
2. derive and freeze an explicit blueprint
3. compile bounded local packets
4. generate components from those packets
5. recompose the system
6. validate the system with as many robust programmatic checks and as many
   robust LLM checks as needed

This includes, in the long run:

1. pre-freeze inspection of real input data and source artifacts
2. schema discovery from those artifacts
3. library selection, installation, and usage
4. documentation and repository search
5. LLM semantic review of business logic, strategy, and final outputs
6. realistic end-to-end acceptance checks against requirements

AC14 is not fundamentally:

1. a support-ticket system
2. a deterministic-only compiler
3. a narrow pipeline generator
4. a golden-set-only evaluator

## Frozen First Proof Slice

The current frozen proof slice is intentionally narrower than the long-term
vision.

It is proving:

1. blueprint-driven decomposition
2. typed ports and schemas
3. bounded local packets
4. explicit recomposition
5. evidence-backed validation

It is not yet proving the full long-term front half of the system, including:

1. messy-input discovery
2. automatic schema inference from live artifacts
3. broad tool and library use
4. multi-domain generality
5. rich LLM semantic acceptance as a first-class artifact everywhere

The proof slice is a subset of the vision, not a replacement for it.

## Current Implementation

The current implementation is one working subset of the proof slice.

It currently emphasizes:

1. code-component blueprints
2. local fixtures
3. recomposition scenarios
4. deterministic generation as the control lane
5. optional LLM generation
6. suite proof and semantic comparison

This does not mean those are the full boundaries of AC14.

Current examples, current generator responsibilities, and current CLI surfaces
are implementation artifacts. They are evidence, not the product definition.

## Local Heuristics

Local heuristics are allowed only as temporary evaluation devices.

Examples:

1. current example domains such as support-ticket workflows
2. current terminology such as `semantic_family_count`
3. current exact-match checks where exactness is appropriate
4. current conservative inference of full-recomposition scenarios

These heuristics may be useful, but they are not the vision and they are not
the blueprint model.

If a heuristic starts shaping the product definition, it should either:

1. be promoted explicitly into the blueprint/spec
2. or be renamed/contained as a proof-only device

## Validation Philosophy

AC14 should use both:

1. as many robust programmatic validation techniques as possible
2. as many robust LLM-based validation techniques as necessary

Neither side replaces the other.

Programmatic checks are strongest for:

1. structure
2. schemas
3. bindings
4. invariants
5. fixture coverage
6. exact cases where exactness is appropriate

LLM checks are strongest for:

1. business-logic reasonableness
2. requirements-aware semantic review
3. strategy and product-value review
4. concern detection
5. final acceptance on realistic end-to-end outputs

AC14 should not drift into a deterministic-only understanding of validation.

## Example Selection

Example diversity is a proof-breadth issue, not a product-definition issue.

When choosing examples, the goal is to prevent overclaiming by broadening:

1. component responsibility sets
2. graph shapes
3. schema shapes
4. state/update patterns
5. failure modes

This is why the project may talk about workflow diversity or proof breadth.

Those are evaluation ideas, not core ontology inside the system.

## Drift Tests

A statement about AC14 is probably drifting if it implies any of these:

1. current example domain equals product scope
2. deterministic checks equal the whole validation philosophy
3. current generator heuristics equal the blueprint language
4. current proof slice equals the final system
5. evaluation shorthand equals a core system concept

## Working Rule

When describing or planning AC14:

1. say whether you mean the vision, the proof slice, the implementation, or a
   local heuristic
2. do not let lower layers redefine higher layers
3. prefer the term `proof breadth` over turning evaluation heuristics into
   system ontology

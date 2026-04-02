# AC14 Implementation Status

Last updated: 2026-04-02
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

The main current issue is no longer architectural incoherence. It is the lack
of a completed empirical comparison verdict against a fair monolithic baseline,
plus the need to state clearly that the current gate is a bounded back-half
comparison rather than the full end-to-end thesis test. Plan #49 fixed the
harness-observability gap, Plan #50 landed the latest targeted repair slice,
and the next honest step is now a fresh bounded smoke verdict rather than more
speculative repair work.

## What Is Implemented

### Frozen Blueprint Spine

Implemented:

1. six-file blueprint bundle
2. canonical in-memory models
3. blueprint loading
4. structural validation
5. packet compilation
6. structural packet-sufficiency artifact
7. default deterministic proof/evidence bundle now includes realistic-input final-gate acceptance when a shipped realistic-input artifact exists
8. recomposition proof surfaces

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
8. per-attempt empirical harness artifacts now persist packet and recomposition reports directly
9. packet and recomposition semantic-evaluation prompt paths now normalize datetime-bearing fixture values before templating

This means the back half of the proof slice is real, not just planned.

### Pre-Freeze Front Half

Implemented:

1. local input inspection
2. environment and dependency inventory
3. local project-document inventory
4. persisted external documentation and repository retrieval artifacts
5. advisory dependency and library planning
6. explicit dependency execution probes for dependency-plan recommendations
7. dependency-aware draft blueprint planning with confirmed and blocked probe carry-forward
8. draft bundle materialization with shared `meta-process` dependency-probe policy consumption
9. freeze readiness that now blocks on unresolved dependency probes
10. explicit freeze decision and remediation planning
11. persisted directly attached freeze-semantic review artifacts for draft/freeze quality whenever `decide-freeze` evaluates a draft bundle with readiness evidence
12. persisted realistic-input front-half acceptance from discovery through freeze decision plus structured semantic review
13. one suite-level front-half acceptance artifact across the shipped realistic-input examples, including per-example report paths, directly attached freeze-semantic review paths, and separate review-vs-freeze aggregates
14. one explicit messy-input front-half proof lane on a reviewable CSV asset, proving discovery-through-freeze remains explicit on inputs messier than the clean JSON suite
15. one explicit dependency-remediation lane that reruns previously blocked install probes, persists a remediation delta artifact, and points to a fresh dependency execution artifact for downstream reuse
16. direct draft-planning consumption of dependency-remediation artifacts, with explicit persisted provenance for both the remediation artifact path and the chosen dependency execution artifact path
17. one remediation-driven refined draft-plan artifact that preserves source plan, blocked freeze decision, remediation plan provenance, and refinement round instead of forcing manual bundle edits as the first retry step
18. one explicit retry-chain artifact that runs refine -> materialize -> refreeze and preserves every intermediate path instead of leaving the first retry as manual command orchestration
19. one opt-in retry-aware realistic-input front-half acceptance path that preserves both the initial freeze decision and the retry artifact instead of replacing blocked freeze evidence
20. one opt-in retry-aware front-half suite breadth path that aggregates retry-attempted and retry-approved counts while preserving per-example retry artifact paths
21. one explicit retry-aware messy-input front-half proof on the support-ticket CSV asset, preserving discovery, the initial blocked freeze, the retry-chain artifact, and the final semantic front-half review without inventing a new artifact type
22. persisted realistic-input full-system acceptance in `reference` and `deterministic` modes with actual outputs plus final semantic review
23. one suite-level realistic-input acceptance artifact across shipped examples for supported non-LLM modes
24. one bounded realistic-input full-system acceptance slice in `llm` mode
25. one per-blueprint realistic-input mode-comparison artifact across `reference`, `deterministic`, and `llm`
26. one fixture-backed suite-level realistic-input acceptance artifact in `llm` mode across shipped examples
27. one explicit operator-gated live-readiness artifact for realistic-input `llm` acceptance with `ready`, `blocked`, and `skipped` states
28. suite-level default proof/evidence now carries realistic-input final-gate acceptance explicitly, with `included`, `missing`, and `unsupported` states per example
29. one shared structured-input loading surface between discovery and realistic-input acceptance, so the final gate now supports record-bearing `json`, `jsonl`, `csv`, and `yaml` inputs instead of only top-level JSON lists
30. one explicit messy-input realistic-input final-gate proof on the support-ticket CSV asset in `reference` and `deterministic` modes, plus a matching non-LLM realistic mode-comparison artifact
31. one bounded fixture-backed messy-input realistic-input final-gate proof on the same support-ticket CSV asset in `llm` mode, plus a matching realistic mode-comparison artifact across `reference`, `deterministic`, and `llm`
32. explicit realistic-input manifests plus a shared resolver for shipped examples, so the clean default and alternate profiles are named explicitly instead of relying on hidden file precedence
33. explicit profile-aware suite and operator surfaces for realistic-input acceptance, including persisted `missing_profile` states instead of silent fallback or silent skipping
34. one explicit suite-level `messy` profile proof across `reference`, `deterministic`, and bounded fixture-backed `llm`, while preserving the clean default path and explicit `missing_profile` states
35. one explicit bounded directory-input discovery lane that inventories supported structured candidates plus supporting local context files, chooses one deterministic primary structured candidate, and persists both the chosen primary candidate and the alternatives explicitly
36. one explicit bounded directory-input front-half proof lane, including CLI and Make parity, that preserves the directory input path plus the chosen primary candidate through discovery, draft planning, and freeze review artifacts
37. bounded summaries for alternate structured candidates and supporting local context files during directory discovery, including CLI and Make parity, while preserving one explicit primary structured planning input
38. one explicit bounded front-half propagation proof showing that those new directory summaries survive the discovery-through-freeze chain, including CLI and Make parity
39. explicit bounded schema-divergence concerns between primary and alternate structured candidates during directory discovery, including CLI and Make parity

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

1. explicit front-half proof that the new directory schema-divergence concerns survive discovery-through-freeze
2. deeper schema inference from realistic corpora
3. broad source-code understanding outside retrieved snippets
4. completing the current back-half empirical gate cleanly
5. proving that the full end-to-end decomposition approach materially beats
   monolithic generation on a system complex enough for the thesis to matter
6. closing the remaining Plan #50 blocker set: generator-contract stability plus benchmark-local fidelity

### Semantic Validation

Semantic validation exists, but not yet uniformly at every important gate.

Implemented:

1. semantic comparison artifacts
2. requirements-aware acceptance artifacts
3. optional LLM-backed generation comparison
4. realistic-input front-half acceptance artifacts that judge discovery through freeze against explicit requirements
5. realistic-input full-system acceptance artifacts that review actual outputs from realistic inputs in `reference` and `deterministic` modes
6. one suite-level realistic-input acceptance artifact across shipped examples for supported non-LLM modes
7. one bounded realistic-input `llm` acceptance slice plus a per-blueprint realistic-input mode-comparison artifact
8. one fixture-backed suite-level realistic-input acceptance artifact in `llm` mode
9. one explicit operator-gated live-readiness artifact that keeps fixture-backed breadth distinct from actual live-readiness evidence
10. suite-level default proof/evidence now carries realistic-input final-gate acceptance explicitly, with aggregate included/missing/unsupported counts
11. default-generator recommendation now consumes suite-level realistic-input default-gate evidence instead of reasoning only from structural suite comparison and semantic comparison
12. suite-level live-readiness artifact now persists per-example and aggregate `ready` / `blocked` / `skipped` results for realistic-input `llm` acceptance while remaining operator-gated
13. default-generator recommendation now consumes both the bounded one-example live-readiness artifact and the broader suite-level live-readiness artifact
14. draft/freeze quality now carries a directly attached semantic review artifact instead of leaving front-half business-logic review only to later acceptance surfaces

Still weaker than desired:

1. business-logic review as a first-class artifact everywhere
2. strategy/value review during draft and freeze phases beyond the current artifact set
3. directory-input front-half proof beyond raw discovery
4. broader automatic dependency execution/install remediation beyond the current narrow rerun artifact, first draft-planning hand-off, refined-plan retry step, explicit retry-chain wrapper, one bounded front-half retry integration, one bounded front-half retry breadth lane, one bounded messy-input retry proof, one bounded messy-input non-LLM final-gate proof, one bounded messy-input `llm` final-gate proof, one explicit realistic-input manifest layer, one explicit profile-aware suite/operator layer, and one explicit messy-profile suite proof

### Generality

AC14 is broader than one toy slice, but still narrow overall.

Implemented:

1. more than one shipped workflow slice
2. proof breadth as an explicit evaluation concern

Still missing:

1. broad domain diversity
2. strong evidence that the decomposition discipline generalizes beyond current examples
3. one empirical baseline comparison against a fair monolithic condition

## What Is Not Implemented Yet

1. directory schema-divergence propagation through the front-half chain
2. a completed monolithic-versus-decomposition comparison verdict
3. broad automatic dependency installation and post-install verification as a normal lane
4. real shared-tool execution inside blueprinted components
5. first-class runtime tool nodes or retrieval nodes in the blueprint model
6. broad automatic NL-to-blueprint derivation from messy real inputs
7. strong notebook-driven execution parity inside the AC14 repo itself until this resynchronization

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

### 3. No Empirical Baseline Gate Yet

AC14 still does not have one explicit comparison artifact showing whether the
decomposition approach beats a fair monolithic baseline on a system where
context collapse should matter.

Without that gate, it is too easy to mistake internal proof-hygiene progress
for project-level thesis validation.

### 3a. The current empirical gate is only a first back-half gate

The current benchmark and runner compare packetized local generation against
whole-package generation over a fixed decomposition. That is useful and worth
finishing, but it is narrower than the strongest version of the full thesis.

### 4. Front Half Still Weaker Than Back Half

The repo is now much better at discovery and draft preparation than it was at
the start, but recomposition/proof is still stronger than real-world blueprint
derivation from messy inputs.

### 5. Generator Generality

The deterministic lane is still more of a controlled proof mechanism than a
general synthesis engine. That is acceptable for the proof slice, but it is not
the long-term end state.

## Current Percent Complete

These are rough but honest estimates:

1. proof-slice infrastructure: 99%
2. proof-slice thesis validation: 70-75%
3. long-term general coding agent vision: 55-60%

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
6. the project never runs a fair monolithic-versus-decomposition comparison

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
3. run the empirical comparison gate before defaulting to more propagation-proof micro-lanes
4. continue only when the next lane clearly strengthens the decomposition thesis
5. do not let side artifacts become disconnected from freeze, packets, and proof

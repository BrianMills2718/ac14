# AC14 Roadmap

Last updated: 2026-04-02
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
3. empirical evidence that favors AC14 over a fair monolithic baseline
4. first-class tool/runtime nodes in the blueprint model
5. a completed long-term front half

## Horizon 1: Finish The Proof Slice

Goal:

Prove that blueprint-driven decomposition is real, not just well-instrumented.

Remaining emphasis:

1. realistic-input final gates that carry into suite-level proof/evidence by default
2. slightly broader proof breadth
3. operator-reviewed live/default readiness evidence beyond the new explicit boundary artifact
4. stronger recomposition evidence as breadth grows

Exit criteria:

1. the frozen blueprint spine is stable
2. dependency and environment assumptions can be checked explicitly
3. realistic-input acceptance exists as persisted artifacts across controlled modes, including bounded and fixture-backed `llm` breadth
4. the proof slice is documented with clear pass/fail criteria

Failure signs:

1. artifact machinery keeps growing without stronger evidence
2. packet sufficiency still depends on hidden global context
3. recomposition only works on narrow repeated examples

## Horizon 1 Gate: Empirical Comparison

Goal:

Answer the main thesis question before more propagation-proof micro-lanes
accumulate:

Does AC14's decomposition discipline materially beat a fair monolithic baseline
on a system complex enough for context management to matter?

Current results:

The first two benchmark gates are now complete.

Gate 1: `.ac14_out/full_trials_gate_1/experiment_decision.json` -> `inconclusive`

- AC14: `2/5` successful trials
- monolithic: `2/5` successful trials
- secondary metrics did not separate them cleanly
- monolithic was faster and cheaper on this benchmark

Gate 2: `.ac14_out/full_trials_gate_2/experiment_decision.json` -> `monolithic_wins`

- AC14: `0/5` successful trials
- monolithic: `5/5` successful trials
- average semantic score tied
- monolithic used fewer repair loops, less time, and less cost

That means the project now has real baseline artifacts, and the current
harder benchmark evidence does not support the stronger thesis claim. Plan #62
was still the right move, but the second gate now says the current back-half
decomposition slice loses on the harder benchmark.

Focus areas:

1. interpret the second-gate loss honestly
2. diagnose whether the dominant misses are benchmark-local, packet-context, or generation-stability failures
3. decide whether the next move is a reusable repair lane, a broader strategic pivot, or a stronger end-to-end front-half test
4. keep any next empirical response explicit and falsifiable

Important scope note:

The current first empirical gate is a bounded back-half comparison over a fixed
decomposition. It is the right next gate, but it is not yet the full
front-half-plus-back-half end-to-end thesis test.

Exit criteria:

1. the target systems and baseline protocol are explicit
2. the scoring rubric and decision rule are explicit
3. the current evidence is interpreted honestly
4. the project does not reopen benchmark-local tuning after a decisive loss unless a boundary decision says so
5. the next empirical direction is explicit rather than implied

Failure signs:

1. AC14 continues to count proof-hygiene progress as thesis validation after a hard empirical loss
2. the project explains away the second-gate loss without diagnosis
3. the next empirical direction becomes another unbounded micro-repair chain
4. the project keeps tuning one benchmark locally without first extracting a reusable failure taxonomy or claim-boundary adjustment

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

1. (done — Plan #62) diagnose why the first benchmark ended `inconclusive`:
   packet-test LLM eval noise dominated the signal; runtime outputs passed in
   virtually all attempts for both conditions; next gate needs both a harder
   benchmark and a runtime-primary success criterion
2. (done — Plan #61) remediate the notebook surface so the empirical-comparison
   notebook is a real artifact-backed journey notebook
3. (done — Plan #63) freeze the runtime-first second-gate contract and split
   the next chain explicitly into benchmark, smoke, and full-gate/blocker
   branches
4. (done — Plan #64) land the harder second benchmark bundle
5. (done — Plan #65) run the bounded smoke gate on that bundle
6. (done — Plans #66-#71) complete the five-trial gate, repair interrupted-run integrity, and lock the second verdict
7. (done — Plan #72) lock the second-gate verdict honestly across the active docs
8. (done — Plans #73-#76) diagnose the second-gate loss, test one bounded post-loss grounding repair, and freeze a repair boundary instead of continuing local tuning by habit
9. (done — Plan #77) classify which empirical failures are reusable AC14 weaknesses and freeze the next lane from that taxonomy
10. (done — Plan #78) implement one reusable packet-rule-grounding repair
11. (done — Plan #79) rerun the bounded smoke gate and confirm the harder second gate still does not reopen
12. (done — Plans #81-#82) freeze the strategic pivot and front-half-first empirical contract
13. (done — Plan #83) implement the minimal structured-spec input contract for front-half drafting
14. (done — Plan #84) prove one full structured-spec front-half lane through freeze and semantic review
15. (done — Plan #85) freeze one benchmark-ready structured-spec bundle anchored to the existing `resource_scaling` runtime evaluation assets
16. (now — Plan #86) implement the front-half-first smoke contract and runner
17. (next — Plan #87) spend one bounded front-half-first smoke trial
18. (then — Plan #88 or #89) either run the full front-half-first gate or diagnose the blocker directly from the smoke verdict

## Current empirical branch rule

The harder back-half gate remains closed.

- gate 1: `inconclusive`
- gate 2: `monolithic_wins`
- reusable packet-rule-grounding smoke rerun: still `0/3` AC14 successes

That means the next honest horizon is front-half-first, not more local tuning
of `resource_scaling_v1`.

## Working Rule

The next implementation lane is valuable only if it strengthens at least one of
these:

1. decomposition fidelity
2. packet sufficiency
3. recomposition confidence
4. pre-freeze context quality
5. breadth of evidence

If a lane strengthens none of those, it is probably side machinery.

If a lane only propagates a newly added artifact field but does not materially
improve the empirical gate, it is probably lower priority than the comparison
plan.

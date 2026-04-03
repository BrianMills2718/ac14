# AC14 Uncertainties

Status: Canonical uncertainty tracker
Last updated: 2026-04-02

Use this file to track open, investigating, resolved, deferred, and blocked
uncertainties that matter to AC14's architecture, proof slice, or active
implementation lane.

This file is not the active checklist. That remains in [TODO.md](/home/brian/projects/ac14/docs/TODO.md).

## Status Key

| Status | Meaning |
|--------|---------|
| Open | Important uncertainty not yet investigated enough |
| Investigating | Actively being resolved in the current lane |
| Resolved | Decision made and grounded in code, docs, or evidence |
| Deferred | Known uncertainty accepted for a later phase |
| Blocked | Needs outside input or a prerequisite event |

## Active Lane Uncertainties

### U-001: What should the dependency execution-probe result model be?
**Status:** Resolved
**Context:** The active lane needs explicit result states such as `confirmed`,
`blocked`, and `skipped` instead of implicit shell success or failure.
**Why it matters:** The probe artifact must be reviewable and composable with
later planning and freeze surfaces.
**Resolution:** AC14 now persists explicit `confirmed`, `blocked`, and
`skipped` probe states in the dependency execution artifact.
**Date resolved:** 2026-03-31

### U-002: How much environment mutation is acceptable in the first probe lane?
**Status:** Resolved
**Context:** AC14 should test approved dependency recommendations without
quietly becoming a broad automatic installer.
**Why it matters:** The first bridge must stay thesis-preserving and reviewable.
**Resolution:** The first probe lane defaults to `check_only` and only attempts
install commands when the operator explicitly enables `--allow-install`.
**Date resolved:** 2026-03-31

### U-003: What post-probe environment observations should be persisted?
**Status:** Resolved
**Context:** Command output alone is not enough for follow-on planning.
**Why it matters:** Later phases need explicit environment deltas and blocking
signals.
**Resolution:** AC14 now persists compact before/after snapshots, command exit
codes, per-probe observations, and cross-cutting environment observations.
**Date resolved:** 2026-03-31

### U-012: How should blocked dependency probes affect freeze?
**Status:** Resolved
**Context:** Probe artifacts only matter if blocked results can stop the front
half from freezing a plan that depends on unavailable libraries.
**Why it matters:** Otherwise dependency execution remains a disconnected side
artifact.
**Resolution:** Blocked dependency probes now become explicit freeze-readiness
blockers and grouped freeze-remediation tasks.
**Date resolved:** 2026-03-31

### U-013: Where should dependency-probe policy live?
**Status:** Resolved
**Context:** Multiple projects will need the same project-process decision about
whether blocked dependency probes should block, warn, or be ignored.
**Why it matters:** If the policy vocabulary lives only in AC14, other projects
do not get the configuration model for free.
**Resolution:** The shared vocabulary now lives in `meta-process.yaml` under
`planning.dependency_probe_policy`, and AC14 consumes it with `strict` default
behavior.
**Date resolved:** 2026-03-31

### U-014: Should AC14 persist one realistic-input front-half acceptance artifact?
**Status:** Resolved
**Context:** Discovery, dependency planning, probing, draft planning, draft
authoring, and freeze decisions already existed, but the front half still
lacked one artifact that judged the whole chain against explicit requirements.
**Why it matters:** Without one persisted front-half verdict, AC14 remained
stronger on frozen-blueprint proof than on realistic-input pre-freeze work.
**Resolution:** AC14 now persists `front_half_acceptance_report.json`, which
runs discovery through freeze decision on a realistic input file and adds a
structured semantic review that can still say `promising_but_blocked` when
freeze is not yet approved.
**Date resolved:** 2026-03-31

### U-015: Should AC14 persist one realistic-input full-system acceptance artifact?
**Status:** Resolved
**Context:** The front-half lane existed, but the final gate still lacked one
artifact that judged actual system outputs from realistic input data.
**Why it matters:** Without this, AC14 would remain much stronger at planning
and proof setup than at final realistic-input acceptance.
**Resolution:** AC14 now persists a realistic-input full-system acceptance
artifact in `reference` mode, including the realistic input record, actual
outputs, and a structured semantic review.
**Date resolved:** 2026-03-31

## Deferred Project Uncertainties

### U-049: AC14 still lacks an empirical baseline comparison against monolithic generation.
**Status:** Resolved
**Context:** The repo had strong proof machinery and narrow example breadth, but
no persisted experiment comparing AC14 decomposition against a fair monolithic
generation condition on a system complex enough for the thesis to matter.
**Why it matters:** Without this gate, the project could keep validating internal
machinery while the top-level thesis remained unmeasured.
**Resolution:** `.ac14_out/full_trials_gate_1/experiment_decision.json` now exists and records the first five-trial comparison against a fair monolithic baseline. The verdict is `inconclusive`, but the baseline artifact is real.
**Date resolved:** 2026-04-02

### U-050: The plan sequence can continue generating propagation-proof micro-lanes without a thesis gate.
**Status:** Resolved
**Context:** Plans #32-#37 formed a coherent pattern of discovery feature ->
front-half propagation proof. That pattern was locally reasonable but could outrun
the main empirical question if not interrupted deliberately.
**Why it matters:** The active planning surface should force the next gate to be
thesis-relevant rather than merely the next clean propagation story.
**Resolution:** Plan #38 inserted an explicit empirical gate, Plans #39 and #43 executed it, and Plan #44 locked the first verdict before resuming adjacent lanes.
**Date resolved:** 2026-04-02

### U-051: The empirical comparison runner exists, but bounded smoke trials still have zero hard-harness successes.
**Status:** Resolved
**Context:** The benchmark bundle, paired-trial runner, and decision artifact
existed, but earlier smoke baselines still had zero hard-harness successes.
**Why it matters:** A five-trial gate is not worth running yet if one smoke
trial cannot produce a single hard-harness success in either condition.
**Resolution:** Plan #60 produced `.ac14_out/empirical_smoke_gate_repair11/`
with `hard_harness_success = true`, `verdict = ready_for_full_trials`, and no
infrastructure-only contamination.
**Date resolved:** 2026-04-02

### U-052: Provider instability is currently mixed into the empirical gate.
**Status:** Investigating
**Context:** Earlier live smoke trials observed repeated Gemini disconnects,
DNS/API connection failures, and `503` demand errors while the empirical
comparison was running. The full five-trial gate did complete, but it still saw
provider `503` demand spikes during live execution.
**Why it matters:** The primary success outcome is now real, but provider noise
may still contaminate time/cost interpretation and some attempt-level failure
paths.

### U-053: The current empirical gate is narrower than the full AC14 thesis.
**Status:** Open
**Context:** The current benchmark declares
`comparison_scope: decomposition_vs_monolithic_back_half`, and the monolithic
condition receives the frozen blueprint plus benchmark-local test context.
**Why it matters:** A successful Plan #39 result would be meaningful, but it
would still validate a bounded back-half claim rather than the strongest
end-to-end front-half-plus-back-half version of the thesis.

### U-054: The next blocker is benchmark-fidelity exactness, not infrastructure.
**Status:** Resolved
**Context:** The late smoke lane stayed `blocked_on_harness` without provider
contamination. Plan #49 fixed the harness-observability gap, so the remaining
mismatches were benchmark-local rather than provider-local.
**Why it matters:** The next repair lane needed to stay benchmark-local and avoid
turning one empirical benchmark's needs into broad AC14 runtime policy by
accident.
**Resolution:** The benchmark-local repair chain completed, repair11 cleared the smoke gate, and the full five-trial gate ran to completion.
**Date resolved:** 2026-04-02

### U-055: AC14 still loses bounded smoke attempts to syntax-invalid generated modules.
**Status:** Resolved
**Context:** In `.ac14_out/empirical_smoke_gate_repair7/`, the old classifier
syntax blocker moved, but the AC14 lane still lost attempts to other
contract-level generation failures such as multiline boolean conditions without
parentheses and pre-class `GeneratedComponent` return annotations.
**Why it matters:** The empirical gate cannot measure benchmark logic honestly
if one condition burns bounded repair budget on recurring codegen-contract
mistakes.
**Resolution:** The later repair chain hardened prompt and validator surfaces enough that the five-trial gate no longer failed on this syntax class. AC14's decisive failures in the completed comparison were packet/recomposition semantics, not syntax-invalid modules.
**Date resolved:** 2026-04-02

### U-056: The remaining benchmark-local fidelity misses are still narrow and unresolved.
**Status:** Resolved
**Context:** In `.ac14_out/empirical_smoke_gate_repair8/`, the AC14 lane moved
past the old broad packet/recomposition opacity and showed a narrower blocker
set: `case_parser.normalized_notes` exactness plus benchmark-local rationale and
priority-branch fidelity.
**Why it matters:** The repair lane needed to tighten those explicit
benchmark-local rules before spending the five-trial budget.
**Resolution:** The benchmark-local repair chain culminated in repair11, which cleared the smoke gate, and then the full five-trial comparison completed. The first benchmark result is now `inconclusive`, so the open question is no longer whether the narrow repair chain exists but what the benchmark result means.
**Date resolved:** 2026-04-02

### U-057: Empirical attempt artifacts were too lossy to diagnose harness failures directly.
**Status:** Resolved
**Context:** Repair7 required a manual rerun of packet and recomposition checks
against a saved attempt package because the attempt artifact only carried a
coarse failure summary.
**Why it matters:** The next repair lane should be driven by first-class
attempt artifacts, not by ad hoc reproduction.
**Resolution:** Empirical attempts now always persist `packet_test_report.json`
and `recomposition_report.json`, and the attempt report points directly to both
paths.
**Date resolved:** 2026-04-02

### U-058: Semantic-evaluation prompt templating failed on datetime-bearing fixture data.
**Status:** Resolved
**Context:** Benchmark fixtures parse ISO timestamps into Python `datetime`
objects, but packet and recomposition semantic-evaluation prompts rendered
those values through Jinja `tojson` without normalization.
**Why it matters:** The empirical harness cannot tell the truth about semantic
mismatches if the prompt-building path crashes before the LLM judge sees the
case.
**Resolution:** Packet and recomposition semantic-evaluation helpers now
normalize prompt inputs into JSON-safe values before templating.
**Date resolved:** 2026-04-02

### U-059: Packet and recomposition failures were still too lossy for retry guidance.
**Status:** Resolved
**Context:** Repair8 still required reading packet and recomposition artifacts by
hand because empirical failure summaries compressed benchmark-local mismatches
into generic labels such as `packet-local tests failed`.
**Why it matters:** The retry loop cannot spend its bounded attempts well if the
repair guidance discards field-level mismatch evidence the harness already has.
**Resolution:** AC14 now persists bounded mismatch details in packet and
recomposition results, threads those details into empirical failure summaries,
and uses the same bounded diff helper across those surfaces.
**Date resolved:** 2026-04-02

### U-060: Empirical comparison calls were missing explicit experiment context.
**Status:** Resolved
**Context:** The empirical lane emitted `llm_client` warnings that evaluation
and benchmark calls lacked experiment context and feature-profile activation.
**Why it matters:** Without real experiment context, the observability story for
the thesis gate is weaker and harder to analyze honestly.
**Resolution:** Empirical attempts now execute inside a real
`llm_client.io_log.experiment_run(...)` plus `activate_feature_profile(...)`
context using benchmark/trial/attempt provenance.
**Date resolved:** 2026-04-02

### U-061: Repair10 still loses bounded attempts to one shared shipping-only semantic mismatch.
**Status:** Resolved
**Context:** The repair10 smoke artifact remained `blocked_on_harness` without an
infrastructure-only explanation. The compound inventory and broad shipping-risk
ambiguities narrowed further, but both conditions still disagreed on the same
shipping-only standard-customer case: `factor_correlator` kept forcing
`escalation_required=true`, while the monolithic `priority_scorer` still tied
shipping-only `high` priority to escalation.
**Why it matters:** Plan #60 should only unblock full trials if the next smoke
artifact proves that shipping-only rule no longer dominates the bounded attempts.
**Resolution:** Plans #58 and #59 tightened that rule and the repair11 smoke
artifact cleared the gate. AC14 passed on attempt 1, so the old shared
shipping-only mismatch no longer dominates the smoke lane.
**Date resolved:** 2026-04-02

### U-062: Monolithic invalid-Python failures still lose observability.
**Status:** Resolved
**Context:** Plan #56 fixed the main failed-source persistence path, but repair10
showed one remaining pre-emit validation path in `agenerate_monolithic_system_with_llm(...)`
that could still fail before the full failed-source artifact was written.
**Why it matters:** The empirical gate cannot be debugged honestly if one
condition burns attempts on invalid code that the artifact chain does not
preserve for direct review.
**Resolution:** Plan #59 moved module-contract validation fully into
`emit_monolithic_package_with_llm(...)`, so invalid monolithic module source is
now preserved before the attempt fails.
**Date resolved:** 2026-04-02

### U-063: AC14 still loses bounded attempts to `resolution_assembler` generation instability.
**Status:** Resolved
**Context:** In repair10 the AC14 lane still lost bounded attempts to
`resolution_assembler` failures such as missing `build_component()` and non-ASCII
corruption. Plan #59 hardened both prompt and validator surfaces around those
exact failures.
**Why it matters:** The empirical gate cannot measure benchmark logic honestly
if one condition continues to waste attempts on known codegen-contract failures.
**Resolution:** The completed five-trial gate no longer showed `resolution_assembler` contract instability as a dominant failure mode. AC14's remaining failures were benchmark-semantic packet and recomposition mismatches.
**Date resolved:** 2026-04-02

### U-064: The first empirical benchmark did not separate the conditions clearly enough.
**Status:** Open
**Context:** `.ac14_out/full_trials_gate_1/experiment_decision.json` returned `inconclusive`. Both conditions succeeded on `2/5` trials, both averaged `1.6` repair loops and semantic score `2.0`, and monolithic was faster and cheaper.
**Why it matters:** The project now has a real baseline artifact, but not yet a decisive empirical answer about whether decomposition helps on a system where context pressure should matter. The next lane must decide whether the current benchmark is too benchmark-local, too back-half-only, or simply not differentiating enough.

### U-065: Deterministic exact-match benchmarks can still fail on under-grounded LLM semantic review.
**Status:** Resolved
**Context:** In `.ac14_out/full_trials_gate_2_smoke/trial_1/monolithic/attempt_1/attempt_report.json`, all four runtime cases matched expected outputs exactly, but semantic review still returned `concern` and claimed `RSC-103 request_rate_rps = 60` was `< 20`.
**Why it matters:** A deterministic categorical benchmark should not remain smoke-blocked because an advisory LLM review contradicts exact outputs.
**Resolution:** `BenchmarkConfig` now exposes `semantic_review_policy`, and `resource_scaling_v1` uses `advisory_on_exact_match` so exact runtime-output matches remain the primary gate while the review artifact is still persisted.
**Date resolved:** 2026-04-02

### U-066: Monolithic module validation still misses unknown literal input-port names.
**Status:** Resolved
**Context:** In `.ac14_out/full_trials_gate_2_smoke/trial_1/monolithic/attempt_3/generated/`, several modules reference `inputs['on_compliance']` even though that input port is not declared by the affected components. The current validator catches syntax/import failures but not this contract class.
**Why it matters:** Invalid port references should become precise pre-emit validation failures, not noisy runtime surprises.
**Resolution:** Monolithic emit now threads the allowed input-port set into module validation and fails loud on literal undeclared `inputs[...]` and `inputs.get(...)` references before runtime, while still persisting failed source and validation metadata.
**Date resolved:** 2026-04-02

### U-004: The generated component logic is still semantic-responsibility-specific.
**Status:** Deferred
**Context:** The current generator remains more of a controlled proof mechanism
than a general synthesis engine.
**Why it matters:** This constrains generality claims.

### U-005: Realistic-input acceptance is still synthetic-but-plausible.
**Status:** Deferred
**Context:** AC14 now has a persisted front-half realistic-input acceptance
lane, but the shipped input is still a plausible structured batch rather than a
broader messy-corpus proof.
**Why it matters:** The front half is still weaker than the back half.

### U-016: Should realistic-input full-system acceptance broaden beyond the manual reference lane?
**Status:** Resolved
**Context:** The final realistic-input gate initially existed only in
`reference` mode, which made the broader mode story too weak.
**Why it matters:** The proof slice needed at least one non-reference lane and
one explicit breadth artifact before moving to `llm`.
**Resolution:** AC14 now supports realistic-input full-system acceptance in
`reference` and `deterministic` modes, plus one suite-level realistic-input
acceptance artifact across shipped examples for those supported modes.
**Date resolved:** 2026-03-31

### U-017: Should realistic-input full-system acceptance include one honest `llm` lane?
**Status:** Resolved
**Context:** After the controlled `reference` and `deterministic` lanes,
realistic-input `llm` coverage was the next meaningful gap.
**Why it matters:** The project vision is not deterministic-only, so the final
gate needed one bounded `llm` slice before broader breadth claims.
**Resolution:** AC14 now supports one realistic-input `llm` acceptance slice on
the support-ticket blueprint, plus one per-blueprint realistic-input
comparison artifact across `reference`, `deterministic`, and `llm`.
**Date resolved:** 2026-03-31

### U-018: Can fixture-backed `llm` breadth extend honestly across multiple blueprints?
**Status:** Resolved
**Context:** The initial fixture-backed LLM codegen path keyed responses by
component ID only, which was too weak for multi-blueprint breadth.
**Why it matters:** Suite-level `llm` breadth would have been misleading until
the fixture path became blueprint-aware and failed loud on ambiguity.
**Resolution:** AC14 now carries `blueprint_id` through packets and codegen
contexts, fixture-backed LLM codegen can disambiguate by `blueprint_id` plus
`component_id`, and one fixture-backed suite-level realistic-input `llm`
acceptance artifact now exists across shipped examples.
**Date resolved:** 2026-03-31

### U-019: Fixture-backed `llm` breadth is still not the same as live readiness.
**Status:** Resolved
**Context:** AC14 now has suite-level fixture-backed `llm` breadth, but that is
not yet equivalent to live/default readiness.
**Why it matters:** Recommendation and status surfaces need to stay conservative
until live evidence is explicit and reviewable.
**Resolution:** AC14 now persists a dedicated live-readiness artifact for
realistic-input `llm` acceptance, recommendation/status surfaces consume that
artifact explicitly, and live runs require `AC14_ENABLE_LIVE_LLM_READINESS=1`
so ambient credentials cannot silently upgrade the readiness story.
**Date resolved:** 2026-04-01

### U-020: Ambient credentials can blur “live readiness” intent.
**Status:** Resolved
**Context:** `llm_client`-level auth loading can make a process capable of live
LLM calls even when the shell environment does not obviously expose provider
keys.
**Why it matters:** The readiness boundary should reflect explicit operator
intent, not accidental ambient auth.
**Resolution:** AC14 now requires `AC14_ENABLE_LIVE_LLM_READINESS=1` before it
attempts a live readiness run; otherwise it records an explicit `skipped`
artifact instead of inferring permission from ambient process state.
**Date resolved:** 2026-04-01

### U-021: Packet existence is not the same as packet sufficiency.
**Status:** Resolved
**Context:** AC14 already had compiled packets and bounded codegen contexts,
but it still lacked one explicit artifact proving the local structural contract
was present per packet.
**Why it matters:** The thesis depends on packets being enough for bounded local
generation, not merely on packets existing.
**Resolution:** AC14 now persists a structural packet-sufficiency artifact that
records local schemas, neighboring context, fixtures, packet-local tests, and
any missing structural elements per packet without overclaiming semantic
sufficiency.
**Date resolved:** 2026-04-01

### U-022: Realistic-input full-system acceptance was still outside the default proof path.
**Status:** Resolved
**Context:** AC14 had realistic-input acceptance artifacts, but the default
single-example proof/evidence bundle still ended at structural and recomposition
artifacts.
**Why it matters:** The final proof story should include actual realistic-input
execution plus semantic review, not just offer it as a side command.
**Resolution:** AC14 now persists a `realistic_input_gate.json` artifact inside
the default deterministic proof/evidence bundle, includes realistic-input
acceptance when shipped input exists, and records explicit `missing` or
`unsupported` states instead of silently skipping the final gate.
**Date resolved:** 2026-04-01

### U-023: Realistic-input suite acceptance was still outside the default suite proof path.
**Status:** Resolved
**Context:** AC14 had suite-level realistic-input acceptance artifacts, but the
default suite proof story still ended at structural and recomposition evidence.
**Why it matters:** The suite proof story should carry final-gate realistic-input
acceptance explicitly instead of leaving it as a side artifact.
**Resolution:** AC14 now persists realistic-input final-gate status per shipped
example in the default suite proof report, with aggregate `included`,
`missing`, and `unsupported` counts across the suite.
**Date resolved:** 2026-04-01

### U-024: Recommendation logic was not consuming the suite default-gate evidence.
**Status:** Resolved
**Context:** AC14 had default-gate evidence at single-example and suite level,
but the default-generator recommendation still reasoned from suite comparison,
semantic comparison, and live readiness without consuming that default-gate
coverage.
**Why it matters:** Recommendation should reflect the same default proof story
that AC14 claims elsewhere.
**Resolution:** Recommendation now persists the suite proof report path, records
suite-level default-gate counts, and includes explicit reasons when default-gate
coverage is incomplete.
**Date resolved:** 2026-04-01

### U-025: Live readiness was still only a one-example artifact.
**Status:** Resolved
**Context:** AC14 had an explicit operator-gated live-readiness artifact for
realistic-input `llm` acceptance, but it only probed one shipped example.
**Why it matters:** Broader live/default readiness evidence should not rely on
one example once suite-level realistic-input breadth exists elsewhere.
**Resolution:** AC14 now persists a suite-level live-readiness artifact with
per-example and aggregate `ready`, `blocked`, and `skipped` results while
keeping live execution operator-explicit.
**Date resolved:** 2026-04-01

### U-026: Recommendation logic was not consuming the suite live-readiness artifact.
**Status:** Resolved
**Context:** AC14 had both the bounded one-example live-readiness artifact and
the broader suite-level live-readiness artifact, but recommendation still
looked only at the smaller probe.
**Why it matters:** Recommendation should reflect the broader explicit
live-readiness evidence once it exists.
**Resolution:** Recommendation now persists suite live-readiness status, suite
live artifact path, suite ready/blocked/skipped counts, and explicit reasons
when suite live readiness is not ready.
**Date resolved:** 2026-04-01

### U-027: Draft/freeze quality still lacked one directly attached semantic review artifact.
**Status:** Resolved
**Context:** AC14 had stronger semantic review at front-half acceptance and
final acceptance than directly at freeze time.
**Why it matters:** Business-logic review should become visible before final
execution, not only after a full system run.
**Resolution:** `decide-freeze` now persists `freeze_semantic_review.json` for
draft bundles with readiness evidence, publishes its path on the freeze
decision artifact, and front-half acceptance carries that path forward.
**Date resolved:** 2026-04-01

### U-028: Front-half breadth was still only a one-example story.
**Status:** Resolved
**Context:** AC14 had a strong per-example front-half artifact plus a directly
attached freeze-semantic review, but no suite-level breadth artifact across the
shipped realistic-input examples.
**Why it matters:** The front half should have explicit breadth evidence rather
than leaving breadth only to the back half of the proof slice.
**Resolution:** AC14 now persists `front_half_acceptance_suite_report.json`
with per-example report paths, directly attached freeze-semantic review paths,
separate review-vs-freeze aggregate counts, and explicit missing-input states.
**Date resolved:** 2026-04-01

### U-029: The front half was still too clean relative to the messy-input thesis.
**Status:** Resolved
**Context:** AC14 had front-half breadth across shipped JSON examples, but the
first realistic inputs were still relatively schema-friendly.
**Why it matters:** The project thesis is about helping with messy context, not
just clean structured inputs.
**Resolution:** AC14 now proves one explicit front-half lane on a reviewable CSV
asset under the support-ticket example, keeping discovery, draft planning,
freeze review, and semantic front-half review explicit on a messier artifact.
**Date resolved:** 2026-04-01

### U-030: Dependency blockers still stopped at diagnosis more often than controlled action.
**Status:** Resolved
**Context:** AC14 could plan dependencies, probe them, and block freeze when
needed libraries remained unavailable, but it still lacked a narrow remediation
lane.
**Why it matters:** The long-term system needs to install and use libraries in a
reviewable way, not just report blockers.
**Resolution:** AC14 now persists an explicit dependency-remediation artifact
that reruns previously blocked install probes, records the delta, and points to
a fresh dependency execution artifact for downstream reuse.
**Date resolved:** 2026-04-01

### U-031: Dependency remediation still required manual execution-path extraction before draft planning.
**Status:** Resolved
**Context:** AC14 could rerun blocked dependency probes and produce a fresh
dependency execution artifact, but operators still had to manually thread that
path back into later front-half work.
**Why it matters:** Remediation should reduce hand-off friction without hiding
which execution evidence actually drove the next planning step.
**Resolution:** Draft planning now accepts a remediation artifact directly,
selects the remediated dependency execution artifact from it, persists both
paths explicitly, and fails loud if direct execution-path input disagrees with
the remediation artifact.
**Date resolved:** 2026-04-01

### U-032: The first blocked-freeze retry step still required manual bundle editing.
**Status:** Resolved
**Context:** AC14 could emit remediation tasks from a blocked freeze decision,
but the first explicit retry still depended on a human editing the materialized
bundle directly.
**Why it matters:** The next thesis-preserving automation step should refine
the plan, not mutate the bundle in place.
**Resolution:** AC14 now emits a remediation-driven refined draft planning
artifact that preserves the source plan, freeze decision, remediation plan,
and refinement round while letting later phases rematerialize from the updated
plan instead of editing the bundle directly.
**Date resolved:** 2026-04-01

### U-033: The first explicit retry still required manual multi-command orchestration.
**Status:** Resolved
**Context:** AC14 could refine a blocked draft plan, but operators still had to
manually run materialization and freeze again.
**Why it matters:** The first retry chain should stay explicit and artifact-backed
instead of depending on remembered command sequencing.
**Resolution:** AC14 now persists one retry-chain artifact that runs refine ->
materialize -> refreeze and records every intermediate path plus the refreshed
freeze result.
**Date resolved:** 2026-04-01

### U-034: Retry evidence still stopped at standalone artifacts instead of front-half acceptance.
**Status:** Resolved
**Context:** AC14 could emit retry-chain artifacts, but realistic-input
front-half acceptance still stopped at the initial freeze decision.
**Why it matters:** The front-half evidence story should be able to include one
bounded retry without overwriting the original blocked freeze result.
**Resolution:** AC14 now offers an opt-in retry-aware front-half acceptance path
that preserves the initial freeze decision, adds the retry artifact path, and
publishes final freeze approval separately from the original blocked result.
**Date resolved:** 2026-04-01

### U-035: Retry-aware front-half evidence still did not have breadth across the shipped suite.
**Status:** Resolved
**Context:** AC14 could produce retry-aware front-half acceptance per example,
but the suite-level front-half artifact still only aggregated the initial freeze
result.
**Why it matters:** The retry-aware front-half story should have at least one
breadth artifact before broader claims are made.
**Resolution:** AC14 now offers an opt-in retry-aware front-half suite artifact
that aggregates retry-attempted and retry-approved counts while preserving
per-example retry artifact paths.
**Date resolved:** 2026-04-01

### U-036: Realistic-input final acceptance still assumed top-level JSON lists.
**Status:** Resolved
**Context:** Front-half discovery already supports multiple structured input
formats, but full-system realistic-input acceptance still only loads top-level
JSON lists and only auto-discovers `.json` input files.
**Why it matters:** The final semantic gate cannot honestly claim messy-input
coverage while it silently excludes the same structured formats the front half
already supports.
**Resolution:** AC14 now shares one structured-input loading surface between
discovery and acceptance, supports `json`, `jsonl`, `csv`, and `yaml` object
records at the final gate, and can auto-discover structured realistic-input
artifacts without hardcoding `.json`.
**Date resolved:** 2026-04-01

### U-006: Proof breadth is still narrow overall.
**Status:** Deferred
**Context:** AC14 now spans more than one workflow slice, but breadth remains
limited.
**Why it matters:** Strong artifact discipline can still overfit to a small set
of workflow patterns.

### U-007: Live LLM acceptance may remain too expensive for the default gate.
**Status:** Deferred
**Context:** Requirements-aware semantic review is valuable, but always-on live
evaluation may be too costly.
**Why it matters:** AC14 needs a realistic balance between semantic rigor and
operator cost.

### U-008: Manual remediation loops still dominate blocked freeze decisions.
**Status:** Deferred
**Context:** Direct draft-bundle editing exists, but automated rewrite loops are
not yet proven.
**Why it matters:** Future automation could help or could add noisy churn.

### U-037: The messy-input final gate is still unproven in bounded `llm` mode.
**Status:** Resolved
**Context:** Bounded realistic-input `llm` acceptance exists on the cleaner
JSON slice, but the messy CSV asset still has no explicit `llm` final-gate
evidence.
**Why it matters:** AC14 should broaden non-deterministic validation honestly
without letting fixture-backed `llm` evidence drift into live-readiness claims.
**Resolution:** AC14 now proves one bounded fixture-backed messy-input `llm`
acceptance lane on the support-ticket CSV asset and persists a matching
realistic mode-comparison artifact across `reference`, `deterministic`, and
`llm`.
**Date resolved:** 2026-04-01

### U-038: The first messy-input final-gate proof could have hidden runtime normalization.
**Status:** Resolved
**Context:** Once the final gate started consuming the shipped messy CSV asset,
the easiest workaround would have been to invent implicit runtime normalization
for missing required fields.
**Why it matters:** Hidden runtime normalization would blur whether the input
artifact is actually executable against the frozen blueprint contract.
**Resolution:** AC14 now keeps the messy CSV artifact schema-sufficient for the
frozen source schema and decodes JSON-like CSV cells explicitly, rather than
hiding missing required fields behind runtime heuristics.
**Date resolved:** 2026-04-01

### U-039: Realistic-input selection is still implicit and inconsistent across surfaces.
**Status:** Resolved
**Context:** The support-ticket example now ships both a clean JSON realistic
input and a messy CSV realistic input. `acceptance.py` can discover structured
candidates, while `front_half_acceptance.py` still defaults to `.json` only.
**Why it matters:** Hidden selection precedence and cross-surface drift make the
proof story ambiguous once one example ships more than one realistic-input
artifact.
**Resolution:** AC14 now gives shipped examples explicit realistic-input
manifests with named defaults and named alternate profiles, and both
acceptance surfaces use the shared resolver for shipped-example defaults.
**Date resolved:** 2026-04-01

### U-040: Alternate realistic-input profile behavior is not yet explicit at suite level.
**Status:** Resolved
**Context:** Once realistic-input selection becomes explicit per example, suite
surfaces still need to say whether a requested alternate profile is included or
missing for each shipped example.
**Why it matters:** Suite breadth should not silently fall back to the default
profile or silently skip examples when an alternate profile is absent.
**Resolution:** AC14 suite surfaces now persist the requested realistic-input
profile and explicit `missing_profile` counts/results instead of silently
falling back or silently skipping examples.
**Date resolved:** 2026-04-01

### U-041: Operator surfaces do not yet expose realistic-input profile selection explicitly.
**Status:** Resolved
**Context:** The manifest and shared resolver now exist, but CLI and Make
surfaces still assume the implicit default profile.
**Why it matters:** Alternate realistic-input profiles should be operable and
reviewable without changing code or silently redefining the clean default path.
**Resolution:** Front-half suite and realistic-input suite CLI/Make surfaces now
accept an explicit realistic-input profile selector while preserving the clean
default profile when the flag is omitted.
**Date resolved:** 2026-04-01

### U-042: The explicit messy-profile suite proof is still incomplete in bounded `llm` mode.
**Status:** Resolved
**Context:** AC14 can now request the explicit `messy` profile across suite and
operator surfaces, but the suite-level alternate-profile proof has not yet been
completed across the bounded fixture-backed `llm` lane.
**Why it matters:** The next honest step is one reviewable non-deterministic
suite proof on the alternate profile, not another policy-only lane.
**Resolution:** AC14 now proves the explicit `messy` profile across
`reference`, `deterministic`, and bounded fixture-backed `llm` in the
realistic-input suite artifact while preserving explicit `missing_profile`
states for the other shipped examples.
**Date resolved:** 2026-04-01

### U-043: Discovery is still centered on one input file at a time.
**Status:** Resolved
**Context:** AC14 can inspect one input file well, but real blueprint derivation
often requires looking across a directory of related structured files and local
context artifacts before choosing the primary planning input.
**Why it matters:** The front half remains weaker than the thesis if discovery
cannot review a bounded multi-artifact input set explicitly.
**Resolution:** Discovery now accepts one bounded directory input, inventories
supported structured candidates plus supporting local context files, chooses
one deterministic primary structured candidate, and persists both the chosen
primary candidate and the alternatives explicitly.
**Date resolved:** 2026-04-01

### U-044: Directory-input discovery is implemented, but the front-half acceptance lane has not yet proven it end to end.
**Status:** Resolved
**Context:** AC14 can now persist explicit directory-input discovery artifacts,
but the front-half acceptance proof still focuses on single-file inputs.
**Why it matters:** The new discovery capability remains weaker than the thesis
until the same explicit directory-input story survives the discovery-through-freeze chain.
**Resolution:** Front-half acceptance now has one explicit directory-input proof
lane, and CLI plus Make preserve the same directory-input discovery evidence
without hiding which structured candidate became primary.
**Date resolved:** 2026-04-01

### U-045: Directory discovery still persists only paths for alternate candidates and supporting context.
**Status:** Resolved
**Context:** AC14 now inventories alternate structured candidates and supporting
local context files explicitly, but the persisted discovery artifact still
provides only their file paths.
**Why it matters:** Planning remains weaker than it should be if the surrounding
directory context cannot be reviewed in a compact bounded summary.
**Resolution:** Directory discovery now persists bounded summaries for
alternate structured candidates and supporting local context files while
preserving one explicit primary structured planning input.
**Date resolved:** 2026-04-01

### U-046: The new directory summaries are not yet proven through the front-half chain.
**Status:** Resolved
**Context:** AC14 now persists bounded directory summaries at raw discovery,
but the front-half acceptance proof has not yet shown that those summary fields
survive discovery-through-freeze on a directory input bundle.
**Why it matters:** Summary enrichment remains weaker than the thesis if it is
only proven at `discover-input` and not in the front-half artifact chain.
**Resolution:** Front-half acceptance now preserves both alternate structured
candidate summaries and supporting-context summaries on a directory input, and
CLI plus Make preserve the same propagated summary story.
**Date resolved:** 2026-04-01

### U-047: Directory discovery still does not compare primary and alternate structured candidates explicitly.
**Status:** Resolved
**Context:** AC14 can now inventory and summarize alternate structured
candidates, but it still leaves schema drift between the primary and alternate
candidates implicit.
**Why it matters:** The front half remains weaker than it should be if schema
divergence across related input artifacts is not surfaced before freeze.
**Resolution:** Directory discovery now compares primary and alternate
structured candidates and persists bounded schema-divergence concerns when the
field shapes differ materially.
**Date resolved:** 2026-04-01

### U-048: The new directory schema-divergence concerns are not yet proven through the front-half chain.
**Status:** Open
**Context:** AC14 now persists bounded directory schema-divergence concerns at
raw discovery time, but the front-half acceptance proof has not yet shown that
those concerns survive discovery-through-freeze on a directory input bundle.
**Why it matters:** Schema-divergence detection remains weaker than the thesis
if it is only proven at `discover-input` and not in the broader front-half
artifact chain.

### U-067: Interrupted full-trial empirical runs were leaving zero-byte artifacts and no safe resume path.
**Status:** Resolved
**Context:** The first attempt at the second full-trial gate died mid-run and
left empty `paired_trial_report.json`, `attempt_report.json`, and generated
module artifacts.
**Why it matters:** Without atomic writes and resume behavior, the empirical
gate would depend on manual cleanup and could silently lose observability.
**Resolution:** Plan #71 added atomic empirical artifact writes, reuse of valid
completed paired-trial reports, and archival of incomplete trial directories
under `_interrupted_trials/` before rerun.
**Date resolved:** 2026-04-02

### U-068: The harder second empirical gate might still be unresolved or infrastructure-contaminated.
**Status:** Resolved
**Context:** Before the repaired full-trial rerun completed, the second gate
had only smoke evidence plus an interrupted full-trial directory.
**Why it matters:** The project needed to know whether the harder benchmark
would validate AC14, remain inconclusive, or lose cleanly.
**Resolution:** `.ac14_out/full_trials_gate_2/experiment_decision.json` now
exists with verdict `monolithic_wins`. All five trials recorded observed costs,
and the completed reports do not show infrastructure-provider as the dominant
failure class.
**Date resolved:** 2026-04-02

### U-069: Does the second-gate loss reflect benchmark-local business-rule misses or deeper packet/context limitations?
**Status:** Investigating
**Context:** The harder benchmark now finished decisively in favor of the
monolithic baseline, but AC14's dominant failure surfaces span repeated packet
fixture mismatches, recomposition mismatches, and one late syntax failure.
**Why it matters:** The next lane should be diagnosis first, not reflexive
benchmark-local tuning or premature thesis-level overreaction.

### U-009: Proof breadth metrics are still approximate.
**Status:** Deferred
**Context:** Current breadth accounting relies on workflow signatures and light
heuristics rather than a richer benchmark taxonomy.
**Why it matters:** Breadth claims must remain conservative.

### U-010: Shared retrieval and dependency-install surfaces still need a cleaner integration boundary.
**Status:** Deferred
**Context:** Shared retrieval exists and dependency planning exists, but the
execution boundary is not yet settled.
**Why it matters:** Poor integration here could create tool sprawl or hidden side channels.

## Planning-Artifact Uncertainty History

### U-011: Planning-artifact drift was the biggest recent risk.
**Status:** Resolved
**Context:** Implementation had moved beyond the original bootstrap notebook and
earlier planning surfaces.
**Resolution:** AC14-native doctrine, roadmap, implementation status, adoption
plan, numbered plan surface, and current notebook now exist to close that gap.
**Date resolved:** 2026-03-31

# AC14 Uncertainties

Status: Canonical uncertainty tracker
Last updated: 2026-04-01

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

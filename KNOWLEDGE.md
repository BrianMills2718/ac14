# Operational Knowledge — ac14

Shared findings from all agent sessions. Any agent brain can read and append.
Human-reviewed periodically.

## Findings

### 2026-03-29 — codex — schema-gotcha
Full-graph recomposition and semantic comparison are inferred conservatively from
blueprint scenarios. A scenario is runnable only when it supplies exactly one
fixture per component for the current blueprint; negative or incomplete
scenarios are skipped from full-graph execution and remain packet-level only.

### 2026-03-29 — codex — best-practice
Default-generator recommendation is intentionally conservative. `llm` should not
be promoted unless it passes suite proof, matches expected/reference semantics,
and the shipped suite covers more than one semantic-responsibility family.

### 2026-03-30 — codex — schema-gotcha
Scenario meaning should be explicit in blueprint data, not inferred from
scenario-id naming. AC14 now treats `kind`, evaluator IDs, realistic-input
flags, and requirements as first-class scenario fields, and validation fails
loud when end-to-end coverage or semantic-acceptance requirements are missing.

### 2026-03-30 — codex — best-practice
For semantic-acceptance review, use both kinds of evidence: strong programmatic
checks to prove structure/execution constraints and `llm_client` structured
review to judge requirement satisfaction, business-logic reasonableness, and
final acceptance on actual system outputs.

### 2026-03-30 — codex — best-practice
Pre-freeze discovery should persist what it learned from real local inputs
instead of relying on human memory or chat history. AC14 now records compact
sample data, inferred field paths, sparse/mixed-type concerns, and dependency
installation status before blueprint freeze.

### 2026-03-30 — codex — best-practice
Discovery artifacts are not enough by themselves. AC14 now uses them as inputs
to a separate draft blueprint planning artifact so decomposition proposals stay
explicit, reviewable, and distinct from frozen proof artifacts.

### 2026-03-30 — codex — best-practice
Draft planning is still not authoring. AC14 now materializes a real six-file
draft bundle plus a freeze-readiness report so missing fixtures, placeholder
contracts, and unresolved questions become explicit artifacts instead of hidden
gaps.

### 2026-03-30 — codex — best-practice
Readiness is still not a decision. AC14 now persists an explicit freeze
decision artifact and only promotes when approval is true, so promotion is no
longer an implicit manual interpretation step.

### 2026-03-31 — codex — best-practice
Proof breadth is an evaluation heuristic, not project ontology. AC14 now uses a
broader shipped suite with `incident_alert_digest` plus ticket-digest slices,
and the recommendation surface talks about `proof_breadth_count` rather than
`semantic_family_count`.

### 2026-03-31 — codex — best-practice
Pre-freeze discovery should not stop at input shape plus package inventory.
AC14 now persists a local project-context inventory so README, CLAUDE, and docs
become explicit reviewable planning inputs before blueprint freeze.

### 2026-03-31 — codex — best-practice
External web and repository lookup should stay reviewable. AC14 now persists
external retrieval artifacts with explicit queries, URLs, repo paths, and
concerns, then folds only compact summaries into discovery artifacts so
planning context stays inspectable instead of disappearing into prompt text.

### 2026-03-31 — codex — best-practice
Dependency and library choices should stay advisory and evidence-backed before
freeze. AC14 now persists an explicit dependency plan with `reuse`, `install`,
`investigate`, and `avoid` actions grounded in environment state, retrieved
docs/repos, and carried-forward concerns instead of hiding package judgments in
draft-planning prompts.

### 2026-03-31 — codex — best-practice
Dependency planning should not stop at a side artifact. AC14 now feeds
dependency-plan provenance, compact dependency actions, and unresolved
dependency questions into draft blueprint planning so draft authoring and freeze
readiness can surface those issues explicitly.

### 2026-03-31 — codex — best-practice
Planning-artifact drift is a real failure mode. AC14 now has an AC14-native
execution/alignment notebook plus a blunt implementation-status document so the
story artifact can stay synchronized with the code instead of relying only on
the older bootstrap notebook in `ac12`.

### 2026-03-31 — codex — best-practice
Dependency execution should stay explicit and reviewable. AC14 now persists a
dependency execution artifact with `confirmed` / `blocked` / `skipped` results,
before/after package snapshots, and narrow default behavior that blocks install
mutation unless the operator explicitly enables it.

### 2026-03-31 — codex — best-practice
Dependency probe evidence should not stop at a side artifact. AC14 now carries
confirmed and blocked probe summaries into draft planning, turns blocked probe
results into explicit freeze-readiness blockers, and groups those blockers into
freeze-remediation tasks so unavailable libraries cannot slip past freeze as
mere warnings.

### 2026-03-31 — codex — best-practice
Project-process policy for dependency evidence should be shared infrastructure,
not AC14-only convention. AC14 now reads `planning.dependency_probe_policy`
from `meta-process.yaml` with `strict` default behavior, while `project-meta`
defines the shared `strict|warn|ignore` vocabulary.

### 2026-03-31 — codex — best-practice
Realistic-input proof should not begin at frozen blueprints. AC14 now persists
one `front_half_acceptance_report.json` artifact that runs discovery,
dependency planning, dependency probing, draft planning, draft authoring, and
freeze decision on a realistic input file, then adds a structured semantic
review that can still conclude `promising_but_blocked` when the front half
looks sound but freeze is not yet approved.

### 2026-03-31 — codex — best-practice
Realistic-input final acceptance should use actual system outputs, not only
front-half artifacts. AC14 now lets `acceptance-review` run a realistic input
record through a shipped blueprint in `reference` mode, persist the real
outputs, and then add a structured semantic review at the final gate.

### 2026-03-31 — codex — best-practice
Realistic-input breadth should fail loud on missing shipped artifacts instead of
quietly shrinking the suite. When AC14 added a realistic-input suite artifact,
it surfaced that `support_ticket_digest_auth_mix` declared a realistic-input
scenario but shipped no input file; the right fix was to add the missing input
artifact and keep suite coverage explicit rather than silently filtering the
example out.

### 2026-03-31 — codex — bug-pattern
`llm` realistic-input acceptance was structurally broken inside AC14's async
acceptance path because LLM codegen still routed through the sync wrapper with
`asyncio.run()`. The right fix was not a test workaround; it was an async
generated-package path so acceptance can call async LLM codegen directly when
already inside an event loop.

### 2026-03-31 — codex — best-practice
Fixture-backed `llm` breadth needs blueprint-aware keys, not just component
IDs. Once AC14 widened realistic-input `llm` acceptance beyond one blueprint,
flat fixture maps became ambiguous because multiple blueprints reused component
IDs with different embedded deterministic state. The right fix was carrying
`blueprint_id` through packets/codegen contexts and resolving fixtures by
`blueprint_id + component_id`.

### 2026-04-01 — codex — best-practice
Live-readiness evidence should be operator-explicit, not inferred from ambient
credentials. AC14 now requires `AC14_ENABLE_LIVE_LLM_READINESS=1` before it
attempts a real live-readiness run, persists an explicit `ready` / `blocked` /
`skipped` artifact, and keeps that evidence separate from fixture-backed `llm`
breadth in recommendation/status surfaces.

### 2026-04-01 — codex — best-practice
Packet existence is not enough. AC14 now persists a structural
`packet_sufficiency_report.json` so the project can show, per packet, that
local schemas, neighboring context, fixtures, and packet-local tests are
present without pretending that this alone proves semantic sufficiency.

### 2026-04-01 — codex — best-practice
If realistic-input final acceptance matters to the thesis, it should live in
the default proof story. AC14 now persists `realistic_input_gate.json` inside
the default deterministic proof/evidence bundle, includes realistic-input
acceptance when shipped input exists, and records explicit `missing` or
`unsupported` states instead of silently skipping the gate.

### 2026-04-01 — codex — best-practice
Once realistic-input final acceptance is part of the suite default proof story,
recommendation/default-generator logic should consume that evidence directly
instead of reasoning only from structural suite comparison and semantic
comparison artifacts.

### 2026-04-01 — codex — best-practice
Live readiness should not stop at a one-example probe once suite-level
realistic-input breadth exists. The next honest artifact is a suite-level live
readiness report that stays operator-gated and keeps per-example `ready` /
`blocked` / `skipped` results explicit.

### 2026-04-01 — codex — best-practice
Once suite-level live readiness exists, recommendation should consume it
directly instead of relying only on the bounded one-example live probe.

### 2026-04-01 — codex — best-practice
Front-half business-logic review should attach directly to freeze quality, not
float only as a later acceptance artifact. AC14 now persists
`freeze_semantic_review.json` whenever `decide-freeze` evaluates a draft bundle
with readiness evidence, and front-half acceptance now carries that path
forward explicitly.

### 2026-04-01 — codex — best-practice
Once front-half semantic review exists per example, the next honest breadth step
is a suite-level front-half artifact across shipped realistic-input examples.
AC14 now persists `front_half_acceptance_suite_report.json` with per-example
report paths, attached freeze-semantic paths, and separate semantic-vs-freeze
aggregate counts instead of leaving front-half breadth implicit.

### 2026-04-01 — codex — best-practice
The first honest messy-input step does not need a new blueprint family or a new
runtime feature. AC14 now proves the front-half chain on a reviewable CSV asset
under the support-ticket example so discovery-through-freeze can be tested on a
messier artifact without scope sprawl.

### 2026-04-01 — codex — best-practice
Dependency remediation does not need a second dependency system. AC14 now uses
the existing dependency execution artifact as the hand-off, reruns previously
blocked install probes explicitly, and persists a remediation delta artifact
plus a fresh dependency execution artifact for downstream reuse.

### 2026-04-01 — codex — best-practice
The first remediation automation step should stay plan-first. AC14 now lets
draft planning consume a remediation artifact directly, preserves both the
remediation path and the selected dependency execution path, and fails loud
when those two sources disagree.

### 2026-04-01 — codex — best-practice
The first blocked-freeze retry step should refine the plan, not mutate the
bundle. AC14 now emits a refined draft planning artifact from the original
plan plus the blocked freeze/remediation inputs, preserves explicit retry
provenance, and increments a refinement round so later retries stay reviewable.

### 2026-04-01 — codex — best-practice
Once a refined plan exists, the next honest automation step is an explicit
retry chain, not hidden command sequencing. AC14 now persists one retry-chain
artifact that runs refine -> materialize -> refreeze and keeps every
intermediate path visible.

### 2026-04-01 — codex — best-practice
Retry-aware front-half evidence should preserve the first blocked freeze
record. AC14 now lets realistic-input front-half acceptance opt into one
explicit retry chain while keeping both the initial freeze decision path and
the retry artifact path visible in the final report.

### 2026-04-01 — codex — best-practice
Once single-example retry-aware front-half acceptance exists, the next honest
breadth step is a suite artifact that stays opt-in and preserves per-example
retry artifact paths. AC14 now aggregates retry-attempted and retry-approved
counts without collapsing the per-example provenance.

---

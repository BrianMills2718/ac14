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

---

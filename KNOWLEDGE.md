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
Retry-aware messy-input proof also does not need a new artifact type. AC14 now
reuses the existing front-half acceptance artifact on the support-ticket CSV
asset and keeps the initial blocked freeze, the retry-chain artifact, and the
final semantic review explicit instead of collapsing them into one success
claim.

### 2026-04-01 — codex — best-practice
If discovery supports multiple structured realistic-input formats, the final
gate should not quietly narrow back to JSON-only. AC14 now shares one
structured-input loader between discovery and acceptance, so record-bearing
`json`, `jsonl`, `csv`, and `yaml` inputs remain executable all the way through
semantic acceptance.

### 2026-04-01 — codex — best-practice
The first honest messy-input final-gate proof should keep the input artifact
messy but still schema-sufficient. AC14 now proves the support-ticket CSV
asset through `reference` and `deterministic` final acceptance by keeping the
required source fields explicit and decoding JSON-like CSV cells for list
fields, rather than inventing hidden runtime normalization.

### 2026-04-02 — codex — best-practice
When the empirical lane is blocked on benchmark fidelity, repair guidance must
not stay as one undifferentiated summary copied to every component. AC14 now
renders packet-local schema definitions in the component prompt and combines
benchmark-local component guidance with bounded prior-attempt guidance so the
repair loop is targeted without changing the attempt-count fairness contract.

### 2026-04-01 — codex — best-practice
Once the non-LLM messy-input final gate is explicit, the next honest
non-deterministic step is one bounded fixture-backed `llm` proof on the same
asset, not a vague breadth claim. AC14 now proves the support-ticket CSV asset
through the final gate in bounded `llm` mode and keeps that lane separate from
live readiness.

### 2026-04-01 — codex — best-practice
Once one shipped example has both clean and messy realistic-input artifacts,
file-extension precedence stops being an honest policy. AC14 now gives shipped
examples explicit realistic-input manifests and a shared resolver so both
acceptance surfaces use the same named default.

### 2026-04-01 — codex — best-practice
Once the manifest exists, alternate profiles need explicit suite/operator
semantics too. AC14 now records `missing_profile` explicitly instead of
silently falling back, which keeps the clean default proof path separate from
alternate-profile experiments.

### 2026-04-01 — codex — best-practice
Directory discovery is only useful if the primary planning input stays
explicit. AC14 now persists the chosen primary structured candidate plus the
alternative structured candidates and supporting local context files whenever
discovery starts from a directory input, instead of collapsing that choice
into hidden prompt context.

### 2026-04-01 — codex — best-practice
Directory-input proof should not stop at raw discovery. AC14 now proves the
same explicit directory-input story through front-half acceptance, while the
next honest gap is bounded summaries for alternate candidates and supporting
context rather than only their file paths.

### 2026-04-02 — codex — best-practice
Empirical harness observability must stay structured all the way into retry
guidance. AC14 now persists bounded field-level mismatch details inside packet
and recomposition reports and threads those details into empirical failure
summaries instead of collapsing them into generic labels like `packet-local
tests failed`.

### 2026-04-02 — codex — best-practice
The empirical thesis gate should use real `llm_client` experiment context, not
warning-only observability. AC14 now wraps each empirical attempt in
`experiment_run(...)` plus `activate_feature_profile(...)` with benchmark,
trial, attempt, and condition provenance.

### 2026-04-02 — codex — schema-gotcha
The order-exception benchmark was still underspecified in narrow ways even
after the larger harness repairs. The benchmark now states the
`case_parser.normalized_notes` trailing-period rule, keeps absent override
fields omitted, distinguishes override-vs-compound priority branches, and the
shared generation prompts now require ASCII-only Python source so bounded smoke
attempts do not burn retries on non-Python identifiers.

### 2026-04-02 — codex — schema-gotcha
Repair9 showed that the remaining shared benchmark ambiguity was about shipping
materiality and escalation semantics, not generic packet failure. The benchmark
now states that shipping risk is already `high` at 24+ hours, that logistics
routing does not automatically imply `escalation_required=true`, and that a
moderate shortage with delayed replenishment may still be `high` risk while the
reason stays in the partial-fulfillment/back-order family.

### 2026-04-02 — codex — best-practice
Empirical monolithic failures must persist invalid source, not just exception
strings. AC14 now writes `monolithic_response.json`, `<component>.failed.py`,
and validation metadata before failing a monolithic attempt on invalid Python so
the next repair lane can inspect the actual bad code directly.

### 2026-04-01 — codex — best-practice
Once directory discovery grows bounded summaries, the next honest proof is
propagation rather than more raw discovery features. The summaries now exist at
`discover-input`; the next gap is proving that the same summary fields survive
the front-half discovery-through-freeze chain without creating a second truth
surface.

### 2026-04-01 — codex — best-practice
When AC14 enters a sequence of clean propagation-proof micro-lanes, the next
honest gate is not automatically the next propagation proof. If the main
thesis is still unmeasured, insert an explicit empirical comparison gate before
continuing so plan completion does not masquerade as thesis validation.

### 2026-04-01 — codex — integration-issue
AC14's retrieval surface depended on `open_web_retrieval`, but the repo had not
declared that shared dependency explicitly and the current editable install was
pointing at a stale worktree. The correct fix was to add
`open-web-retrieval` to `pyproject.toml` and repoint the editable install to
the canonical shared repo, not to weaken mypy or the retrieval import path.

### 2026-04-01 — codex — best-practice
Once directory summaries exist, the next honest schema-inference step is
bounded divergence evidence, not hidden multi-file schema merging. AC14 now
persists explicit concerns when alternate structured candidates expose fields
that are absent from the primary structured planning input.

### 2026-04-01 — codex — best-practice
The first honest alternate-profile breadth proof is not to replace the default
path; it is to run one explicit bounded suite lane and make absence visible.
AC14 now proves the `messy` profile across the realistic-input suite in
bounded `llm` mode while recording `missing_profile` for the other examples.

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
Once the empirical comparison gate exists, the next honest step is not always
the full five-trial run. AC14 now persists an explicit smoke-readiness artifact
with `ready_for_full_trials`, `blocked_on_infrastructure`, and
`blocked_on_harness` so the stop/go decision is reviewable instead of living
only in chat.

### 2026-04-01 — codex — best-practice
When AC14 LLM codegen fails during import-time validation, the raw module source
must still be persisted for diagnosis. Otherwise the empirical lane only learns
an exception string and the next repair step becomes guesswork.

### 2026-04-01 — codex — best-practice
If empirical smoke failures are now clearly benchmark-local, keep the next
repair lane benchmark-local too. The current blocker has moved from provider
noise to fidelity against the benchmark contract, so the next lane should
tighten benchmark guidance rather than adding broad new AC14 runtime behavior.

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

### 2026-04-01 — codex — integration-issue
The empirical-comparison runtime harness initially persisted mutable references
to the stateful digest store, so later cases mutated earlier runtime artifacts.
Deep-copy final outputs when recording runtime-case evidence or the smoke-trial
reports become internally inconsistent.

### 2026-04-01 — codex — best-practice
Do not spend the full five-trial empirical-comparison budget until one bounded
smoke paired trial produces a hard-harness success or the benchmark/generator
setup is explicitly documented as the blocker. The runner is real now, but
provider instability and zero-success smoke runs are themselves part of the
gate evidence.

### 2026-04-02 — claude-code — best-practice
Exact string comparison for free-form text fields (reason, action_summary, score) is the
wrong evaluation method throughout the harness. LLM-generated components will never
reproduce exact phrasing. The correct architecture is two-phase: (1) strip free-form
fields and do categorical exact comparison for routing/classification fields; (2) use an
LLM judge for semantic correctness of free-form fields. This pattern applies at the
packet-test level, recomposition level, AND the final runtime evaluation level.
Building this in at every layer prevents repeated harness failures as new benchmarks are
added.

### 2026-04-02 — claude-code — schema-gotcha
Blueprint fixtures must not include expected values for free-form fields unless LLM
evaluation is wired in. The fields `reason`, `action_summary`, and `score` in fixture
expected_outputs will never exactly match LLM-generated values. Either omit them from
expected_outputs (existence-only) or use the LLM evaluation path. Keeping them in
expected_outputs as documentation of intent is fine only if the comparison logic strips
them before exact comparison.

### 2026-04-02 — claude-code — best-practice
Compound exception fixtures must be added to the blueprint for the LLM generator to
handle compound cases correctly. Without a compound exception fixture example, generated
components produce wrong categorical values (e.g., priority_band='high' instead of
'critical' for compound_exception cases). The fixture provides the concrete
input/output contract that guides generation.

### 2026-04-02 — codex — best-practice
When the empirical smoke gate is blocked by repeated syntax-invalid code, the
next honest fix is prompt and repair-guidance discipline, not a hidden
syntax-only retry loop. In the order-exception benchmark, the productive repair
was to forbid comment-only branches and schema-invalid fallback labels, and to
name the exact missing-schema-field bug (`shipping_risk` does not expose
`shipment_status`) directly in benchmark-local guidance.

### 2026-04-02 — codex — best-practice
If an empirical attempt can fail in packet tests or recomposition, persist those
reports directly inside the attempt artifact directory before defining the next
repair lane. Otherwise the project ends up debugging through generic summaries
and manual reruns instead of first-class harness evidence.

### 2026-04-02 — codex — bug-pattern
Benchmark fixtures can parse ISO timestamps into Python `datetime` objects long
before the LLM judge sees them. Any semantic-evaluation prompt path that renders
fixture data through Jinja `tojson` must normalize those values first or the
harness will crash with `Object of type datetime is not JSON serializable`.

### 2026-04-02 — codex — best-practice
When a smoke rerun narrows the blocker set to concrete generation-contract
failures, encode those failures directly in both the prompt and the repair
artifact surface. In this benchmark that meant forbidding unparenthesized
multiline boolean expressions, forbidding pre-class `GeneratedComponent`
annotations on `build_component()`, naming the ORX-101 shipping-only rule
explicitly, and pinning `case_parser.normalized_notes` to lowercasing-only
normalization.

---

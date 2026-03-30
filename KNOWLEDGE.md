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

---

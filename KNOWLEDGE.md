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

---

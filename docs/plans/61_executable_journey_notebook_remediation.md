# Plan #61: Executable Journey Notebook Remediation

**Status:** Complete
**Type:** documentation + planning
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14's notebooks are mostly structured status/design memos. They do
not yet satisfy the intended notebook protocol for executable journey notebooks.

**Target:** Make the AC14 notebook surface truthful and useful by:

1. clearly demoting governance/status notebooks that are not real journeys
2. creating at least one artifact-backed executable journey notebook for a real
   AC14 flow
3. updating the notebook registry and docs so notebook roles are unambiguous

**Why:** The current notebooks are misleading. They look like canonical journey
notebooks, but they are mostly static dict summaries rather than real phase
contracts with explicit artifact flow.

---

## References Reviewed

- `~/.claude/skills/notebook-planning/SKILL.md`
- `~/projects/project-meta/docs/ops/JUPYTER_NOTEBOOK_SHORT_TERM_RULES.md`
- `notebooks/01_ac14_execution_status_journey.ipynb`
- `notebooks/02_ac14_empirical_comparison_gate.ipynb`
- `notebooks/notebook_registry.yaml`
- `docs/AC14_IMPLEMENTATION_STATUS.md`
- `docs/AC14_ROADMAP.md`
- `~/projects/investigations/ac14/2026-04-02-notebook-purpose-audit.md`

---

## Open Questions

### Q1: Should the current status notebook stay?
**Status:** Resolved
**Decision:** Yes, but only as governance/status surface. It should not be
presented as the canonical journey notebook once real journey notebooks exist.

### Q2: What is the first notebook that should become a real executable journey?
**Status:** Resolved
**Decision:** The empirical comparison notebook. It is the current thesis gate
and already has a strong artifact chain to anchor a real journey notebook.

### Q3: Should this plan rewrite every notebook at once?
**Status:** Resolved
**Decision:** No. First make one notebook honestly match the protocol, then
freeze the migration map for the remaining journey notebooks.

---

## Files Affected

- `notebooks/02_ac14_empirical_comparison_gate.ipynb` (modify)
- `notebooks/01_ac14_execution_status_journey.ipynb` (modify or demote)
- `notebooks/notebook_registry.yaml` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)

---

## Plan

### Steps

1. Convert the empirical comparison notebook into a real artifact-backed journey
   notebook with explicit per-phase `input -> output`, acceptance criteria,
   `status`, and `execution_mode`.
2. Make each notebook phase run through explicit live or provisional artifacts
   rather than static dict summaries.
3. Demote or relabel the execution-status notebook as governance-only if it is
   still needed.
4. Update the notebook registry so notebook roles and journey status are
   truthful.
5. Lock the roadmap and implementation-status docs to describe the notebook
   surface accurately.

---

## Required Tests

- notebook JSON parses for every modified notebook
- notebook code cells execute top-to-bottom for every modified notebook
- local `notebook_registry.yaml` parses cleanly

---

## Acceptance Criteria

- [x] The empirical comparison notebook is artifact-backed and runnable
  top-to-bottom in planning/proof terms instead of relying on static dict
  summaries.
- [x] The notebook registry describes notebook roles truthfully.
- [x] The execution-status notebook is either demoted clearly or rewritten so it
  is not mistaken for the canonical journey notebook.
- [x] AC14 docs describe the notebook surface without ambiguity.

---

## Implementation Summary (2026-04-02)

What changed:

- `02_ac14_empirical_comparison_gate.ipynb` is now an artifact-backed notebook that loads the real decision artifact, paired trial reports, failure-pattern diagnostics, and active governance docs
- `01_ac14_execution_status_journey.ipynb` is now explicitly a governance-only status surface rather than a fake canonical journey notebook
- `notebook_registry.yaml` now describes those roles truthfully
- README and the active control docs now stop implying that the status notebook is the canonical journey surface

Verification:

- both notebook JSON files parse cleanly
- both notebooks' code cells execute top-to-bottom
- the local `notebook_registry.yaml` parses cleanly

## Notes

This plan is intentionally notebook-focused, not thesis-focused. The goal is
to make the notebook discipline truthful and useful after the empirical verdict
is locked, not to change the verdict itself.

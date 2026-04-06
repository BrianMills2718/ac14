# Plan #176: Option C — Archive AC14 as Research Artifact and Write Lessons-Learned

**Status:** Planned (conditional — execute only if Brian chooses Option C)
**Priority:** Medium
**Blocked By:** Brian's direction on Theory Forge decision point (Plans #149–#175)
**Date:** 2026-04-05

## Precondition

This plan executes ONLY if Brian explicitly chooses Option C: "declare Theory Forge series
complete, do not continue empirical work in AC14, pivot to a different domain or approach."

If Brian chooses Option A (scale test) or Option B (planning step synthesis), skip this plan
entirely and define the corresponding implementation plan instead.

## Gap

**Current:** If Option C is chosen, AC14 ends as an active development repo. But:
- `CLAUDE.md` still says "NEVER STOP" and references AC14 as a production system
- The thesis and anti-drift doctrine are unresolved against the empirical findings
- No lessons-learned document extracts the findings for future projects
- The repo is not archived or clearly marked as research-complete

**Target:** AC14 is cleanly closed as a research artifact — the empirical findings are
documented, the repo is marked research-complete, reusable components are identified, and
`CLAUDE.md` is updated to reflect the archival state.

## Steps

| Step | What | Status |
|------|------|--------|
| 1 | Write `docs/theory_forge/LESSONS_LEARNED.md` — what AC14 proved, what it didn't, what the next version would need | Not started |
| 2 | Update `CLAUDE.md`: remove "NEVER STOP" mandatory execution contract; replace with "ARCHIVED — research complete" header | Not started |
| 3 | Update `docs/AC14_ANTI_DRIFT_DOCTRINE.md` to reconcile against empirical findings | Not started |
| 4 | Identify reusable components: blueprint/packet system, structured-spec format, programmatic harness, trace_eval adapter | Not started |
| 5 | Tag the final state: `git tag theory-forge-series-complete` | Not started |
| 6 | Update `project-meta/PROJECT_GRAPH.json` status from `active` to `research-archived` | Not started |
| 7 | Record final summary in `agent_memory` | Not started |

## Acceptance Criteria

- [ ] `LESSONS_LEARNED.md` explains what AC14 proved (decomposition is sound in principle), what it didn't (efficiency advantage at ≤40 components), and what the next version would need (planning step that synthesizes formulas; 50+ component test domain)
- [ ] `CLAUDE.md` header clearly marks the repo as research-archived (not active development)
- [ ] PROJECT_GRAPH.json status updated
- [ ] final git tag created
- [ ] no uncommitted changes at close

## Reusable Components (not to discard)

These AC14 artifacts have value beyond AC14 and should be referenced in future work:

| Artifact | Reuse value |
|----------|------------|
| Blueprint + packet format | The structured decomposition schema is general-purpose |
| Structured-spec format | Useful for any spec-driven generation task |
| Front-half-first empirical contract | Testing methodology for staged generation |
| `trace_eval_adapter.py` | AC14-specific but documents the adapter pattern |
| Theory Forge benchmark suite | Reusable benchmark for any future coding agent comparison |

## Failure Modes

| Failure | How to detect | How to fix |
|---------|--------------|-----------|
| Repo left in half-archived state | CLAUDE.md still says active but no new work happens | complete steps 1-6 atomically; do not stop halfway |
| Findings not recorded | future agents repeat the same experiments | check `agent_memory` for the Theory Forge finding before closing |

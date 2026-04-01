# Plan #9: Live LLM Readiness Boundary

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 now has fixture-backed suite-level realistic-input `llm`
breadth, but the project still lacks a clean, explicit boundary between
fixture-backed proof breadth and live/default readiness.

**Target:** AC14 can persist an explicit live-readiness artifact for realistic-input
`llm` acceptance, record `skipped` honestly when live keys are unavailable, and
feed that distinction into the recommendation/status surface.

**Why:** The current `llm` breadth evidence is valuable, but it should not be
mistaken for live production readiness. The next honest step is to make that
boundary explicit and reviewable.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and current proof-expansion rule
- `docs/AC14_ROADMAP.md` - Horizon 1 proof-slice completion and bounded readiness
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current distinction between proof breadth and missing live readiness
- `docs/UNCERTAINTIES.md` - current live-readiness uncertainty
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/08_llm_realistic_input_breadth.md` - just-completed suite-level fixture-backed `llm` breadth lane
- `tests/test_live_llm_codegen.py` - existing optional live LLM smoke test surface
- `ac14/recommendation.py` - current default-generator recommendation logic

---

## Open Questions

### Q1: Should the next lane require live provider keys?
**Status:** Resolved
**Why it matters:** The plan should strengthen honesty without turning missing
keys into a fake failure.
**Resolution:** No. The lane should persist an explicit live-readiness artifact
that can say `ready`, `blocked`, or `skipped`.

### Q2: What should happen when no live provider key is present?
**Status:** Resolved
**Why it matters:** The absence of keys is not the same as a failing live run.
**Resolution:** Persist a `skipped` live-readiness artifact with the reason and
keep recommendation logic conservative.

### Q3: What counts as “done” for the readiness boundary?
**Status:** Resolved
**Why it matters:** The lane should improve decision quality, not just add a
new optional script.
**Resolution:** Done means one persisted live-readiness artifact exists, the
recommendation/status surface distinguishes fixture-backed breadth from live
evidence, and the docs explain the boundary plainly.

---

## Files Affected

- `CLAUDE.md` (modify)
- `ac14/recommendation.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `README.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Add a persisted realistic-input live-readiness artifact for `llm` acceptance
   with explicit `ready`, `blocked`, or `skipped` status.
2. Feed that artifact into the recommendation/status surface so fixture-backed
   breadth and live readiness are never conflated.
3. Expose any required CLI/Make surfaces cleanly.
4. Run full verification and lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_cli.py` | `test_cli_live_llm_readiness_reports_skipped_without_keys` | CLI surface persists an explicit skipped artifact when no live key exists |
| `tests/test_make_targets.py` | `test_make_live_llm_readiness_reports_skipped_without_keys` | Make surface persists an explicit skipped artifact when no live key exists |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `tests/test_live_llm_codegen.py` | Existing live LLM smoke remains the lower-level execution proof surface |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [x] AC14 can persist one realistic-input live-readiness artifact for `llm` acceptance.
- [x] Missing live keys produce an explicit `skipped` artifact rather than an implicit no-op.
- [x] Recommendation/status surfaces distinguish fixture-backed breadth from live evidence.
- [x] CLI and Make expose the readiness surface without manual glue.
- [x] Full local verification passes and the docs match the lane.

---

## Notes

- Keep this lane honest: fixture-backed suite breadth is useful, but it is not
  the same as live default readiness.
- The goal is not to force live calls in every environment. The goal is to make
  the boundary explicit and reviewable.
- AC14 now also requires `AC14_ENABLE_LIVE_LLM_READINESS=1` before attempting a
  live-readiness run so ambient credentials cannot silently turn a skipped lane
  into a live one.

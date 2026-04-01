# Plan #23: Front-Half Retry Integration

**Status:** Planned
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 now has an explicit retry-chain artifact for blocked freeze
decisions, but the realistic-input front-half acceptance artifact still stops
at the initial freeze decision.

**Target:** AC14 should let front-half acceptance optionally run one explicit
retry chain when the initial freeze is blocked and surface both the initial and
retried freeze outcomes.

**Why:** The next high-value front-half strengthening step is to show that
realistic-input acceptance can include one bounded remediation-aware retry
instead of ending at the first blocked freeze.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and current proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 front-half strengthening direction
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current front-half/manual-retry status
- `docs/plans/22_freeze_retry_chain.md` - just-completed retry-chain lane
- `ac14/front_half_acceptance.py` - current realistic-input front-half artifact
- `ac14/freeze_retry.py` - retry-chain artifact contract
- `ac14/freeze_decision.py` - freeze artifact contract

---

## Open Questions

### Q1: Should retry integration be automatic or opt-in?
**Status:** Planned
**Why it matters:** The first integration should strengthen front-half evidence
without silently changing the default story.
**Default:** Opt-in through an explicit flag.

### Q2: What should the front-half artifact expose after retry?
**Status:** Planned
**Why it matters:** Retry integration should add evidence, not replace the
original blocked freeze record.
**Default:** Keep the initial freeze decision path and add an optional retry
artifact path plus retry-approved summary fields.

---

## Files Affected

- `ac14/front_half_acceptance.py` (modify)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_front_half_acceptance.py` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Pre-make retry integration as one explicit optional extension to front-half acceptance.
2. Thread the retry-chain artifact into front-half acceptance without replacing the initial freeze artifact.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_report_supports_retry_freeze` | Front-half acceptance can persist one retry artifact and expose both freeze outcomes |
| `tests/test_cli.py` | `test_cli_front_half_acceptance_supports_retry_freeze` | CLI front-half acceptance supports retry integration |
| `tests/test_make_targets.py` | `test_make_front_half_acceptance_supports_retry_freeze` | Make front-half acceptance supports retry integration |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [ ] AC14 can optionally run one explicit retry chain during realistic-input front-half acceptance.
- [ ] The front-half artifact preserves both the initial freeze decision and the retry artifact path.
- [ ] The lane stays explicit and does not silently replace the initial blocked freeze evidence.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

This lane is about bounded retry-aware front-half evidence, not broad automatic healing.

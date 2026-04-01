# Plan #25: Messy-Input Retry Proof

**Status:** Planned
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 now has retry-aware front-half acceptance for both
single-example and suite breadth on the shipped structured inputs, but it has
not yet shown that the same retry-aware flow stays explicit on the messier CSV
input slice.

**Target:** AC14 should prove one retry-aware front-half lane on the existing
messy CSV asset.

**Why:** The next honest proof step is to show that retry-aware front-half
workflows still behave explicitly on messier inputs, not just on the cleaner
shipped JSON assets.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and current proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 2 front-half strengthening direction
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current messy-input/front-half retry status
- `docs/plans/18_messy_input_front_half_proof.md` - first messy-input front-half lane
- `docs/plans/24_front_half_retry_suite_breadth.md` - just-completed retry breadth lane
- `ac14/front_half_acceptance.py` - current retry-aware front-half artifact

---

## Open Questions

### Q1: Should the messy-input retry proof be a new artifact type?
**Status:** Planned
**Why it matters:** The next lane should prove retry-aware behavior without multiplying artifact types unnecessarily.
**Default:** No. Reuse the existing front-half acceptance artifact.

### Q2: What should count as success?
**Status:** Planned
**Why it matters:** The messy-input retry lane is about explicitness and boundedness, not necessarily about passing freeze.
**Default:** Success is preserving explicit discovery, initial freeze, retry artifact, and final review on the messy CSV asset.

---

## Files Affected

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

1. Reuse the existing messy CSV asset and enable retry-aware front-half acceptance on it.
2. Verify that discovery, initial freeze, retry artifact, and final review all stay explicit.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_front_half_acceptance.py` | `test_build_front_half_acceptance_report_supports_retry_freeze_on_messy_input` | Retry-aware front-half acceptance stays explicit on the messy CSV asset |
| `tests/test_cli.py` | `test_cli_front_half_acceptance_supports_retry_freeze_on_messy_input` | CLI retry-aware front-half acceptance works on the messy CSV asset |
| `tests/test_make_targets.py` | `test_make_front_half_acceptance_supports_retry_freeze_on_messy_input` | Make retry-aware front-half acceptance works on the messy CSV asset |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [ ] AC14 can run retry-aware front-half acceptance on the messy CSV artifact.
- [ ] The resulting artifact preserves discovery, initial freeze, retry, and final review paths explicitly.
- [ ] The lane stays explicit and does not claim success just because a retry happened.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

This lane is about retry-aware explicitness on messy input, not about broadening the runtime model.

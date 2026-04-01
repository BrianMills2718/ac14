# Plan #10: Packet Sufficiency Evidence

**Status:** In Progress
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 compiles packets, codegen contexts, packet-local tests, and
recomposition proof, but it still lacks one explicit artifact that states
whether each packet is informationally sufficient for bounded local generation.

**Target:** AC14 can persist a packet-sufficiency artifact that records, per
packet, whether the local contract, schemas, neighboring context, fixtures, and
packet-local tests are present without requiring whole-blueprint context.

**Why:** The core thesis is not just that packets exist. It is that packets are
enough to let a bounded local coder work without hidden global context.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and updated proof-expansion focus
- `docs/AC14_ROADMAP.md` - Horizon 1 emphasis after the live-readiness boundary
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current gap between packet existence and packet-sufficiency evidence
- `docs/UNCERTAINTIES.md` - current uncertainty state after closing the live-readiness boundary
- `docs/TODO.md` - active control surface that should track this lane
- `docs/AC14_NEXT_24_HOURS.md` - tactical summary that should mirror this lane
- `docs/plans/09_live_llm_readiness_boundary.md` - just-completed readiness-boundary lane
- `ac14/packets.py` - packet compilation surface
- `ac14/codegen_context.py` - bounded local codegen context projection
- `ac14/packet_tests.py` - packet-local test materialization
- `ac14/generated_codegen.py` - current local generation consumer of packet/codegen context

---

## Open Questions

### Q1: What should count as packet sufficiency in the first artifact?
**Status:** Resolved
**Why it matters:** The lane should avoid grand claims it cannot actually verify.
**Resolution:** The first artifact should verify structural sufficiency only:
local component contract, referenced schemas, neighboring port/binding context,
fixtures, and packet-local tests are present and projected into the bounded
context.

### Q2: Should the first lane claim semantic sufficiency?
**Status:** Resolved
**Why it matters:** Overclaiming would make the artifact misleading.
**Resolution:** No. The first lane should only claim structural/local-contract
sufficiency and should leave broader semantic sufficiency to later evidence.

### Q3: Should packet sufficiency live at one-blueprint or suite level first?
**Status:** Resolved
**Why it matters:** The lane should land a useful artifact quickly.
**Resolution:** Start with one-blueprint and make the artifact shape reusable.
Suite aggregation can come later if the single-blueprint artifact is sound.

---

## Files Affected

- `CLAUDE.md` (modify)
- `ac14/packets.py` (modify or read-only dependency)
- `ac14/codegen_context.py` (modify or read-only dependency)
- `ac14/packet_tests.py` (modify or read-only dependency)
- `ac14/__main__.py` (modify)
- `Makefile` (modify)
- `tests/test_cli.py` (modify)
- `tests/test_make_targets.py` (modify)
- `tests/test_packets.py` (modify or add)
- `tests/test_codegen_context.py` (modify or add)
- `README.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `KNOWLEDGE.md` (modify)

---

## Plan

### Steps

1. Define a persisted packet-sufficiency artifact that records one packet's
   structural local-context completeness.
2. Add a builder and CLI/Make surface for one blueprint.
3. Feed the artifact into status/docs so packet existence and packet
   sufficiency are never conflated.
4. Run full verification and lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_packets.py` or `tests/test_codegen_context.py` | `test_build_packet_sufficiency_report_flags_complete_packet_context` | The artifact records structural sufficiency for a shipped packet |
| `tests/test_cli.py` | `test_cli_packet_sufficiency_runs_end_to_end` | CLI surface persists the packet-sufficiency artifact |
| `tests/test_make_targets.py` | `test_make_packet_sufficiency_runs_end_to_end` | Make surface persists the packet-sufficiency artifact |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [ ] AC14 can persist one packet-sufficiency artifact for a shipped blueprint.
- [ ] The artifact records structural local-context sufficiency without claiming more than it proves.
- [ ] CLI and Make expose the packet-sufficiency surface cleanly.
- [ ] Recommendation/status docs stop conflating packet existence with packet sufficiency.
- [ ] Full local verification passes and the docs match the lane.

---

## Notes

- Keep this lane narrow: the goal is to make packet sufficiency explicit, not to
  solve all semantic sufficiency questions.
- Do not smuggle whole-blueprint context back into the artifact just to make it
  look complete.

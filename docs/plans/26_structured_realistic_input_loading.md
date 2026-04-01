# Plan #26: Structured Realistic-Input Loading

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** 27, 28

---

## Gap

**Current:** Front-half discovery already supports `json`, `jsonl`, `csv`, and
`yaml`, but full-system realistic-input acceptance still assumes a top-level
JSON list and only auto-discovers `.json` input files.

**Target:** AC14 should share structured realistic-input loading between
discovery and acceptance, fail loud on unsupported forms, and broaden default
realistic-input discovery beyond `.json` without changing the semantic
acceptance contract.

**Why:** Messy-input full-system proof cannot be honest while the final gate
silently excludes the same structured formats the front half already supports.

---

## References Reviewed

- `CLAUDE.md` - active continuation rules and current proof-expansion chain
- `docs/AC14_ROADMAP.md` - Horizon 2 front-half strengthening and Horizon 1 realistic-input proof
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current realistic-input loading gap
- `docs/plans/25_messy_input_retry_proof.md` - just-completed messy-input retry prerequisite
- `ac14/discovery.py` - current structured-input detection/loading helpers
- `ac14/acceptance.py` - current JSON-only realistic-input loading and `.json` discovery

---

## Open Questions

### Q1: Should acceptance import private discovery helpers directly?
**Status:** Resolved
**Why it matters:** Sharing format support should not deepen coupling to private discovery internals.
**Decision:** No. Extract a shared structured-input module and make both surfaces consume it.

### Q2: Which formats should count as realistic-input records?
**Status:** Resolved
**Why it matters:** The final gate should broaden honestly without pretending every format is executable input.
**Decision:** Support structured record-bearing formats already present in discovery: `json`, `jsonl`, `csv`, and `yaml`. Keep plain text unsupported and fail loud.

---

## Files Affected

- `ac14/structured_inputs.py` (create)
- `ac14/discovery.py` (modify)
- `ac14/acceptance.py` (modify)
- `tests/test_structured_inputs.py` (create)
- `tests/test_acceptance.py` (modify)
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

1. Extract shared structured-input format detection and loading from discovery into a dedicated module.
2. Make realistic-input acceptance load one record from the shared structured formats and make default input discovery consider non-JSON structured files.
3. Run targeted verification, then full verification, then lock the docs.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_structured_inputs.py` | `test_load_structured_input_records_supports_supported_formats` | Shared structured-input loading supports `json`, `jsonl`, `csv`, and `yaml` record streams |
| `tests/test_structured_inputs.py` | `test_load_structured_input_records_fails_loud_on_text` | Shared loading rejects unsupported text realistic inputs |
| `tests/test_acceptance.py` | `test_discover_realistic_input_path_supports_structured_non_json_inputs` | Acceptance can auto-discover a structured realistic-input artifact even when only non-JSON structured files exist |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression verification |
| `python -m mypy ac14 tests` | Keep the lane type-clean |
| `python -m ruff check ac14 tests` | Keep the lane lint-clean |

---

## Acceptance Criteria

- [x] Discovery and acceptance share one structured realistic-input loading surface.
- [x] Realistic-input acceptance can load record-bearing `json`, `jsonl`, `csv`, and `yaml` inputs and still fail loud on unsupported text inputs.
- [x] Default realistic-input discovery no longer hardcodes `.json` as the only acceptable artifact type.
- [x] Full local verification passes and the docs match the lane.

## Verification

- Targeted structured-input loading verification passed:
  - `python -m pytest -q tests/test_structured_inputs.py tests/test_acceptance.py::test_discover_realistic_input_path_supports_structured_non_json_inputs`
  - `python -m mypy ac14/structured_inputs.py ac14/discovery.py ac14/acceptance.py tests/test_structured_inputs.py tests/test_acceptance.py`
  - `python -m ruff check ac14/structured_inputs.py ac14/discovery.py ac14/acceptance.py tests/test_structured_inputs.py tests/test_acceptance.py`

## Outcome

AC14 now shares one structured-input loading surface between discovery and
realistic-input acceptance, can load record-bearing `json`, `jsonl`, `csv`,
and `yaml` inputs at the final gate, and can auto-discover a structured
realistic-input artifact even when a shipped example has no `.json` input file.

---

## Notes

This lane should broaden structured input support without broadening the
semantic-acceptance contract beyond one-record execution.

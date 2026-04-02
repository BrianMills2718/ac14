# Plan #64: Second-Gate Benchmark Bundle

**Status:** Complete
**Type:** benchmark design + implementation
**Priority:** Critical
**Blocked By:** 63
**Blocks:** 65

---

## Gap

**Current:** The runtime-first contract is frozen, but the repo still needs a
verified second-gate benchmark bundle and aligned docs/tests.

**Target:** Add and verify one new reviewable benchmark bundle with 12+ components,
stronger fan-in/fan-out, categorical-only final outputs, and realistic runtime
cases that can stress context management more than the first gate.

**Why:** The second empirical gate should differ from the first in both
measurement quality and benchmark pressure.

---

## References Reviewed

- `CLAUDE.md`
- `docs/AC14_ROADMAP.md`
- `docs/AC14_IMPLEMENTATION_STATUS.md`
- `docs/plans/38_empirical_comparison_gate.md`
- `docs/plans/62_inconclusive_comparison_diagnosis.md`
- `docs/plans/63_runtime_first_comparison_contract.md`
- `benchmarks/order_exception_resolution/benchmark.yaml`
- `benchmarks/order_exception_resolution/requirements.md`
- `benchmarks/order_exception_resolution/blueprint/`
- `ac14/empirical_comparison.py`

---

## Open Questions

### Q1: Should the second benchmark switch domains completely?
**Status:** Resolved
**Decision:** Yes. Use a new domain, but keep the benchmark shaped around the
same empirical question: does decomposition outperform monolithic generation
once the system is large enough to stress context management?

### Q2: What should make this benchmark harder?
**Status:** Resolved
**Decision:** Use 13 components, multiple join layers, state accumulation, and
categorical-only final outputs with four runtime cases covering immediate,
manual, compliance-blocked, and no-action paths.

### Q3: Should the bundle be benchmark-only or also fixture-rich?
**Status:** Resolved
**Decision:** Fixture-rich. The benchmark must be a valid AC14 blueprint with
packet-local fixture coverage, not just a runtime-only dataset.

---

## Files Affected

- `benchmarks/resource_scaling/benchmark.yaml` (create)
- `benchmarks/resource_scaling/requirements.md` (create)
- `benchmarks/resource_scaling/blueprint/metadata.yaml` (create)
- `benchmarks/resource_scaling/blueprint/schemas.yaml` (create)
- `benchmarks/resource_scaling/blueprint/components.yaml` (create)
- `benchmarks/resource_scaling/blueprint/architecture.yaml` (create)
- `benchmarks/resource_scaling/blueprint/validation.yaml` (create)
- `benchmarks/resource_scaling/blueprint/fixtures.yaml` (create)
- `benchmarks/resource_scaling/input/runtime_cases.json` (create)
- `benchmarks/resource_scaling/input/expected_runtime_outputs.json` (create)
- `ac14/empirical_comparison.py` (modify — benchmark-local guidance for the new bundle)
- `tests/test_empirical_comparison.py` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `README.md` (modify)

---

## Plan

### Steps

1. Finalize the `resource_scaling_v1` benchmark contract and runtime cases.
2. Write the full benchmark bundle and source artifacts.
3. Add benchmark-local repair guidance and a benchmark-load regression test.
4. Update the active docs so Plan #65 can run without chat history.
5. Commit the verified bundle as its own checkpoint.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_empirical_comparison.py` | `test_resource_scaling_benchmark_loads` | The new benchmark bundle loads, compiles packets, and exposes 12+ components with aligned runtime-case ids |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q tests/test_empirical_comparison.py` | New benchmark regression plus existing empirical tests |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type safety |
| `python -m ruff check ac14 tests` | Lint and import hygiene |

---

## Acceptance Criteria

- [x] The new benchmark bundle exists under `benchmarks/resource_scaling/`.
- [x] The bundle loads through `load_benchmark_bundle()` and compiles packets cleanly.
- [x] The benchmark has 13 components, multiple join layers, and four runtime cases.
- [x] Final outputs are categorical-only and exactly comparable.
- [x] Verification passes and the active docs point to Plan #65 next.

---

## Implementation Summary (2026-04-02)

`resource_scaling_v1` is now the canonical second-gate benchmark bundle. It
uses 13 components, two final output ports, four runtime cases, and no dynamic
output fields. The bundle is intentionally categorical-only so the second gate
measures decomposition quality under runtime-first evaluation instead of
free-form semantic drift.

Remaining work in this plan is verification and doc/test alignment before Plan
#65 spends the smoke budget.

## Verification (2026-04-02)

- `python -m pytest -q tests/test_empirical_comparison.py` -> `27 passed`
- `python -m pytest -q` -> `247 passed`
- `python -m mypy ac14 tests` -> success
- `python -m ruff check ac14 tests` -> success

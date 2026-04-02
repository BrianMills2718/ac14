# Plan #63: Runtime-First Comparison Contract

**Status:** In Progress
**Type:** evaluation + benchmark design
**Priority:** Critical
**Blocked By:** None
**Blocks:** 37

---

## Gap

**Current:** The first monolithic-vs-AC14 benchmark completed and returned
`inconclusive`. Plan #62 showed that packet-level failures dominated the
verdict even when final runtime outputs were often correct.

**Target:** Redesign the comparison contract so final runtime output correctness
is the primary success gate, while packet-level tests remain explicit secondary
diagnostic evidence.

**Why:** The project needs the next empirical gate to measure the thesis more
cleanly: does decomposition produce systems with more correct final outputs,
not merely fewer intermediate packet mismatches.

---

## Open Questions

### Q1: Should packet tests remain part of the comparison?
**Status:** Resolved
**Decision:** Yes, but as explicit diagnostic evidence rather than the primary
trial-success gate.

### Q2: Should the first benchmark be discarded?
**Status:** Resolved
**Decision:** No. Keep `order_exception_resolution` as the first completed data
point. However, the diagnosis showed runtime outputs passed for both conditions
in virtually all attempts. Rerunning the same benchmark with runtime-primary
criterion will likely still return `inconclusive` because neither condition
fails at the runtime level. The cleaner next move is a harder benchmark
alongside the runtime-primary criterion fix, so that both improvements land
together and the next gate is maximally informative.

### Q5: Should this plan design a new harder benchmark alongside the criterion fix?
**Status:** Resolved
**Decision:** Yes. Plan #63 owns both the runtime-primary harness change AND
a new benchmark with stronger context pressure (more components, deeper
fan-in/fan-out, categorical-dominant expected outputs). These land together so
the second gate differs from the first in both measurement quality and stress.

### Q3: Should the decision rule itself be abandoned?
**Status:** Resolved
**Decision:** No. Keep the same disciplined frozen-rule approach, but rewrite
the success definition around runtime correctness first.

---

## Files Affected

- `docs/plans/63_runtime_first_comparison_contract.md` (modify)
- `benchmarks/<new_benchmark_name>/` (create — new benchmark with 12–15
  components, stronger fan-in/fan-out, categorical-dominant expected outputs)
- `ac14/empirical_comparison.py` (modify — runtime-primary success criterion)
- `ac14/generated_evidence.py` (modify — decouple packet test pass/fail from
  trial success, add `run_runtime_output_eval`)
- `prompts/evaluate_runtime_output.yaml` (create — LLM eval for final system
  output only, not intermediate component outputs)
- `tests/test_empirical_comparison.py` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/TODO.md` (modify)
- `docs/plans/CLAUDE.md` (modify)

---

## Plan

### Steps

1. Design new benchmark system (12–15 components, strong fan-in/fan-out, state
   accumulation, categorical-dominant expected outputs).
2. Write full benchmark bundle: `requirements.md`, `blueprint/`, `input/`.
3. Implement runtime-primary harness changes:
   a. `evaluate_runtime_output.yaml` prompt for final output LLM eval
   b. `run_runtime_output_eval` in `generated_evidence.py`
   c. Updated trial success criterion in `empirical_comparison.py`
4. Run one bounded smoke trial to verify the new criterion works.
5. Run the full five-trial gate to `.ac14_out/full_trials_gate_2/`.
6. Record the new verdict and compare to the first gate.

---

## Required Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_empirical_comparison.py` | `test_trial_success_does_not_require_packet_tests` | Trial success uses runtime outputs as primary gate |
| `tests/test_empirical_comparison.py` | `test_packet_tests_logged_as_diagnostic` | Packet test results still appear in trial report |

Existing tests:
- `python -m pytest -q`
- `python -m mypy ac14 tests`
- `python -m ruff check ac14 tests`

---

## Acceptance Criteria

- [ ] New benchmark with 12–15 components and categorical-dominant expected
  outputs is complete and reviewable.
- [ ] The trial success criterion uses runtime output correctness as the
  primary gate.
- [ ] Packet test results are logged but do not determine trial pass/fail.
- [ ] One bounded smoke trial confirms the new criterion works.
- [ ] The full five-trial gate runs to `.ac14_out/full_trials_gate_2/`.
- [ ] The new verdict is recorded and the active docs are updated.
- [ ] Full local verification passes.

---

## Notes

This plan has two simultaneous improvements over the first gate: a harder
benchmark (more context pressure, so decomposition advantage can emerge if it
exists) and a cleaner success criterion (runtime-primary, so the verdict is not
swamped by intermediate packet-eval noise). If the second gate is also
inconclusive, the diagnosis will be more informative because the measurement
surface is cleaner.

# Plan #39: Monolithic Vs AC14 Comparison Execution

**Status:** Blocked
**Type:** evaluation
**Priority:** Critical
**Blocked By:** 51
**Blocks:** 37

---

## Gap

**Current:** AC14 now has a frozen empirical comparison contract in Plan #38,
but no benchmark assets, paired-trial runner, or persisted comparison result.

**Target:** AC14 should run one explicit comparison experiment on the frozen
`order_exception_resolution` target, persist paired monolithic and AC14 trial
artifacts, score them with the same harness and semantic review, and produce a
decision artifact that says `ac14_wins`, `monolithic_wins`, or `inconclusive`.

This plan measures a bounded back-half comparison over a fixed decomposition.
It does not by itself measure the full end-to-end front-half-plus-back-half
thesis.

**Why:** Until this experiment runs, AC14 still lacks the main evidence needed
to justify the project's stronger thesis claim.

---

## References Reviewed

- `CLAUDE.md` - continuation rules and thesis-first execution discipline
- `docs/AC14_ROADMAP.md` - empirical gate priority
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current risks and lack of baseline comparison
- `docs/AC14_ANTI_DRIFT_DOCTRINE.md` - hierarchy of truth
- `docs/plans/38_empirical_comparison_gate.md` - frozen comparison contract
- `notebooks/02_ac14_empirical_comparison_gate.ipynb` - target system, protocol, and decision rule

---

## Open Questions

### Q1: Where should the benchmark assets live?
**Status:** Resolved
**Why it matters:** The comparison target should not be confused with a shipped example or disappear into ad hoc temp files.
**Decision:** Create a dedicated `benchmarks/order_exception_resolution/` tree for requirements, inputs, expected evaluation harness, and trial outputs.

### Q2: How should paired trials be recorded?
**Status:** Resolved
**Why it matters:** The result must be reviewable trial-by-trial rather than only as one final summary.
**Decision:** Persist one artifact directory per paired trial under the
caller-specified experiment output root, with separate `monolithic/` and
`ac14/` subdirectories plus a paired summary JSON.

### Q3: What should count as a failed trial?
**Status:** Resolved
**Why it matters:** The primary outcome is trial-level success rate, so failure semantics must be explicit before execution starts.
**Decision:** A trial fails if the evaluation harness does not pass, if semantic review is below `acceptable`, or if manual code edits are required.

### Q4: Should this plan build a new custom semantic-scoring framework?
**Status:** Resolved
**Why it matters:** AC14 already has shared evaluation infrastructure in the ecosystem, and another bespoke scoring layer would increase machinery without helping the thesis.
**Decision:** No. Keep the benchmark asset bundle and paired-trial orchestration in AC14, but use shared infrastructure such as `llm_client` and `prompt_eval` where practical for semantic review and comparison aggregation.

---

## Files Affected

- `benchmarks/order_exception_resolution/` (create)
- `ac14/empirical_comparison.py` (create)
- `tests/test_empirical_comparison.py` (create)
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

1. Finalize and validate the benchmark asset bundle for
   `order_exception_resolution`, including requirements, input artifacts,
   allowed dependency surface, runtime inputs, expected outputs, and the frozen
   six-file benchmark blueprint.
2. Implement the bounded monolithic condition so one whole-task generation
   attempt can run end to end and persist attempts, time, cost, outputs, and
   pass/fail reasons without manual edits.
3. Implement the bounded AC14 condition so one packetized generation attempt
   can run end to end and persist packet tests, recomposition proof,
   realistic-input execution, attempts, time, cost, outputs, and pass/fail
   reasons without manual edits.
4. Add scoring and decision logic that applies the primary outcome and
   secondary metrics from Plan #38 and persists a final experiment-decision
   artifact plus per-trial summaries.
5. After Plan #40 unblocks the lane, run 5 fresh paired trials, then lock the
   docs and status surface around the result.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_empirical_comparison.py` | `test_build_benchmark_bundle_order_exception_resolution` | Benchmark assets load and validate |
| `tests/test_empirical_comparison.py` | `test_run_paired_trial_persists_monolithic_and_ac14_artifacts` | Paired-trial runner records both conditions explicitly |
| `tests/test_empirical_comparison.py` | `test_build_experiment_decision_artifact_applies_plan_38_rule` | Decision artifact follows the frozen success rule |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Keep the experiment lane type-clean |
| `python -m ruff check ac14 tests` | Keep the experiment lane lint-clean |

---

## Acceptance Criteria

- [x] The benchmark asset bundle exists under `benchmarks/order_exception_resolution/`.
- [x] AC14 can run paired monolithic and AC14 trials under the frozen fairness rules.
- [x] The project persists one final experiment-decision artifact with `ac14_wins`, `monolithic_wins`, or `inconclusive`.
- [ ] Five fresh paired trials complete and are reviewable artifact-by-artifact.
- [ ] Full local verification passes and the docs match the result.

---

## Notes

This plan is the first direct thesis test. It is intentionally higher priority
than blocked propagation plans unless the experiment itself shows that one of
those blocked lanes is required for a fair comparison.

Current live-execution note:

- the benchmark bundle, paired-trial runner, and decision artifact now exist
- bounded live smoke trials have been executed
- Plans #40 and #41 are complete
- the full five-trial gate should not proceed until Plan #40 either produces a
  smoke verdict of `ready_for_full_trials` or documents a stable blocker
- the latest bounded smoke rerun remains `blocked_on_harness`
- The active repair chain is now Plan #50 followed by Plan #51 for the next smoke rerun

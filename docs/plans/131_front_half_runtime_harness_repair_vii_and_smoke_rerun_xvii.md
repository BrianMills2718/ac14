# Plan #131: Front-Half Runtime-Harness Repair VII And Smoke Rerun XVII

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 130
**Blocks:** None

---

## Gap

**Current:** smoke_16 still says `blocked_on_harness`. Plan #123's fix (load
`refined_draft_bundle_dir` for retry-approved artifacts) cleared the self-loop
topology issue from smoke_15, but smoke_16 attempt_2 reveals a different
topology where two non-source components both emit the spec output schema
(`scaling_decision_entry`), and the inference cascade reaches the
`non_source_schema_name_candidates` tier with 2 candidates and raises.

**Concrete blocker (smoke_16 attempt_2 topology):**
```
EventNormalizer → PolicyEvaluator    → ComplianceAndExecution → DecisionRecorder
                                 ↘→ ComplianceAndExecution
PolicyEvaluator.recommendation_out: scaling_decision_entry → ComplianceAndExecution.recommendation_in
ComplianceAndExecution.final_decision_out: scaling_decision_entry → DecisionRecorder.decision_in
DecisionRecorder.store_out: scaling_decision_store  (leaf, different schema)
```

Both `PolicyEvaluator.recommendation_out` and `ComplianceAndExecution.final_decision_out`
have schema `scaling_decision_entry`. Neither is a leaf (both are consumed downstream).
The `_collect_leaf_non_source_output_candidates` tier returns nothing for this schema.
The `non_source_schema_name_candidates` tier finds both, raises "multiple non-source
schema-name candidates."

**Root cause:** The inference cascade has no "terminal" tier — a tier that
prefers the candidate consumed by a component that does NOT itself produce the
same schema:
- `PolicyEvaluator.recommendation_out` feeds `ComplianceAndExecution`, which
  produces `scaling_decision_entry` → NOT terminal (intermediate step)
- `ComplianceAndExecution.final_decision_out` feeds `DecisionRecorder`, which
  does NOT produce `scaling_decision_entry` → TERMINAL ✓

**Target:** Add a `terminal_non_source_schema_name_candidates` tier between
the leaf tier and the general non-source tier. A "terminal" candidate for
schema X is a non-source, non-leaf port with schema X that is consumed only by
components that do NOT produce any output port with schema X.

**Why:** The terminal heuristic is semantically correct: the last computation
of an intermediate schema before it flows to a recorder or store updater is the
contract-relevant final output.

---

## Acceptance Criteria

- [x] smoke_16 says `blocked_on_harness` (blocker now documented)
- [ ] `terminal_non_source_schema_name_candidates` tier added to `_select_structured_spec_output_candidate`
- [ ] Targeted test proves the fix: topology with two non-source candidates where one is terminal
- [ ] `python -m mypy ac14 tests` passes
- [ ] `python -m ruff check ac14 tests` passes
- [ ] `python -m pytest -q` passes
- [ ] One fresh smoke artifact (smoke_17) exists after the repair
- [ ] The next branch is explicit from the new artifact

---

## Execution Contract

1. add `terminal_non_source_schema_name_candidates` tier to inference cascade
   in `_infer_final_output_bindings` and `_select_structured_spec_output_candidate`
2. add targeted test proving topology fix: two non-source candidates, one terminal
3. verify with mypy, ruff, full test suite
4. commit in worktree, merge to master
5. rerun smoke_17 immediately after merge
6. branch from the persisted rerun verdict without pause

---

## Files Affected

- `ac14/front_half_first_empirical.py` — `_infer_final_output_bindings`,
  `_select_structured_spec_output_candidate`, new helper computation
- `tests/test_front_half_first_empirical.py` — targeted test for terminal tier

## References Reviewed

- `.ac14_out/front_half_first_smoke_16/smoke_readiness_report.json` — verdict
  `blocked_on_harness`, attempt_2 failure: "multiple non-source schema-name candidates"
- `.ac14_out/front_half_first_smoke_16/trial_1/ac14/attempt_2/front_half/draft_bundle/` — actual topology
- `ac14/front_half_first_empirical.py` lines ~1099–1220 — inference cascade

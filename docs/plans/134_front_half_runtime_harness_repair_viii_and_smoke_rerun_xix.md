# Plan #134: Front-Half Runtime-Harness Repair VIII And Smoke Rerun XIX

**Status:** Complete
**Type:** implementation + evaluation
**Priority:** Critical
**Blocked By:** 133
**Blocks:** None

---

## Gap

**Current:** smoke_18 produced `blocked_on_harness`. The dominant blocker (from
Plan #133) is that 3 components each have an output port named
`scaling_decision_entry`. The `non_source_exact_name_candidates` tier finds all
3 and raises because none is a leaf and there is no terminal tier for exact-name
candidates.

**Target:** Add `terminal_non_source_exact_name_candidates` tier to the
inference cascade, verify with targeted tests, and spend one fresh smoke rerun
immediately.

**Why:** The terminal tier logic (first applied to schema-name in Plan #131)
resolves multi-component chains where an intermediate component re-emits an
output with the same name before passing it forward. The same logic applies to
exact-name matching.

---

## Acceptance Criteria

- [x] `terminal_non_source_exact_name_candidates` tier added in `front_half_first_empirical.py`
- [x] Unit test proves 3-component exact-name chain selects the terminal component
- [x] All existing tests still pass (303 passed, 1 skipped)
- [x] Changes merged to master
- [ ] One fresh smoke artifact (smoke_19) exists after the repair
- [ ] The next branch is explicit from the new artifact

---

## Execution Contract

1. Add `consuming_produces_same_exact_name` set to `_infer_final_output_bindings`
   - For each binding, if `binding.to_component` has any output port with name
     == `structured_output.name`, add `(binding.from_component, binding.from_port)` to the set
2. Add `terminal_non_source_exact_name_candidates` list:
   - Start with `non_source_exact_name_candidates`
   - Filter out those in `consuming_produces_same_exact_name`
3. Add `terminal_non_source_exact_name_candidates` to `_select_structured_spec_output_candidate`
   call signature and function signature
4. Insert the terminal tier check between `leaf_non_source_exact_name` and
   `non_source_exact_name` in `_select_structured_spec_output_candidate`
5. Add unit test for 3-component exact-name chain
6. Run `python3 -m pytest tests/ -x -q` — all pass
7. Commit in worktree, merge to master
8. Run smoke_19 immediately

---

## Files Affected

- `ac14/front_half_first_empirical.py` — add terminal_non_source_exact_name tier
- `tests/test_front_half_first_empirical.py` — add 3-component exact-name unit test

---

## References Reviewed

- `docs/plans/133_front_half_runtime_harness_boundary_viii.md` — blocker diagnosis
- `ac14/front_half_first_empirical.py:1140-1234` — existing candidate computation
- `ac14/front_half_first_empirical.py:1303-1436` — `_select_structured_spec_output_candidate` cascade
- smoke_18 readiness report: all 3 AC14 attempts `generation` failures, exact-name tier raises with 3 candidates

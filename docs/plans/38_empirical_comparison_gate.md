# Plan #38: Empirical Comparison Gate

**Status:** Complete
**Type:** evaluation
**Priority:** Critical
**Blocked By:** None
**Blocks:** 39

---

## Gap

**Current:** AC14 has strong internal proof machinery, but no persisted
comparison experiment showing whether decomposition materially beats a credible
monolithic baseline on a system complex enough for the thesis to matter.

**Target:** AC14 should have one explicit empirical comparison plan and notebook
that define the target system, baseline protocol, AC14 condition, metrics,
rubric, repetitions, cost/time accounting, and success/failure rule clearly
enough that the experiment can be run without redefining the question midstream.

**Why:** Without this gate, AC14 can keep generating coherent propagation and
proof-hygiene lanes while the main project claim remains unmeasured.

---

## References Reviewed

- `CLAUDE.md` - current continuation rules and propagation bias risk
- `docs/AC14_ROADMAP.md` - current horizons and missing empirical gate
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current state, risks, and over-optimistic completion framing
- `docs/AC14_ANTI_DRIFT_DOCTRINE.md` - hierarchy of truth and thesis boundary
- `docs/AC14_NEXT_24_HOURS.md` - current tactical lane
- `docs/TODO.md` - current control-surface drift and stale active-lane state
- `docs/plans/37_directory_divergence_front_half_proof.md` - paused propagation lane
- `notebooks/01_ac14_execution_status_journey.ipynb` - current AC14-native notebook surface

---

## Open Questions

### Q1: What target system is hard enough to stress monolithic generation without becoming unreviewable?
**Status:** Resolved
**Why it matters:** If the comparison target is too small, the experiment will
not test the thesis; if it is too large, the first gate will become muddy and
hard to diagnose.
**Decision:** Use one `order_exception_resolution` system with 9 components,
multi-source fan-in, one optional manual-override input, one state-owning sink,
mixed CSV/JSON inputs, `pandas` as a real dependency, and explicit
cross-component SLA/business rules.

### Q2: What counts as a fair monolithic baseline?
**Status:** Resolved
**Why it matters:** AC14 should not compare itself against a deliberately
crippled prompt or workflow. The baseline needs normal whole-task generation
with reasonable repo context and standard engineering iteration.
**Decision:** The monolithic condition gets the same requirements, input
artifacts, allowed dependencies, and evaluation harness as AC14, uses the same
model family/version when practical, and is allowed one initial generation plus
up to 2 bounded repair loops from failing tests/evaluator findings.

### Q3: What should the decision rule optimize for?
**Status:** Resolved
**Why it matters:** AC14 might win on recomposition reliability, maintainability,
or semantic quality without winning on speed or cost. The comparison needs an
explicit primary outcome rather than vague “better overall.”
**Decision:** The primary outcome is trial-level success rate across 5 fresh
trials, where a success requires the evaluation harness to pass and the final
requirements-aware semantic review to return `acceptable` or better. Secondary
metrics are repair loops used, wall-clock time, total cost, and semantic-review
strength. AC14 wins if it beats the monolithic condition by at least 2/5 trials
or ties on success while matching semantic quality and using fewer repair loops.
If the success gap is at most 1/5 and the secondary metrics are mixed, the
result is inconclusive.

### Q4: Should Plan #37 remain blocked unless it directly supports the experiment?
**Status:** Resolved
**Why it matters:** Without a gate, the plan sequence will keep expanding
front-half propagation proof instead of answering the thesis question.
**Decision:** Yes. Plan #37 stays blocked unless the comparison design shows it
is required for experiment validity.

---

## Files Affected

- `CLAUDE.md` (modify)
- `README.md` (modify)
- `docs/AC14_ROADMAP.md` (modify)
- `docs/AC14_IMPLEMENTATION_STATUS.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/TODO.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `docs/plans/CLAUDE.md` (modify)
- `docs/plans/37_directory_divergence_front_half_proof.md` (modify)
- `docs/plans/38_empirical_comparison_gate.md` (create)
- `notebooks/01_ac14_execution_status_journey.ipynb` (modify)
- `notebooks/02_ac14_empirical_comparison_gate.ipynb` (create)
- `notebooks/notebook_registry.yaml` (modify)

---

## Plan

### Steps

1. Rewrite the active control surface so Plan #38 is the explicit next gate and
   Plan #37 is blocked behind it.
2. Add one AC14-native empirical comparison notebook that freezes the target,
   fairness constraints, metrics, repetitions, and decision rule.
3. Tighten the roadmap, implementation status, uncertainties, and top-level
   execution rules so propagation micro-lanes do not outrun the empirical gate.
4. Validate the notebook/registry artifacts and lock the docs.

---

## Required Tests

### Validation

| Artifact | Validation | What It Verifies |
|----------|------------|------------------|
| `notebooks/01_ac14_execution_status_journey.ipynb` | JSON parse | Updated execution-status notebook stays valid |
| `notebooks/02_ac14_empirical_comparison_gate.ipynb` | JSON parse | New empirical gate notebook stays valid |
| `notebooks/notebook_registry.yaml` | YAML parse | Registry remains valid after adding the new journey |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `python - <<'PY' ... json.load(...) ... PY` | Ensure new notebook JSON parses |
| `python - <<'PY' ... yaml.safe_load(...) ... PY` | Ensure notebook registry YAML parses |

---

## Acceptance Criteria

- [x] The control surface was pivoted away from another default propagation-proof lane.
- [x] Plan #37 is no longer the default next step.
- [x] AC14 has one explicit empirical comparison notebook with a frozen experiment contract.
- [x] The roadmap and implementation-status docs state clearly that the next strategic gate is empirical comparison against a credible monolithic baseline.
- [x] Notebook JSON and registry YAML parse cleanly.

---

## Notes

This plan is intentionally a gate, not the experiment execution itself. The
deliverable here is a truthful, reviewable experiment contract that prevents
the next plan from defaulting to another propagation proof by inertia.

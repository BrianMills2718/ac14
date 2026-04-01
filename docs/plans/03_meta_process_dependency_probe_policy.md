# Plan #3: Meta-Process Dependency Probe Policy

**Status:** Complete
**Type:** implementation
**Priority:** High
**Blocked By:** None
**Blocks:** None

---

## Gap

**Current:** AC14 always treats blocked dependency probes as freeze blockers, but
that policy is only implied by AC14 code and docs. It is not yet expressed in
the shared `meta-process` vocabulary that other projects can also use.

**Target:** `meta-process` defines a shared `dependency_probe_policy`
configuration vocabulary, and AC14 consumes that policy from `meta-process.yaml`
so dependency-probe behavior is configurable without forking a private AC14-only
policy model.

**Why:** This issue is bigger than AC14. Multiple projects will need consistent
project-process policy for how dependency evidence affects planning and gating.

---

## References Reviewed

- `CLAUDE.md` - active execution rules and proof-expansion rule
- `docs/AC14_ROADMAP.md` - roadmap context for stronger front-half evidence
- `docs/AC14_IMPLEMENTATION_STATUS.md` - current front-half status
- `docs/AC14_META_PROCESS_ADOPTION_PLAN.md` - rationale for broader meta-process adoption
- `docs/plans/02_dependency_probe_integration.md` - completed prerequisite lane
- `meta-process.yaml` - current AC14 shared process config
- `ac14/draft_authoring.py` - current readiness blocker implementation
- `project-meta/meta-process/README.md` - shared framework overview
- `project-meta/meta-process/GETTING_STARTED.md` - shared configuration guidance
- `project-meta/meta-process/templates/meta-process.yaml.example` - canonical config template

---

## Open Questions

### Q1: Where should the shared dependency-probe policy live?
**Status:** Resolved
**Why it matters:** If the policy vocabulary lives only in AC14 docs, it cannot
be reused cleanly by other projects.
**Resolution:** The shared vocabulary lives in `meta-process.yaml` under the
`planning` section.

### Q2: Which modes should exist first?
**Status:** Resolved
**Why it matters:** Too many modes now would add ambiguity before there is real
evidence for them.
**Resolution:** Start with `strict`, `warn`, and `ignore`. Keep `strict` as the
default.

### Q3: What should AC14 do when the config file is missing?
**Status:** Resolved
**Why it matters:** AC14 must stay fail-loud in behavior without requiring every
consumer to finish all meta-process setup first.
**Resolution:** Missing config falls back to `strict`.

---

## Files Affected

- `ac14/meta_process_policy.py` (create)
- `ac14/draft_authoring.py` (modify)
- `ac14/meta-process.yaml` (modify)
- `tests/test_draft_authoring.py` (modify)
- `tests/test_meta_process_policy.py` (create)
- `docs/TODO.md` (modify)
- `docs/AC14_NEXT_24_HOURS.md` (modify)
- `docs/UNCERTAINTIES.md` (modify)
- `README.md` (modify)
- `KNOWLEDGE.md` (modify)
- `project-meta/meta-process/README.md` (modify)
- `project-meta/meta-process/GETTING_STARTED.md` (modify)
- `project-meta/meta-process/templates/meta-process.yaml.example` (modify)
- `project-meta/meta-process/templates/meta-process.yaml.docs-only` (modify)

---

## Plan

### Steps

1. Add the shared `dependency_probe_policy` vocabulary to meta-process docs and templates.
2. Add a small AC14 config reader for that policy with `strict` default behavior.
3. Make draft authoring/readiness apply `strict`, `warn`, or `ignore` to blocked dependency probes.
4. Add deterministic tests for policy loading and policy-specific readiness findings.
5. Run verification, update docs, and commit both repos cleanly.

---

## Required Tests

### New Tests

| Test File | Test Function | What It Verifies |
|-----------|---------------|------------------|
| `tests/test_meta_process_policy.py` | `test_load_dependency_probe_policy_defaults_to_strict` | Missing config falls back to strict |
| `tests/test_draft_authoring.py` | `test_materialize_draft_blueprint_bundle_warns_on_dependency_probe_results_when_policy_warn` | Warn policy downgrades blocked dependency findings |

### Existing Tests

| Test Pattern | Why |
|--------------|-----|
| `tests/test_draft_authoring.py` | Readiness integration stays coherent |
| `python -m pytest -q` | Full regression check |
| `python -m mypy ac14 tests` | Type-check verification |
| `python -m ruff check ac14 tests` | Lint verification |

---

## Acceptance Criteria

- [x] Meta-process defines `dependency_probe_policy` as shared planning vocabulary.
- [x] AC14 consumes the policy from `meta-process.yaml`.
- [x] `strict`, `warn`, and `ignore` behave distinctly for blocked dependency probes.
- [x] Verification passes and docs reflect the new shared-policy model.

---

## Notes

- This lane is about shared process policy, not automatic dependency remediation.
- The shared vocabulary belongs in meta-process; the artifact-level meaning still
  belongs in AC14.

# AC14 Meta-Process Adoption Plan

Last updated: 2026-03-31
Status: Proposed migration plan

## Purpose

This document defines how AC14 should adopt `meta-process` governance patterns
without letting the process layer obscure AC14's own product thesis.

The goal is not to make AC14 "be meta-process."

The goal is to use the strongest `meta-process` disciplines to reduce the exact
failure modes that have hurt prior AC attempts:

1. stale or weak plans
2. implementation outrunning planning artifacts
3. uncertainty getting lost across sessions
4. notebooks becoming decorative instead of operational
5. local execution lanes silently redefining the vision

## Decision

AC14 should adopt a **broad but deliberate** subset of `meta-process`.

That means:

1. adopt the planning and governance philosophy seriously
2. refactor AC14 docs to match it where useful
3. keep AC14 terminology authoritative where AC14 already has stronger concepts
4. defer the parts of `meta-process` that solve problems AC14 does not yet have

## Non-Goals

This migration does **not** mean:

1. AC14 runtime or blueprint design should depend on `meta-process`
2. AC14 should rename its proof slice or validation model to fit older
   `acceptance_gate` terminology
3. AC14 should add multi-agent coordination machinery before it actually needs it
4. Claude-only hook enforcement should become the single source of discipline

## Canonical Sources After Adoption

Interpret AC14 governance in this order:

1. [AC14_ANTI_DRIFT_DOCTRINE.md](/home/brian/projects/ac14/docs/AC14_ANTI_DRIFT_DOCTRINE.md)
2. [AC14_ROADMAP.md](/home/brian/projects/ac14/docs/AC14_ROADMAP.md)
3. `docs/plans/CLAUDE.md`
4. active numbered plan in `docs/plans/`
5. [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md)
6. [TODO.md](/home/brian/projects/ac14/docs/TODO.md)
7. notebook registry and active journey notebook

The rule is:

- doctrine and roadmap define what AC14 is trying to become
- numbered plans define current implementation work
- status docs and notebooks keep implementation honest

## What To Adopt

### 1. Numbered Plan Workflow

Adopt:

- numbered plan files under `docs/plans/`
- a plan index in `docs/plans/CLAUDE.md`
- required `References Reviewed`
- required `Files Affected`
- required `Required Tests`
- plan status discipline

Why:

- this is the biggest upgrade available for implementation traceability
- it gives AC14 a stronger bridge between roadmap and execution

### 2. Question-Driven Planning

Adopt:

- a required questions section in each significant plan
- explicit investigation-before-implementation discipline

Why:

- AC14's front half depends on investigated context, not assumptions

### 3. Dedicated Uncertainty Tracking

Adopt:

- `docs/UNCERTAINTIES.md`
- status model such as `open`, `investigating`, `resolved`, `deferred`, `blocked`

Why:

- `TODO.md` is currently overloaded
- uncertainty is one of the main ways drift returns

### 4. Executable Journey Notebook Discipline

Adopt:

- explicit `status` and `execution_mode` semantics in notebook registry and notebooks
- explicit provisional artifacts when phases are not yet live
- notebook as operational journey rendering, not just narrative

Why:

- AC14 already wants this and should do it more rigorously

### 5. Light Commit Discipline

Adopt:

- commit prefix convention such as `[Plan #N]` and `[Trivial]`
- optional commit-msg hook enforcement

Why:

- low-cost traceability
- makes plan linkage durable in git history

## What To Adapt Rather Than Copy

### 1. Acceptance-Gate Philosophy

Adopt:

- the idea that completion should be tied to real verification and visible
  criteria, not vague implementation

Adapt:

- keep AC14's own proof slice / validation / freeze terminology
- do not force AC14 into `acceptance_gates/*.yaml` right now

Why:

- AC14 already has stronger, more relevant language for its current system

### 2. Linkage / Traceability

Adopt:

- stronger mapping between plans, notebooks, code, tests, and docs

Adapt:

- use AC14's existing docs and notebook registry rather than importing an older
  gate-linkage file structure wholesale

## What To Defer

### 1. Worktree Claims And Messaging

Defer until AC14 actually needs concurrent multi-agent edit coordination.

### 2. Full Meta-Process Installer Footprint

Defer:

- blind `install.sh --full`
- blind `install.sh --minimal`

Why:

- AC14 already has an established doc and Make surface
- installer output would create overlap before clarity

### 3. Claude-Specific Hook Gating As Primary Enforcement

Defer as a hard dependency.

Use only as optional reinforcement after the doc/process refactor is clear.

## Doc Refactor Plan

### Keep

Keep as authoritative:

- [AC14_ANTI_DRIFT_DOCTRINE.md](/home/brian/projects/ac14/docs/AC14_ANTI_DRIFT_DOCTRINE.md)
- [AC14_ROADMAP.md](/home/brian/projects/ac14/docs/AC14_ROADMAP.md)
- [AC14_IMPLEMENTATION_STATUS.md](/home/brian/projects/ac14/docs/AC14_IMPLEMENTATION_STATUS.md)
- notebook registry and active notebook
- [README.md](/home/brian/projects/ac14/README.md)

### Add

Add:

- `docs/plans/CLAUDE.md`
- `docs/plans/TEMPLATE.md`
- `docs/plans/01_<current_lane>.md`
- `docs/UNCERTAINTIES.md`
- optionally `meta-process.yaml` as a light config surface

### Reduce

Reduce the scope of:

- [TODO.md](/home/brian/projects/ac14/docs/TODO.md)
- [AC14_NEXT_24_HOURS.md](/home/brian/projects/ac14/docs/AC14_NEXT_24_HOURS.md)

After migration:

- `TODO.md` should be an active checklist and current-state ledger
- `AC14_NEXT_24_HOURS.md` should be a tactical lane summary, not the main plan system

## Migration Sequence

### Phase 1: Planning Surfaces

Deliverables:

- `docs/plans/CLAUDE.md`
- `docs/plans/TEMPLATE.md`
- first active numbered plan

Acceptance criteria:

- AC14 has a real numbered plan workflow
- the current implementation lane is represented as a numbered plan
- roadmap, active plan, and TODO are no longer competing authorities

### Phase 2: Uncertainty Split

Deliverables:

- `docs/UNCERTAINTIES.md`
- uncertainty content moved out of `TODO.md`

Acceptance criteria:

- uncertainties are tracked separately from the control checklist
- open versus resolved questions are visible

### Phase 3: Notebook Tightening

Deliverables:

- updated notebook registry
- updated active notebook with stronger phase semantics

Acceptance criteria:

- phases explicitly state status and execution mode
- provisional artifacts are explicit where needed

### Phase 4: Light Enforcement

Deliverables:

- commit-prefix convention
- optional commit-msg hook
- optional `meta-process.yaml`

Acceptance criteria:

- commit history becomes traceable to plans
- enforcement is lightweight and does not add process confusion

### Phase 5: Control-Surface Cleanup

Deliverables:

- slimmer `TODO.md`
- slimmer `AC14_NEXT_24_HOURS.md`
- updated README links if needed

Acceptance criteria:

- there is one obvious place for long-term direction
- one obvious place for active plans
- one obvious place for uncertainties
- one obvious place for implementation reality

## Risks

### 1. Process Duplication

If AC14 adds plans and uncertainties without simplifying existing docs, it will
create more clutter instead of less.

Mitigation:

- every addition should be paired with a reduction in another doc's scope

### 2. Terminology Collision

If `meta-process` terms are copied blindly, AC14 may lose clarity.

Mitigation:

- keep AC14 doctrine and roadmap authoritative
- adapt terms where AC14 already has better language

### 3. Hook-Centric Enforcement

If too much discipline lives only in Claude hooks, the workflow becomes uneven
across agent surfaces.

Mitigation:

- prefer docs, plan structure, and repo-visible enforcement first

## Recommendation

Proceed with this migration.

The next step should be:

1. create `docs/plans/`
2. create `docs/UNCERTAINTIES.md`
3. convert the current dependency execution-probing lane into `Plan #1`
4. then clean up `TODO.md` and `AC14_NEXT_24_HOURS.md` so the process surface
   becomes simpler, not larger

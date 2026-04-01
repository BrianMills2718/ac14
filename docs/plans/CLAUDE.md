# AC14 Implementation Plans

Status: Canonical numbered-plan index
Last updated: 2026-03-31

Use numbered plans for implementation work that changes AC14's code or active
control surfaces. The roadmap defines direction; numbered plans define the
current executable lane.

## Active Plans

| # | Name | Priority | Status | Blocks |
|---|------|----------|--------|--------|
| 1 | [Dependency Execution Probing](01_dependency_execution_probing.md) | High | Complete | - |
| 2 | [Dependency Probe Integration](02_dependency_probe_integration.md) | High | Complete | - |

## Status Key

| Status | Meaning |
|--------|---------|
| Planned | Ready for implementation |
| In Progress | Actively being implemented |
| Blocked | Waiting on a real unresolved dependency or decision |
| Complete | Implemented and verified |

## Working Rules

1. Every significant implementation lane should have a numbered plan.
2. Each plan must include `References Reviewed`, `Open Questions`,
   `Files Affected`, and `Required Tests`.
3. The numbered plan is the authoritative implementation contract for the lane.
4. `TODO.md` is the active checklist, not the long-form plan.
5. `AC14_NEXT_24_HOURS.md` is the tactical summary, not the source of detailed
   implementation requirements.

## Creating A New Plan

1. Copy `TEMPLATE.md` to `NN_name.md`.
2. Fill in the gap, questions, references, files, steps, tests, and criteria.
3. Add the plan to this index.
4. Link active tactical docs back to the new plan if it becomes the current lane.

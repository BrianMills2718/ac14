# AC14

AC14 is the clean-slate implementation of the blueprint and decomposition work
defined in `~/projects/ac12/docs/AC14_BLUEPRINT_SPEC.md`.

## Thesis

Large software generation fails when one model has to hold too much of the
system in context. AC14 addresses that by compiling a specification into a
frozen blueprint with explicit components, typed ports, and recomposition
rules, then projecting that blueprint into bounded local packets.

## Anti-Drift Hierarchy

Read [docs/AC14_ANTI_DRIFT_DOCTRINE.md](./docs/AC14_ANTI_DRIFT_DOCTRINE.md)
before broad architectural changes or strategic claims.

The short version:

1. AC14 is a general coding agent through decomposition.
2. The current repo is only a narrow proof slice of that vision.
3. Current examples and heuristics are implementation artifacts, not product scope.
4. Validation is not deterministic-only; it must combine strong programmatic
   checks with strong LLM-based semantic checks.
5. Pre-freeze data inspection, schema discovery, library/doc/repo use, and
   realistic end-to-end acceptance are part of the long-term system even when
   the current proof slice does not implement them yet.

## First Proof Slice

The first slice must prove:

1. a six-file blueprint bundle can be loaded into a canonical model
2. B1 validation can fail loud on structural and graph errors
3. packets can be compiled for each component without hidden global context

Do not broaden scope before that works.

## Execution Discipline

- Continue through planned milestones without pausing for permission.
- If there is uncertainty, document it and choose the smallest
  thesis-preserving option.
- Commit every verified increment.
- Do not add fallbacks to hide design mistakes.

## Active Overnight Mode

When AC14 has an active next-24-hours plan, execute it aggressively:

- do not stop at a passing test and ask what to do next
- do not treat documented uncertainties as blockers
- log the uncertainty, make the smallest thesis-preserving choice, and continue
- keep pushing until the active implementation lane is exhausted
- commit every verified increment so rollback stays cheap
- keep the active TODO ledger current and use it as the running control surface
- when one phase passes, immediately advance the TODO state and start the next
- the default assumption is CONTINUE, not WAIT
- define explicit phase acceptance criteria before starting the phase
- if a phase uncovers a new uncertainty, record it in the plan/TODO and keep moving
- if one path is blocked, switch to the next thesis-preserving subphase instead of waiting
- do not leave the repo in a half-landed state at the end of a work block; verify and commit

The default failure mode here is waiting too early. Avoid that.

## Active Proof Expansion Rule

The active lane after proof breadth expansion is discovery-context expansion.

- extend discovery beyond local input files into persisted project-document context
- keep the first bridge local and reviewable instead of jumping straight to opaque
  external retrieval
- treat README, CLAUDE, and project docs as first-class pre-freeze context
- keep broader GitHub/web/documentation retrieval logged explicitly without
  blocking the smaller thesis-preserving lane
- keep the TODO ledger and active 24-hour plan synchronized with the real lane

## Continuation Rule

This repo should continue through the active 24-hour lane without pausing for
permission.

- define the phases before implementation
- update TODO state as each phase lands
- log uncertainties and continue unless they contradict the frozen proof slice
- commit every verified checkpoint
- do not leave partial work uncommitted at the end of a work block

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
- If there is uncertainty, document the lane-specific part in the active plan
  and the durable/project-level part in `docs/UNCERTAINTIES.md`, then choose
  the smallest thesis-preserving option.
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
- for the active 24-hour lane, define every phase explicitly and keep the plan
  unambiguous enough that another agent could continue without rereading chat
- when one numbered plan completes, immediately define the next numbered plan
  before continuing implementation
- the expected behavior is to keep running through the active 24-hour sequence
  until every planned lane is complete or a real contradiction appears
- for the active 24-hour chain, keep at least one next numbered plan explicit
  at all times so continuation does not depend on chat memory

The default failure mode here is waiting too early. Avoid that.

Treat this as a strong mandatory rule:

- the default behavior is CONTINUE until the active numbered plan is complete
- do not pause after one passing subphase just because the repo is currently green
- do not let unlogged uncertainty become an excuse to stop
- if a concern can be written down and bounded, write it down and keep moving
- only stop for a real contradiction to the thesis, a real blocker, or a user redirect

Treat the active numbered plan as a mandatory execution contract:

- do not stop because a phase revealed uncertainty that can be logged
- do not stop because one subphase passed; continue until the whole active plan is verified and committed
- do not leave the TODO ledger stale while continuing implementation
- if a lane spans the full work block, keep iterating until every phase is either complete or blocked by a real contradiction to the thesis

Treat waiting for further permission before the active plan is complete as a
process failure. The required behavior is:

- define the next phases clearly
- execute them in order
- log uncertainties without stopping
- keep going until the active plan is finished or a real contradiction appears
- keep the 24-hour sequence explicit in numbered plans, TODO, and
  `AC14_NEXT_24_HOURS.md` rather than only in conversation

## Active Proof Expansion Rule

The current focus after landing one honest messy-input front-half proof lane is
proving retry-aware front-half behavior on the messy CSV slice.

- keep fixture-backed breadth and live readiness as separate evidence categories
- do not let fixture-backed `llm` breadth silently upgrade the default-generator
  or live-readiness story
- keep live readiness operator-explicit; require
  `AC14_ENABLE_LIVE_LLM_READINESS=1` before attempting a live readiness run
- persist explicit live-readiness artifacts that can say `ready`, `blocked`, or
  `skipped`
- keep realistic-input final acceptance tied to actual blueprint execution
  rather than a disconnected review workflow
- keep the final verdict as combined evidence: hard programmatic artifacts plus
  LLM semantic review
- preserve the AC14-native notebook and implementation-status doc as the
  canonical story surface while implementation continues
- keep uncertainties logged, but do not treat them as blockers unless they
  contradict the frozen proof slice
- keep the TODO ledger and active 24-hour plan synchronized with the real lane
- keep dependency remediation explicit, reviewable, and artifact-backed
- do not let remediation collapse into silent broad environment mutation
- keep dependency remediation wired back into the front-half chain rather than
  leaving it as an isolated side command
- keep the first blocked-freeze retry step plan-first; prefer refined planning
  artifacts over in-place bundle mutation
- once refinement exists, keep the next retry step explicit too; prefer a
  persisted retry-chain artifact over hidden multi-command orchestration
- once the retry chain exists, integrate it into front-half evidence carefully;
  preserve the initial blocked freeze record instead of replacing it
- once single-example retry-aware front-half acceptance exists, broaden it to
  suite breadth carefully; preserve per-example retry provenance instead of
  collapsing everything into one aggregate claim
- once retry-aware suite breadth exists, prove the same retry-aware path on the
  messy CSV slice before making bigger generality claims

## Continuation Rule

This repo should continue through the active 24-hour lane without pausing for
permission.

- define the phases before implementation
- update TODO state as each phase lands
- log uncertainties and continue unless they contradict the frozen proof slice
- commit every verified checkpoint
- do not leave partial work uncommitted at the end of a work block

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

## Execution Discipline — MANDATORY, NO EXCEPTIONS

**NEVER STOP. This is the primary execution rule.**

For the current front-half-first chain, this means: do not stop at smoke_7, do
not stop at a clean test run, and do not stop at one completed repair. The
required behavior is to spend the active rerun, read the verdict, update the
control docs, and continue immediately into the already-defined next numbered
plan for that verdict.

- The default behavior is CONTINUE until every active plan in the 24-hour chain
  is complete or a genuine thesis contradiction appears. There is no other valid
  stopping condition.
- Do not stop after one passing test. Do not stop after one completed plan. Do not
  stop to ask what to do next. The next numbered plan is the answer.
- If there is uncertainty, document it in `docs/UNCERTAINTIES.md` and keep moving.
  Documented uncertainty is not a blocker. Only an irresolvable thesis contradiction is.
- Commit every verified increment. Uncommitted work is invisible and unrecoverable.
- Do not add fallbacks to hide design mistakes.
- Do not pause between plans. When one plan completes and passes full verification,
  immediately advance the TODO state and start the next plan.
- The 24-hour chain must stay explicit in numbered plans and `AC14_NEXT_24_HOURS.md`
  at all times. Another agent must be able to continue without reading chat history.
- Stopping early is a process failure. The only acceptable behavior is to run until
  the active 24-hour chain is exhausted or a real contradiction appears.

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
- if the current sequence is mostly propagation-proof work, stop and insert an
  empirical gate before defining another similar micro-lane when the main
  thesis is still unmeasured

The default failure mode here is waiting too early. Avoid that.

Treat this as a strong mandatory rule:

- the default behavior is CONTINUE until the active numbered plan is complete
- do not pause after one passing subphase just because the repo is currently green
- do not let unlogged uncertainty become an excuse to stop
- if a concern can be written down and bounded, write it down and keep moving
- only stop for a real contradiction to the thesis, a real blocker, or a user redirect
- do not confuse steady plan completion with thesis validation; when the main
  empirical question is still open, the next plan should usually sharpen that
  question rather than extend a propagation chain

Treat the active numbered plan as a mandatory execution contract:

- do not stop because a phase revealed uncertainty that can be logged
- do not stop because one subphase passed; continue until the whole active plan is verified and committed
- do not leave the TODO ledger stale while continuing implementation
- if a lane spans the full work block, keep iterating until every phase is either complete or blocked by a real contradiction to the thesis

For the active empirical-comparison lane, this rule is especially strict:

- do not define another propagation-proof numbered plan before the comparison
  experiment is executed or explicitly blocked by a thesis-level contradiction
- keep the next 24-hour chain expressed as concrete implementation phases with
  explicit success criteria, not as vague continuation language
- when the active lane is a thesis gate, prefer finishing the gate over
  broadening adjacent proof machinery
- if the active thesis gate uncovers a real blocker such as smoke instability
  or provider contamination, freeze a blocker-clearing numbered plan and
  execute that plan before resuming the parent gate
- do not describe a back-half comparison over a fixed decomposition as if it
  were already the full end-to-end thesis test
- keep the active empirical chain explicit as:
  1. targeted repair plan
  2. bounded smoke rerun
  3. full five-trial gate only if smoke says `ready_for_full_trials`
  4. verdict interpretation only after the five-trial gate exists
- do not mark a repair lane complete just because code landed; the empirical
  gate must still earn the next phase through a persisted smoke artifact
- if the smoke artifact still says `blocked_on_harness`, freeze a narrower
  blocker-clearing plan immediately and do not spend the five-trial budget
- when the smoke artifact is stale or the control docs lag the latest run,
  update the docs before continuing so another agent can resume without chat
  history
- if a full-trial empirical run is interrupted and leaves partial or zero-byte
  artifacts, freeze a restart-integrity plan immediately; preserve incomplete
  trial evidence, make the runner resume-safe, and only then continue the gate
- after a decisive harder-benchmark loss, allow at most one bounded post-loss
  benchmark-local repair before freezing a repair-boundary plan; if that repair
  still produces `0` hard-harness successes in the fresh smoke artifact, do not
  continue local tuning by default
- after the repair boundary is frozen, the next default chain must be:
  1. cross-benchmark taxonomy
  2. one reusable repair lane
  3. one bounded smoke rerun
  4. either a full rerun or a strategic pivot based on the smoke artifact
- if the bounded smoke rerun still yields `0` AC14 hard-harness successes, the
  full rerun stays closed and the next default move is a front-half-first
  empirical contract plus one bounded implementation lane toward that contract
- once the first bounded structured-spec input contract lands, the next default
  chain is:
  1. structured-spec front-half acceptance
  2. structured-spec benchmark bundle
  3. front-half-first smoke contract and runner
  4. one bounded front-half-first smoke execution
  5. either a full front-half-first trial gate or a blocker diagnosis directly
     from the smoke verdict
- for the active front-half-first empirical chain, keep the contract explicit:
  - AC14 must first produce an approved structured-spec front-half artifact
  - runtime hard-harness success remains the end-to-end success surface
  - monolithic stays runtime-only; do not invent a fake monolithic front-half
    artifact for symmetry theater
  - do not spend the full-trial budget until the new smoke artifact exists and
    says `ready_for_full_trials`
  - do not treat \"Plan #88 exists\" as permission to stop; if the smoke rerun
    opens the gate and the runner surface is still missing, implement that
    runner immediately as part of the next active plan and continue into the
    full gate without waiting for new human direction
  - the current mandatory chain is:
    1. Plan #86 runner contract and implementation -> complete
    2. Plan #87 bounded smoke execution -> complete with `blocked_on_front_half`
    3. Plan #89 blocker diagnosis -> complete
    4. Plan #90 bounded contract-and-observability repair -> complete
    5. Plan #91 smoke rerun -> complete with `blocked_on_front_half`
    6. Plan #92 second blocker boundary -> complete
    7. Plan #93 async-safe freeze review repair -> complete
    8. Plan #94 smoke rerun II -> complete with `blocked_on_infrastructure`
    9. Plan #95 front-half infrastructure boundary -> complete
    10. Plan #96 smoke rerun III with explicit `MODEL=gpt-5-mini` -> complete with `blocked_on_infrastructure`
    11. Plan #99 hidden-default-model infrastructure boundary -> complete
    12. Plan #106 model-propagation repair plus smoke rerun IV -> complete with `blocked_on_front_half`
    13. Plan #97 front-half freeze-fidelity boundary -> complete
    14. Plan #104 freeze-fidelity repair plus smoke rerun V -> active
    15. Plan #88 full trial gate if the rerun verdict is `ready_for_full_trials`
    16. Plan #100 verdict interpretation and next horizon immediately after Plan #88
    17. Plan #98 runtime-harness boundary if the rerun verdict is `blocked_on_harness`
    18. Plan #105 runtime-harness repair plus smoke rerun IV immediately after Plan #98
    19. Plan #107 external-provider boundary II if the rerun verdict is `blocked_on_infrastructure`
    20. Plan #108 front-half freeze-fidelity boundary II if the rerun verdict is still `blocked_on_front_half`
    21. Plan #109 freeze-fidelity repair II plus smoke rerun VI immediately after Plan #108
  - for the current 24-hour branch tree, every unlocked verdict branch must
    already have its next numbered plan defined in docs before the rerun is
    spent; \"we will decide after the artifact exists\" is not good enough
  - once Plan #104 starts, the required behavior is:
    1. repair the shared freeze-fidelity blocker class from smoke_6
    2. rerun the smoke gate with explicit `MODEL=gpt-5-mini`
    3. update docs from the persisted verdict immediately
    4. continue into Plan #88, #98, #107, or #108 with no permission pause
    5. continue into Plan #100, #105, or #109 the moment that branch unlocks
    6. leave every new uncertainty in `docs/UNCERTAINTIES.md` rather than
       treating uncertainty as a stop condition
- after Plan #60 and Plan #43, the first empirical comparison is now complete under `.ac14_out/full_trials_gate_1/` with verdict `inconclusive`
- the active empirical chain is now:
  1. Plan #44 verdict interpretation and doc lock
  2. Plan #62 inconclusive-comparison diagnosis
  3. freeze the next empirical direction before resuming unrelated blocked lanes
  4. keep notebook remediation explicit as Plan #61 instead of leaving the notebook surface misleading
- maximize observability and testing protocol inside the empirical lane:
  - every empirical attempt must persist `packet_test_report.json` and `recomposition_report.json`
  - packet and recomposition failures must include bounded field-level mismatch details whenever the harness can derive them
  - empirical retry guidance must consume those structured diffs rather than collapsing them into generic failure labels
  - monolithic validation failures must persist the invalid module source when the harness has it; do not lose failed code behind exception-only summaries
  - empirical attempts must run inside a real `llm_client` experiment context and feature profile instead of relying on warning-only guardrails
  - if a semantic-eval prompt path crashes on fixture data types such as `datetime`, fix the harness before tuning more benchmark logic

Treat waiting for further permission before the active plan is complete as a
process failure. The required behavior is:

- define the next phases clearly
- execute them in order
- log uncertainties without stopping
- keep going until the active plan is finished or a real contradiction appears
- keep the 24-hour sequence explicit in numbered plans, TODO, and
  `AC14_NEXT_24_HOURS.md` rather than only in conversation
- for the active chain, do not stop after one green checkpoint if the next
  numbered plan is already clear and thesis-preserving; update the plan docs
  and continue immediately
- keep the next 24-hour chain explicit as a sequence of numbered plans with
  unambiguous success criteria; do not rely on chat memory for continuation
- for the current empirical chain specifically, the repo must always make these
  phases explicit: Plan #65 smoke gate, Plan #67 blocker diagnosis, Plans #68-#69
  blocker-clearing harness repairs, Plan #70 smoke rerun, then either Plan #66
  full gate or Plan #71 blocker diagnosis based on the persisted rerun verdict;
  do not collapse those into one oversized plan

## Active Proof Expansion Rule

The current focus after landing one honest messy-input front-half proof lane is
to carry that realism all the way into the full-system acceptance surface.

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
- treat notebooks as executable journey contracts with explicit per-phase
  `input -> output`, acceptance criteria, `status`, and `execution_mode`; do
  not use notebooks as retrospective status decks or static dict dumps
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
- once retry-aware messy-input front-half proof exists, remove the JSON-only
  assumption from realistic-input final acceptance before making stronger
  messy-input claims
- after structured realistic-input loading is shared, prove messy-input
  full-system acceptance in `reference` and `deterministic` modes
- only after the non-LLM messy-input final gate is explicit should AC14 add one
  bounded messy-input `llm` comparison lane
- once one bounded messy-input `llm` lane exists, make realistic-input
  selection explicit instead of relying on hidden file-extension precedence
- keep front-half and final-gate realistic-input defaults aligned; do not let
  one surface stay JSON-only while the other supports structured candidates
- once explicit realistic-input selection exists, make suite/profile behavior
  explicit too; preserve the clean default proof path while allowing reviewable
  alternate profiles such as messy-input variants

## Continuation Rule

This repo should continue through the active 24-hour lane without pausing for
permission.

- define the phases before implementation
- update TODO state as each phase lands
- log uncertainties and continue unless they contradict the frozen proof slice
- commit every verified checkpoint
- do not leave partial work uncommitted at the end of a work block

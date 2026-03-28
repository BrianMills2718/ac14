# AC14

AC14 is the clean-slate implementation of the blueprint and decomposition work
defined in `~/projects/ac12/docs/AC14_BLUEPRINT_SPEC.md`.

## Thesis

Large software generation fails when one model has to hold too much of the
system in context. AC14 addresses that by compiling a specification into a
frozen blueprint with explicit components, typed ports, and recomposition
rules, then projecting that blueprint into bounded local packets.

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

The default failure mode here is waiting too early. Avoid that.

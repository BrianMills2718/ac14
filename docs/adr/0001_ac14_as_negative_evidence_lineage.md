# ADR 0001: Treat AC14 As Negative-Evidence Lineage For Portfolio Use

Wiki home: http://localhost:8088/index.php/Project_Wiki

## Status

Accepted.

## Context

AC14 contains a large amount of implementation, planning, and benchmark
history. A reviewer who sees only the artifact count could mistake the repo for
the current successful autocoder lead. The tracked evidence does not support
that interpretation.

The repo's own status documents record that the harder back-half gate favored
the monolithic baseline, and the Theory Forge series conclusion records no
meaningful `ac14_wins` verdict across the tested regime. The restart manifest
then explains why AC15 starts clean with per-component validator-healer loops.

## Decision

For portfolio and wiki use, AC14 will be presented as supporting lineage and
negative evidence:

- AC12 explains the blueprint-compiler proof;
- AC14 records empirical failure modes and front-half exploration;
- AC15 is the current measured autocoder artifact.

AC14 pages must not imply that AC14 proved the decomposition thesis or beat the
monolithic baseline.

## Consequences

Benefits:

- prevents overclaiming;
- makes the AC lineage easier to understand;
- preserves the value of negative results;
- clarifies why AC15 exists.

Costs:

- AC14 becomes a supporting artifact, not a lead portfolio artifact;
- some historical docs still use active execution language and need careful
  interpretation;
- the wiki needs an AC lineage page to avoid sending reviewers through 175+
  plan files.

## Controls

- [PROJECT.md](../../PROJECT.md) states the safe portfolio framing.
- [docs/VALIDATION.md](../VALIDATION.md) defines licensed and unlicensed claims.
- [docs/CONCERNS.md](../CONCERNS.md) tracks interpretation risks.
- [RESTART_MANIFEST.md](../../RESTART_MANIFEST.md) records the AC14 -> AC15
  rationale.

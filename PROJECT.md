# AC14 Project Dossier

Wiki home: http://localhost:8088/index.php/Project_Wiki

## Portfolio Role

AC14 is supporting evidence for the autocoder lineage. Its value is not that it
beat the monolithic baseline. It did not. Its value is that it produced a large,
artifact-backed empirical record about where decomposition-first code
generation worked, where it failed, and why AC15 needed a cleaner architecture.

AC14 should be presented as disciplined negative evidence and transition work:
it sharpened the decomposition thesis, exposed benchmark and information-parity
issues, and generated the restart manifest that led to AC15.

## Current Status

The checked-out publication branch is
`backup/2026-05-23/ac14-master`, matching the branch policy in
`PROJECT_GRAPH.json`.

Safe current claims:

- frozen blueprint spine, packet compilation, recomposition proof, and
  front-half discovery/freeze artifacts exist;
- AC14 built realistic-input and empirical benchmark machinery;
- the first back-half gate was `inconclusive`;
- the second harder back-half gate was `monolithic_wins`;
- the Theory Forge series closed after 10 benchmarks with no meaningful
  `ac14_wins` verdict;
- the restart manifest records what carried forward into AC15 and what failed.

Do not claim:

- AC14 proved the decomposition thesis;
- AC14 is the current portfolio lead over AC15;
- AC14 beat monolithic generation in the tracked benchmark series;
- the large plan history itself is evidence of success;
- the Theory Forge benchmark failures invalidate every future decomposition
  approach rather than this implementation and scale regime.

## Reviewer Path

1. Read [README.md](README.md) for the project frame and blunt current status.
2. Read [docs/AC14_IMPLEMENTATION_STATUS.md](docs/AC14_IMPLEMENTATION_STATUS.md)
   for what is implemented and what failed.
3. Read [docs/AC14_ROADMAP.md](docs/AC14_ROADMAP.md) for horizon-level context.
4. Read [docs/theory_forge/series_conclusion.md](docs/theory_forge/series_conclusion.md)
   for the strongest empirical conclusion.
5. Read [RESTART_MANIFEST.md](RESTART_MANIFEST.md) for the AC14 -> AC15 restart
   rationale.
6. Read [docs/METHODOLOGY.md](docs/METHODOLOGY.md),
   [docs/VALIDATION.md](docs/VALIDATION.md), and
   [docs/CONCERNS.md](docs/CONCERNS.md) before using AC14 in a portfolio.

## Why It Matters For An AI Engineer Portfolio

AC14 shows that you can run an empirical engineering program honestly even when
the result is not flattering. It records benchmark failures, information
asymmetry, pipeline fragility, and a clear restart path instead of burying a
bad result.

For a CIA-oriented portfolio, AC14 should not be a lead artifact. It should be
supporting evidence that you can diagnose failed systems, preserve evidence,
and turn negative results into a better next architecture.

## Next Evidence To Create

The next useful artifact is not another AC14 benchmark. It is an AC lineage
page that shows:

1. AC12 as blueprint-compiler proof;
2. AC14 as empirical negative evidence and front-half exploration;
3. AC15 as the current measured validator-healer architecture;
4. which claims survived, which were discarded, and why.

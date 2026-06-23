# AC14 Validation Register

Wiki home: http://localhost:8088/index.php/Project_Wiki

## Validation Position

AC14 has real validation value, but the evidence does not support a success
claim for this implementation. The repo is strongest as negative evidence,
lineage, and a source of lessons for AC15.

The key distinction:

- **artifact-valid:** AC14 produced blueprint, packet, freeze, proof, and
  benchmark artifacts;
- **empirically-measured:** AC14 ran comparisons against monolithic baselines;
- **thesis-supported:** evidence favors the decomposition architecture over
  monolithic generation.

AC14 satisfies the first two categories. It does not satisfy the third for the
tracked benchmark regime.

## Current Evidence

| Evidence area | Current artifact | Claim licensed |
|---|---|---|
| Blueprint and packet spine | `README.md`, `AC14_IMPLEMENTATION_STATUS.md` | AC14 implemented the decomposition proof machinery. |
| Anti-drift doctrine | `docs/AC14_ANTI_DRIFT_DOCTRINE.md` | The project kept vision, proof slice, and implementation separate. |
| Back-half gate 1 | `README.md`, `AC14_ROADMAP.md` | First gate was inconclusive. |
| Back-half gate 2 | `README.md`, `AC14_ROADMAP.md` | Harder gate favored monolithic generation. |
| Theory Forge series | `docs/theory_forge/series_conclusion.md` | 10 benchmarks found no meaningful `ac14_wins` verdict. |
| Restart rationale | `RESTART_MANIFEST.md` | AC15 starts from the validated lessons and missing architecture. |

## Evidence Not Yet Present

Do not claim the following without new evidence:

- AC14 beat a fair monolithic baseline;
- AC14 proved the full decomposition thesis;
- AC14 is the current lead autocoder artifact;
- large plan count equals project success;
- front-half proof machinery alone resolves the missing B3 validator-healer
  mechanism;
- future decomposition work is invalidated by AC14's results.

## Commands

Core checks:

```bash
make test
make check
python scripts/check_markdown_links.py PROJECT.md docs/METHODOLOGY.md docs/ARTIFACTS.md docs/VALIDATION.md docs/CONCERNS.md docs/wiki_manifest.yaml
python scripts/meta/sync_plan_status.py --check
git diff --check
```

## Portfolio Readiness Gate

AC14 is portfolio-ready only as supporting evidence when it is framed honestly:

1. It records disciplined negative evidence.
2. It explains why AC15 exists.
3. It shows how benchmark failures were preserved and interpreted.
4. It does not claim a win that the artifacts do not show.

It becomes easier to use externally when the generated wiki has an AC lineage
page and a compact negative-evidence summary table.

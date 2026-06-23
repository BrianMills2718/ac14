# AC14 Methodology

Wiki home: http://localhost:8088/index.php/Project_Wiki

## Goal

AC14 tested a decomposition-first coding-agent thesis: inspect inputs, freeze a
blueprint, compile bounded local packets, generate components from those
packets, recompose the system, and validate the output.

The intended loop was:

```text
input inspection -> blueprint freeze -> packet compilation ->
component generation -> recomposition -> empirical comparison
```

## Architecture

AC14 split the system into a front half and a back half.

Front half:

- local input inspection;
- project/document inventory;
- retrieval and dependency planning;
- draft blueprint planning;
- freeze readiness and freeze decision;
- retry/remediation artifacts after blocked freezes.

Back half:

- packet compilation;
- packet sufficiency checks;
- component generation;
- recomposition proof;
- proof/evidence bundles;
- empirical comparison against monolithic generation.

The anti-drift doctrine is the governing interpretive layer: current examples
and heuristics are implementation artifacts, not the whole product definition.

## Empirical Discipline

AC14 is most useful because it did not stop at proof machinery. It ran baseline
comparisons and recorded unfavorable results:

- first back-half empirical gate: `inconclusive`;
- second harder back-half gate: `monolithic_wins`;
- Theory Forge series: 10 benchmarks, no meaningful `ac14_wins` verdict;
- restart manifest: AC15 should implement per-component validator-healer loops
  before claiming the thesis.

The method lesson is that decomposition must be measured against a fair
monolithic baseline with information parity and an architecture that includes
the robustness mechanism being claimed.

## Modality Split

Deductive / plan-first surfaces:

- blueprint bundle structure;
- packet compilation and sufficiency contracts;
- freeze decision artifacts;
- benchmark command surfaces;
- result/verdict artifact paths;
- anti-drift hierarchy and proof-slice boundaries.

Exploratory / ladder surfaces:

- whether decomposition beats monolithic generation at a given scale;
- where the scale threshold begins for modern models;
- whether information asymmetry contaminated a benchmark;
- whether front-half planning can synthesize missing implementation knowledge;
- which AC14 concepts should survive into AC15.

Exploratory surfaces need empirical gates, not confident claims.

## ADR Map

- [0001_ac14_as_negative_evidence_lineage.md](adr/0001_ac14_as_negative_evidence_lineage.md)
  records the portfolio interpretation: AC14 is supporting negative evidence
  and lineage, not the current lead artifact.

The detailed decision history lives in numbered plans under
[docs/plans/](plans/) and in [RESTART_MANIFEST.md](../RESTART_MANIFEST.md).

## Main Failure Modes

| Failure mode | Why it matters | Control |
|---|---|---|
| Treating volume of plans as success | Large artifact history can obscure the thesis result. | Dossier foregrounds verdicts and restart rationale. |
| Overclaiming decomposition | Tracked gates did not favor AC14. | Validation register separates evidence from aspiration. |
| Benchmark information asymmetry | Monolithic may have received useful hints AC14 packets did not. | Restart manifest requires information parity before future gates. |
| Missing per-component healing | AC14 measured a weaker architecture than the intended thesis. | AC15 carries forward validator-healer loops. |
| Continuing local tuning after decisive loss | Risks benchmark overfitting. | AC14 froze series conclusions and restarted. |

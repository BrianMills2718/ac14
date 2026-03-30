# AC14

AC14 is a clean implementation of the decomposition-first coding-agent thesis.

The first proof slice is intentionally narrow:

- frozen six-file blueprint bundle
- canonical in-memory blueprint model
- B1 blueprint validation
- packet compilation and B2 packet validation

AC14 is not trying to solve enterprise deployment, full autonomy, or broad
tool/runtime integration in the first pass.

## Current Proof Surface

AC14 now supports:

- loading and validating the six-file blueprint bundle
- enforcing explicit scenario kinds, evaluator definitions, component fixture coverage, and realistic-input semantic-acceptance coverage
- discovering a shipped suite of blueprint examples
- compiling bounded component packets
- emitting standalone generated Python components from packet/codegen contexts
- running packet-local tests and recomposition proof on generated code
- writing persisted evidence bundles and repeated fresh-run summaries
- comparing deterministic and LLM-backed generators
- building suite-level proof and comparison artifacts across shipped examples
- building semantic comparison artifacts across reference and generated modes
- building requirements-aware semantic-acceptance artifacts against actual system outputs
- producing an evidence-backed default-generator recommendation

## Quickstart

```bash
make test
make verify-blueprint
make list-examples
make generate-components OUTPUT=.ac14_out/generated
make prove-example OUTPUT=.ac14_out/proof TRIALS=3
make fresh-runs OUTPUT=.ac14_out/fresh TRIALS=3
make acceptance-review INPUT=examples/support_ticket_digest/blueprint OUTPUT=.ac14_out/acceptance GENERATOR=deterministic
make prove-suite OUTPUT=.ac14_out/suite TRIALS=1
make compare-suite OUTPUT=.ac14_out/suite_compare TRIALS=1 GENERATORS=deterministic
make semantic-compare-suite OUTPUT=.ac14_out/suite_semantic MODES="reference deterministic"
make acceptance-review-suite OUTPUT=.ac14_out/suite_acceptance GENERATOR=deterministic
make recommend-default-generator OUTPUT=.ac14_out/recommend GENERATORS=deterministic TRIALS=1
```

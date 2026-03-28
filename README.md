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
- compiling bounded component packets
- emitting standalone generated Python components from packet/codegen contexts
- running packet-local tests and recomposition proof on generated code
- writing persisted evidence bundles and repeated fresh-run summaries

## Quickstart

```bash
make test
make verify-blueprint
make generate-components OUTPUT=.ac14_out/generated
make prove-example OUTPUT=.ac14_out/proof TRIALS=3
make fresh-runs OUTPUT=.ac14_out/fresh TRIALS=3
```

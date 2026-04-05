# Information Theory Entropy Suite — Benchmark Requirements

## Overview

Implement Shannon's four core entropy formulas as a linear four-component pipeline.
Each component implements exactly one formula. All computations use log base 2 (bits).

## Formulas

### 1. Zero-Order Entropy (H_0)

```
H_0 = -sum(p_i * log2(p_i))   for all symbols i
```

- `symbol_frequencies`: dict mapping symbol to probability (values sum to 1.0)
- Convention: 0 * log2(0) = 0.0 (zero-probability symbols contribute nothing)
- Result: H_0 in bits/symbol, range [0.0, log2(alphabet_size)]

### 2. Maximum Entropy (H_max)

```
H_max = log2(alphabet_size)
```

- `alphabet_size`: number of distinct symbols
- Result: H_max in bits/symbol (entropy of a uniform distribution over the alphabet)

### 3. Relative Entropy (eta)

```
eta = H_0 / H_max
```

- Degenerate case: if H_max == 0.0, return 0.0
- Result: dimensionless, range [0.0, 1.0]

### 4. Redundancy (D)

```
D = 1.0 - H_0 / H_max   (equivalently, D = 1 - eta)
```

- Degenerate case: if H_max == 0.0, return 1.0
- Result: dimensionless, range [0.0, 1.0]

## Critical Implementation Constraint

**Use `math.log2` (log base 2) for all computations.** Do NOT use `math.log`
(natural logarithm). Using `math.log` gives results in nats, not bits, and will
fail every test case.

## Pipeline Structure

The four components form a strict linear chain:

```
entropy_request
  → compute_zero_order_entropy  → zero_order_entropy_output
  → compute_maximum_entropy     → maximum_entropy_output
  → compute_relative_entropy    → relative_entropy_output
  → compute_redundancy          → entropy_results
```

Each stage passes accumulated values to the next stage. The final output
`entropy_results` contains all four computed measures.

## Test Cases

| case_id | H_0 | H_max | eta | D |
|---------|-----|-------|-----|---|
| fair_coin (0.5, 0.5) | 1.0 | 1.0 | 1.0 | 0.0 |
| biased_75_25 (0.75, 0.25) | 0.8112781244591328 | 1.0 | 0.8112781244591328 | 0.18872187554086717 |
| uniform_4 (0.25 each) | 2.0 | 2.0 | 1.0 | 0.0 |
| skewed_3 (0.5, 0.3, 0.2) | 1.4854752972273344 | 1.584962500721156 | 0.9372305632161296 | 0.06276943678387037 |
| binary_90_10 (0.9, 0.1) | 0.4689955935892812 | 1.0 | 0.4689955935892812 | 0.5310044064107188 |

Expected values are exact Python `math.log2` results — no rounding or tolerance. Any
correct implementation using `math.log2` will produce these exact values.

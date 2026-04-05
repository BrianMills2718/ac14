# Plan #171: Wire packet_focus → implementation_constraints

## Status: COMPLETE

## Problem

The planning step's `PlannedComponent.packet_focus` field gets explicit formula
contracts when the spec is explicit (e.g., "disc_alpha = exp(-(r^alpha) * T)").
However, `draft_authoring.py` ignores `packet_focus` and always uses PLACEHOLDER_CONSTRAINT
for `implementation_constraints`. The codegen never sees the planning step's derived formulas.

From `zeta_gate_1` (explicit spec), planning step correctly derived in packet_focus:
- "Compute disc_alpha as exp(-(r^alpha) * T), not exp(-rT)."
- "Compute d1_zeta with zeta scaling only on the variance term zeta*sigma^2/2."

But codegen saw: "TODO: confirm implementation constraints before blueprint freeze"

## Fix

1. Change `PlannedComponent.packet_focus` description to explicitly ask for DERIVED FORMULAS
2. Wire `packet_focus` → `implementation_constraints` in `draft_authoring.py`

## Predicted Impact

### For Explicit Spec (zeta_options)
- Planning step already derives exact formulas in packet_focus ✓
- After fix: codegen will see these formulas in implementation_constraints
- Expected: no regression (already works without this — but now redundantly correct)

### For Noisy Spec (zeta_options_noisy_spec)
- Planning step has access to FULL structured_spec including success_criteria
- success_criteria has: "disc_alpha approx 0.9246 (NOT the standard exp(-rT) = 0.9512)"
- After strengthened prompt + fix: planning LLM may derive "disc_alpha = exp(-r^alpha * T)"
  from the 0.9246 hint and put it in packet_focus → implementation_constraints
- Expected: codegen now sees explicit formula → correct implementation

## Acceptance Criteria
1. `packet_focus` flows to `implementation_constraints` in draft bundle components.yaml
2. No existing tests break
3. Noisy-spec smoke rerun shows AC14 getting disc_alpha correct (≈ 0.9246)


## Results

### Improvement Achieved
- `disc_alpha`: FIXED ✓ — planning step correctly derives `exp(-r^alpha * T)` from the 0.9246 hint
- Packet_focus now contains explicit formulas (not just vague guidance)

### Remaining Gap
- `d1_zeta`: STILL WRONG — planning step consistently uses denominator `sigma*sqrt(zeta*T)` 
  instead of `sigma*sqrt(T)`, giving d1=0.3825 instead of 0.32
- Root cause: planning LLM doesn't do numerical cross-verification against success_criteria
  It derives what looks reasonable algebraically but doesn't verify `d1=0.32` against its formula
  
### What Would Complete the Fix
- Planning step numerical verification: after deriving each formula, plug in the base case
  values and check against success_criteria hints. If mismatch → retry with different formula.
- This requires a more sophisticated planning prompt with verification step.
- OR: make the noisy spec even more explicit about the d1_zeta denominator: 
  "The denominator of d1_zeta is sigma*sqrt(T), UNCHANGED from standard BS"

### Net Impact of Plan #171
The packet_focus → implementation_constraints wiring is a real improvement:
- For explicit specs: codegen now sees the planning step's derived formulas (not just TODO)
- For noisy specs: disc_alpha now correct; other formulas still require better planning step intelligence

## Status: COMPLETE (partial fix — disc_alpha now correct, d1_zeta denominator still wrong)

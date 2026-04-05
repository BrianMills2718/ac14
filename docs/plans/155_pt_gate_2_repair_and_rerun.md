# Plan #155: PT Gate 2 Repair — Validation Fix, Context Wiring, Codex SDK Switch

**Status**: Complete  
**Started**: 2026-04-04  
**Completed**: 2026-04-04

---

## Context

Gate_1 on the Prospect Theory benchmark showed `monolithic_wins` (5/5 vs 0/5 AC14).
Root cause from Plan #154:
1. Synthetic packet fixtures wrapped list fields as `{'items': [...]}` dicts
2. Per-component hint `business_rules` were not threaded to codegen LLM
3. Model was Gemini flash-lite — not strong enough for structured decomposition

Gate_2a (Gemini with context fixes) — ran but no fixture file issue yet diagnosed.
Gate_2b (Codex SDK attempt) — blocked by exhausted Codex credits.
Gate_2c (gpt-4.1) — all 5 trials failed at front-half stage with E-B1-SCHEMA-FIELD-REF-MISSING.

---

## Root Cause of Gate_2c Failures

gpt-4.1 generates blueprint schemas with `type: list` for list fields.
The B1 validator treated `list` as a named schema reference (not in the primitives set),
causing E-B1-SCHEMA-FIELD-REF-MISSING errors on every list field. This blocked
freeze approval before any codegen ran.

---

## Fixes Applied

### Fix 1: Blueprint Validation — Accept `list` and `array` as Primitive Types (validation.py)

Added `"list"` and `"array"` to the primitives set in `_is_named_schema_reference`.
Added `array[...]` container stripping in `_strip_container` (parallel to `list[...]`).

**Before**: `type: list` → treated as schema reference "list" → E-B1-SCHEMA-FIELD-REF-MISSING  
**After**: `type: list` → treated as primitive container → no error

### Fix 2: Draft Authoring — Synthetic Fixture Values for Bare Container Types (draft_authoring.py)

Added `array[...]` and bare `list`/`array` handling in `_draft_value_for_field_type`.

**Before**: `type: list` → fell through to `return f"draft_{field_name}"` → string value  
**After**: `type: list` → returns `[]`, `type: array[string]` → returns `["draft_fieldname"]`

### Fix 3: Per-Component Hint Rules (generated_codegen.py + front_half_first_empirical.py)

Built `hint_rules_by_component` from `structured_spec.workflow_hints` and passed it
through `emit_generated_package` → `_merge_component_rules` → `CodegenContext`.

Each component now receives its specific hint `business_rules` prepended to
the top-level system rules.

### Fix 4: Codex SDK `additionalProperties: false` (llm_client agents_codex_runtime.py)

Applied `_strict_json_schema()` to both Codex structured call paths so OpenAI's
Strict Structured Output enforcement doesn't reject Pydantic schemas.

### Fix 5: Switch Default Model to `codex` (Makefile)

`MODEL ?= codex`, `RETRY_MODEL ?= codex`

Note: Codex credits were exhausted during gate_2b testing. Gate_2d uses
`MODEL=openai/gpt-4.1` as a working fallback.

---

## Verification

- 304 tests pass after all fixes
- Trial_1 attempt_1 draft bundle from gate_2c now validates as `passed=True` with 0 errors
- Smoke gate (pt_gate_2d_smoke) returns `ready_for_full_trials` with gpt-4.1
  - AC14 front_half_success: true
  - runtime_hard_harness_success: true

---

## Active Gate

**pt_gate_2d**: full 5-trial gate with `openai/gpt-4.1`
Output: `.ac14_out/pt_gate_2d/`

---

## Next Plan

Plan #156: PT gate_2d verdict interpretation.

Branches:
- `ac14_wins`: write ADR + update TODO + plan broader benchmark breadth
- `monolithic_wins`: diagnose remaining failure modes, write boundary doc
- `inconclusive`: identify strongest signal and plan targeted repair
- `ready_for_full_trials` from gate not yet spent: proceed with gate

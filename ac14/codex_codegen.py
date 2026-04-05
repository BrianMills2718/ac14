"""Codex SDK-backed component generator for AC14.

Uses `codex exec` to run an agentic loop that writes the component module,
executes the packet tests, and iterates until tests pass — or exhausts attempts.

The integration point is `generate_component_with_codex()`, which is a drop-in
replacement for `agenerate_component_module_with_llm()` in `llm_codegen.py`.
"""

from __future__ import annotations

import json
import subprocess
import textwrap
import time
from pathlib import Path

from ac14.codegen_context import CodegenContext
from ac14.llm_codegen import GeneratedModuleResponse, GeneratedModuleValidationError, _validate_generated_module

try:
    from llm_client.sdk.agents_codex import (  # type: ignore[import-not-found]
        parse_codex_exec_events as _parse_codex_exec_events,
        log_codex_exec_session as _log_codex_exec_session,
    )
    _LLMCLIENT_OBSERVABILITY = True
except ImportError:
    _LLMCLIENT_OBSERVABILITY = False
    _parse_codex_exec_events = None  # type: ignore[assignment]
    _log_codex_exec_session = None   # type: ignore[assignment]


_CODEX_EXEC = "codex"
_DEFAULT_TIMEOUT_SECONDS = 600  # assembler has 39 input ports, needs extra time


def _compute_timeout(context: CodegenContext) -> int:
    """Scale timeout with component complexity (input port count)."""
    base = _DEFAULT_TIMEOUT_SECONDS
    n_ports = len(context.input_ports) + len(context.output_ports)
    if n_ports > 20:
        return base * 3  # assembler-class components: 1800s
    if n_ports > 5:
        return base * 2  # mid-complexity: 1200s
    return base  # simple components: 600s


def generate_component_with_codex(
    context: CodegenContext,
    *,
    trace_dir: Path,
) -> GeneratedModuleResponse:
    """Generate one component module using Codex exec with self-verification.

    Codex runs in an isolated per-component work_dir so it cannot see (and
    therefore cannot waste tokens reading) sibling components in trace_dir.
    After success the generated .py is copied back into trace_dir.
    """
    trace_dir = trace_dir.resolve()

    # Isolated working directory — only this component's files land here.
    work_dir = trace_dir / f"_work_{context.component_id}"
    work_dir.mkdir(exist_ok=True)

    output_file = work_dir / f"{context.component_id}.py"
    context_file = work_dir / f"{context.component_id}.context.json"
    test_file = work_dir / f"test_{context.component_id}_packet.py"
    last_msg_file = work_dir / f"{context.component_id}.codex_last_msg.txt"

    timeout_s = _compute_timeout(context)

    # Write context for Codex to inspect
    context_file.write_text(context.model_dump_json(indent=2))

    # Write runnable packet tests
    test_file.write_text(_render_packet_tests(context))

    prompt = _build_prompt(context, output_file=output_file, test_file=test_file)

    _t0 = time.monotonic()
    result = subprocess.run(
        [
            _CODEX_EXEC,
            "exec",
            "--dangerously-bypass-approvals-and-sandbox",
            "--json",
            "-C", str(work_dir),
            "--output-last-message", str(last_msg_file),
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    _elapsed = time.monotonic() - _t0

    # Persist trace files in trace_dir (standard naming for diagnostics)
    _persist_codex_trace(trace_dir, context.component_id, result)
    # Also keep a copy of the context.json at the trace_dir level for make diagnose-attempt
    (trace_dir / f"{context.component_id}.context.json").write_text(
        context_file.read_text()
    )

    if not output_file.exists():
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        raise GeneratedModuleValidationError(
            component_id=context.component_id,
            module_code="",
            message=(
                f"Codex did not write {output_file.name}. "
                f"exit={result.returncode}. stderr={stderr[:400]}. stdout={stdout[:400]}"
            ),
        )

    module_code = output_file.read_text()
    try:
        _validate_generated_module(module_code, component_id=context.component_id)
    except ValueError as exc:
        raise GeneratedModuleValidationError(
            component_id=context.component_id,
            module_code=module_code,
            message=str(exc),
        ) from exc

    # Copy the generated module into trace_dir so the recomposition runner finds it
    (trace_dir / f"{context.component_id}.py").write_text(module_code)

    last_msg = last_msg_file.read_text().strip() if last_msg_file.exists() else ""

    session = _parse_codex_exec_events(result.stdout, result.stderr) if _LLMCLIENT_OBSERVABILITY else {}  # type: ignore[misc]
    tokens_used = session.get("total_tokens") if session else None
    token_note = f" tokens={tokens_used:,}" if tokens_used else ""

    if _LLMCLIENT_OBSERVABILITY and session:
        _log_codex_exec_session(  # type: ignore[misc]
            session,
            task=f"ac14/{context.component_id}",
            trace_id=f"codex_exec/{trace_dir.parent.parent.name}/{context.component_id}",
            latency_s=_elapsed,
            component_id=context.component_id,
            exit_code=result.returncode,
        )

    return GeneratedModuleResponse(
        module_code=module_code,
        implementation_notes=[f"Codex exec (self-verified).{token_note} {last_msg[:200]}"],
    )


def _build_prompt(context: CodegenContext, *, output_file: Path, test_file: Path) -> str:
    """Build the task prompt for `codex exec`."""
    rules_block = ""
    if context.structured_spec_business_rules:
        rules = "\n".join(f"  - {r}" for r in context.structured_spec_business_rules)
        rules_block = f"\nBusiness rules (implement ALL of these exactly):\n{rules}\n"

    invariants_block = ""
    if context.local_invariants:
        inv = "\n".join(f"  - {i}" for i in context.local_invariants)
        invariants_block = f"\nLocal invariants:\n{inv}\n"

    repair_block = ""
    if context.repair_guidance:
        repairs = "\n".join(f"  - {r}" for r in context.repair_guidance)
        repair_block = f"\nRepair guidance from previous failure:\n{repairs}\n"

    input_ports = "\n".join(f"  - {name}: {sid}" for name, sid in context.input_ports.items())
    output_ports = "\n".join(f"  - {name}: {sid}" for name, sid in context.output_ports.items())

    return textwrap.dedent(f"""\
        Implement an AC14 component module for: {context.component_id}
        Purpose: {context.purpose}

        Input ports:
        {input_ports}

        Output ports:
        {output_ports}
        {invariants_block}{rules_block}{repair_block}
        Runtime contract (MANDATORY):
        - Define a `GeneratedComponent` class with `execute(self, inputs)` method
        - Define `build_component()` returning `GeneratedComponent()`
        - `inputs` is a plain dict keyed by port name; each value is a plain dict
        - Access fields as `inputs['port_name']['field']` NOT with dot notation
        - Return a plain dict keyed by output port name: {{"output_port": {{...fields...}}}}
        - Fail loud (raise ValueError) rather than silently returning wrong values
        - No external imports beyond the Python standard library

        Steps:
        1. Write the complete module to {output_file.name}
        2. Run: python -m pytest {test_file.name} -v
        3. If any tests fail, read the failure output, fix the module, and re-run
        4. Repeat until all tests pass

        The full codegen context (schemas, test cases) is in {output_file.stem}.context.json.
    """)


def _render_packet_tests(context: CodegenContext) -> str:
    """Render packet test cases as a runnable pytest module."""
    cases_json = json.dumps(
        [tc.model_dump(mode="json") for tc in context.packet_test_cases],
        indent=2,
    )
    return textwrap.dedent(f"""\
        \"\"\"Packet tests for {context.component_id} — generated by AC14 harness.\"\"\"
        import importlib.util, json, math, sys
        from pathlib import Path
        import pytest

        _MODULE_FILE = Path(__file__).parent / "{context.component_id}.py"

        def _load_component():
            spec = importlib.util.spec_from_file_location("{context.component_id}", _MODULE_FILE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.build_component()

        _CASES = {cases_json}

        def _approx_equal(a, b, rel_tol=1e-9, abs_tol=1e-12):
            if isinstance(a, float) and isinstance(b, float):
                if a == 0.0 and b == 0.0:
                    return True
                return abs(a - b) <= max(abs_tol, rel_tol * max(abs(a), abs(b)))
            if isinstance(a, dict) and isinstance(b, dict):
                return set(a) == set(b) and all(_approx_equal(a[k], b[k]) for k in a)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                return _approx_equal(float(a), float(b))
            return a == b

        @pytest.mark.parametrize("case", _CASES, ids=[c["case_id"] for c in _CASES])
        def test_packet(case):
            comp = _load_component()
            result = comp.execute(case["inputs"])
            assert _approx_equal(result, case["expected_outputs"]), (
                f"Output mismatch:\\nExpected: {{json.dumps(case['expected_outputs'], indent=2)}}\\n"
                f"Got:      {{json.dumps(result, indent=2)}}"
            )
    """)


def _persist_codex_trace(trace_dir: Path, component_id: str, result: subprocess.CompletedProcess[str]) -> None:
    """Persist codex subprocess stdout/stderr for diagnosis.

    With --json, stdout is a JSONL event stream (one JSON object per line).
    stderr is the human-readable transcript (tool calls, reasoning summaries).
    """
    if result.stdout:
        (trace_dir / f"{component_id}.codex_events.jsonl").write_text(result.stdout)
    if result.stderr:
        (trace_dir / f"{component_id}.codex_stderr.txt").write_text(result.stderr)
    (trace_dir / f"{component_id}.codex_exit.txt").write_text(str(result.returncode))

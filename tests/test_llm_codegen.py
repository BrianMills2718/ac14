"""Tests for the LLM-backed generator contract."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from ac14.codegen_context import CodegenContext, build_codegen_context
from ac14.llm_codegen import (
    GeneratedModuleResponse,
    PROMPT_PATH,
    agenerate_component_module_with_llm,
    generate_component_module_with_llm,
)
from ac14.loader import load_blueprint_dir
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def _digest_assembler_context() -> CodegenContext:
    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)
    packet_cases = materialize_packet_test_cases(packet_bundle)
    return build_codegen_context(
        packet_bundle.packets["digest_assembler"],
        packet_cases["digest_assembler"],
    )


@pytest.mark.asyncio
async def test_agenerate_component_module_with_llm_uses_structured_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LLM-backed generation should call llm_client with the expected structured contract."""

    # mock-ok: live LLM calls are not reliable for unit tests; this verifies the local contract.
    fake_call = AsyncMock(
        return_value=(
            GeneratedModuleResponse(
                module_code=(
                    "class GeneratedComponent:\n"
                    "    def execute(self, inputs):\n"
                    "        return {}\n\n"
                    "def build_component():\n"
                    "    return GeneratedComponent()\n"
                ),
                implementation_notes=["proof-slice test"],
            ),
            object(),
        ),
    )
    monkeypatch.setattr("ac14.llm_codegen.acall_llm_structured", fake_call)

    response = await agenerate_component_module_with_llm(
        _digest_assembler_context(),
        trace_id="test/llm_codegen/async",
        max_budget=0.1,
    )

    assert "GeneratedComponent" in response.module_code
    assert PROMPT_PATH.exists()
    assert fake_call.await_count == 1
    assert fake_call.await_args is not None
    kwargs = fake_call.await_args.kwargs
    assert kwargs["task"] == "ac14_generate_component"
    assert kwargs["trace_id"] == "test/llm_codegen/async"
    assert kwargs["max_budget"] == 0.1
    assert kwargs["response_model"] is GeneratedModuleResponse


def test_generate_component_module_with_llm_sync_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    """Synchronous wrapper should return the structured response."""

    async def _fake_async_call(*args: object, **kwargs: object) -> GeneratedModuleResponse:
        return GeneratedModuleResponse(
            module_code=(
                "class GeneratedComponent:\n"
                "    def execute(self, inputs):\n"
                "        return {}\n\n"
                "def build_component():\n"
                "    return GeneratedComponent()\n"
            ),
            implementation_notes=["sync wrapper test"],
        )

    monkeypatch.setattr("ac14.llm_codegen.agenerate_component_module_with_llm", _fake_async_call)

    response = generate_component_module_with_llm(
        _digest_assembler_context(),
        trace_id="test/llm_codegen/sync",
        max_budget=0.1,
    )

    assert response.implementation_notes == ["sync wrapper test"]


def test_llm_codegen_fails_loud_on_missing_build_component(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed module output should fail loud before it reaches disk."""

    async def _fake_async_call(*args: object, **kwargs: object) -> tuple[GeneratedModuleResponse, object]:
        return (
            GeneratedModuleResponse(
                module_code=(
                    "class GeneratedComponent:\n"
                    "    def execute(self, inputs):\n"
                    "        return {}\n"
                ),
                implementation_notes=["missing builder"],
            ),
            object(),
        )

    monkeypatch.setattr("ac14.llm_codegen.acall_llm_structured", _fake_async_call)

    with pytest.raises(ValueError, match="missing build_component"):
        asyncio.run(
            agenerate_component_module_with_llm(
                _digest_assembler_context(),
                trace_id="test/llm_codegen/fail_loud",
                max_budget=0.1,
            ),
        )

"""Tests for the LLM-backed generator contract."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from ac14.codegen_context import CodegenContext, build_codegen_context
from ac14.generated_codegen import emit_generated_package
from ac14.llm_codegen import (
    GeneratedModuleResponse,
    PROMPT_PATH,
    agenerate_component_module_with_llm,
    generate_component_module_with_llm,
)
from ac14.loader import load_blueprint_dir
from ac14.packet_tests import materialize_packet_test_cases
from ac14.packets import compile_packets
from llm_client import render_prompt  # type: ignore[import-not-found]


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"
AUTH_MIX_EXAMPLE_DIR = (
    Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest_auth_mix" / "blueprint"
)


def _component_context(blueprint_dir: Path, component_id: str) -> CodegenContext:
    blueprint = load_blueprint_dir(blueprint_dir)
    packet_bundle = compile_packets(blueprint)
    packet_cases = materialize_packet_test_cases(packet_bundle)
    return build_codegen_context(
        packet_bundle.packets[component_id],
        packet_cases[component_id],
    )


def _digest_assembler_context() -> CodegenContext:
    return _component_context(EXAMPLE_DIR, "digest_assembler")


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


def test_generate_component_module_with_llm_uses_fixture_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Fixture-backed LLM codegen should return deterministic module code without a live call."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)
    deterministic_package = emit_generated_package(
        packet_bundle,
        tmp_path / "deterministic_generated",
        generator_kind="deterministic",
    )
    fixture_payload = {
        component_id: {
            "module_code": Path(module_path).read_text(),
            "implementation_notes": ["fixture-backed llm codegen"],
        }
        for component_id, module_path in deterministic_package.module_paths.items()
    }
    fixture_path = tmp_path / "llm_codegen_fixture.json"
    fixture_path.write_text(json.dumps(fixture_payload, indent=2, sort_keys=True))

    monkeypatch.setenv("AC14_LLM_CODEGEN_FIXTURE", str(fixture_path))

    response = generate_component_module_with_llm(
        _digest_assembler_context(),
        trace_id="test/llm_codegen/fixture_env",
        max_budget=0.1,
    )

    assert "class GeneratedComponent" in response.module_code
    assert response.implementation_notes == ["fixture-backed llm codegen"]


def test_component_prompt_includes_local_schema_definitions() -> None:
    """The component prompt should expose packet-local schema definitions explicitly."""

    messages = render_prompt(
        PROMPT_PATH,
        context=_digest_assembler_context().model_dump(mode="json"),
    )

    user_message = next(message["content"] for message in messages if message["role"] == "user")
    assert "Local schema definitions:" in user_message
    assert "schema_id:" in user_message
    assert "required=" in user_message
    assert "absence_meaning=" in user_message


def test_generate_component_module_with_llm_uses_blueprint_aware_fixture_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Fixture-backed LLM codegen should disambiguate repeated component ids by blueprint."""

    fixture_path = tmp_path / "llm_codegen_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "support_ticket_digest_v1": {
                    "customer_context_loader": {
                        "module_code": (
                            "class GeneratedComponent:\n"
                            "    def execute(self, inputs):\n"
                            "        return {}\n\n"
                            "def build_component():\n"
                            "    return GeneratedComponent()\n"
                        ),
                        "implementation_notes": ["support blueprint fixture"],
                    }
                },
                "support_ticket_digest_auth_mix_v1": {
                    "customer_context_loader": {
                        "module_code": (
                            "class GeneratedComponent:\n"
                            "    def execute(self, inputs):\n"
                            "        return {}\n\n"
                            "def build_component():\n"
                            "    return GeneratedComponent()\n"
                        ),
                        "implementation_notes": ["auth-mix blueprint fixture"],
                    }
                },
            },
            indent=2,
            sort_keys=True,
        )
    )

    monkeypatch.setenv("AC14_LLM_CODEGEN_FIXTURE", str(fixture_path))

    support_response = generate_component_module_with_llm(
        _component_context(EXAMPLE_DIR, "customer_context_loader"),
        trace_id="test/llm_codegen/blueprint_aware/support",
        max_budget=0.1,
    )
    auth_mix_response = generate_component_module_with_llm(
        _component_context(AUTH_MIX_EXAMPLE_DIR, "customer_context_loader"),
        trace_id="test/llm_codegen/blueprint_aware/auth_mix",
        max_budget=0.1,
    )

    assert support_response.implementation_notes == ["support blueprint fixture"]
    assert auth_mix_response.implementation_notes == ["auth-mix blueprint fixture"]

"""LLM-backed component generation from AC14 codegen contexts."""

from __future__ import annotations

import ast
import asyncio
import json
import os
from pathlib import Path
from typing import cast

from pydantic import BaseModel, Field

from ac14.codegen_context import CodegenContext
from llm_client import acall_llm_structured, render_prompt  # type: ignore[import-not-found]


DEFAULT_LLM_MODEL = "gemini/gemini-2.5-flash-lite"
DEFAULT_LLM_MAX_BUDGET = 0.50
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "generate_component.yaml"


class GeneratedModuleResponse(BaseModel):
    """Structured response contract for LLM-backed module generation."""

    module_code: str = Field(
        description=(
            "Complete standalone Python module source code. Must define a "
            "`GeneratedComponent` class with an `execute(inputs)` method and a "
            "`build_component()` function returning the component instance."
        ),
    )
    implementation_notes: list[str] = Field(
        description="Short notes about key implementation choices or limitations.",
    )


class GeneratedModuleValidationError(ValueError):
    """Raised when LLM-generated module code fails AC14 contract validation."""

    def __init__(self, *, component_id: str, module_code: str, message: str) -> None:
        super().__init__(message)
        self.component_id = component_id
        self.module_code = module_code


async def agenerate_component_module_with_llm(
    context: CodegenContext,
    *,
    model: str = DEFAULT_LLM_MODEL,
    trace_id: str,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    task: str = "ac14_generate_component",
) -> GeneratedModuleResponse:
    """Generate one component module from a codegen context using llm_client."""

    fixture_path = os.environ.get("AC14_LLM_CODEGEN_FIXTURE")
    if fixture_path:
        response = _load_fixture_response(
            fixture_path=Path(fixture_path),
            blueprint_id=context.blueprint_id,
            component_id=context.component_id,
        )
        try:
            _validate_generated_module(response.module_code, component_id=context.component_id)
        except ValueError as exc:
            raise GeneratedModuleValidationError(
                component_id=context.component_id,
                module_code=response.module_code,
                message=str(exc),
            ) from exc
        return response

    messages = render_prompt(
        PROMPT_PATH,
        context=context.model_dump(mode="json"),
    )
    response, _meta = await acall_llm_structured(
        model,
        messages,
        response_model=GeneratedModuleResponse,
        task=task,
        trace_id=trace_id,
        max_budget=max_budget,
    )
    typed_response = cast(GeneratedModuleResponse, response)
    try:
        _validate_generated_module(typed_response.module_code, component_id=context.component_id)
    except ValueError as exc:
        raise GeneratedModuleValidationError(
            component_id=context.component_id,
            module_code=typed_response.module_code,
            message=str(exc),
        ) from exc
    return typed_response


def generate_component_module_with_llm(
    context: CodegenContext,
    *,
    model: str = DEFAULT_LLM_MODEL,
    trace_id: str,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    task: str = "ac14_generate_component",
) -> GeneratedModuleResponse:
    """Synchronous wrapper for LLM-backed component generation."""

    return asyncio.run(
        agenerate_component_module_with_llm(
            context,
            model=model,
            trace_id=trace_id,
            max_budget=max_budget,
            task=task,
        ),
    )


def _validate_generated_module(module_code: str, *, component_id: str) -> None:
    """Fail loud when generated module code does not meet the minimum contract."""

    try:
        tree = ast.parse(module_code)
    except SyntaxError as exc:  # pragma: no cover - exercised through fail-loud behavior
        raise ValueError(f"generated module for {component_id} is not valid Python: {exc}") from exc

    has_generated_component = any(
        isinstance(node, ast.ClassDef) and node.name == "GeneratedComponent" for node in tree.body
    )
    has_build_component = any(
        isinstance(node, ast.FunctionDef) and node.name == "build_component" for node in tree.body
    )
    if not has_generated_component:
        raise ValueError(
            f"generated module for {component_id} is missing GeneratedComponent class",
        )
    if not has_build_component:
        raise ValueError(
            f"generated module for {component_id} is missing build_component function",
        )

    namespace: dict[str, object] = {}
    try:
        exec(module_code, namespace)
    except Exception as exc:  # pragma: no cover - fail-loud validation path
        raise ValueError(
            f"generated module for {component_id} failed during import-time validation: {exc}",
        ) from exc

    build_component = namespace.get("build_component")
    if not callable(build_component):
        raise ValueError(
            f"generated module for {component_id} has a non-callable build_component",
        )
    try:
        component = build_component()
    except Exception as exc:  # pragma: no cover - fail-loud validation path
        raise ValueError(
            f"generated module for {component_id} failed when build_component() was called: {exc}",
        ) from exc
    execute = getattr(component, "execute", None)
    if not callable(execute):
        raise ValueError(
            f"generated module for {component_id} build_component() did not return a runtime component",
        )


def _load_fixture_response(
    *,
    fixture_path: Path,
    blueprint_id: str,
    component_id: str,
) -> GeneratedModuleResponse:
    """Load one deterministic LLM-codegen fixture response for a component."""

    payload = json.loads(fixture_path.read_text())
    if not isinstance(payload, dict):
        raise ValueError("AC14_LLM_CODEGEN_FIXTURE must point to a JSON object")
    if "module_code" in payload:
        return GeneratedModuleResponse.model_validate(payload)
    blueprint_payload = payload.get(blueprint_id)
    if blueprint_payload is not None:
        if not isinstance(blueprint_payload, dict):
            raise ValueError(
                "AC14_LLM_CODEGEN_FIXTURE blueprint entry must map component ids to responses",
            )
        component_payload = blueprint_payload.get(component_id)
        if component_payload is None:
            raise ValueError(
                f"AC14_LLM_CODEGEN_FIXTURE blueprint entry {blueprint_id} "
                f"has no component {component_id}",
            )
        return GeneratedModuleResponse.model_validate(component_payload)
    component_payload = payload.get(component_id)
    if component_payload is None:
        raise ValueError(
            "AC14_LLM_CODEGEN_FIXTURE has no entry for "
            f"blueprint {blueprint_id} component {component_id}",
        )
    return GeneratedModuleResponse.model_validate(component_payload)

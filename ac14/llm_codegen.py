"""LLM-backed component generation from AC14 codegen contexts."""

from __future__ import annotations

import ast
import asyncio
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


async def agenerate_component_module_with_llm(
    context: CodegenContext,
    *,
    model: str = DEFAULT_LLM_MODEL,
    trace_id: str,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    task: str = "ac14_generate_component",
) -> GeneratedModuleResponse:
    """Generate one component module from a codegen context using llm_client."""

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
    _validate_generated_module(typed_response.module_code, component_id=context.component_id)
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

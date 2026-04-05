"""Fail-loud model normalization and validation for AC14 CLI workflows.

AC14 historically accepted arbitrary ``MODEL=...`` overrides from plans and
Make targets, which allowed stale benchmark-era model IDs to reach deep
structured-call boundaries before failing. This module blocks that failure mode
at the CLI ingress so empirical runs either normalize to a valid route or fail
immediately with an actionable message.
"""

from __future__ import annotations

from functools import lru_cache

from llm_client.core.models import list_models
from llm_client.core.routing import normalize_model_for_policy
from llm_client.execution.call_contracts import _check_model_deprecation

_KNOWN_INVALID_MODELS: dict[str, str] = {
    "openrouter/anthropic/claude-haiku-4-5-20251001": (
        "OpenRouter does not provide this Anthropic Haiku 4.5 id in the current ecosystem setup. "
        "Use `gemini/gemini-2.5-flash-lite`, `openrouter/openai/gpt-4.1`, or `codex` instead."
    ),
    "openrouter/anthropic/claude-3-haiku-20240307": (
        "This older OpenRouter Claude Haiku id is not available in the current ecosystem setup. "
        "Use `gemini/gemini-2.5-flash-lite`, `openrouter/openai/gpt-4.1`, or `codex` instead."
    ),
}

_KNOWN_GOOD_EXAMPLES = (
    "gemini/gemini-2.5-flash-lite",
    "gemini/gemini-2.5-flash",
    "openrouter/openai/gpt-4.1",
    "openrouter/openai/gpt-5.4",
    "codex",
)


@lru_cache(maxsize=1)
def _registry_model_ids() -> set[str]:
    """Return known registry model ids once for fail-loud validation."""

    return {str(model["litellm_id"]) for model in list_models(available_only=False)}


def _is_codex_family(model: str) -> bool:
    """Return whether a model is handled by the Codex-specific runtime path."""

    normalized = model.strip().lower()
    return normalized.startswith(("codex", "gpt-5.3-codex", "gpt-5.2-codex", "gpt-5.1-codex"))


def _normalize_ac14_model_alias(model: str) -> str:
    """Handle stale benchmark aliases that should route through OpenRouter."""

    raw = model.strip()
    lower = raw.lower()
    if lower.startswith("google/gemini-"):
        return f"openrouter/{raw}"
    return normalize_model_for_policy(raw, "openrouter")


def normalize_and_validate_model(model: str, *, field_name: str = "model") -> str:
    """Normalize one AC14 CLI model override and reject known bad inputs early."""

    raw = str(model or "").strip()
    if not raw:
        raise ValueError(f"{field_name} must be non-empty")

    normalized = _normalize_ac14_model_alias(raw)
    lower = normalized.lower()

    if lower in _KNOWN_INVALID_MODELS:
        raise ValueError(f"Unsupported {field_name} '{raw}': {_KNOWN_INVALID_MODELS[lower]}")

    if _is_codex_family(normalized):
        return normalized

    _check_model_deprecation(normalized)

    if normalized in _registry_model_ids():
        return normalized

    if lower.startswith("openrouter/google/gemini-"):
        return normalized

    examples = ", ".join(_KNOWN_GOOD_EXAMPLES)
    raise ValueError(
        f"Unsupported {field_name} '{raw}' after normalization to '{normalized}'. "
        f"Use one of: {examples}."
    )

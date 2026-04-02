"""Bounded structured diff helpers for AC14 output-comparison surfaces."""

from __future__ import annotations

from typing import Any


def summarize_mapping_mismatch(
    *,
    expected: dict[str, Any] | None,
    actual: dict[str, Any] | None,
    limit: int = 6,
) -> list[str]:
    """Return bounded path-level differences between two mapping outputs."""

    if expected is None and actual is None:
        return []
    if expected is None:
        return ["output unexpectedly present in actual result"]
    if actual is None:
        return ["output missing from actual result"]
    return collect_bounded_differences(
        expected=expected,
        actual=actual,
        prefix="",
        limit=limit,
    ) or ["outputs differed without a bounded field diff"]


def collect_bounded_differences(
    *,
    expected: Any,
    actual: Any,
    prefix: str,
    limit: int,
) -> list[str]:
    """Collect bounded path-level differences between expected and actual values."""

    if limit <= 0:
        return []

    if isinstance(expected, dict) and isinstance(actual, dict):
        differences: list[str] = []
        for key in sorted(set(expected) | set(actual)):
            if len(differences) >= limit:
                break
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in actual:
                differences.append(f"{path} missing from actual output")
                continue
            if key not in expected:
                differences.append(f"{path} unexpectedly present in actual output")
                continue
            differences.extend(
                collect_bounded_differences(
                    expected=expected[key],
                    actual=actual[key],
                    prefix=path,
                    limit=limit - len(differences),
                )
            )
        return differences

    if isinstance(expected, list) and isinstance(actual, list):
        list_differences: list[str] = []
        max_len = max(len(expected), len(actual))
        for index in range(max_len):
            if len(list_differences) >= limit:
                break
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            if index >= len(actual):
                list_differences.append(f"{path} missing from actual output")
                continue
            if index >= len(expected):
                list_differences.append(f"{path} unexpectedly present in actual output")
                continue
            list_differences.extend(
                collect_bounded_differences(
                    expected=expected[index],
                    actual=actual[index],
                    prefix=path,
                    limit=limit - len(list_differences),
                )
            )
        return list_differences

    if expected != actual:
        path = prefix or "value"
        return [f"{path} expected={expected!r} actual={actual!r}"]
    return []

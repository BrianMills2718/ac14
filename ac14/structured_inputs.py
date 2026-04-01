"""Shared structured-input loading helpers for discovery and realistic acceptance."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]


InputFormat = Literal["json", "jsonl", "csv", "yaml", "text"]


def detect_input_format(path: Path) -> InputFormat:
    """Detect the supported input format from a path suffix."""

    suffix = path.suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".jsonl":
        return "jsonl"
    if suffix == ".csv":
        return "csv"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    return "text"


def load_input(path: Path, input_format: InputFormat | None = None) -> object:
    """Load a supported local input file into its native Python structure."""

    normalized_format = input_format or detect_input_format(path)
    if normalized_format == "json":
        return json.loads(path.read_text())
    if normalized_format == "jsonl":
        return [
            json.loads(line)
            for line in path.read_text().splitlines()
            if line.strip()
        ]
    if normalized_format == "csv":
        with path.open(newline="") as handle:
            rows: list[dict[str, Any]] = []
            for row in csv.DictReader(handle):
                if None in row:
                    raise ValueError("csv structured input row has more columns than the header")
                rows.append(
                    {
                        cast(str, key): _coerce_csv_cell(value)
                        for key, value in row.items()
                    },
                )
            return rows
    if normalized_format == "yaml":
        return yaml.safe_load(path.read_text())
    return path.read_text().splitlines()


def load_structured_input_records(path: Path | str) -> list[dict[str, Any]]:
    """Load a structured input artifact as a sequence of object records.

    This is the shared contract for realistic-input execution surfaces. It keeps
    the acceptance path broad enough for structured non-JSON artifacts while
    still failing loud on inputs that do not describe object records.
    """

    normalized_path = Path(path)
    input_format = detect_input_format(normalized_path)
    if input_format == "text":
        raise ValueError("structured realistic-input execution does not support plain text inputs")

    payload = load_input(normalized_path, input_format)
    if isinstance(payload, dict):
        return [cast(dict[str, Any], payload)]
    if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
        return cast(list[dict[str, Any]], payload)
    raise ValueError("structured realistic-input execution requires object record inputs")


def discover_structured_input_candidates(input_dir: Path) -> list[Path]:
    """Return supported realistic-input candidates in stable preference order."""

    patterns = ("*.json", "*.jsonl", "*.csv", "*.yaml", "*.yml")
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(sorted(input_dir.glob(pattern)))
    return candidates


def _coerce_csv_cell(value: str | None) -> Any:
    """Decode JSON-like CSV cell payloads while leaving ordinary scalars alone."""

    if value is None:
        return ""
    stripped = value.strip()
    if not stripped:
        return ""
    if (
        stripped.startswith("[")
        and stripped.endswith("]")
    ) or (
        stripped.startswith("{")
        and stripped.endswith("}")
    ):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return value
    return value

"""Load shared meta-process policy values consumed by AC14 gates."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, cast

import yaml  # type: ignore[import-untyped]


DependencyProbePolicy = Literal["strict", "warn", "ignore"]
DEFAULT_DEPENDENCY_PROBE_POLICY: DependencyProbePolicy = "strict"
DEFAULT_META_PROCESS_CONFIG_PATH = Path(__file__).resolve().parents[1] / "meta-process.yaml"


def load_dependency_probe_policy(
    config_path: Path | str | None = None,
) -> DependencyProbePolicy:
    """Return the shared dependency-probe policy with a strict default."""

    resolved_path = Path(config_path) if config_path is not None else DEFAULT_META_PROCESS_CONFIG_PATH
    if not resolved_path.exists():
        return DEFAULT_DEPENDENCY_PROBE_POLICY
    payload = yaml.safe_load(resolved_path.read_text()) or {}
    meta_process = payload.get("meta_process", {})
    planning = meta_process.get("planning", {})
    raw_policy = planning.get("dependency_probe_policy", DEFAULT_DEPENDENCY_PROBE_POLICY)
    if raw_policy not in {"strict", "warn", "ignore"}:
        raise ValueError(
            f"unsupported dependency_probe_policy {raw_policy!r} in {resolved_path}",
        )
    return cast(DependencyProbePolicy, raw_policy)

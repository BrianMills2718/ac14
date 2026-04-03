"""Atomic text and JSON artifact writes for AC14 proof surfaces."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


def atomic_write_text(path: Path | str, content: str) -> None:
    """Write text to disk atomically within one filesystem directory."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.parent / (
        f".{destination.name}.{os.getpid()}.{time.time_ns()}.tmp"
    )
    temp_path.write_text(content)
    temp_path.replace(destination)


def atomic_write_json(path: Path | str, payload: Any) -> None:
    """Serialize one JSON payload and write it atomically."""

    atomic_write_text(
        path,
        json.dumps(payload, indent=2, sort_keys=True),
    )

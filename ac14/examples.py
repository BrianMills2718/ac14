"""Discovery of shipped AC14 blueprint examples and their realistic-input policy."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from ac14.loader import load_blueprint_dir


DEFAULT_EXAMPLES_ROOT = Path(__file__).resolve().parents[1] / "examples"
REALISTIC_INPUT_MANIFEST_NAME = "realistic_inputs.json"


class RealisticInputPolicy(BaseModel):
    """Explicit realistic-input profiles for one shipped example."""

    default_profile: str = Field(description="Profile name used by default for this shipped example.")
    profiles: dict[str, str] = Field(
        description="Absolute realistic-input artifact paths keyed by profile name.",
    )


class ShippedBlueprintExample(BaseModel):
    """Summary of one shipped blueprint example."""

    example_id: str = Field(description="Directory-derived shipped example identifier.")
    blueprint_dir: str = Field(description="Absolute path to the blueprint directory.")
    blueprint_id: str = Field(description="Blueprint identifier from metadata.")
    name: str = Field(description="Human-readable blueprint name.")
    realistic_input_policy: RealisticInputPolicy | None = Field(
        default=None,
        description="Explicit realistic-input profile policy for this shipped example when present.",
    )


def resolve_realistic_input_path(
    example: ShippedBlueprintExample | object,
    *,
    profile: str | None = None,
) -> Path:
    """Resolve a shipped example's realistic-input path through its explicit policy."""

    typed_example = (
        example
        if isinstance(example, ShippedBlueprintExample)
        else ShippedBlueprintExample.model_validate(example)
    )
    policy = typed_example.realistic_input_policy
    if policy is None:
        raise ValueError(f"shipped example {typed_example.example_id} has no realistic-input policy")
    selected_profile = policy.default_profile if profile is None else profile
    selected_path = policy.profiles.get(selected_profile)
    if selected_path is None:
        raise ValueError(
            f"shipped example {typed_example.example_id} has no realistic-input profile '{selected_profile}'",
        )
    return Path(selected_path)


def discover_shipped_blueprints(
    examples_root: Path | str | None = None,
) -> list[ShippedBlueprintExample]:
    """Discover shipped blueprint examples from the repo examples directory."""

    root = DEFAULT_EXAMPLES_ROOT if examples_root is None else Path(examples_root)
    discovered: list[ShippedBlueprintExample] = []
    for example_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        blueprint_dir = example_dir / "blueprint"
        if not blueprint_dir.is_dir():
            continue
        blueprint = load_blueprint_dir(blueprint_dir)
        realistic_input_policy = _load_realistic_input_policy(example_dir)
        discovered.append(
            ShippedBlueprintExample(
                example_id=example_dir.name,
                blueprint_dir=str(blueprint_dir),
                blueprint_id=blueprint.metadata.blueprint_id,
                name=blueprint.metadata.name,
                realistic_input_policy=realistic_input_policy,
            ),
        )

    if not discovered:
        raise ValueError(f"no shipped blueprints found under {root}")
    return discovered


def _load_realistic_input_policy(example_dir: Path) -> RealisticInputPolicy | None:
    """Load and validate the explicit realistic-input policy for one shipped example."""

    input_dir = example_dir / "input"
    if not input_dir.is_dir():
        return None

    manifest_path = input_dir / REALISTIC_INPUT_MANIFEST_NAME
    if not manifest_path.is_file():
        raise ValueError(
            f"shipped example {example_dir.name} has input artifacts but no {REALISTIC_INPUT_MANIFEST_NAME}",
        )

    payload = json.loads(manifest_path.read_text())
    default_profile = payload.get("default_profile")
    if not isinstance(default_profile, str) or not default_profile:
        raise ValueError(f"{manifest_path} must define a non-empty default_profile")

    raw_profiles = payload.get("profiles")
    if not isinstance(raw_profiles, dict) or not raw_profiles:
        raise ValueError(f"{manifest_path} must define a non-empty profiles mapping")

    resolved_profiles: dict[str, str] = {}
    for profile_name, relative_path in raw_profiles.items():
        if not isinstance(profile_name, str) or not profile_name:
            raise ValueError(f"{manifest_path} contains an invalid realistic-input profile name")
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError(f"{manifest_path} profile '{profile_name}' must map to a relative file path")
        candidate = (input_dir / relative_path).resolve()
        try:
            candidate.relative_to(input_dir.resolve())
        except ValueError as exc:
            raise ValueError(
                f"{manifest_path} profile '{profile_name}' must stay within the input directory",
            ) from exc
        if not candidate.is_file():
            raise ValueError(f"{manifest_path} profile '{profile_name}' points to a missing file")
        resolved_profiles[profile_name] = str(candidate)

    if default_profile not in resolved_profiles:
        raise ValueError(
            f"{manifest_path} default_profile '{default_profile}' is not present in profiles",
        )

    return RealisticInputPolicy(
        default_profile=default_profile,
        profiles=resolved_profiles,
    )

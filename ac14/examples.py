"""Discovery of shipped AC14 blueprint examples."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from ac14.loader import load_blueprint_dir


DEFAULT_EXAMPLES_ROOT = Path(__file__).resolve().parents[1] / "examples"


class ShippedBlueprintExample(BaseModel):
    """Summary of one shipped blueprint example."""

    example_id: str = Field(description="Directory-derived shipped example identifier.")
    blueprint_dir: str = Field(description="Absolute path to the blueprint directory.")
    blueprint_id: str = Field(description="Blueprint identifier from metadata.")
    name: str = Field(description="Human-readable blueprint name.")


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
        discovered.append(
            ShippedBlueprintExample(
                example_id=example_dir.name,
                blueprint_dir=str(blueprint_dir),
                blueprint_id=blueprint.metadata.blueprint_id,
                name=blueprint.metadata.name,
            ),
        )

    if not discovered:
        raise ValueError(f"no shipped blueprints found under {root}")
    return discovered

"""Loader for six-file AC14 blueprint bundles."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel

from ac14.models import (
    ArchitectureFile,
    ComponentsFile,
    FixturesFile,
    FrozenBlueprint,
    MetadataFile,
    SchemasFile,
    ValidationFile,
)

T = TypeVar("T", bound=BaseModel)


REQUIRED_FILES = {
    "metadata": "metadata.yaml",
    "schemas": "schemas.yaml",
    "components": "components.yaml",
    "architecture": "architecture.yaml",
    "validation": "validation.yaml",
    "fixtures": "fixtures.yaml",
}


def load_blueprint_dir(path: Path | str) -> FrozenBlueprint:
    """Load a six-file blueprint bundle into the canonical frozen blueprint model."""

    blueprint_dir = Path(path)
    metadata_file = _load_yaml_model(blueprint_dir / REQUIRED_FILES["metadata"], MetadataFile)
    schemas_file = _load_yaml_model(blueprint_dir / REQUIRED_FILES["schemas"], SchemasFile)
    components_file = _load_yaml_model(blueprint_dir / REQUIRED_FILES["components"], ComponentsFile)
    architecture_file = _load_yaml_model(
        blueprint_dir / REQUIRED_FILES["architecture"],
        ArchitectureFile,
    )
    validation_file = _load_yaml_model(blueprint_dir / REQUIRED_FILES["validation"], ValidationFile)
    fixtures_file = _load_yaml_model(blueprint_dir / REQUIRED_FILES["fixtures"], FixturesFile)

    return FrozenBlueprint(
        metadata=metadata_file.metadata,
        compiler_profile=metadata_file.compiler_profile,
        generation_policy=metadata_file.generation_policy,
        schemas=_index_by_id(schemas_file.schemas, "schema_id", "schema"),
        components=_index_by_id(components_file.components, "component_id", "component"),
        bindings=architecture_file.bindings,
        state_stores=_index_by_id(architecture_file.state_stores, "store_id", "state_store"),
        global_invariants=validation_file.global_invariants,
        evaluators=_index_by_id(validation_file.evaluators, "evaluator_id", "evaluator"),
        scenarios=_index_by_id(validation_file.scenarios, "scenario_id", "scenario"),
        fixtures=_index_by_id(fixtures_file.fixtures, "fixture_id", "fixture"),
    )


def _load_yaml_model(path: Path, model_type: type[T]) -> T:
    """Load one YAML file and parse it into the requested Pydantic model."""

    if not path.exists():
        raise FileNotFoundError(f"missing blueprint file: {path}")
    raw = yaml.safe_load(path.read_text())
    return model_type.model_validate(raw)


def _index_by_id(items: list[T], attr_name: str, kind: str) -> dict[str, T]:
    """Index a list of models by id and fail loud on duplicates."""

    indexed: dict[str, T] = {}
    for item in items:
        item_id = getattr(item, attr_name)
        if item_id in indexed:
            raise ValueError(f"duplicate {kind}_id detected: {item_id}")
        indexed[item_id] = item
    return indexed

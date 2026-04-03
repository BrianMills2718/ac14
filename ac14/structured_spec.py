"""Bounded structured-spec artifacts for front-half draft planning.

This module exists to give AC14 one truthful front-half input surface that is
larger than raw local data discovery but smaller than broad free-prose
NL-to-blueprint claims. The artifact is meant to be reviewable, typed, and
stable enough for later empirical comparison work.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field, model_validator


InterfaceKind = Literal["record", "scalar", "collection"]


class StructuredSpecField(BaseModel):
    """One declared field in a structured input or output surface."""

    field_name: str = Field(description="Stable field name in the declared shape.")
    field_type: str = Field(description="Compact type label for the declared field.")
    description: str = Field(description="Why this field exists and what it carries.")
    required: bool = Field(description="Whether downstream behavior depends on this field.")


class StructuredSpecInterface(BaseModel):
    """One declared external interface in the structured specification."""

    name: str = Field(description="Stable interface name used in hints and planning.")
    kind: InterfaceKind = Field(description="Whether this interface is record, scalar, or collection-shaped.")
    description: str = Field(description="Why this interface exists in the system boundary.")
    fields: list[StructuredSpecField] = Field(
        default_factory=list,
        description="Declared fields for record-shaped interfaces.",
    )

    @model_validator(mode="after")
    def _validate_fields(self) -> "StructuredSpecInterface":
        """Fail loud when the interface shape is internally inconsistent."""

        if self.kind != "record" and self.fields:
            raise ValueError("non-record structured spec interfaces must not declare fields")
        field_names = [field.field_name for field in self.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError(f"structured spec interface {self.name!r} contains duplicate field names")
        return self


class WorkflowHint(BaseModel):
    """One bounded workflow hint carried into blueprint drafting."""

    hint_id: str = Field(description="Stable workflow-hint identifier.")
    summary: str = Field(description="Bounded description of one workflow stage or decision.")
    input_names: list[str] = Field(
        default_factory=list,
        description="Declared interfaces consumed by this hint.",
    )
    output_names: list[str] = Field(
        default_factory=list,
        description="Declared interfaces produced by this hint.",
    )
    business_rules: list[str] = Field(
        default_factory=list,
        description="Specific business rules that should remain salient during drafting.",
    )


class StructuredSpecDocument(BaseModel):
    """Normalized structured-spec document accepted by the front half."""

    system_name: str = Field(description="Human-facing name for the requested system.")
    purpose: str = Field(description="Why the system exists and what outcome it should produce.")
    requirements: list[str] = Field(
        description="Explicit requirements that the draft blueprint must satisfy.",
    )
    success_criteria: list[str] = Field(
        default_factory=list,
        description="How the resulting system should be judged once built.",
    )
    business_rules: list[str] = Field(
        default_factory=list,
        description="Cross-cutting rules that should stay salient during decomposition.",
    )
    inputs: list[StructuredSpecInterface] = Field(
        default_factory=list,
        description="Declared external inputs for the requested system.",
    )
    outputs: list[StructuredSpecInterface] = Field(
        default_factory=list,
        description="Declared external outputs for the requested system.",
    )
    workflow_hints: list[WorkflowHint] = Field(
        default_factory=list,
        description="Bounded workflow hints that help the draft planner without freezing the graph.",
    )
    human_context_notes: list[str] = Field(
        default_factory=list,
        description="Optional bounded human notes that should remain visible during drafting.",
    )

    @model_validator(mode="after")
    def _validate_document(self) -> "StructuredSpecDocument":
        """Fail loud when the structured-spec contract is internally inconsistent."""

        if not self.requirements:
            raise ValueError("structured spec document requires at least one requirement")
        input_names = [item.name for item in self.inputs]
        output_names = [item.name for item in self.outputs]
        if len(input_names) != len(set(input_names)):
            raise ValueError("structured spec document contains duplicate input names")
        if len(output_names) != len(set(output_names)):
            raise ValueError("structured spec document contains duplicate output names")
        hint_ids = [hint.hint_id for hint in self.workflow_hints]
        if len(hint_ids) != len(set(hint_ids)):
            raise ValueError("structured spec document contains duplicate workflow hint ids")

        declared_names = {*input_names, *output_names}
        for hint in self.workflow_hints:
            unknown_inputs = sorted(name for name in hint.input_names if name not in declared_names)
            unknown_outputs = sorted(name for name in hint.output_names if name not in declared_names)
            if unknown_inputs:
                raise ValueError(
                    f"workflow hint {hint.hint_id!r} references unknown inputs {unknown_inputs!r}",
                )
            if unknown_outputs:
                raise ValueError(
                    f"workflow hint {hint.hint_id!r} references unknown outputs {unknown_outputs!r}",
                )
        return self


class StructuredSpecArtifact(BaseModel):
    """Persisted structured-spec artifact consumed by draft blueprint planning."""

    source_path: str = Field(description="Path to the raw structured-spec document.")
    spec: StructuredSpecDocument = Field(description="Normalized structured-spec document.")
    open_concerns: list[str] = Field(
        description="Bounded concerns that should remain visible during draft planning.",
    )


def build_structured_spec_artifact(
    input_path: Path | str,
    output_dir: Path | str,
) -> StructuredSpecArtifact:
    """Validate a raw structured spec and persist a normalized artifact."""

    source_path = Path(input_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    raw_payload = _load_structured_spec_payload(source_path)
    spec = StructuredSpecDocument.model_validate(raw_payload)
    artifact = StructuredSpecArtifact(
        source_path=str(source_path),
        spec=spec,
        open_concerns=_build_open_concerns(spec),
    )
    (destination / "structured_spec_artifact.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def _load_structured_spec_payload(path: Path) -> object:
    """Load one structured-spec document from JSON or YAML."""

    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(path.read_text())
    if suffix in {".yaml", ".yml"}:
        payload = yaml.safe_load(path.read_text())
        if payload is None:
            raise ValueError("structured spec document must not be empty")
        return payload
    raise ValueError("structured spec input must be .json, .yaml, or .yml")


def _build_open_concerns(spec: StructuredSpecDocument) -> list[str]:
    """Return bounded planning concerns derived from the structured spec."""

    concerns: list[str] = []
    if not spec.workflow_hints:
        concerns.append("structured spec does not declare workflow hints yet")
    if not spec.success_criteria:
        concerns.append("structured spec does not declare explicit success criteria yet")
    if not spec.human_context_notes:
        concerns.append("structured spec does not include bounded human context notes yet")
    return concerns

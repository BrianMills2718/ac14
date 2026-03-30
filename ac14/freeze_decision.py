"""Explicit freeze decisions and promotion for AC14 bundles."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from pydantic import BaseModel, Field

from ac14.draft_authoring import FreezeReadinessReport
from ac14.loader import REQUIRED_FILES, load_blueprint_dir
from ac14.models import ValidationFinding
from ac14.validation import validate_blueprint


class FreezeDecisionArtifact(BaseModel):
    """Persisted approve/block decision for bundle promotion."""

    source_bundle_dir: str = Field(description="Bundle directory evaluated for promotion.")
    readiness_report_path: str | None = Field(
        default=None,
        description="Readiness report used for the decision when available.",
    )
    approved: bool = Field(description="Whether the bundle is approved for freeze promotion.")
    decision_summary: str = Field(description="Compact summary of the freeze decision.")
    findings: list[ValidationFinding] = Field(
        description="Blocking or qualifying findings carried into the decision artifact.",
    )
    promoted_bundle_dir: str | None = Field(
        default=None,
        description="Promoted frozen bundle directory when approval succeeds.",
    )


def build_freeze_decision(
    bundle_dir: Path | str,
    output_dir: Path | str,
    *,
    readiness_report_path: Path | str | None = None,
) -> FreezeDecisionArtifact:
    """Persist a freeze decision and promote the bundle only when approved."""

    source_dir = Path(bundle_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    if readiness_report_path is not None:
        readiness_path = Path(readiness_report_path)
        readiness_report = FreezeReadinessReport.model_validate_json(readiness_path.read_text())
        findings = readiness_report.findings
        approved = readiness_report.ready
        decision_summary = (
            "bundle approved for freeze promotion"
            if approved
            else "bundle blocked by freeze-readiness findings"
        )
    else:
        blueprint = load_blueprint_dir(source_dir)
        validation_result = validate_blueprint(blueprint)
        findings = validation_result.findings
        approved = validation_result.passed
        readiness_path = None
        decision_summary = (
            "bundle approved for freeze promotion"
            if approved
            else "bundle blocked by frozen-blueprint validation findings"
        )

    promoted_bundle_dir: str | None = None
    if approved:
        promoted_dir = destination / "frozen_bundle"
        promoted_dir.mkdir(parents=True, exist_ok=True)
        for filename in REQUIRED_FILES.values():
            shutil.copy2(source_dir / filename, promoted_dir / filename)
        promoted_bundle_dir = str(promoted_dir)

    decision = FreezeDecisionArtifact(
        source_bundle_dir=str(source_dir),
        readiness_report_path=str(readiness_path) if readiness_report_path is not None else None,
        approved=approved,
        decision_summary=decision_summary,
        findings=findings,
        promoted_bundle_dir=promoted_bundle_dir,
    )
    (destination / "freeze_decision.json").write_text(
        json.dumps(decision.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return decision

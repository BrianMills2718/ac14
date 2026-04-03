"""Explicit retry-chain artifacts for blocked freeze decisions.

This module keeps remediation-driven retries reviewable by persisting every
intermediate artifact path instead of hiding refine -> materialize -> refreeze
behind transient orchestration.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from pydantic import BaseModel, Field

from ac14.blueprint_planning import (
    DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
    DEFAULT_BLUEPRINT_PLAN_MODEL,
    abuild_refined_draft_blueprint_plan,
)
from ac14.draft_authoring import materialize_draft_blueprint_bundle
from ac14.freeze_decision import abuild_freeze_decision


class FreezeRetryArtifact(BaseModel):
    """Persisted retry-chain artifact from blocked freeze input."""

    source_draft_blueprint_plan_path: str = Field(
        description="Original draft planning artifact retried by this chain.",
    )
    source_freeze_decision_path: str = Field(
        description="Blocked freeze decision that triggered this retry chain.",
    )
    refined_draft_blueprint_plan_path: str = Field(
        description="Refined draft planning artifact path emitted by the retry chain.",
    )
    refined_draft_bundle_dir: str = Field(
        description="Directory containing the rematerialized draft bundle.",
    )
    refreshed_freeze_readiness_report_path: str = Field(
        description="Freeze-readiness report path for the rematerialized bundle.",
    )
    refreshed_freeze_decision_path: str = Field(
        description="Refreshed freeze decision path after the retry chain reran freeze.",
    )
    refreshed_freeze_semantic_review_path: str | None = Field(
        default=None,
        description="Refreshed freeze-semantic review path when one was produced.",
    )
    refinement_round: int = Field(
        description="Refinement round number of the emitted refined planning artifact.",
    )
    approved: bool = Field(
        description="Whether the refreshed freeze decision approved promotion.",
    )
    summary: str = Field(
        description="Compact summary of the retry result.",
    )


async def abuild_freeze_retry_artifact(
    plan_artifact_path: Path | str,
    freeze_decision_path: Path | str,
    output_dir: Path | str,
    *,
    model: str = DEFAULT_BLUEPRINT_PLAN_MODEL,
    max_budget: float = DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
) -> FreezeRetryArtifact:
    """Run one explicit remediation-driven retry chain and persist its outputs."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    refined_plan = await abuild_refined_draft_blueprint_plan(
        plan_artifact_path=plan_artifact_path,
        freeze_decision_path=freeze_decision_path,
        output_dir=destination / "refined_plan",
        model=model,
        max_budget=max_budget,
    )
    refined_plan_path = destination / "refined_plan" / "draft_blueprint_plan.json"

    manifest = materialize_draft_blueprint_bundle(
        plan_artifact_path=refined_plan_path,
        output_dir=destination / "refined_bundle",
    )

    refreshed_freeze = await abuild_freeze_decision(
        bundle_dir=manifest.draft_bundle_dir,
        output_dir=destination / "refreshed_freeze_decision",
        readiness_report_path=manifest.freeze_readiness_report_path,
    )
    refreshed_freeze_decision_path = destination / "refreshed_freeze_decision" / "freeze_decision.json"

    summary = (
        "retry chain produced a freeze-approved refined bundle"
        if refreshed_freeze.approved
        else "retry chain kept the refined bundle blocked at freeze"
    )
    artifact = FreezeRetryArtifact(
        source_draft_blueprint_plan_path=str(Path(plan_artifact_path)),
        source_freeze_decision_path=str(Path(freeze_decision_path)),
        refined_draft_blueprint_plan_path=str(refined_plan_path),
        refined_draft_bundle_dir=manifest.draft_bundle_dir,
        refreshed_freeze_readiness_report_path=manifest.freeze_readiness_report_path,
        refreshed_freeze_decision_path=str(refreshed_freeze_decision_path),
        refreshed_freeze_semantic_review_path=refreshed_freeze.semantic_review_path,
        refinement_round=refined_plan.refinement_round,
        approved=refreshed_freeze.approved,
        summary=summary,
    )
    (destination / "freeze_retry_artifact.json").write_text(
        json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True),
    )
    return artifact


def build_freeze_retry_artifact(
    plan_artifact_path: Path | str,
    freeze_decision_path: Path | str,
    output_dir: Path | str,
    *,
    model: str = DEFAULT_BLUEPRINT_PLAN_MODEL,
    max_budget: float = DEFAULT_BLUEPRINT_PLAN_MAX_BUDGET,
) -> FreezeRetryArtifact:
    """Synchronous wrapper for the explicit remediation-driven retry chain."""

    return asyncio.run(
        abuild_freeze_retry_artifact(
            plan_artifact_path=plan_artifact_path,
            freeze_decision_path=freeze_decision_path,
            output_dir=output_dir,
            model=model,
            max_budget=max_budget,
        ),
    )

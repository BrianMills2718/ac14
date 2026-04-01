"""Tests for shipped example discovery."""

from __future__ import annotations

from pathlib import Path

import pytest

from ac14.examples import discover_shipped_blueprints, resolve_realistic_input_path


EXAMPLES_ROOT = Path(__file__).resolve().parents[1] / "examples"


def test_discover_shipped_blueprints_finds_multiple_examples() -> None:
    """Shipped blueprint discovery should find the growing proof suite."""

    examples = discover_shipped_blueprints(EXAMPLES_ROOT)

    assert len(examples) >= 2
    assert [example.example_id for example in examples] == sorted(
        example.example_id for example in examples
    )
    assert {example.example_id for example in examples} >= {
        "incident_alert_digest",
        "support_ticket_digest",
        "support_ticket_digest_auth_mix",
    }
    support_ticket = next(example for example in examples if example.example_id == "support_ticket_digest")
    assert support_ticket.realistic_input_policy is not None
    assert support_ticket.realistic_input_policy.default_profile == "default"
    assert set(support_ticket.realistic_input_policy.profiles) == {"default", "messy"}


def test_resolve_realistic_input_path_fails_loud_on_unknown_profile() -> None:
    """Shipped example realistic-input selection should fail loud on unknown profiles."""

    support_ticket = next(
        example
        for example in discover_shipped_blueprints(EXAMPLES_ROOT)
        if example.example_id == "support_ticket_digest"
    )

    resolved_default = resolve_realistic_input_path(support_ticket)
    resolved_messy = resolve_realistic_input_path(support_ticket, profile="messy")

    assert resolved_default.name == "realistic_ticket_batch.json"
    assert resolved_messy.name == "realistic_ticket_batch_messy.csv"
    with pytest.raises(ValueError, match="has no realistic-input profile 'missing'"):
        resolve_realistic_input_path(support_ticket, profile="missing")

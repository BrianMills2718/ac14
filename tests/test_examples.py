"""Tests for shipped example discovery."""

from __future__ import annotations

from pathlib import Path

from ac14.examples import discover_shipped_blueprints


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

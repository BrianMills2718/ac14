"""Manual reference components for the current ticket-digest semantic family."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from typing import Any

from ac14.models import FrozenBlueprint
from ac14.runtime import RuntimeComponent


class TicketParserComponent:
    """Normalize a raw support ticket into a parsed ticket."""

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Build a ParsedTicket payload from one RawTicket input."""

        raw_ticket = inputs["raw_ticket"]
        normalized_text = str(raw_ticket["body"]).strip().lower().rstrip(".")
        return {
            "parsed_ticket": {
                "ticket_id": raw_ticket["ticket_id"],
                "customer_id": raw_ticket.get("customer_id"),
                "issue_summary": raw_ticket["subject"],
                "normalized_text": normalized_text,
                "features": list(raw_ticket.get("tags", [])),
            },
        }


class IssueClassifierComponent:
    """Classify parsed tickets into a small issue taxonomy."""

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Emit one IssueLabel from one ParsedTicket input."""

        parsed_ticket = inputs["parsed_ticket"]
        normalized_text = parsed_ticket["normalized_text"]
        features = set(parsed_ticket.get("features", []))
        if "billing" in features or "billing" in normalized_text or "renewal" in normalized_text:
            label = "billing"
            reason = "keywords indicate a billing problem"
        elif "profile" in features or "account" in normalized_text:
            label = "account"
            reason = "profile update maps to account domain"
        elif "login" in normalized_text or "auth" in normalized_text:
            label = "auth"
            reason = "login language maps to auth"
        else:
            label = "general"
            reason = "no stronger category matched"
        return {
            "issue_label": {
                "ticket_id": parsed_ticket["ticket_id"],
                "label": label,
                "reason": reason,
            },
        }


class PriorityScorerComponent:
    """Assign a deterministic priority score from parsed ticket content."""

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Emit one PriorityScore from one ParsedTicket input."""

        parsed_ticket = inputs["parsed_ticket"]
        normalized_text = parsed_ticket["normalized_text"]
        features = set(parsed_ticket.get("features", []))
        if "billing" in features and "renewal" in features:
            priority_band = "high"
            score = 91
            reason = "renewal failure affects revenue"
        elif "profile" in features or "cannot" in normalized_text:
            priority_band = "medium"
            score = 55
            reason = "functional issue but no outage"
        else:
            priority_band = "low"
            score = 20
            reason = "issue appears non-urgent"
        return {
            "priority_score": {
                "ticket_id": parsed_ticket["ticket_id"],
                "priority_band": priority_band,
                "score": score,
                "reason": reason,
            },
        }


class CustomerContextLoaderComponent:
    """Load optional customer context from a small deterministic lookup table."""

    def __init__(self, customer_context_by_id: dict[str, dict[str, Any]]) -> None:
        """Store deterministic customer context fixtures keyed by customer_id."""

        self._customer_context_by_id = customer_context_by_id

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Return customer context when customer_id is available and known."""

        parsed_ticket = inputs["parsed_ticket"]
        customer_id = parsed_ticket.get("customer_id")
        if not customer_id or customer_id not in self._customer_context_by_id:
            return {}
        return {
            "customer_context": {
                "ticket_id": parsed_ticket["ticket_id"],
                **self._customer_context_by_id[customer_id],
            },
        }


class DigestAssemblerComponent:
    """Join required inputs and maintain a deterministic digest store."""

    def __init__(self, generated_at_by_ticket_id: dict[str, str]) -> None:
        """Initialize the store and deterministic timestamp source."""

        self._generated_at_by_ticket_id = generated_at_by_ticket_id
        self._entries_by_ticket_id: "OrderedDict[str, dict[str, Any]]" = OrderedDict()

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Join the latest inputs on ticket_id and emit digest entry plus store snapshot."""

        ticket = inputs["on_ticket"]
        label = inputs["on_label"]
        priority = inputs["on_priority"]
        customer_context = inputs.get("on_customer_context")
        ticket_id = ticket["ticket_id"]
        if label["ticket_id"] != ticket_id or priority["ticket_id"] != ticket_id:
            raise ValueError("required inputs must share the same ticket_id")
        if customer_context is not None and customer_context["ticket_id"] != ticket_id:
            raise ValueError("optional customer context must share the same ticket_id")

        digest_entry = {
            "ticket_id": ticket_id,
            "summary": ticket["issue_summary"],
            "label": label["label"],
            "priority_band": priority["priority_band"],
            "action_hint": _action_hint(label["label"], priority["priority_band"]),
        }
        if customer_context is not None:
            digest_entry["customer_tier"] = customer_context["customer_tier"]

        self._entries_by_ticket_id[ticket_id] = digest_entry
        generated_at = self._generated_at_by_ticket_id[ticket_id]
        digest_store = {
            "generated_at": generated_at,
            "entries": list(self._entries_by_ticket_id.values()),
        }
        return {"digest_entry": digest_entry, "digest_store": digest_store}


def build_support_ticket_digest_components() -> dict[str, RuntimeComponent]:
    """Create the deterministic component set for the shipped proof example."""

    return {
        "ticket_parser": TicketParserComponent(),
        "issue_classifier": IssueClassifierComponent(),
        "priority_scorer": PriorityScorerComponent(),
        "customer_context_loader": CustomerContextLoaderComponent(
            customer_context_by_id={
                "C-7": {
                    "customer_tier": "enterprise",
                    "open_ticket_count": 2,
                    "account_health": "watch",
                },
            },
        ),
        "digest_assembler": DigestAssemblerComponent(
            generated_at_by_ticket_id={
                "T-100": "2026-03-28T01:00:00Z",
                "T-101": "2026-03-28T01:05:00Z",
                "T-102": "2026-03-28T01:10:00Z",
            },
        ),
    }


def build_reference_components_for_blueprint(
    blueprint: FrozenBlueprint,
) -> dict[str, RuntimeComponent]:
    """Create reference components for one supported blueprint."""

    builders = build_reference_component_builders_for_blueprint(blueprint)
    return {
        component_id: builder()
        for component_id, builder in builders.items()
    }


def build_reference_component_builders_for_blueprint(
    blueprint: FrozenBlueprint,
) -> dict[str, Callable[[], RuntimeComponent]]:
    """Create reference component builders for one supported blueprint."""

    component_ids = _component_ids_by_semantic_responsibility(blueprint)
    customer_context_by_id = _customer_context_by_id_from_blueprint(
        blueprint,
        component_ids["load_customer_context"],
    )
    generated_at_by_ticket_id = _generated_at_by_ticket_id_from_blueprint(
        blueprint,
        component_ids["assemble_digest_entry_and_update_store"],
    )
    return {
        component_ids["parse_ticket"]: TicketParserComponent,
        component_ids["classify_issue"]: IssueClassifierComponent,
        component_ids["score_priority"]: PriorityScorerComponent,
        component_ids["load_customer_context"]: lambda: CustomerContextLoaderComponent(
            customer_context_by_id=dict(customer_context_by_id),
        ),
        component_ids["assemble_digest_entry_and_update_store"]: lambda: DigestAssemblerComponent(
            generated_at_by_ticket_id=dict(generated_at_by_ticket_id),
        ),
    }


def _action_hint(label: str, priority_band: str) -> str:
    """Derive a deterministic operator action hint from label and priority."""

    if label == "billing" and priority_band == "high":
        return "escalate to billing operations"
    if label == "account":
        return "route to account support"
    if priority_band == "high":
        return "escalate to specialist queue"
    return "queue for standard triage"


def _component_ids_by_semantic_responsibility(
    blueprint: FrozenBlueprint,
) -> dict[str, str]:
    """Resolve supported semantic responsibilities to concrete component ids."""

    supported = {
        "parse_ticket",
        "classify_issue",
        "score_priority",
        "load_customer_context",
        "assemble_digest_entry_and_update_store",
    }
    resolved: dict[str, str] = {}
    for component_id, component in blueprint.components.items():
        responsibility = component.semantic_responsibility
        if responsibility not in supported:
            raise ValueError(
                "reference component family does not support semantic responsibility "
                f"{responsibility!r} in component {component_id}"
            )
        if responsibility in resolved:
            raise ValueError(
                "reference component family requires unique semantic responsibilities, "
                f"but {responsibility!r} appears more than once"
            )
        resolved[responsibility] = component_id

    missing = sorted(supported.difference(resolved))
    if missing:
        raise ValueError(
            "reference component family is missing supported semantic responsibilities: "
            + ", ".join(missing)
        )
    return resolved


def _customer_context_by_id_from_blueprint(
    blueprint: FrozenBlueprint,
    customer_context_component_id: str,
) -> dict[str, dict[str, Any]]:
    """Derive deterministic customer-context records from blueprint fixtures."""

    context_by_customer_id: dict[str, dict[str, Any]] = {}
    for fixture in blueprint.fixtures.values():
        if fixture.component_id != customer_context_component_id:
            continue
        parsed_ticket = fixture.inputs.get("parsed_ticket")
        expected_context = fixture.expected_outputs.get("customer_context")
        if parsed_ticket is None or expected_context is None:
            continue
        customer_id = parsed_ticket.get("customer_id")
        if not customer_id:
            continue
        context_by_customer_id[str(customer_id)] = {
            key: value for key, value in expected_context.items() if key != "ticket_id"
        }
    return context_by_customer_id


def _generated_at_by_ticket_id_from_blueprint(
    blueprint: FrozenBlueprint,
    digest_assembler_component_id: str,
) -> dict[str, str]:
    """Derive deterministic digest-store timestamps from blueprint fixtures."""

    generated_at_by_ticket_id: dict[str, str] = {}
    for fixture in blueprint.fixtures.values():
        if fixture.component_id != digest_assembler_component_id:
            continue
        on_ticket = fixture.inputs.get("on_ticket")
        expected_store = fixture.expected_outputs.get("digest_store")
        if on_ticket is None or expected_store is None:
            continue
        generated_at = expected_store.get("generated_at")
        if generated_at is None:
            continue
        generated_at_by_ticket_id[str(on_ticket["ticket_id"])] = str(generated_at)
    return generated_at_by_ticket_id

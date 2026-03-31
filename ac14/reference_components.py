"""Manual reference components for the shipped AC14 proof-breadth slices."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from typing import Any

from ac14.models import FrozenBlueprint
from ac14.runtime import RuntimeComponent

TICKET_SIGNATURE = {
    "parse_ticket",
    "classify_issue",
    "score_priority",
    "load_customer_context",
    "assemble_digest_entry_and_update_store",
}

INCIDENT_SIGNATURE = {
    "parse_alert",
    "classify_impact",
    "score_urgency",
    "load_service_context",
    "assemble_incident_digest_and_update_store",
}


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
    """Load optional customer context from a deterministic lookup table."""

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
            "action_hint": _ticket_action_hint(label["label"], priority["priority_band"]),
        }
        if customer_context is not None:
            digest_entry["customer_tier"] = customer_context["customer_tier"]

        self._entries_by_ticket_id[ticket_id] = digest_entry
        digest_store = {
            "generated_at": self._generated_at_by_ticket_id[ticket_id],
            "entries": list(self._entries_by_ticket_id.values()),
        }
        return {"digest_entry": digest_entry, "digest_store": digest_store}


class AlertParserComponent:
    """Normalize a raw operational alert into a parsed alert."""

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Build a ParsedAlert payload from one RawAlert input."""

        raw_alert = inputs["raw_alert"]
        normalized_text = str(raw_alert["body"]).strip().lower().rstrip(".")
        return {
            "parsed_alert": {
                "alert_id": raw_alert["alert_id"],
                "service_id": raw_alert.get("service_id"),
                "alert_summary": raw_alert["title"],
                "normalized_text": normalized_text,
                "signals": list(raw_alert.get("tags", [])),
            },
        }


class ImpactClassifierComponent:
    """Classify parsed alerts into a small incident-impact taxonomy."""

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Emit one ImpactLabel from one ParsedAlert input."""

        parsed_alert = inputs["parsed_alert"]
        normalized_text = parsed_alert["normalized_text"]
        signals = set(parsed_alert.get("signals", []))
        if {"production", "error"} <= signals or "500" in normalized_text or "error" in normalized_text:
            label = "reliability"
            reason = "production error signals indicate reliability impact"
        elif "latency" in signals or "latency" in normalized_text:
            label = "performance"
            reason = "latency signals indicate a performance issue"
        elif "deploy" in signals:
            label = "release"
            reason = "deployment signals indicate release risk"
        else:
            label = "general"
            reason = "no stronger incident category matched"
        return {
            "impact_label": {
                "alert_id": parsed_alert["alert_id"],
                "label": label,
                "reason": reason,
            },
        }


class UrgencyScorerComponent:
    """Assign a deterministic urgency score from parsed alert content."""

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Emit one UrgencyScore from one ParsedAlert input."""

        parsed_alert = inputs["parsed_alert"]
        normalized_text = parsed_alert["normalized_text"]
        signals = set(parsed_alert.get("signals", []))
        if {"production", "error"} <= signals or "500" in normalized_text:
            urgency_band = "critical"
            score = 95
            reason = "production errors imply immediate customer impact"
        elif "latency" in signals:
            urgency_band = "high"
            score = 72
            reason = "latency spike may already affect customers"
        elif "deploy" in signals:
            urgency_band = "medium"
            score = 48
            reason = "deployment warning needs active watch"
        else:
            urgency_band = "low"
            score = 18
            reason = "alert appears informational"
        return {
            "urgency_score": {
                "alert_id": parsed_alert["alert_id"],
                "urgency_band": urgency_band,
                "score": score,
                "reason": reason,
            },
        }


class ServiceContextLoaderComponent:
    """Load optional service context from a deterministic lookup table."""

    def __init__(self, service_context_by_id: dict[str, dict[str, Any]]) -> None:
        """Store deterministic service-context fixtures keyed by service_id."""

        self._service_context_by_id = service_context_by_id

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Return service context when service_id is available and known."""

        parsed_alert = inputs["parsed_alert"]
        service_id = parsed_alert.get("service_id")
        if not service_id or service_id not in self._service_context_by_id:
            return {}
        return {
            "service_context": {
                "alert_id": parsed_alert["alert_id"],
                **self._service_context_by_id[service_id],
            },
        }


class IncidentAssemblerComponent:
    """Join required alert inputs and maintain a deterministic incident digest store."""

    def __init__(self, generated_at_by_alert_id: dict[str, str]) -> None:
        """Initialize the store and deterministic timestamp source."""

        self._generated_at_by_alert_id = generated_at_by_alert_id
        self._entries_by_alert_id: "OrderedDict[str, dict[str, Any]]" = OrderedDict()

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Join the latest inputs on alert_id and emit digest entry plus store snapshot."""

        alert = inputs["on_alert"]
        impact = inputs["on_impact"]
        urgency = inputs["on_urgency"]
        service_context = inputs.get("on_service_context")
        alert_id = alert["alert_id"]
        if impact["alert_id"] != alert_id or urgency["alert_id"] != alert_id:
            raise ValueError("required inputs must share the same alert_id")
        if service_context is not None and service_context["alert_id"] != alert_id:
            raise ValueError("optional service context must share the same alert_id")

        digest_entry = {
            "alert_id": alert_id,
            "summary": alert["alert_summary"],
            "label": impact["label"],
            "urgency_band": urgency["urgency_band"],
            "action_hint": _incident_action_hint(impact["label"], urgency["urgency_band"]),
        }
        if service_context is not None:
            digest_entry["service_tier"] = service_context["service_tier"]

        self._entries_by_alert_id[alert_id] = digest_entry
        digest_store = {
            "generated_at": self._generated_at_by_alert_id[alert_id],
            "entries": list(self._entries_by_alert_id.values()),
        }
        return {
            "incident_digest_entry": digest_entry,
            "incident_digest_store": digest_store,
        }


def build_support_ticket_digest_components() -> dict[str, RuntimeComponent]:
    """Create the deterministic component set for the ticket-digest slice."""

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


def build_incident_alert_digest_components() -> dict[str, RuntimeComponent]:
    """Create the deterministic component set for the incident-alert slice."""

    return {
        "alert_parser": AlertParserComponent(),
        "impact_classifier": ImpactClassifierComponent(),
        "urgency_scorer": UrgencyScorerComponent(),
        "service_context_loader": ServiceContextLoaderComponent(
            service_context_by_id={
                "S-1": {
                    "service_tier": "tier1",
                    "open_incident_count": 1,
                    "deployment_state": "degraded",
                },
            },
        ),
        "incident_assembler": IncidentAssemblerComponent(
            generated_at_by_alert_id={
                "A-100": "2026-03-30T02:00:00Z",
                "A-101": "2026-03-30T02:05:00Z",
                "A-102": "2026-03-30T02:10:00Z",
            },
        ),
    }


def build_reference_components_for_blueprint(
    blueprint: FrozenBlueprint,
) -> dict[str, RuntimeComponent]:
    """Create reference components for one supported blueprint."""

    builders = build_reference_component_builders_for_blueprint(blueprint)
    return {component_id: builder() for component_id, builder in builders.items()}


def build_reference_component_builders_for_blueprint(
    blueprint: FrozenBlueprint,
) -> dict[str, Callable[[], RuntimeComponent]]:
    """Create reference component builders for one supported blueprint."""

    signature = {
        component.semantic_responsibility
        for component in blueprint.components.values()
    }
    if signature == TICKET_SIGNATURE:
        return _build_ticket_reference_component_builders(blueprint)
    if signature == INCIDENT_SIGNATURE:
        return _build_incident_reference_component_builders(blueprint)
    raise ValueError(
        "reference components do not support this proof-breadth slice: "
        + ", ".join(sorted(signature))
    )


def _build_ticket_reference_component_builders(
    blueprint: FrozenBlueprint,
) -> dict[str, Callable[[], RuntimeComponent]]:
    """Create reference component builders for the ticket-digest slice."""

    component_ids = _component_ids_by_semantic_responsibility(blueprint, TICKET_SIGNATURE)
    customer_context_by_id = _lookup_records_from_blueprint(
        blueprint=blueprint,
        component_id=component_ids["load_customer_context"],
        input_port_name="parsed_ticket",
        output_port_name="customer_context",
        key_field="customer_id",
        output_id_field="ticket_id",
    )
    generated_at_by_ticket_id = _generated_at_by_upstream_id_from_blueprint(
        blueprint=blueprint,
        component_id=component_ids["assemble_digest_entry_and_update_store"],
        input_port_name="on_ticket",
        store_output_name="digest_store",
        upstream_id_field="ticket_id",
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


def _build_incident_reference_component_builders(
    blueprint: FrozenBlueprint,
) -> dict[str, Callable[[], RuntimeComponent]]:
    """Create reference component builders for the incident-alert slice."""

    component_ids = _component_ids_by_semantic_responsibility(blueprint, INCIDENT_SIGNATURE)
    service_context_by_id = _lookup_records_from_blueprint(
        blueprint=blueprint,
        component_id=component_ids["load_service_context"],
        input_port_name="parsed_alert",
        output_port_name="service_context",
        key_field="service_id",
        output_id_field="alert_id",
    )
    generated_at_by_alert_id = _generated_at_by_upstream_id_from_blueprint(
        blueprint=blueprint,
        component_id=component_ids["assemble_incident_digest_and_update_store"],
        input_port_name="on_alert",
        store_output_name="incident_digest_store",
        upstream_id_field="alert_id",
    )
    return {
        component_ids["parse_alert"]: AlertParserComponent,
        component_ids["classify_impact"]: ImpactClassifierComponent,
        component_ids["score_urgency"]: UrgencyScorerComponent,
        component_ids["load_service_context"]: lambda: ServiceContextLoaderComponent(
            service_context_by_id=dict(service_context_by_id),
        ),
        component_ids["assemble_incident_digest_and_update_store"]: lambda: IncidentAssemblerComponent(
            generated_at_by_alert_id=dict(generated_at_by_alert_id),
        ),
    }


def _ticket_action_hint(label: str, priority_band: str) -> str:
    """Derive a deterministic operator action hint from ticket label and priority."""

    if label == "billing" and priority_band == "high":
        return "escalate to billing operations"
    if label == "account":
        return "route to account support"
    if priority_band == "high":
        return "escalate to specialist queue"
    return "queue for standard triage"


def _incident_action_hint(label: str, urgency_band: str) -> str:
    """Derive a deterministic operator action hint from incident label and urgency."""

    if label == "reliability" and urgency_band == "critical":
        return "page incident commander"
    if label == "performance":
        return "open performance investigation"
    if urgency_band == "critical":
        return "page on-call immediately"
    if label == "release":
        return "coordinate with release manager"
    return "queue for standard operational triage"


def _component_ids_by_semantic_responsibility(
    blueprint: FrozenBlueprint,
    supported: set[str],
) -> dict[str, str]:
    """Resolve supported semantic responsibilities to concrete component ids."""

    resolved: dict[str, str] = {}
    for component_id, component in blueprint.components.items():
        responsibility = component.semantic_responsibility
        if responsibility not in supported:
            raise ValueError(
                "reference slice does not support semantic responsibility "
                f"{responsibility!r} in component {component_id}"
            )
        if responsibility in resolved:
            raise ValueError(
                "reference slice requires unique semantic responsibilities, "
                f"but {responsibility!r} appears more than once"
            )
        resolved[responsibility] = component_id

    missing = sorted(supported.difference(resolved))
    if missing:
        raise ValueError(
            "reference slice is missing required semantic responsibilities: "
            + ", ".join(missing)
        )
    return resolved


def _lookup_records_from_blueprint(
    *,
    blueprint: FrozenBlueprint,
    component_id: str,
    input_port_name: str,
    output_port_name: str,
    key_field: str,
    output_id_field: str,
) -> dict[str, dict[str, Any]]:
    """Derive deterministic lookup records from shipped blueprint fixtures."""

    records_by_key: dict[str, dict[str, Any]] = {}
    for fixture in blueprint.fixtures.values():
        if fixture.component_id != component_id:
            continue
        input_payload = fixture.inputs.get(input_port_name)
        expected_output = fixture.expected_outputs.get(output_port_name)
        if input_payload is None or expected_output is None:
            continue
        lookup_key = input_payload.get(key_field)
        if not lookup_key:
            continue
        records_by_key[str(lookup_key)] = {
            key: value
            for key, value in expected_output.items()
            if key != output_id_field
        }
    return records_by_key


def _generated_at_by_upstream_id_from_blueprint(
    *,
    blueprint: FrozenBlueprint,
    component_id: str,
    input_port_name: str,
    store_output_name: str,
    upstream_id_field: str,
) -> dict[str, str]:
    """Derive deterministic digest-store timestamps from shipped blueprint fixtures."""

    generated_at_by_id: dict[str, str] = {}
    for fixture in blueprint.fixtures.values():
        if fixture.component_id != component_id:
            continue
        upstream_payload = fixture.inputs.get(input_port_name)
        expected_store = fixture.expected_outputs.get(store_output_name)
        if upstream_payload is None or expected_store is None:
            continue
        generated_at = expected_store.get("generated_at")
        if generated_at is None:
            continue
        generated_at_by_id[str(upstream_payload[upstream_id_field])] = str(generated_at)
    return generated_at_by_id

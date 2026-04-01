"""Generated component emission and loading for supported AC14 proof-breadth slices."""

from __future__ import annotations

import hashlib
import importlib.util
from collections.abc import Callable
from typing import TYPE_CHECKING, Literal
from pathlib import Path
from types import ModuleType

from pydantic import BaseModel, Field

from ac14.codegen_context import CodegenContext, build_codegen_context
from ac14.models import PacketBundle
from ac14.packet_tests import materialize_packet_test_cases
from ac14.runtime import RuntimeComponent

GeneratorKind = Literal["deterministic", "llm"]
DEFAULT_LLM_MODEL = "gemini/gemini-2.5-flash-lite"
DEFAULT_LLM_MAX_BUDGET = 0.50

if TYPE_CHECKING:
    from ac14.llm_codegen import GeneratedModuleResponse


def generate_component_module_with_llm(
    context: CodegenContext,
    *,
    model: str = DEFAULT_LLM_MODEL,
    trace_id: str,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    task: str = "ac14_generate_component",
) -> GeneratedModuleResponse:
    """Lazily import the LLM codegen helper so non-LLM paths avoid import-time dependency failures."""

    from ac14.llm_codegen import generate_component_module_with_llm as _generate_component_module_with_llm

    return _generate_component_module_with_llm(
        context,
        model=model,
        trace_id=trace_id,
        max_budget=max_budget,
        task=task,
    )


async def agenerate_component_module_with_llm(
    context: CodegenContext,
    *,
    model: str = DEFAULT_LLM_MODEL,
    trace_id: str,
    max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    task: str = "ac14_generate_component",
) -> GeneratedModuleResponse:
    """Lazily import the async LLM codegen helper for callers already in an event loop."""

    from ac14.llm_codegen import agenerate_component_module_with_llm as _agenerate_component_module_with_llm

    return await _agenerate_component_module_with_llm(
        context,
        model=model,
        trace_id=trace_id,
        max_budget=max_budget,
        task=task,
    )

class GeneratedPackage(BaseModel):
    """Record of files emitted for a generated component package."""

    output_dir: str = Field(description="Directory containing emitted modules.")
    generator_kind: GeneratorKind = Field(description="Generator used for emitted modules.")
    module_paths: dict[str, str] = Field(
        description="Module paths keyed by component identifier.",
    )


def emit_generated_package(
    packet_bundle: PacketBundle,
    output_dir: Path | str,
    *,
    generator_kind: GeneratorKind = "deterministic",
    llm_model: str = DEFAULT_LLM_MODEL,
    llm_max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    trace_id_prefix: str = "ac14/generated_codegen",
) -> GeneratedPackage:
    """Emit standalone Python modules for all components in a packet bundle."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "__init__.py").write_text('"""Generated AC14 components."""\n')

    packet_cases = materialize_packet_test_cases(packet_bundle)
    module_paths: dict[str, str] = {}
    for component_id, packet in packet_bundle.packets.items():
        context = build_codegen_context(packet, packet_cases[component_id])
        module_source = _render_module_source(
            context,
            generator_kind=generator_kind,
            llm_model=llm_model,
            llm_max_budget=llm_max_budget,
            trace_id=f"{trace_id_prefix}/{component_id}",
        )
        module_path = destination / f"{component_id}.py"
        module_path.write_text(module_source)
        module_paths[component_id] = str(module_path)

    return GeneratedPackage(
        output_dir=str(destination),
        generator_kind=generator_kind,
        module_paths=module_paths,
    )


async def aemit_generated_package(
    packet_bundle: PacketBundle,
    output_dir: Path | str,
    *,
    generator_kind: GeneratorKind = "deterministic",
    llm_model: str = DEFAULT_LLM_MODEL,
    llm_max_budget: float = DEFAULT_LLM_MAX_BUDGET,
    trace_id_prefix: str = "ac14/generated_codegen",
) -> GeneratedPackage:
    """Async package emission for callers already running inside an event loop."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "__init__.py").write_text('"""Generated AC14 components."""\n')

    packet_cases = materialize_packet_test_cases(packet_bundle)
    module_paths: dict[str, str] = {}
    for component_id, packet in packet_bundle.packets.items():
        context = build_codegen_context(packet, packet_cases[component_id])
        module_source = await _arender_module_source(
            context,
            generator_kind=generator_kind,
            llm_model=llm_model,
            llm_max_budget=llm_max_budget,
            trace_id=f"{trace_id_prefix}/{component_id}",
        )
        module_path = destination / f"{component_id}.py"
        module_path.write_text(module_source)
        module_paths[component_id] = str(module_path)

    return GeneratedPackage(
        output_dir=str(destination),
        generator_kind=generator_kind,
        module_paths=module_paths,
    )


def load_generated_component_builders(
    generated_package: GeneratedPackage,
) -> dict[str, Callable[[], RuntimeComponent]]:
    """Load build_component factories from emitted modules."""

    builders: dict[str, Callable[[], RuntimeComponent]] = {}
    for component_id, module_path_str in generated_package.module_paths.items():
        module_path = Path(module_path_str)
        module = _load_module(component_id, module_path)
        build_component = getattr(module, "build_component")
        builders[component_id] = build_component
    return builders


def _load_module(component_id: str, module_path: Path) -> ModuleType:
    """Import one emitted component module from disk."""

    module_hash = hashlib.sha1(str(module_path).encode("utf-8")).hexdigest()[:10]
    module_name = f"ac14_generated_{component_id}_{module_hash}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load generated module for {component_id} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _render_module_source(
    context: CodegenContext,
    *,
    generator_kind: GeneratorKind,
    llm_model: str,
    llm_max_budget: float,
    trace_id: str,
) -> str:
    """Render a standalone module for one supported semantic responsibility."""

    if generator_kind == "llm":
        response = generate_component_module_with_llm(
            context,
            model=llm_model,
            trace_id=trace_id,
            max_budget=llm_max_budget,
        )
        return response.module_code
    if context.semantic_responsibility == "parse_ticket":
        return _render_parse_ticket_module()
    if context.semantic_responsibility == "classify_issue":
        return _render_classify_issue_module()
    if context.semantic_responsibility == "score_priority":
        return _render_score_priority_module()
    if context.semantic_responsibility == "load_customer_context":
        return _render_load_customer_context_module(context)
    if context.semantic_responsibility == "assemble_digest_entry_and_update_store":
        return _render_digest_assembler_module(context)
    if context.semantic_responsibility == "parse_alert":
        return _render_parse_alert_module()
    if context.semantic_responsibility == "classify_impact":
        return _render_classify_impact_module()
    if context.semantic_responsibility == "score_urgency":
        return _render_score_urgency_module()
    if context.semantic_responsibility == "load_service_context":
        return _render_load_service_context_module(context)
    if context.semantic_responsibility == "assemble_incident_digest_and_update_store":
        return _render_incident_assembler_module(context)
    raise ValueError(
        "unsupported semantic responsibility for generated proof-breadth slice: "
        f"{context.semantic_responsibility}"
    )


async def _arender_module_source(
    context: CodegenContext,
    *,
    generator_kind: GeneratorKind,
    llm_model: str,
    llm_max_budget: float,
    trace_id: str,
) -> str:
    """Async module rendering for callers already inside an event loop."""

    if generator_kind == "llm":
        response = await agenerate_component_module_with_llm(
            context,
            model=llm_model,
            trace_id=trace_id,
            max_budget=llm_max_budget,
        )
        return response.module_code
    return _render_module_source(
        context,
        generator_kind=generator_kind,
        llm_model=llm_model,
        llm_max_budget=llm_max_budget,
        trace_id=trace_id,
    )


def _render_parse_ticket_module() -> str:
    """Render the parser component module."""

    return """\
\"\"\"Generated component for parse_ticket.\"\"\"

from __future__ import annotations

from typing import Any


class GeneratedComponent:
    \"\"\"Normalize a raw ticket into a parsed ticket.\"\"\"

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Build ParsedTicket from RawTicket.\"\"\"

        raw_ticket = inputs[\"raw_ticket\"]
        normalized_text = str(raw_ticket[\"body\"]).strip().lower().rstrip(\".\")
        return {
            \"parsed_ticket\": {
                \"ticket_id\": raw_ticket[\"ticket_id\"],
                \"customer_id\": raw_ticket.get(\"customer_id\"),
                \"issue_summary\": raw_ticket[\"subject\"],
                \"normalized_text\": normalized_text,
                \"features\": list(raw_ticket.get(\"tags\", [])),
            },
        }


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated parser component.\"\"\"

    return GeneratedComponent()
"""


def _render_classify_issue_module() -> str:
    """Render the classifier component module."""

    return """\
\"\"\"Generated component for classify_issue.\"\"\"

from __future__ import annotations

from typing import Any


class GeneratedComponent:
    \"\"\"Classify parsed tickets into a small deterministic taxonomy.\"\"\"

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Emit an IssueLabel from ParsedTicket.\"\"\"

        parsed_ticket = inputs[\"parsed_ticket\"]
        normalized_text = parsed_ticket[\"normalized_text\"]
        features = set(parsed_ticket.get(\"features\", []))
        if \"billing\" in features or \"billing\" in normalized_text or \"renewal\" in normalized_text:
            label = \"billing\"
            reason = \"keywords indicate a billing problem\"
        elif \"profile\" in features or \"account\" in normalized_text:
            label = \"account\"
            reason = \"profile update maps to account domain\"
        elif \"login\" in normalized_text or \"auth\" in normalized_text:
            label = \"auth\"
            reason = \"login language maps to auth\"
        else:
            label = \"general\"
            reason = \"no stronger category matched\"
        return {
            \"issue_label\": {
                \"ticket_id\": parsed_ticket[\"ticket_id\"],
                \"label\": label,
                \"reason\": reason,
            },
        }


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated classifier component.\"\"\"

    return GeneratedComponent()
"""


def _render_score_priority_module() -> str:
    """Render the priority scorer component module."""

    return """\
\"\"\"Generated component for score_priority.\"\"\"

from __future__ import annotations

from typing import Any


class GeneratedComponent:
    \"\"\"Assign deterministic priority scores from ParsedTicket.\"\"\"

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Emit a PriorityScore from ParsedTicket.\"\"\"

        parsed_ticket = inputs[\"parsed_ticket\"]
        normalized_text = parsed_ticket[\"normalized_text\"]
        features = set(parsed_ticket.get(\"features\", []))
        if \"billing\" in features and \"renewal\" in features:
            priority_band = \"high\"
            score = 91
            reason = \"renewal failure affects revenue\"
        elif \"profile\" in features or \"cannot\" in normalized_text:
            priority_band = \"medium\"
            score = 55
            reason = \"functional issue but no outage\"
        else:
            priority_band = \"low\"
            score = 20
            reason = \"issue appears non-urgent\"
        return {
            \"priority_score\": {
                \"ticket_id\": parsed_ticket[\"ticket_id\"],
                \"priority_band\": priority_band,
                \"score\": score,
                \"reason\": reason,
            },
        }


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated priority scorer component.\"\"\"

    return GeneratedComponent()
"""


def _render_load_customer_context_module(context: CodegenContext) -> str:
    """Render the customer-context loader component module."""

    context_by_customer_id: dict[str, dict[str, object]] = {}
    for case in context.packet_test_cases:
        parsed_ticket = case.inputs.get("parsed_ticket")
        expected_context = case.expected_outputs.get("customer_context")
        if parsed_ticket is None or expected_context is None:
            continue
        customer_id = parsed_ticket.get("customer_id")
        if not customer_id:
            continue
        context_by_customer_id[str(customer_id)] = {
            key: value for key, value in expected_context.items() if key != "ticket_id"
        }
    return f"""\
\"\"\"Generated component for load_customer_context.\"\"\"

from __future__ import annotations

from typing import Any


CONTEXT_BY_CUSTOMER_ID = {context_by_customer_id!r}


class GeneratedComponent:
    \"\"\"Load optional customer context from fixture-derived constants.\"\"\"

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Emit customer context when a known customer_id is present.\"\"\"

        parsed_ticket = inputs[\"parsed_ticket\"]
        customer_id = parsed_ticket.get(\"customer_id\")
        if not customer_id or customer_id not in CONTEXT_BY_CUSTOMER_ID:
            return {{}}
        return {{
            \"customer_context\": {{
                \"ticket_id\": parsed_ticket[\"ticket_id\"],
                **CONTEXT_BY_CUSTOMER_ID[str(customer_id)],
            }},
        }}


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated customer-context component.\"\"\"

    return GeneratedComponent()
"""


def _render_digest_assembler_module(context: CodegenContext) -> str:
    """Render the digest assembler component module."""

    generated_at_by_ticket_id: dict[str, str] = {}
    for case in context.packet_test_cases:
        ticket = case.inputs.get("on_ticket")
        expected_store = case.expected_outputs.get("digest_store")
        if ticket is None or expected_store is None:
            continue
        generated_at = expected_store.get("generated_at")
        if generated_at is not None:
            generated_at_by_ticket_id[str(ticket["ticket_id"])] = str(generated_at)
    return f"""\
\"\"\"Generated component for assemble_digest_entry_and_update_store.\"\"\"

from __future__ import annotations

from collections import OrderedDict
from typing import Any


GENERATED_AT_BY_TICKET_ID = {generated_at_by_ticket_id!r}


class GeneratedComponent:
    \"\"\"Join required inputs and maintain a deterministic digest store.\"\"\"

    def __init__(self) -> None:
        \"\"\"Initialize fixture-derived store state.\"\"\"

        self._entries_by_ticket_id: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Emit digest_entry and digest_store from the latest joined inputs.\"\"\"

        ticket = inputs[\"on_ticket\"]
        label = inputs[\"on_label\"]
        priority = inputs[\"on_priority\"]
        customer_context = inputs.get(\"on_customer_context\")
        ticket_id = ticket[\"ticket_id\"]
        if label[\"ticket_id\"] != ticket_id or priority[\"ticket_id\"] != ticket_id:
            raise ValueError(\"required inputs must share the same ticket_id\")
        if customer_context is not None and customer_context[\"ticket_id\"] != ticket_id:
            raise ValueError(\"optional customer context must share the same ticket_id\")

        digest_entry = {{
            \"ticket_id\": ticket_id,
            \"summary\": ticket[\"issue_summary\"],
            \"label\": label[\"label\"],
            \"priority_band\": priority[\"priority_band\"],
            \"action_hint\": _action_hint(label[\"label\"], priority[\"priority_band\"]),
        }}
        if customer_context is not None:
            digest_entry[\"customer_tier\"] = customer_context[\"customer_tier\"]

        self._entries_by_ticket_id[ticket_id] = digest_entry
        digest_store = {{
            \"generated_at\": GENERATED_AT_BY_TICKET_ID[ticket_id],
            \"entries\": list(self._entries_by_ticket_id.values()),
        }}
        return {{\"digest_entry\": digest_entry, \"digest_store\": digest_store}}


def _action_hint(label: str, priority_band: str) -> str:
    \"\"\"Derive a deterministic action hint.\"\"\"

    if label == \"billing\" and priority_band == \"high\":
        return \"escalate to billing operations\"
    if label == \"account\":
        return \"route to account support\"
    if priority_band == \"high\":
        return \"escalate to specialist queue\"
    return \"queue for standard triage\"


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated digest assembler component.\"\"\"

    return GeneratedComponent()
"""


def _render_parse_alert_module() -> str:
    """Render the alert parser component module."""

    return """\
\"\"\"Generated component for parse_alert.\"\"\"

from __future__ import annotations

from typing import Any


class GeneratedComponent:
    \"\"\"Normalize a raw alert into a parsed alert.\"\"\"

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Build ParsedAlert from RawAlert.\"\"\"

        raw_alert = inputs[\"raw_alert\"]
        normalized_text = str(raw_alert[\"body\"]).strip().lower().rstrip(\".\")
        return {
            \"parsed_alert\": {
                \"alert_id\": raw_alert[\"alert_id\"],
                \"service_id\": raw_alert.get(\"service_id\"),
                \"alert_summary\": raw_alert[\"title\"],
                \"normalized_text\": normalized_text,
                \"signals\": list(raw_alert.get(\"tags\", [])),
            },
        }


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated alert parser component.\"\"\"

    return GeneratedComponent()
"""


def _render_classify_impact_module() -> str:
    """Render the incident-impact classifier component module."""

    return """\
\"\"\"Generated component for classify_impact.\"\"\"

from __future__ import annotations

from typing import Any


class GeneratedComponent:
    \"\"\"Classify parsed alerts into a deterministic incident-impact taxonomy.\"\"\"

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Emit an ImpactLabel from ParsedAlert.\"\"\"

        parsed_alert = inputs[\"parsed_alert\"]
        normalized_text = parsed_alert[\"normalized_text\"]
        signals = set(parsed_alert.get(\"signals\", []))
        if {\"production\", \"error\"} <= signals or \"500\" in normalized_text or \"error\" in normalized_text:
            label = \"reliability\"
            reason = \"production error signals indicate reliability impact\"
        elif \"latency\" in signals or \"latency\" in normalized_text:
            label = \"performance\"
            reason = \"latency signals indicate a performance issue\"
        elif \"deploy\" in signals:
            label = \"release\"
            reason = \"deployment signals indicate release risk\"
        else:
            label = \"general\"
            reason = \"no stronger incident category matched\"
        return {
            \"impact_label\": {
                \"alert_id\": parsed_alert[\"alert_id\"],
                \"label\": label,
                \"reason\": reason,
            },
        }


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated incident-impact classifier.\"\"\"

    return GeneratedComponent()
"""


def _render_score_urgency_module() -> str:
    """Render the urgency scorer component module."""

    return """\
\"\"\"Generated component for score_urgency.\"\"\"

from __future__ import annotations

from typing import Any


class GeneratedComponent:
    \"\"\"Assign deterministic urgency scores from ParsedAlert.\"\"\"

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Emit an UrgencyScore from ParsedAlert.\"\"\"

        parsed_alert = inputs[\"parsed_alert\"]
        normalized_text = parsed_alert[\"normalized_text\"]
        signals = set(parsed_alert.get(\"signals\", []))
        if {\"production\", \"error\"} <= signals or \"500\" in normalized_text:
            urgency_band = \"critical\"
            score = 95
            reason = \"production errors imply immediate customer impact\"
        elif \"latency\" in signals:
            urgency_band = \"high\"
            score = 72
            reason = \"latency spike may already affect customers\"
        elif \"deploy\" in signals:
            urgency_band = \"medium\"
            score = 48
            reason = \"deployment warning needs active watch\"
        else:
            urgency_band = \"low\"
            score = 18
            reason = \"alert appears informational\"
        return {
            \"urgency_score\": {
                \"alert_id\": parsed_alert[\"alert_id\"],
                \"urgency_band\": urgency_band,
                \"score\": score,
                \"reason\": reason,
            },
        }


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated urgency scorer component.\"\"\"

    return GeneratedComponent()
"""


def _render_load_service_context_module(context: CodegenContext) -> str:
    """Render the service-context loader component module."""

    context_by_service_id: dict[str, dict[str, object]] = {}
    for case in context.packet_test_cases:
        parsed_alert = case.inputs.get("parsed_alert")
        expected_context = case.expected_outputs.get("service_context")
        if parsed_alert is None or expected_context is None:
            continue
        service_id = parsed_alert.get("service_id")
        if not service_id:
            continue
        context_by_service_id[str(service_id)] = {
            key: value for key, value in expected_context.items() if key != "alert_id"
        }
    return f"""\
\"\"\"Generated component for load_service_context.\"\"\"

from __future__ import annotations

from typing import Any


CONTEXT_BY_SERVICE_ID = {context_by_service_id!r}


class GeneratedComponent:
    \"\"\"Load optional service context from fixture-derived constants.\"\"\"

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Emit service context when a known service_id is present.\"\"\"

        parsed_alert = inputs[\"parsed_alert\"]
        service_id = parsed_alert.get(\"service_id\")
        if not service_id or service_id not in CONTEXT_BY_SERVICE_ID:
            return {{}}
        return {{
            \"service_context\": {{
                \"alert_id\": parsed_alert[\"alert_id\"],
                **CONTEXT_BY_SERVICE_ID[str(service_id)],
            }},
        }}


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated service-context component.\"\"\"

    return GeneratedComponent()
"""


def _render_incident_assembler_module(context: CodegenContext) -> str:
    """Render the incident digest assembler component module."""

    generated_at_by_alert_id: dict[str, str] = {}
    for case in context.packet_test_cases:
        alert = case.inputs.get("on_alert")
        expected_store = case.expected_outputs.get("incident_digest_store")
        if alert is None or expected_store is None:
            continue
        generated_at = expected_store.get("generated_at")
        if generated_at is not None:
            generated_at_by_alert_id[str(alert["alert_id"])] = str(generated_at)
    return f"""\
\"\"\"Generated component for assemble_incident_digest_and_update_store.\"\"\"

from __future__ import annotations

from collections import OrderedDict
from typing import Any


GENERATED_AT_BY_ALERT_ID = {generated_at_by_alert_id!r}


class GeneratedComponent:
    \"\"\"Join required inputs and maintain a deterministic incident digest store.\"\"\"

    def __init__(self) -> None:
        \"\"\"Initialize fixture-derived incident store state.\"\"\"

        self._entries_by_alert_id: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        \"\"\"Emit incident_digest_entry and incident_digest_store from the latest joined inputs.\"\"\"

        alert = inputs[\"on_alert\"]
        impact = inputs[\"on_impact\"]
        urgency = inputs[\"on_urgency\"]
        service_context = inputs.get(\"on_service_context\")
        alert_id = alert[\"alert_id\"]
        if impact[\"alert_id\"] != alert_id or urgency[\"alert_id\"] != alert_id:
            raise ValueError(\"required inputs must share the same alert_id\")
        if service_context is not None and service_context[\"alert_id\"] != alert_id:
            raise ValueError(\"optional service context must share the same alert_id\")

        incident_digest_entry = {{
            \"alert_id\": alert_id,
            \"summary\": alert[\"alert_summary\"],
            \"label\": impact[\"label\"],
            \"urgency_band\": urgency[\"urgency_band\"],
            \"action_hint\": _action_hint(impact[\"label\"], urgency[\"urgency_band\"]),
        }}
        if service_context is not None:
            incident_digest_entry[\"service_tier\"] = service_context[\"service_tier\"]

        self._entries_by_alert_id[alert_id] = incident_digest_entry
        incident_digest_store = {{
            \"generated_at\": GENERATED_AT_BY_ALERT_ID[alert_id],
            \"entries\": list(self._entries_by_alert_id.values()),
        }}
        return {{
            \"incident_digest_entry\": incident_digest_entry,
            \"incident_digest_store\": incident_digest_store,
        }}


def _action_hint(label: str, urgency_band: str) -> str:
    \"\"\"Derive a deterministic incident action hint.\"\"\"

    if label == \"reliability\" and urgency_band == \"critical\":
        return \"page incident commander\"
    if label == \"performance\":
        return \"open performance investigation\"
    if urgency_band == \"critical\":
        return \"page on-call immediately\"
    if label == \"release\":
        return \"coordinate with release manager\"
    return \"queue for standard operational triage\"


def build_component() -> GeneratedComponent:
    \"\"\"Build the generated incident digest assembler component.\"\"\"

    return GeneratedComponent()
"""

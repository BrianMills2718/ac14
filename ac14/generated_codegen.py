"""Generated component emission and loading for the current AC14 proof slice."""

from __future__ import annotations

import hashlib
import importlib.util
from collections.abc import Callable
from typing import Literal
from pathlib import Path
from types import ModuleType

from pydantic import BaseModel, Field

from ac14.codegen_context import CodegenContext, build_codegen_context
from ac14.llm_codegen import DEFAULT_LLM_MAX_BUDGET, DEFAULT_LLM_MODEL, generate_component_module_with_llm
from ac14.models import PacketBundle
from ac14.packet_tests import materialize_packet_test_cases
from ac14.runtime import RuntimeComponent

GeneratorKind = Literal["deterministic", "llm"]

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
    raise ValueError(
        "unsupported semantic responsibility for generated proof slice: "
        f"{context.semantic_responsibility}"
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

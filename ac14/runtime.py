"""Reference runtime for executing frozen AC14 blueprints."""

from __future__ import annotations

from typing import Any, Protocol

from ac14.models import FrozenBlueprint, InputPort
from ac14.packets import compile_packets


class RuntimeComponent(Protocol):
    """Protocol implemented by reference or generated components."""

    def execute(self, inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Execute one component against port-keyed inputs."""


def run_blueprint_once(
    blueprint: FrozenBlueprint,
    implementations: dict[str, RuntimeComponent],
    initial_inputs: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Execute one pass through the blueprint using topological order."""

    packet_bundle = compile_packets(blueprint)
    pending_inputs: dict[str, dict[str, dict[str, Any]]] = {
        component_id: dict(initial_inputs.get(component_id, {}))
        for component_id in blueprint.components
    }
    outputs_by_component: dict[str, dict[str, dict[str, Any]]] = {}

    for component_id in packet_bundle.recomposition_plan.execution_order:
        component = blueprint.components[component_id]
        inputs = pending_inputs.get(component_id, {})
        _ensure_required_inputs(component_id, component.input_ports, inputs)
        outputs = implementations[component_id].execute(inputs)
        outputs_by_component[component_id] = outputs

        for binding in packet_bundle.recomposition_plan.bindings:
            if binding.from_component != component_id:
                continue
            payload = outputs.get(binding.from_port)
            if payload is None:
                continue
            pending_inputs.setdefault(binding.to_component, {})[binding.to_port] = payload

    return outputs_by_component


def _ensure_required_inputs(
    component_id: str,
    input_ports: list[InputPort],
    inputs: dict[str, dict[str, Any]],
) -> None:
    """Raise when a required port is absent from a runtime invocation."""

    missing_ports = sorted(port.name for port in input_ports if port.required and port.name not in inputs)
    if missing_ports:
        raise ValueError(f"component {component_id} missing required inputs: {missing_ports}")

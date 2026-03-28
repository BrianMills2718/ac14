"""Tests for generated component emission and loading."""

from __future__ import annotations

from pathlib import Path

from ac14.generated_codegen import emit_generated_package, load_generated_component_builders
from ac14.loader import load_blueprint_dir
from ac14.packets import compile_packets


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples" / "support_ticket_digest" / "blueprint"


def test_emit_generated_package_writes_component_modules(tmp_path: Path) -> None:
    """Generation should emit one standalone Python module per component."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)

    generated_package = emit_generated_package(packet_bundle, tmp_path / "generated")

    assert Path(generated_package.module_paths["ticket_parser"]).exists()
    assert Path(generated_package.module_paths["digest_assembler"]).exists()


def test_load_generated_component_builders_imports_generated_modules(tmp_path: Path) -> None:
    """Generated modules should load into build_component factories."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)
    generated_package = emit_generated_package(packet_bundle, tmp_path / "generated")

    builders = load_generated_component_builders(generated_package)
    outputs = builders["ticket_parser"]().execute(
        blueprint.fixtures["happy_path_ticket_parser"].inputs,
    )

    assert outputs == blueprint.fixtures["happy_path_ticket_parser"].expected_outputs

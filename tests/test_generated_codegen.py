"""Tests for generated component emission and loading."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from pytest import MonkeyPatch

from ac14.generated_codegen import emit_generated_package, load_generated_component_builders
from ac14.loader import load_blueprint_dir
from ac14.llm_codegen import GeneratedModuleValidationError
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


def test_emit_generated_package_llm_path_uses_llm_generator(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """LLM generator mode should delegate module source generation through the LLM path."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)

    fake_llm_generator = Mock(
        return_value=type(
            "Resp",
            (),
            {
                "module_code": (
                    "class GeneratedComponent:\n"
                    "    def execute(self, inputs):\n"
                    "        return {}\n\n"
                    "def build_component():\n"
                    "    return GeneratedComponent()\n"
                ),
            },
        )(),
    )
    monkeypatch.setattr(
        "ac14.generated_codegen.generate_component_module_with_llm",
        fake_llm_generator,
    )

    generated_package = emit_generated_package(
        packet_bundle,
        tmp_path / "generated",
        generator_kind="llm",
        llm_model="test-model",
        llm_max_budget=0.1,
        trace_id_prefix="test/llm",
    )

    assert generated_package.generator_kind == "llm"
    assert fake_llm_generator.call_count == len(packet_bundle.packets)


def test_failed_llm_module_source_is_persisted_for_diagnosis(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """Failed LLM module source should remain inspectable even when validation aborts emission."""

    blueprint = load_blueprint_dir(EXAMPLE_DIR)
    packet_bundle = compile_packets(blueprint)

    def _raise_validation_error(*args: object, **kwargs: object) -> object:
        raise GeneratedModuleValidationError(
            component_id="ticket_parser",
            module_code="import max\n",
            message="generated module for ticket_parser failed during import-time validation: No module named 'max'",
        )

    monkeypatch.setattr(
        "ac14.generated_codegen.generate_component_module_with_llm",
        _raise_validation_error,
    )

    try:
        emit_generated_package(
            packet_bundle,
            tmp_path / "generated",
            generator_kind="llm",
            llm_model="test-model",
            llm_max_budget=0.1,
            trace_id_prefix="test/llm",
        )
    except GeneratedModuleValidationError:
        pass
    else:  # pragma: no cover - fail-loud assertion
        raise AssertionError("expected GeneratedModuleValidationError")

    failed_module = tmp_path / "generated" / "ticket_parser.failed.py"
    validation_error = tmp_path / "generated" / "ticket_parser.validation_error.json"
    assert failed_module.exists()
    assert "import max" in failed_module.read_text()
    assert validation_error.exists()

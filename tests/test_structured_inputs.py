"""Tests for shared structured-input loading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ac14.structured_inputs import detect_input_format, load_structured_input_records


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        ("records.json", json.dumps([{"id": "A-1"}, {"id": "A-2"}], indent=2)),
        ("records.jsonl", '{"id": "A-1"}\n{"id": "A-2"}\n'),
        ("records.csv", "id,status\nA-1,open\nA-2,closed\n"),
        ("records.yaml", "- id: A-1\n- id: A-2\n"),
    ],
)
def test_load_structured_input_records_supports_supported_formats(
    tmp_path: Path,
    filename: str,
    content: str,
) -> None:
    """Shared structured-input loading should support the structured formats used by discovery."""

    input_path = tmp_path / filename
    input_path.write_text(content)

    payload = load_structured_input_records(input_path)

    assert len(payload) == 2
    assert payload[0]["id"] == "A-1"


def test_load_structured_input_records_fails_loud_on_text(tmp_path: Path) -> None:
    """Plain text should remain unsupported for realistic-input execution."""

    input_path = tmp_path / "notes.txt"
    input_path.write_text("one\n two\n")

    with pytest.raises(ValueError, match="does not support plain text"):
        load_structured_input_records(input_path)

    assert detect_input_format(input_path) == "text"


def test_load_structured_input_records_decodes_json_like_csv_cells(tmp_path: Path) -> None:
    """CSV loading should preserve list-valued fields encoded as JSON strings."""

    input_path = tmp_path / "records.csv"
    input_path.write_text(
        'ticket_id,tags\nSUP-1,"[""billing"", ""renewal""]"\n',
    )

    payload = load_structured_input_records(input_path)

    assert payload == [{"ticket_id": "SUP-1", "tags": ["billing", "renewal"]}]

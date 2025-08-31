import json
from cli.utils.formatters import format_output, simplify_edge


def test_format_output_json_compact_and_fields_and_ids_only():
    data = [
        {"uuid": "u1", "name": "DEPENDS_ON", "fact": "A->B", "score": 0.9, "group_id": "g"},
        {"uuid": "u2", "name": "DEPENDS_ON", "fact": "B->C", "score": 0.7, "group_id": "g"},
    ]

    # Compact JSON (no spaces) and field filter
    out = format_output(data, format="json", full_output=True, fields=["uuid", "score"])
    assert out == "[{\"uuid\":\"u1\",\"score\":0.9},{\"uuid\":\"u2\",\"score\":0.7}]"

    # JSONL/NDJSON
    out_l = format_output(data, format="jsonl", full_output=True)
    lines = out_l.splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["uuid"] == "u1"
    assert json.loads(lines[1])["uuid"] == "u2"

    # ids-only collapses to list of UUIDs
    out_ids = format_output(data, format="json", full_output=True, ids_only=True)
    assert out_ids == "[\"u1\",\"u2\"]"


def test_simplify_edge_includes_score_and_uuid_when_present():
    edge = {"name": "DEPENDS_ON", "fact": "A->B", "group_id": "g", "score": 0.8, "uuid": "u1"}
    simplified = simplify_edge(edge)
    assert simplified == {
        "name": "DEPENDS_ON",
        "fact": "A->B",
        "group_id": "g",
        "score": 0.8,
        "uuid": "u1",
    }


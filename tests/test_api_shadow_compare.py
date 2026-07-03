from __future__ import annotations

import json

from api_shadow_compare.cli import main
from api_shadow_compare.core import compare, flatten, render_json, render_text

OLD = {"a": {"id": "a", "status": 200, "latency_ms": 100, "body": {"x": 1}}}
NEW = {"a": {"id": "a", "status": 500, "latency_ms": 300, "body": {"x": 2, "y": 3}}}


def test_flatten_nested_body() -> None:
    assert flatten({"a": {"b": 1}}) == {"a.b": 1}


def test_status_change_detected() -> None:
    assert any(d.kind == "status-change" for d in compare(OLD, NEW, 2))


def test_latency_regression_detected() -> None:
    assert any(d.kind == "latency-regression" for d in compare(OLD, NEW, 2))


def test_new_field_detected() -> None:
    assert any(d.kind == "field-added" for d in compare(OLD, NEW, 9))


def test_text_clean_message() -> None:
    assert "No API drift" in render_text([])


def test_json_render() -> None:
    assert json.loads(render_json(compare(OLD, NEW, 2)))[0]["request_id"] == "a"


def test_cli_help(capsys) -> None:
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    assert "API" in capsys.readouterr().out

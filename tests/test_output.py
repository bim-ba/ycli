"""TDD for ycli.output — the `--format` renderer over pydantic results."""

from __future__ import annotations

import io
import json

import pytest
import yaml
from pydantic import BaseModel, RootModel
from rich.console import Console

from ycli.output import OutputFormat, PrettyStrategy, Serializer, SerializationStrategy


class Item(BaseModel):
    id: int
    name: str
    parent: dict | None = None


class Items(RootModel[list[Item]]):
    pass


def _console(*, tty: bool) -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    return Console(file=buf, force_terminal=tty, width=120), buf


def _render(model: BaseModel, output_format: OutputFormat, console: Console) -> None:
    Serializer.serialize(model, SerializationStrategy.from_format(output_format), console)


def test_auto_pipes_raw_json():
    console, buf = _console(tty=False)
    _render(Item(id=1, name="alice"), OutputFormat.auto, console)
    out = buf.getvalue()
    assert out.endswith("\n")
    assert json.loads(out) == {"id": 1, "name": "alice", "parent": None}


def test_auto_pretty_on_tty():
    console, buf = _console(tty=True)
    _render(Item(id=1, name="alice"), OutputFormat.auto, console)
    out = buf.getvalue()
    assert "alice" in out and "name" in out  # rendered as a field/value table


def test_explicit_json_on_tty_is_highlighted():
    console, buf = _console(tty=True)
    _render(Item(id=7, name="bob"), OutputFormat.json, console)
    out = buf.getvalue()
    assert "bob" in out and "id" in out


def test_yaml_format():
    console, buf = _console(tty=False)
    _render(Item(id=2, name="carol"), OutputFormat.yaml, console)
    assert yaml.safe_load(buf.getvalue()) == {"id": 2, "name": "carol", "parent": None}


def test_pretty_list_renders_table():
    console, buf = _console(tty=True)
    _render(Items([Item(id=1, name="a"), Item(id=2, name="b")]), OutputFormat.pretty, console)
    out = buf.getvalue()
    assert "name" in out and "a" in out and "b" in out


def test_prettify_dispatch():
    strategy = PrettyStrategy()
    assert strategy._prettify("scalar") == "scalar"
    assert strategy._prettify([1, 2]).row_count == 2  # scalar list → single-column table
    assert strategy._prettify({"k": "v"}).row_count == 1  # dict → kv table


def test_cell_rendering():
    strategy = PrettyStrategy()
    assert strategy._cell(None) == ""
    assert strategy._cell("x") == "x"
    assert strategy._cell(3) == "3"
    assert strategy._cell({"a": 1}) == '{"a": 1}'
    assert strategy._cell([1, 2]) == "[1, 2]"

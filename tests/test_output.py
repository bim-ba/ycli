"""TDD for ycli.cli.output — the `--format` renderer over pydantic results."""

from __future__ import annotations

import io
import json

import yaml
from pydantic import BaseModel, RootModel
from rich.console import Console
from rich.table import Table

from ycli.cli.output import OutputFormat, PrettyStrategy, SerializationStrategy, Serializer


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


def test_render_scalar_and_null():
    strategy = PrettyStrategy()
    assert strategy._render("scalar") == "scalar"
    assert strategy._render(3) == "3"
    assert strategy._render(None) is None


def test_render_object_omits_null_fields():
    strategy = PrettyStrategy()
    table = strategy._render({"a": "1", "b": None})  # b dropped; a remains as a one-row table
    assert isinstance(table, Table)
    assert table.row_count == 1
    assert strategy._render({"a": None}) is None  # all-null object is omitted entirely


def test_render_multi_field_object_is_kv_table():
    strategy = PrettyStrategy()
    table = strategy._render({"a": "1", "b": "2"})
    assert isinstance(table, Table)
    assert table.row_count == 2


def test_render_nested_multifield_object_in_cell():
    strategy = PrettyStrategy()
    table = strategy._render({"name": "root", "meta": {"a": "1", "b": "2"}})
    assert isinstance(table, Table)
    assert table.row_count == 2  # name row + meta row (a nested table in the cell)


def test_render_scalar_list_joins_and_empty_is_omitted():
    strategy = PrettyStrategy()
    assert strategy._render(["alpha", "beta"]) == "alpha, beta"
    assert strategy._render([]) is None


def test_render_object_list_table_drops_all_empty_columns():
    strategy = PrettyStrategy()
    table = strategy._render(
        [{"id": "1", "name": "a", "extra": None}, {"id": "2", "name": "b", "extra": None}]
    )
    assert isinstance(table, Table)
    assert [column.header for column in table.columns] == ["id", "name"]  # all-null 'extra' gone


def test_render_object_list_with_mixed_nondict_item():
    strategy = PrettyStrategy()
    table = strategy._render([{"a": "1", "b": "2"}, "loose"])
    assert isinstance(table, Table)
    assert [column.header for column in table.columns] == ["a", "b"]  # columns from the dict only
    assert table.row_count == 2  # the non-dict row renders as empty cells


def test_render_all_null_model_prints_blank_line():
    console, buf = _console(tty=True)

    class Empty(BaseModel):
        a: int | None = None

    PrettyStrategy().render(Empty(), console)
    assert buf.getvalue().strip() == ""

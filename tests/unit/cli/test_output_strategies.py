"""output.py serialization strategies."""

from __future__ import annotations

import csv
import json
from io import StringIO
from typing import Annotated, Any

import pytest
from pydantic import BaseModel, ConfigDict, Field, RootModel
from rich.console import Console

from ycli.cli.output import (
    AutoStrategy,
    CSVStrategy,
    JSONStrategy,
    MarkdownStrategy,
    NameStrategy,
    NDJSONStrategy,
    OutputFormat,
    PrettyStrategy,
    SerializationStrategy,
    YAMLStrategy,
    has_names,
)
from ycli.yandex.core.listing import Listing
from ycli.yandex.errors import YandexUnexpectedReplyError
from ycli.yandex.models import ItemList, Listed
from ycli.yandex.sync.marks import Identity


class _Row(BaseModel):
    key: str
    name: str


class _M(BaseModel):
    key: str


def _console(*, terminal: bool) -> tuple[Console, StringIO]:
    buf = StringIO()
    return Console(file=buf, force_terminal=terminal, width=200), buf


def test_json_strategy_emits_pristine_json_when_piped():
    console, buf = _console(terminal=False)
    JSONStrategy().render(_Row(key="ABC-1", name="x"), console)
    assert buf.getvalue().strip() == '{"key":"ABC-1","name":"x"}'


def test_yaml_strategy_emits_yaml():
    console, buf = _console(terminal=False)
    YAMLStrategy().render(_Row(key="ABC-1", name="x"), console)
    assert "key: ABC-1" in buf.getvalue()


def test_pretty_strategy_renders_bare_key_on_terminal():
    console, buf = _console(terminal=True)
    PrettyStrategy().render(_Row(key="ABC-1", name="x"), console)
    out = buf.getvalue()
    assert "ABC-1" in out
    assert "tracker.yandex.ru" not in out


def test_pretty_strategy_renders_bare_key_when_piped():
    console, buf = _console(terminal=False)
    PrettyStrategy().render(_Row(key="ABC-1", name="x"), console)
    out = buf.getvalue()
    assert "ABC-1" in out
    assert "tracker.yandex.ru" not in out


def test_auto_strategy_is_json_when_piped():
    console, buf = _console(terminal=False)
    AutoStrategy().render(_Row(key="ABC-1", name="x"), console)
    assert buf.getvalue().strip().startswith("{")


def test_from_format_maps_each_choice():
    assert isinstance(SerializationStrategy.from_format(OutputFormat.json), JSONStrategy)
    assert isinstance(SerializationStrategy.from_format(OutputFormat.yaml), YAMLStrategy)
    assert isinstance(SerializationStrategy.from_format(OutputFormat.pretty), PrettyStrategy)
    assert isinstance(SerializationStrategy.from_format(OutputFormat.auto), AutoStrategy)


def test_pretty_strategy_renders_list_of_dicts():
    class _RowList(BaseModel):
        rows: list[_Row]

    console, buf = _console(terminal=True)
    PrettyStrategy().render(_RowList(rows=[_Row(key="A", name="foo")]), console)
    out = buf.getvalue()
    assert "A" in out


def test_pretty_strategy_renders_scalar_list_as_join():
    console, buf = _console(terminal=True)

    class _Tags(BaseModel):
        tags: list[str]

    PrettyStrategy().render(_Tags(tags=["alpha", "beta"]), console)
    assert "alpha, beta" in buf.getvalue()


def test_pretty_strategy_shows_no_results_for_empty_model():
    console, buf = _console(terminal=True)

    class _Empty(BaseModel):
        maybe: str | None = None

    PrettyStrategy().render(_Empty(), console)
    assert "No results" in buf.getvalue()


def test_pretty_strategy_renders_bool_as_check_and_cross():
    console, buf = _console(terminal=True)

    class _Flags(BaseModel):
        ok: bool
        bad: bool

    PrettyStrategy().render(_Flags(ok=True, bad=False), console)
    out = buf.getvalue()
    assert "✓" in out
    assert "✗" in out
    assert "True" not in out and "False" not in out


def test_pretty_strategy_prints_api_text_that_looks_like_markup_verbatim():
    console, buf = _console(terminal=True)

    class _Issue(BaseModel):
        summary: str
        tags: list[str]
        meta: dict[str, str]

    PrettyStrategy().render(
        _Issue(
            summary="Crash in [bug] handler", tags=["[a]", "b"], meta={"[k]": "Closing [/oops]"}
        ),
        console,
    )
    out = buf.getvalue()
    assert "Crash in [bug] handler" in out
    assert "[a], b" in out
    assert "[k]" in out and "Closing [/oops]" in out


def test_pretty_strategy_prints_markup_like_keys_and_headers_verbatim():
    console, buf = _console(terminal=True)

    class _Rows(BaseModel):
        rows: list[dict[str, str]]

    PrettyStrategy().render(_Rows(rows=[{"[col]": "[/x]"}]), console)
    out = buf.getvalue()
    assert "[col]" in out
    assert "[/x]" in out


class _Status(BaseModel):
    key: str
    display: str | None = None


class _Node(BaseModel):
    """A model that holds itself, an annotated model and a field of more than one kind."""

    key: str
    status: _Status | None = None
    resolution: Annotated[_Status, Field(description="how it ended")] | None = None
    tags: list[str] = []
    parent: _Node | None = None
    owner: _Status | str | None = None
    created_at: str | None = Field(default=None, serialization_alias="createdAt")


class _Bare(BaseModel):
    model_config = ConfigDict(extra="allow")


def _printed(strategy: SerializationStrategy, result: BaseModel) -> str:
    console, buf = _console(terminal=False)
    strategy.render(result, console)
    return buf.getvalue()


_NODE = _Node(
    key="A-1",
    status=_Status(key="open", display="Открыт"),
    tags=["a", "b"],
    parent=_Node(key="A-0"),
    owner="ann",
    created_at="today",
)
_HEADER = (
    "key,status.key,status.display,resolution.key,resolution.display,tags,parent,owner,createdAt"
)


def test_csv_lays_a_nested_object_out_in_columns_and_keeps_a_list_as_json_text():
    header, row = list(csv.reader(StringIO(_printed(CSVStrategy(), _NODE))))
    assert ",".join(header) == _HEADER
    cells = dict(zip(header, row, strict=True))
    assert cells["status.display"] == "Открыт"
    assert cells["resolution.key"] == ""
    assert json.loads(cells["tags"]) == ["a", "b"]
    # A model that holds itself is one cell, not columns without end.
    assert json.loads(cells["parent"])["key"] == "A-0"
    assert cells["owner"] == "ann"


def test_the_columns_are_the_fields_the_model_declares_whatever_the_items_hold():
    listed = Listed[_Node](items=[_Node(key="A-1"), _NODE], truncated=True, next="eJw")
    header, first, second = list(csv.reader(StringIO(_printed(CSVStrategy(), listed))))
    assert ",".join(header) == _HEADER
    assert first == ["A-1", "", "", "", "", "[]", "", "", ""]
    assert second[0] == "A-1" and second[-1] == "today"


def test_csv_quotes_what_would_break_a_row_and_leaves_a_formula_as_it_came():
    printed = _printed(CSVStrategy(), _Row(key='=1+1, "x"', name="two\nlines"))
    assert printed == 'key,name\n"=1+1, ""x""","two\nlines"\n'
    assert list(csv.reader(StringIO(printed)))[1] == ['=1+1, "x"', "two\nlines"]


def test_markdown_escapes_a_pipe_and_a_line_break_inside_a_cell():
    printed = _printed(MarkdownStrategy(), _Row(key="a|b", name="one\r\ntwo\nthree"))
    assert printed == "| key | name |\n| --- | --- |\n| a\\|b | one<br>two<br>three |\n"


def test_ndjson_prints_the_items_alone_one_on_a_line():
    listed = Listed[_Row](items=[_Row(key="A", name="Имя"), _Row(key="B", name="y")], next="eJw")
    assert _printed(NDJSONStrategy(), listed) == (
        '{"key":"A","name":"Имя"}\n{"key":"B","name":"y"}\n'
    )
    assert _printed(NDJSONStrategy(), _M(key="A")) == '{"key":"A"}\n'


def test_items_that_are_not_objects_are_one_column():
    assert _printed(CSVStrategy(), ItemList[str](["a", "b"])) == "value\na\nb\n"
    assert _printed(CSVStrategy(), ItemList[int]([1])) == "value\n1\n"
    assert _printed(NDJSONStrategy(), ItemList[str](["a"])) == '"a"\n'


def test_an_object_that_declares_no_field_is_one_cell():
    printed = _printed(CSVStrategy(), _Bare.model_validate({"a": 1}))
    assert list(csv.reader(StringIO(printed))) == [["value"], ['{"a":1}']]


def test_a_root_model_of_one_object_is_that_object():
    assert _printed(CSVStrategy(), RootModel[_Row](_Row(key="A", name="x"))) == "key,name\nA,x\n"


def test_from_format_maps_the_table_and_line_formats():
    assert isinstance(SerializationStrategy.from_format(OutputFormat.csv), CSVStrategy)
    assert isinstance(SerializationStrategy.from_format(OutputFormat.markdown), MarkdownStrategy)
    assert isinstance(SerializationStrategy.from_format(OutputFormat.ndjson), NDJSONStrategy)


def test_an_empty_listing_has_the_header_of_what_the_command_says_it_returns():
    nothing = Listed[_Row](items=[])
    assert _printed(CSVStrategy(Listing[_Row]), nothing) == "key,name\n"
    assert _printed(MarkdownStrategy(ItemList[_Row]), nothing) == "| key | name |\n| --- | --- |\n"
    assert _printed(CSVStrategy(Listing[_Row | _M]), nothing) == "key,name\n"
    assert _printed(CSVStrategy(Listing[Annotated[_Status | _Row, "kinds"]]), nothing) == (
        "key,display,name\n"
    )
    assert _printed(CSVStrategy(Listed[_Status] | None), nothing) == "key,display\n"
    assert _printed(CSVStrategy(Listing[str]), nothing) == "value\n"
    assert _printed(CSVStrategy(Listing[dict[str, int]]), nothing) == "value\n"


def test_a_result_that_is_no_model_gives_no_columns():
    nothing = Listed[_Row](items=[])
    for declared in (None, str, int | None, Any):
        assert _printed(CSVStrategy(declared), nothing) == ""


def test_the_declared_kinds_come_first_and_what_else_came_is_added():
    printed = _printed(CSVStrategy(Listing[_M]), Listed[Any](items=[_Row(key="A", name="x")]))
    assert printed == "key,name\nA,x\n"


class _Named(BaseModel):
    id: int
    key: Annotated[str | None, Identity()] = Field(default=None, serialization_alias="issueKey")


def test_name_prints_the_marked_field_of_each_item_on_a_line():
    listed = Listed[_Named](items=[_Named(id=1, key="A-1"), _Named(id=2, key="A-2")], next="eJw")
    assert _printed(NameStrategy(), listed) == "A-1\nA-2\n"
    assert _printed(NameStrategy(), _Named(id=1, key="A-1")) == "A-1\n"
    assert _printed(NameStrategy(), ItemList[str](["bug", "ui"])) == "bug\nui\n"
    assert isinstance(SerializationStrategy.from_format(OutputFormat.name), NameStrategy)


def test_a_result_that_is_not_what_the_command_declares_is_printed_as_json_under_name():
    # The plan of --dry-run comes back in place of the object: it has no name.
    assert _printed(NameStrategy(), _Row(key="A", name="x")) == '{"key":"A","name":"x"}\n'


def test_a_command_has_names_when_every_kind_it_returns_marks_one_field():
    assert has_names(Listing[_Named]) and has_names(_Named) and has_names(Listing[str])
    assert not has_names(Listing[_Named | _Row])
    assert not has_names(_Row) and not has_names(None) and not has_names(str)


def test_name_prints_nothing_and_says_which_item_the_reply_left_unnamed():
    listed = Listed[_Named](items=[_Named(id=1, key="A-1"), _Named(id=2), _Named(id=3)])
    console, buf = _console(terminal=False)
    with pytest.raises(YandexUnexpectedReplyError) as failed:
        NameStrategy().render(listed, console)
    assert str(failed.value) == (
        "item 2 of this listing has no issueKey (and 1 more): `-o name` cannot name it. "
        "The request was sent: a command that changes something has changed it"
    )
    assert buf.getvalue() == ""
    with pytest.raises(YandexUnexpectedReplyError, match="item 1 of this listing has no issueKey:"):
        NameStrategy().render(_Named(id=1), console)

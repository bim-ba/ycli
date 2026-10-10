"""Every command of a contract case, printed as ``csv``, ``markdown`` and ``ndjson``.

What ``-o json`` prints is the measure: the same items, under the same keys, and stdout that
its own parser reads whole.
"""

from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import replace
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import BaseModel, RootModel
from typer.testing import CliRunner

from tests.contract.test_contract import CASES, _serve
from ycli.cli.app import app
from ycli.cli.inject import NO_NAME
from ycli.cli.output import _columns
from ycli.yandex.errors import YandexUnexpectedReplyError
from ycli.yandex.models import APIModel

if TYPE_CHECKING:
    from collections.abc import Iterator

    from tests.contract import Case

CLI_CASES = [case for case in CASES if case.cli is not None]
#: A ``|`` that ends a cell: one the cell's own text holds is escaped with a backslash.
_CELL_END = re.compile(r"(?<!\\)\|")


def _printed(case: Case, output_format: str, monkeypatch: pytest.MonkeyPatch) -> bytes:
    assert case.cli is not None
    for name, value in case.env.items():
        monkeypatch.setenv(name, value)
    _serve(monkeypatch, case)
    confirmed = ["--yes"] if case.expected_effect == "destructive" else []
    result = CliRunner().invoke(app, ["--format", output_format, *confirmed, *case.cli])
    assert result.exit_code == 0, result.output
    return result.stdout_bytes


def _items(printed: Any) -> list[Any]:
    """The rows ``-o json`` shows: the items of a listing, a bare array, or the one object."""
    if (
        isinstance(printed, dict)
        and isinstance(printed.get("items"), list)
        and "truncated" in printed
    ):
        return printed["items"]
    return printed if isinstance(printed, list) else [printed]


def _cell(item: Any, header: str) -> str:
    """What the cell under ``header`` must say, read from the item as JSON carries it."""
    value = item
    whole = header == "value" and not (isinstance(item, dict) and "value" in item)
    for key in [] if whole else header.split("."):
        value = value.get(key) if isinstance(value, dict) else None
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


@pytest.mark.parametrize("case", CLI_CASES, ids=[case.id for case in CLI_CASES])
def test_a_command_prints_the_same_items_in_every_format(case: Case, monkeypatch):
    as_json = _printed(case, "json", monkeypatch)
    printed = {name: _printed(case, name, monkeypatch) for name in ("ndjson", "csv", "markdown")}
    try:
        items = _items(json.loads(as_json))
    except ValueError:
        # Text, a count and bytes are not a table: every format prints them as they are.
        assert set(printed.values()) == {as_json}
        return
    if not isinstance(json.loads(as_json), dict | list):
        assert set(printed.values()) == {as_json}
        return

    assert [json.loads(line) for line in printed["ndjson"].splitlines()] == items

    table = list(csv.reader(io.StringIO(printed["csv"].decode(), newline="")))
    if items:
        header, *rows = table
        assert len(rows) == len(items)
        for row, item in zip(rows, items, strict=True):
            assert row == [_cell(item, name) for name in header]
        lines = printed["markdown"].decode().splitlines()
        assert len(lines) == len(items) + 2
        assert {len(_CELL_END.findall(line)) for line in lines} == {len(header) + 1}
    else:
        # An empty listing still says what its columns are.
        assert len(table) == 1
        assert len(printed["markdown"].decode().splitlines()) == 2


def _models(base: type[BaseModel]) -> Iterator[type[BaseModel]]:
    for model in base.__subclasses__():
        yield model
        yield from _models(model)


def test_the_columns_of_every_model_are_the_keys_its_json_has():
    """A column named otherwise than the key would print nothing under it.

    What pydantic says a model serializes to is the measure, for every model the cases loaded.
    """
    checked = 0
    for model in dict.fromkeys(_models(APIModel)):
        if issubclass(model, RootModel) or model.__pydantic_generic_metadata__["parameters"]:
            continue  # a wrapper of one value, or a generic nobody gave its argument
        schema = model.model_json_schema(by_alias=True, mode="serialization")
        if "$ref" in schema:  # a model that holds itself is described under its name
            schema = schema["$defs"][schema["$ref"].rpartition("/")[2]]
        declared = schema.get("properties", {})
        columns = {column[0] for column in _columns(model) if column}
        assert columns == set(declared), model
        checked += 1
    assert checked > 500


def _header(case: Case, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    return next(csv.reader(io.StringIO(_printed(case, "csv", monkeypatch).decode())))


def _first(operation: str) -> Case:
    return next(case for case in CLI_CASES if case.operation == operation)


@pytest.mark.parametrize(
    ("operation", "nothing"),
    [
        # The two listings whose items are of several kinds.
        ("forms.subscriptions.list", []),
        ("datalens.collections.content_list", {"items": [], "nextPageToken": None}),
        ("tracker.queues.list", []),
    ],
)
def test_the_header_is_the_same_for_an_empty_listing_as_for_a_full_one(
    operation, nothing, monkeypatch
):
    case = _first(operation)
    sent, reply = case.exchanges[0]
    empty = replace(case, exchanges=[(sent, replace(reply, json=nothing))])
    assert _printed(empty, "ndjson", monkeypatch) == b""
    printed = _printed(empty, "csv", monkeypatch).decode()
    assert printed.count("\n") == 1  # the header line, and nothing else
    assert printed.rstrip("\n").split(",") == _header(case, monkeypatch)


#: Operations with a case whose reply leaves out the field that names the item: ``-o name``
#: says so and prints nothing, so a script does not act on fewer objects than were listed.
SPARSE = {
    "forms.filling.submit",
    "tracker.boards.list",
    "tracker.comments.list",
    "tracker.resolutions.update",
    "tracker.statuses.update",
    "tracker.users.list",
    "tracker.worklog.list",
}


def _named(case: Case, monkeypatch: pytest.MonkeyPatch) -> tuple[Any, Any]:
    assert case.cli is not None
    for name, value in case.env.items():
        monkeypatch.setenv(name, value)
    api = _serve(monkeypatch, case)
    confirmed = ["--yes"] if case.expected_effect == "destructive" else []
    return CliRunner().invoke(app, ["--format", "name", *confirmed, *case.cli]), api


def test_every_sparse_operation_has_a_case_that_leaves_an_item_unnamed(monkeypatch):
    refused = {
        case.operation
        for case in CLI_CASES
        if case.operation in SPARSE
        and isinstance(_named(case, monkeypatch)[0].exception, YandexUnexpectedReplyError)
    }
    assert refused == SPARSE


@pytest.mark.parametrize("case", CLI_CASES, ids=[case.id for case in CLI_CASES])
def test_name_prints_one_identifier_for_each_item_or_refuses_before_any_request(
    case: Case, monkeypatch
):
    result, api = _named(case, monkeypatch)
    said = " ".join(result.output.replace("│", " ").split())
    if isinstance(result.exception, YandexUnexpectedReplyError):
        assert "`-o name` cannot name it" in str(result.exception)
        assert result.stdout == ""
        assert case.operation in SPARSE
        return
    if result.exit_code:
        assert result.exit_code == 2, result.output
        assert NO_NAME in said
        assert api.calls == []
        return
    as_json = _printed(case, "json", monkeypatch)
    try:
        shown = json.loads(as_json)
    except ValueError:
        shown = None
    if not isinstance(shown, dict | list):
        # Text, a count, bytes: printed as they are in every format.
        assert result.stdout_bytes == as_json
        return
    items = _items(shown)
    names = result.stdout.splitlines()
    assert len(names) == len(items) and all(names)
    for name, item in zip(names, items, strict=True):
        own = item.values() if isinstance(item, dict) else [item]
        assert name in {value if isinstance(value, str) else json.dumps(value) for value in own}

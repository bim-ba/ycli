"""TDD for ColumnsClient — list/get reads + create/edit/delete writes on board columns."""

import json

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.columns.client import ColumnsClient
from ycli.yandex.tracker.columns.models import Column, ColumnCreate, ColumnList, ColumnUpdate


def _client() -> ColumnsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return ColumnsClient(session=s)


@responses.activate
def test_list_returns_board_columns():
    responses.add(
        responses.GET,
        f"{BASE}/boards/73/columns",
        json=[{"id": 1, "name": "Open", "statuses": [{"id": "1", "key": "open"}]}],
        status=200,
    )
    out = _client().list(board_id=73)
    assert isinstance(out, ColumnList)
    assert out.root[0].name == "Open" and out.root[0].statuses[0].key == "open"
    assert responses.calls[0].request.url == f"{BASE}/boards/73/columns"


@responses.activate
def test_get_returns_one_column():
    responses.add(
        responses.GET,
        f"{BASE}/boards/73/columns/1",
        json={"id": 1, "name": "Open"},
        status=200,
    )
    column = _client().get(board_id=73, column_id=1)
    assert isinstance(column, Column) and column.id == 1 and column.name == "Open"


@responses.activate
def test_create_posts_typed_body_to_trailing_slash():
    responses.add(
        responses.POST, f"{BASE}/boards/73/columns/", json={"id": 5, "name": "Approve"}, status=201
    )
    column = _client().create(73, ColumnCreate(name="Approve", statuses=["needInfo", "adjustment"]))
    assert isinstance(column, Column) and column.id == 5
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/boards/73/columns/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Approve",
        "statuses": ["needInfo", "adjustment"],
    }


@responses.activate
def test_edit_patches_only_supplied_fields():
    responses.add(
        responses.PATCH, f"{BASE}/boards/73/columns/5", json={"id": 5, "name": "Pause"}, status=200
    )
    column = _client().edit(73, 5, ColumnUpdate(name="Pause"))
    assert column.name == "Pause"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"name": "Pause"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete_issues_delete_and_returns_response():
    responses.add(responses.DELETE, f"{BASE}/boards/73/columns/5", status=204)
    resp = _client().delete(board_id=73, column_id=5)
    assert resp.status_code == 204
    assert responses.calls[0].request.method == "DELETE"

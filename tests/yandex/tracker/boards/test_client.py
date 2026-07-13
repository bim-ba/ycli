"""TDD for BoardsClient — get + relative-paginated list draining ``/boards/_paginate``."""

import json
from urllib.parse import parse_qs, urlparse

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.boards.client import BoardsClient
from ycli.yandex.tracker.boards.models import Board, BoardCreate, BoardList, BoardUpdate


def _client() -> BoardsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return BoardsClient(session=s)


@responses.activate
def test_get_returns_board():
    responses.add(
        responses.GET,
        f"{BASE}/boards/1",
        json={"id": 1, "name": "My board", "estimateBy": {"display": "Story Points"}},
        status=200,
    )
    board = _client().get(board_id=1)
    assert isinstance(board, Board)
    assert board.id == 1 and board.name == "My board" and board.estimate_by == "Story Points"


def _paginate_callback(request):
    """Three-request drain: page 1 (no id) → id=2 page → id=3 empty page terminates."""
    cursor = parse_qs(urlparse(request.url).query).get("id", [None])[0]
    if cursor is None:
        body = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    elif cursor == "2":
        body = [{"id": 3, "name": "C"}]
    else:  # id=3 → nothing left → RelativeCursorStrategy stops
        body = []
    return (200, {}, json.dumps(body))


@responses.activate
def test_list_drains_paginate_across_pages():
    responses.add_callback(
        responses.GET,
        f"{BASE}/boards/_paginate",
        callback=_paginate_callback,
        content_type="application/json",
    )
    out = _client().list()
    assert isinstance(out, BoardList)
    assert [b.name for b in out.root] == ["A", "B", "C"]  # all pages concatenated in order
    assert len(responses.calls) == 3  # page1 + id=2 page + id=3 empty page
    assert "perPage=100" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    assert "id=2" in responses.calls[1].request.url  # ty: ignore[unsupported-operator]
    assert "id=3" in responses.calls[2].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_list_respects_limit_within_first_page():
    responses.add(
        responses.GET,
        f"{BASE}/boards/_paginate",
        json=[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
        status=200,
    )
    out = _client().list(limit=1)
    assert [b.id for b in out.root] == [1]  # truncated to the limit
    assert len(responses.calls) == 1  # limit satisfied by page 1 — no second fetch


@responses.activate
def test_list_terminates_when_last_board_has_no_id():
    """A last board with a null id yields no cursor, so the walk stops after one page."""
    responses.add(
        responses.GET, f"{BASE}/boards/_paginate", json=[{"id": None, "name": "X"}], status=200
    )
    out = _client().list()
    assert [b.name for b in out.root] == ["X"]
    assert len(responses.calls) == 1


@responses.activate
def test_create_posts_typed_body_to_liveboards():
    """create() targets the /liveBoards/ path and sends the dumped, alias-cased body."""
    responses.add(
        responses.POST, f"{BASE}/liveBoards/", json={"id": 1, "name": "Testing"}, status=201
    )
    board = _client().create(BoardCreate(name="Testing", owner="username", sprints_available=True))
    assert isinstance(board, Board) and board.id == 1
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/liveBoards/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Testing",
        "owner": "username",
        "sprintsAvailable": True,
    }


@responses.activate
def test_edit_patches_board_with_only_supplied_fields():
    responses.add(
        responses.PATCH, f"{BASE}/boards/5", json={"id": 5, "name": "New name"}, status=200
    )
    board = _client().edit(5, BoardUpdate(name="New name"))
    assert board.name == "New name"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"name": "New name"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete_issues_delete_and_returns_response():
    responses.add(responses.DELETE, f"{BASE}/boards/5", status=204)
    resp = _client().delete(board_id=5)
    assert resp.status_code == 204
    assert responses.calls[0].request.method == "DELETE"

"""TDD for CommentsClient — writes + relative-paginated list draining ``id=<last id>``."""

import json
from urllib.parse import parse_qs, urlparse

import requests
import responses

from ycli.yandex.tracker.comments.client import CommentsClient
from ycli.yandex.tracker.comments.models import Comment, CommentList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> CommentsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return CommentsClient(session=s)


def _comments_page_callback(request):
    """Three-request drain: page 1 (no id) → id=2 page → id=3 empty page terminates."""
    cursor = parse_qs(urlparse(request.url).query).get("id", [None])[0]
    if cursor is None:
        body = [
            {"id": 1, "createdBy": {"display": "Сава"}, "text": "first"},
            {"id": 2, "text": "second"},
        ]
    elif cursor == "2":
        body = [{"id": 3, "text": "third"}]
    else:  # id=3 → nothing left → RelativeCursorStrategy stops
        body = []
    return (200, {}, json.dumps(body))


@responses.activate
def test_list_drains_pages_across_relative_cursor():
    responses.add_callback(
        responses.GET,
        f"{BASE}/issues/DE-1/comments",
        callback=_comments_page_callback,
        content_type="application/json",
    )
    out = _client().list("DE-1")
    assert isinstance(out, CommentList)
    assert [c.text for c in out.root] == ["first", "second", "third"]  # pages joined in order
    assert out.root[0].created_by == "Сава"
    assert len(responses.calls) == 3  # page1 + id=2 page + id=3 empty page
    assert "perPage=100" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    assert "id=2" in responses.calls[1].request.url  # ty: ignore[unsupported-operator]
    assert "id=3" in responses.calls[2].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_list_respects_limit_within_first_page():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/comments",
        json=[{"id": 1, "text": "first"}, {"id": 2, "text": "second"}],
        status=200,
    )
    out = _client().list("DE-1", limit=1)
    assert [c.id for c in out.root] == [1]  # truncated to the limit
    assert len(responses.calls) == 1  # limit satisfied by page 1 — no second fetch


@responses.activate
def test_list_terminates_when_last_comment_has_no_id():
    """A last comment with a null id yields no cursor, so the walk stops after one page."""
    responses.add(responses.GET, f"{BASE}/issues/DE-1/comments", json=[{"text": "hi"}], status=200)
    out = _client().list("DE-1")
    assert [c.text for c in out.root] == ["hi"]
    assert len(responses.calls) == 1


@responses.activate
def test_add_posts_body():
    responses.add(
        responses.POST, f"{BASE}/issues/DE-1/comments/", json={"id": 5, "text": "added"}, status=201
    )
    c = _client().add("DE-1", body={"text": "added"})
    assert isinstance(c, Comment) and c.id == 5
    assert json.loads(responses.calls[0].request.body) == {"text": "added"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_edit_patches_body():
    responses.add(
        responses.PATCH,
        f"{BASE}/issues/DE-1/comments/5",
        json={"id": 5, "text": "fixed"},
        status=200,
    )
    c = _client().edit("DE-1", "5", body={"text": "fixed"})
    assert isinstance(c, Comment) and c.text == "fixed"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"text": "fixed"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete_returns_none():
    responses.add(responses.DELETE, f"{BASE}/issues/DE-1/comments/5", status=204)
    assert _client().delete("DE-1", "5") is None
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_react_posts_to_reaction_path():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/comments/5/reactions/LIKE",
        json={"id": 5, "text": "hi"},
        status=200,
    )
    c = _client().react("DE-1", "5", "LIKE")
    assert isinstance(c, Comment) and c.id == 5
    assert responses.calls[0].request.method == "POST"

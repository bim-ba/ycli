import json

import requests
import responses

from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.comments.models import CommentCreated, CommentDeleteResult, CommentList

BASE = "https://api.wiki.yandex.net/v1"


def _client():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return CommentsClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={"results": [{"created_at": "2026-01-01", "content": "hi"}]},
        status=200,
    )
    out = _client().list(page_id=42)
    assert isinstance(out, CommentList)
    assert [c.content for c in out.root] == ["hi"]


@responses.activate
def test_list_maps_body_to_content_and_author_display_name():
    """Bug 4: real list payload carries ``body`` + ``author.display_name``; both must populate."""
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={
            "results": [
                {"id": 1, "body": "hello there", "author": {"id": 9, "display_name": "Сава"}}
            ]
        },
        status=200,
    )
    out = _client().list(page_id=42)
    assert out.root[0].content == "hello there"
    assert out.root[0].author == "Сава"


@responses.activate
def test_list_comments_for_page_id():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={"results": [{"created_at": "2026-01-01", "content": "hi"}]},
        status=200,
    )
    out = _client().list(page_id=42)
    assert isinstance(out, CommentList)
    assert out.root[0].content == "hi"
    assert responses.calls[0].request.params["page_size"] == "100"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_drains_next_cursor_across_pages():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={"results": [{"content": "a"}], "next_cursor": "c1"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={"results": [{"content": "b"}], "next_cursor": None},
        status=200,
    )
    out = _client().list(page_id=42)
    assert [c.content for c in out.root] == ["a", "b"]  # both pages drained
    assert len(responses.calls) == 2
    assert responses.calls[1].request.params["cursor"] == "c1"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_limit_truncates_without_second_fetch():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={"results": [{"content": "a"}, {"content": "b"}], "next_cursor": "c1"},
        status=200,
    )
    out = _client().list(page_id=42, limit=1)
    assert [c.content for c in out.root] == ["a"]  # capped before draining c1
    assert len(responses.calls) == 1


@responses.activate
def test_thread_drains_next_cursor_across_pages():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments/7/thread",
        json={"results": [{"content": "a"}], "next_cursor": "c1"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments/7/thread",
        json={"results": [{"content": "b"}], "next_cursor": None},
        status=200,
    )
    out = _client().thread(page_id=42, comment_id=7)
    assert isinstance(out, CommentList)
    assert [c.content for c in out.root] == ["a", "b"]  # both pages drained
    assert len(responses.calls) == 2
    assert responses.calls[0].request.params["page_size"] == "50"  # ty: ignore[unresolved-attribute]
    assert responses.calls[1].request.params["cursor"] == "c1"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_thread_limit_truncates_without_second_fetch():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments/7/thread",
        json={"results": [{"content": "a"}, {"content": "b"}], "next_cursor": "c1"},
        status=200,
    )
    out = _client().thread(page_id=42, comment_id=7, limit=1)
    assert [c.content for c in out.root] == ["a"]
    assert len(responses.calls) == 1


@responses.activate
def test_create_posts_body_and_returns_created():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/comments",
        json={"id": 99, "body": "LGTM", "parent_id": 7},
        status=200,
    )
    out = _client().create(page_id=42, body={"body": "LGTM", "parent_id": 7})
    assert isinstance(out, CommentCreated)
    assert out.id == 99 and out.parent_id == 7
    assert responses.calls[0].request.method == "POST"
    assert json.loads(responses.calls[0].request.body) == {"body": "LGTM", "parent_id": 7}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete_returns_comments_count():
    responses.add(
        responses.DELETE,
        f"{BASE}/pages/42/comments/7",
        json={"comments_count": 4},
        status=200,
    )
    out = _client().delete(page_id=42, comment_id=7)
    assert isinstance(out, CommentDeleteResult)
    assert out.comments_count == 4
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url.endswith("/pages/42/comments/7")  # ty: ignore[unresolved-attribute]

import json

import requests
import responses

from tests.hosts import WIKI_BASE as BASE
from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.comments.models import CommentCreated, CommentDeleteResult, CommentList


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


# --- thread reconstruction (bug: replies come back flat, /thread endpoint is dead) -------------
#
# Live probing showed the flat list payload carries a reply as a *sibling* of its parent, tagged
# only by ``parent_id`` (``thread_id`` is ``null`` on both, ``thread_info`` is ``null`` on the
# root). The ``/pages/{id}/comments/{cid}/thread`` endpoint returns ``{"results": []}`` for a real
# parent/child pair, so ``thread`` must reconstruct the tree client-side from ``comments list``.


@responses.activate
def test_thread_reconstructs_root_and_reply_from_flat_list():
    """A ``parent_id`` reply, flat in the list, is collected under its root by ``thread``."""
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={
            "results": [
                {
                    "id": 1,
                    "body": "root",
                    "parent_id": None,
                    "thread_id": None,
                    "thread_info": None,
                    "author": {"display_name": "Сава"},
                },
                {
                    "id": 2,
                    "body": "reply",
                    "parent_id": 1,
                    "thread_id": None,
                    "author": {"display_name": "Гость"},
                },
            ]
        },
        status=200,
    )
    out = _client().thread(page_id=42, comment_id=1)
    assert isinstance(out, CommentList)
    # the target comment first, then its reply (which the flat list returned as a sibling)
    assert [c.content for c in out.root] == ["root", "reply"]
    assert out.root[1].parent_id == 1  # the wiring that associates the reply to its parent
    # it reconstructs from the flat list, not the dead /thread endpoint
    assert responses.calls[0].request.url.split("?")[0] == f"{BASE}/pages/42/comments"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_thread_follows_parent_chain_to_any_depth():
    """The chain follows ``parent_id`` to arbitrary depth, not just direct replies (DFS order)."""
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={
            "results": [
                {"id": 1, "body": "root", "parent_id": None},
                {"id": 2, "body": "reply", "parent_id": 1},
                {"id": 3, "body": "reply to reply", "parent_id": 2},
            ]
        },
        status=200,
    )
    out = _client().thread(page_id=42, comment_id=1)
    assert [c.content for c in out.root] == ["root", "reply", "reply to reply"]


@responses.activate
def test_thread_excludes_comments_from_other_threads():
    """Only the target's own subtree is returned — a sibling root and its reply are excluded."""
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={
            "results": [
                {"id": 1, "body": "root", "parent_id": None},
                {"id": 2, "body": "reply", "parent_id": 1},
                {"id": 10, "body": "other root", "parent_id": None},
                {"id": 11, "body": "other reply", "parent_id": 10},
            ]
        },
        status=200,
    )
    out = _client().thread(page_id=42, comment_id=1)
    assert [c.content for c in out.root] == ["root", "reply"]


@responses.activate
def test_thread_unknown_comment_id_returns_empty():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={"results": [{"id": 1, "body": "root", "parent_id": None}]},
        status=200,
    )
    out = _client().thread(page_id=42, comment_id=999)
    assert isinstance(out, CommentList)
    assert out.root == []


@responses.activate
def test_thread_limit_caps_reply_count():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={
            "results": [
                {"id": 1, "body": "root", "parent_id": None},
                {"id": 2, "body": "r1", "parent_id": 1},
                {"id": 3, "body": "r2", "parent_id": 1},
            ]
        },
        status=200,
    )
    out = _client().thread(page_id=42, comment_id=1, limit=1)
    assert [c.content for c in out.root] == ["root", "r1"]  # root + one reply (limit caps replies)


@responses.activate
def test_thread_guards_against_cyclic_parent_id():
    """A cyclic parent_id chain is bounded by the seen-guard — no infinite recursion."""
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={
            "results": [
                {"id": 1, "body": "a", "parent_id": 2},
                {"id": 2, "body": "b", "parent_id": 1},
            ]
        },
        status=200,
    )
    out = _client().thread(page_id=42, comment_id=1)
    assert [c.content for c in out.root] == ["a", "b"]


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

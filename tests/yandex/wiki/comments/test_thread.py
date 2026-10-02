"""Rebuilding one comment thread from the page's flat comment list (no HTTP).

The Wiki ``/thread`` endpoint answers no replies and the listing returns a reply as a sibling of
its parent, so ``CommentsClient.thread`` chains ``parent_id`` client-side.
"""

from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.comments.models import Comment


def _thread(rows: list[dict], comment_id: int, limit: int | None = None) -> list[str | None]:
    comments = [Comment.model_validate(row) for row in rows]
    return [
        c.content for c in CommentsClient._collect_thread(comments, comment_id, limit=limit).root
    ]


def test_follows_the_parent_chain_to_any_depth():
    rows = [
        {"id": 1, "body": "root", "parent_id": None},
        {"id": 2, "body": "reply", "parent_id": 1},
        {"id": 3, "body": "reply to reply", "parent_id": 2},
    ]
    assert _thread(rows, 1) == ["root", "reply", "reply to reply"]


def test_leaves_out_other_threads():
    rows = [
        {"id": 1, "body": "root", "parent_id": None},
        {"id": 2, "body": "reply", "parent_id": 1},
        {"id": 10, "body": "other root", "parent_id": None},
        {"id": 11, "body": "other reply", "parent_id": 10},
    ]
    assert _thread(rows, 1) == ["root", "reply"]


def test_an_unknown_comment_is_an_empty_thread():
    assert _thread([{"id": 1, "body": "root", "parent_id": None}], 999) == []


def test_limit_caps_the_replies_not_the_root():
    rows = [
        {"id": 1, "body": "root", "parent_id": None},
        {"id": 2, "body": "r1", "parent_id": 1},
        {"id": 3, "body": "r2", "parent_id": 1},
    ]
    assert _thread(rows, 1, limit=1) == ["root", "r1"]


def test_a_cyclic_parent_chain_ends():
    rows = [{"id": 1, "body": "a", "parent_id": 2}, {"id": 2, "body": "b", "parent_id": 1}]
    assert _thread(rows, 1) == ["a", "b"]


def test_comments_without_ids_are_tolerated():
    rows = [
        {"id": 1, "body": "root", "parent_id": None},
        {"id": None, "body": "anonymous reply", "parent_id": 1},
        {"id": None, "body": "orphan", "parent_id": None},
    ]
    assert _thread(rows, 1) == ["root", "anonymous reply"]

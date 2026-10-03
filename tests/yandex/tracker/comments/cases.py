"""Contract cases for Tracker issue ``/comments`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent, with_query
from ycli.yandex.tracker.comments.models import CommentUpdate
from ycli.yandex.tracker.models import CommentCreate

CASES = [
    # The default cap (500) asks for full 100-row pages and walks id=<last comment id>.
    Case(
        "tracker.comments.list",
        args=("DE-11",),
        kwargs={"limit": 500},
        cli=["tracker", "comments", "list", "DE-11"],
        mcp=("tracker_comments_list", {"key": "DE-11"}),
        exchanges=[
            (
                Sent("GET", "issues/DE-11/comments", {"perPage": "100"}),
                Reply(json=[{"id": 101, "text": "first"}, {"id": 102, "text": "second"}]),
            ),
            (
                Sent("GET", "issues/DE-11/comments", {"perPage": "100", "id": "102"}),
                Reply(json=[{"id": 103, "text": "third"}]),
            ),
            (
                Sent("GET", "issues/DE-11/comments", {"perPage": "100", "id": "103"}),
                Reply(json=[]),
            ),
        ],
    ),
    Case(
        "tracker.comments.list",
        args=("DE-12",),
        kwargs={"limit": 3},
        cli=["tracker", "comments", "list", "DE-12", "--limit", "3"],
        mcp=("tracker_comments_list", {"key": "DE-12", "limit": 3}),
        exchanges=[
            (
                Sent("GET", "issues/DE-12/comments", {"perPage": "3"}),
                Reply(json=[{"id": 111, "text": "a"}, {"id": 112, "text": "b"}, {"id": 113}]),
            )
        ],
    ),
    # `--all` is uncapped; a last comment without an id ends the walk.
    Case(
        "tracker.comments.list",
        args=("DE-13",),
        cli=["tracker", "comments", "list", "DE-13", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "issues/DE-13/comments", {"perPage": "100"}),
                Reply(json=[{"text": "no id"}]),
            )
        ],
    ),
    Case(
        "tracker.comments.add",
        args=("DE-14", CommentCreate.model_validate({"text": "Готово ✅"})),
        cli=["tracker", "comments", "add", "DE-14", "--text", "Готово ✅"],
        mcp=("tracker_comments_add", {"key": "DE-14", "body": {"text": "Готово ✅"}}),
        exchanges=[
            (
                Sent("POST", "issues/DE-14/comments/", json={"text": "Готово ✅"}),
                Reply(json={"id": 141, "text": "Готово ✅"}, status=201),
            )
        ],
    ),
    # Summonees and attachments are MCP/SDK-only fields of the body.
    Case(
        "tracker.comments.add",
        args=(
            "DE-15",
            CommentCreate.model_validate(
                {
                    "text": "Please review",
                    "summonees": ["bob"],
                    "attachmentIds": ["att-1"],
                    "maillistSummonees": ["team@example.com"],
                }
            ),
        ),
        cli=None,
        mcp=(
            "tracker_comments_add",
            {
                "key": "DE-15",
                "body": {
                    "text": "Please review",
                    "summonees": ["bob"],
                    "attachment_ids": ["att-1"],
                    "maillist_summonees": ["team@example.com"],
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/DE-15/comments/",
                    json={
                        "text": "Please review",
                        "summonees": ["bob"],
                        "attachmentIds": ["att-1"],
                        "maillistSummonees": ["team@example.com"],
                    },
                ),
                Reply(json={"id": 151, "text": "Please review"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.comments.update",
        args=("DE-16", "161", CommentUpdate.model_validate({"text": "fixed typo"})),
        cli=["tracker", "comments", "update", "DE-16", "161", "--text", "fixed typo"],
        mcp=(
            "tracker_comments_update",
            {"key": "DE-16", "comment_id": "161", "body": {"text": "fixed typo"}},
        ),
        exchanges=[
            (
                Sent("PATCH", "issues/DE-16/comments/161", json={"text": "fixed typo"}),
                Reply(json={"id": 161, "text": "fixed typo"}),
            )
        ],
    ),
    Case(
        "tracker.comments.delete",
        args=("DE-17", "171"),
        cli=["tracker", "comments", "delete", "DE-17", "171"],
        mcp=("tracker_comments_delete", {"key": "DE-17", "comment_id": "171"}),
        exchanges=[(Sent("DELETE", "issues/DE-17/comments/171"), Reply(status=204))],
    ),
    Case(
        "tracker.comments.react",
        args=("DE-18", "181", "HEART"),
        cli=["tracker", "comments", "react", "DE-18", "181", "HEART"],
        mcp=("tracker_comments_react", {"key": "DE-18", "comment_id": "181", "name": "HEART"}),
        exchanges=[
            (
                Sent("POST", "issues/DE-18/comments/181/reactions/HEART"),
                Reply(json={"id": 181, "text": "nice"}),
            )
        ],
    ),
    Case(
        "tracker.comments.get",
        args=("DE-5", 9001),
        kwargs={"expand": "attachments,html"},
        cli=["tracker", "comments", "get", "DE-5", "9001", "--expand", "attachments,html"],
        mcp=(
            "tracker_comments_get",
            {"key": "DE-5", "comment_id": "9001", "expand": "attachments,html"},
        ),
        exchanges=[
            (
                Sent("GET", "issues/DE-5/comments/9001", {"expand": "attachments,html"}),
                Reply(
                    json={
                        "id": 9001,
                        "longId": "5fa15a24ac894475aa",
                        "text": "My **first** comment",
                        "textHtml": "<p>My <strong>first</strong> comment</p>",
                        "createdBy": {"display": "Ann"},
                        "updatedBy": {"display": "Bob"},
                        "createdAt": "2017-06-11T05:11:12.347+0000",
                        "updatedAt": "2017-06-12T05:11:12.347+0000",
                        "attachments": [{"id": "1", "display": "Untitled.png"}],
                        "version": 3,
                        "type": "standard",
                        "transport": "internal",
                    }
                ),
            )
        ],
    ),
    Case(
        "tracker.comments.get",
        args=("DE-6", "5fa15a24ac894476bb"),
        cli=["tracker", "comments", "get", "DE-6", "5fa15a24ac894476bb"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "issues/DE-6/comments/5fa15a24ac894476bb"),
                Reply(json={"id": 9002, "text": "By long id"}),
            )
        ],
    ),
]

CASES += [
    with_query(
        CASES,
        "tracker.comments.list",
        kwargs={"expand": "attachments"},
        cli=["--expand", "attachments"],
        params={"expand": "attachments"},
    ),
]

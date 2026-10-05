"""Contract cases for Wiki ``/pages/{id}/comments`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.wiki.comments.models import CommentCreate

ROOT = {"id": 5511, "body": "Ship it?", "author": {"display_name": "Vera"}, "parent_id": None}
REPLY = {"id": 5512, "body": "Agreed", "author": {"display_name": "Ivan"}, "parent_id": 5511}
OTHER = {"id": 5513, "body": "Unrelated", "parent_id": None}
CREATE_BODY = {"body": "Looks good", "inline_text": "Risks", "parent_id": 5511, "thread_id": 77}

CASES = [
    Case(
        "wiki.comments.list",
        args=(5501,),
        kwargs={"limit": 45},
        cli=["wiki", "comments", "list", "5501", "--limit", "45"],
        mcp=("wiki_comments_list", {"page_id": 5501, "limit": 45}),
        exchanges=[
            (
                Sent("GET", "pages/5501/comments", {"page_size": "100"}),
                Reply(json={"results": [ROOT], "next_cursor": "cc-2"}),
            ),
            (
                Sent("GET", "pages/5501/comments", {"page_size": "100", "cursor": "cc-2"}),
                Reply(json={"results": [REPLY], "next_cursor": None}),
            ),
        ],
    ),
    Case(
        "wiki.comments.list",
        args=(5502,),
        cli=["wiki", "comments", "list", "5502", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/5502/comments", {"page_size": "100"}),
                Reply(json={"results": [OTHER]}),
            )
        ],
    ),
    Case(
        "wiki.comments.thread_list",
        output=[
            {
                "id": 5511,
                "parent_id": None,
                "created_at": None,
                "author": "Vera",
                "content": "Ship it?",
                "inline_text": None,
                "thread_id": None,
                "thread_info": None,
                "is_deleted": None,
                "resolve_status": None,
                "reactions": [],
            },
            {
                "id": 5512,
                "parent_id": 5511,
                "created_at": None,
                "author": "Ivan",
                "content": "Agreed",
                "inline_text": None,
                "thread_id": None,
                "thread_info": None,
                "is_deleted": None,
                "resolve_status": None,
                "reactions": [],
            },
        ],
        args=(5503, 5511),
        kwargs={"limit": 15},
        cli=["wiki", "comments", "thread-list", "5503", "5511", "--limit", "15"],
        mcp=("wiki_comments_thread_list", {"page_id": 5503, "comment_id": 5511, "limit": 15}),
        exchanges=[
            (
                Sent("GET", "pages/5503/comments", {"page_size": "100"}),
                Reply(json={"results": [ROOT, OTHER, REPLY]}),
            )
        ],
    ),
    Case(
        "wiki.comments.thread_get",
        args=(5507, 5511),
        kwargs={"limit": 35},
        cli=["wiki", "comments", "thread-get", "5507", "5511", "--limit", "35"],
        mcp=("wiki_comments_thread_get", {"page_id": 5507, "comment_id": 5511, "limit": 35}),
        exchanges=[
            (
                Sent("GET", "pages/5507/comments/5511/thread", {"page_size": "100"}),
                Reply(json={"results": [ROOT], "next_cursor": "tt-2"}),
            ),
            (
                Sent(
                    "GET",
                    "pages/5507/comments/5511/thread",
                    {"page_size": "100", "cursor": "tt-2"},
                ),
                Reply(json={"results": [REPLY], "next_cursor": None}),
            ),
        ],
    ),
    Case(
        "wiki.comments.thread_get",
        args=(5508, 5512),
        cli=["wiki", "comments", "thread-get", "5508", "5512", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/5508/comments/5512/thread", {"page_size": "100"}),
                Reply(json={"results": [], "next_cursor": None}),
            )
        ],
    ),
    Case(
        "wiki.comments.create",
        args=(5504, CommentCreate.model_validate(CREATE_BODY)),
        cli=[
            "wiki",
            "comments",
            "create",
            "5504",
            "--body",
            "Looks good",
            "--inline-text",
            "Risks",
            "--parent-id",
            "5511",
            "--thread-id",
            "77",
        ],
        mcp=("wiki_comments_create", {"page_id": 5504, "body": CREATE_BODY}),
        exchanges=[
            (
                Sent("POST", "pages/5504/comments", json=CREATE_BODY),
                Reply(json={"id": 5514, **CREATE_BODY}),
            )
        ],
    ),
    Case(
        "wiki.comments.create",
        args=(5505, CommentCreate.model_validate({"body": "Plain note"})),
        cli=["wiki", "comments", "create", "5505", "--body", "Plain note"],
        mcp=("wiki_comments_create", {"page_id": 5505, "body": {"body": "Plain note"}}),
        exchanges=[
            (
                Sent("POST", "pages/5505/comments", json={"body": "Plain note"}),
                Reply(json={"id": 5515, "body": "Plain note"}),
            )
        ],
    ),
    Case(
        "wiki.comments.delete",
        args=(5506, 5516),
        cli=["wiki", "comments", "delete", "5506", "5516"],
        mcp=("wiki_comments_delete", {"page_id": 5506, "comment_id": 5516}),
        exchanges=[(Sent("DELETE", "pages/5506/comments/5516"), Reply(json={"comments_count": 4}))],
    ),
    Case(
        "wiki.comments.list",
        args=(5506,),
        kwargs={
            "limit": 16,
            "order_by": "created_at",
            "order_direction": "desc",
            "status_filter": "unresolved",
        },
        cli=[
            "wiki",
            "comments",
            "list",
            "5506",
            "--limit",
            "16",
            "--order-by",
            "created_at",
            "--order-direction",
            "desc",
            "--status-filter",
            "unresolved",
        ],
        mcp=(
            "wiki_comments_list",
            {
                "page_id": 5506,
                "limit": 16,
                "order_by": "created_at",
                "order_direction": "desc",
                "status_filter": "unresolved",
            },
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    "pages/5506/comments",
                    {
                        "page_size": "100",
                        "order_by": "created_at",
                        "order_direction": "desc",
                        "status_filter": "unresolved",
                    },
                ),
                Reply(json={"results": [REPLY, ROOT], "next_cursor": None}),
            )
        ],
    ),
    Case(
        "wiki.comments.create",
        args=(5507, CommentCreate.model_validate({"body": "Done"})),
        cli=["wiki", "comments", "create", "5507", "--body", "Done"],
        mcp=("wiki_comments_create", {"page_id": 5507, "body": {"body": "Done"}}),
        exchanges=[
            (
                Sent("POST", "pages/5507/comments", json={"body": "Done"}),
                Reply(
                    json={
                        "id": 5517,
                        "body": "Done",
                        "inline_text": None,
                        "parent_id": None,
                        "thread_id": None,
                        "created_at": "2026-10-03T12:00:00Z",
                        "author": {
                            "id": 8104,
                            "identity": {"uid": "9104", "cloud_uid": "cloud-9104"},
                            "username": "vera",
                            "display_name": "Vera",
                            "is_dismissed": False,
                            "affiliation": "",
                        },
                        "is_deleted": False,
                        "resolve_status": "unresolved",
                        "reactions": [
                            {
                                "type": "like",
                                "author": {"id": 8105, "username": "ivan", "display_name": "Ivan"},
                                "created_at": "2026-10-03T12:05:00Z",
                            }
                        ],
                    }
                ),
            )
        ],
    ),
]

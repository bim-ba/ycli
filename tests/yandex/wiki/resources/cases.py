"""Contract cases for Wiki ``/pages/{id}/resources`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

ATTACHMENT = {"type": "attachment", "item": {"id": 5411, "name": "plan.pdf"}}
GRID = {"type": "grid", "item": {"id": "g-5412", "title": "Budget"}}

CASES = [
    Case(
        "wiki.resources.list",
        args=(5401,),
        kwargs={"limit": 25, "q": "plan", "types": "attachment,grid"},
        cli=[
            "wiki",
            "resources",
            "list",
            "5401",
            "--limit",
            "25",
            "--q",
            "plan",
            "--types",
            "attachment,grid",
        ],
        mcp=(
            "wiki_resources_list",
            {"page_id": 5401, "limit": 25, "q": "plan", "types": "attachment,grid"},
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    "pages/5401/resources",
                    {"page_size": "100", "q": "plan", "types": "attachment,grid"},
                ),
                Reply(json={"results": [ATTACHMENT], "next_cursor": "rc-2"}),
            ),
            (
                Sent(
                    "GET",
                    "pages/5401/resources",
                    {"page_size": "100", "q": "plan", "types": "attachment,grid", "cursor": "rc-2"},
                ),
                Reply(json={"results": [GRID], "next_cursor": None}),
            ),
        ],
    ),
    Case(
        "wiki.resources.list",
        args=(5402,),
        kwargs={"order_by": "created_at"},
        cli=["wiki", "resources", "list", "5402", "--all", "--order-by", "created_at"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/5402/resources", {"page_size": "100", "order_by": "created_at"}),
                Reply(json={"results": [GRID]}),
            )
        ],
    ),
    Case(
        "wiki.resources.list",
        args=(5403,),
        kwargs={"limit": 4},
        cli=None,
        mcp=("wiki_resources_list", {"page_id": 5403, "limit": 4}),
        exchanges=[
            (
                Sent("GET", "pages/5403/resources", {"page_size": "100"}),
                Reply(json={"results": [ATTACHMENT]}),
            )
        ],
    ),
]

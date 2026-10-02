"""Contract cases for Wiki ``/pages`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent


def _page(page_id: int, slug: str, **extra: object) -> dict[str, object]:
    return {"id": page_id, "slug": slug, "title": f"Page {page_id}", **extra}


def _refs(*pairs: tuple[int, str], cursor: str | None = None) -> dict[str, object]:
    return {"results": [{"id": i, "slug": s} for i, s in pairs], "next_cursor": cursor}


CASES = [
    Case(
        "wiki.pages.get",
        args=("team/handbook",),
        kwargs={"fields": "content,attributes"},
        cli=["wiki", "pages", "get", "team/handbook", "--fields", "content,attributes"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages", {"slug": "team/handbook", "fields": "content,attributes"}),
                Reply(json=_page(4001, "team/handbook", content="# Handbook")),
            )
        ],
        cli_output=b"# Handbook\n",
    ),
    Case(
        "wiki.pages.get",
        args=("team/faq",),
        kwargs={"fields": "content"},
        cli=["wiki", "pages", "get", "team/faq"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages", {"slug": "team/faq", "fields": "content"}),
                Reply(json=_page(4002, "team/faq", content="# FAQ")),
            )
        ],
        cli_output=b"# FAQ\n",
    ),
    Case(
        "wiki.pages.get",
        args=("team/onboarding",),
        kwargs={"fields": "content"},
        cli=None,
        mcp=("wiki_pages_get", {"slug": "team/onboarding"}),
        exchanges=[
            (
                Sent("GET", "pages", {"slug": "team/onboarding", "fields": "content"}),
                Reply(json=_page(4003, "team/onboarding", content="# Welcome")),
            )
        ],
    ),
    Case(
        "wiki.pages.get",
        args=("team/roadmap",),
        kwargs={"fields": "attributes,owner"},
        cli=None,
        mcp=("wiki_pages_meta", {"slug": "team/roadmap"}),
        exchanges=[
            (
                Sent("GET", "pages", {"slug": "team/roadmap", "fields": "attributes,owner"}),
                Reply(json=_page(4004, "team/roadmap", attributes={"comments_count": 3})),
            )
        ],
    ),
    Case(
        "wiki.pages.get",
        args=("team/bare",),
        cli=None,
        mcp=None,
        exchanges=[(Sent("GET", "pages", {"slug": "team/bare"}), Reply(json=_page(4005, "b")))],
    ),
    Case(
        "wiki.pages.get_by_id",
        args=(4101,),
        kwargs={"fields": "content,breadcrumbs"},
        cli=["wiki", "pages", "get-by-id", "4101", "--fields", "content,breadcrumbs"],
        mcp=("wiki_pages_by_id_get", {"page_id": 4101, "fields": "content,breadcrumbs"}),
        exchanges=[
            (
                Sent("GET", "pages/4101", {"fields": "content,breadcrumbs"}),
                Reply(json=_page(4101, "eng/arch", content="# Arch")),
            )
        ],
    ),
    Case(
        "wiki.pages.get_by_id",
        args=(4102,),
        kwargs={"fields": "content"},
        cli=["wiki", "pages", "get-by-id", "4102"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/4102", {"fields": "content"}),
                Reply(json=_page(4102, "eng/ops", content="# Ops")),
            )
        ],
    ),
    Case(
        "wiki.pages.get_by_id",
        args=(4103,),
        cli=None,
        mcp=("wiki_pages_by_id_get", {"page_id": 4103}),
        exchanges=[(Sent("GET", "pages/4103"), Reply(json=_page(4103, "eng/qa")))],
    ),
    Case(
        "wiki.pages.descendants",
        args=("eng",),
        kwargs={"limit": 40},
        cli=["wiki", "pages", "descendants", "eng", "--limit", "40"],
        mcp=("wiki_pages_descendants", {"slug": "eng", "limit": 40}),
        exchanges=[
            (
                Sent("GET", "pages/descendants", {"slug": "eng", "page_size": "100"}),
                Reply(json=_refs((4201, "eng/a"), cursor="cur-eng-2")),
            ),
            (
                Sent(
                    "GET",
                    "pages/descendants",
                    {"slug": "eng", "page_size": "100", "cursor": "cur-eng-2"},
                ),
                Reply(json=_refs((4202, "eng/b"))),
            ),
        ],
    ),
    Case(
        "wiki.pages.descendants",
        args=("ops",),
        cli=["wiki", "pages", "descendants", "ops", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/descendants", {"slug": "ops", "page_size": "100"}),
                Reply(json=_refs((4203, "ops/runbook"))),
            )
        ],
    ),
    Case(
        "wiki.pages.descendants",
        args=("hr",),
        kwargs={"limit": 7, "actuality": "actual"},
        cli=None,
        mcp=None,
        exchanges=[
            (
                Sent(
                    "GET",
                    "pages/descendants",
                    {"slug": "hr", "page_size": "100", "actuality": "actual"},
                ),
                Reply(json=_refs((4204, "hr/policies"))),
            )
        ],
    ),
    Case(
        "wiki.pages.descendants_by_id",
        args=(4210,),
        kwargs={"limit": 35},
        cli=["wiki", "pages", "descendants-by-id", "4210", "--limit", "35"],
        mcp=("wiki_pages_by_id_descendants", {"page_id": 4210, "limit": 35}),
        exchanges=[
            (
                Sent("GET", "pages/4210/descendants", {"page_size": "100"}),
                Reply(json=_refs((4211, "sales/a"), cursor="cur-4210-2")),
            ),
            (
                Sent("GET", "pages/4210/descendants", {"page_size": "100", "cursor": "cur-4210-2"}),
                Reply(json=_refs((4212, "sales/b"))),
            ),
        ],
    ),
    Case(
        "wiki.pages.descendants_by_id",
        args=(4220,),
        kwargs={"limit": 9, "actuality": "deleted"},
        cli=None,
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/4220/descendants", {"page_size": "100", "actuality": "deleted"}),
                Reply(json=_refs((4221, "legal/old"))),
            )
        ],
    ),
    Case(
        "wiki.pages.grids",
        args=(4301,),
        kwargs={"limit": 30},
        cli=["wiki", "pages", "grids", "4301", "--limit", "30"],
        mcp=("wiki_pages_grids_list", {"page_id": 4301, "limit": 30}),
        exchanges=[
            (
                Sent("GET", "pages/4301/grids", {"page_size": "50"}),
                Reply(
                    json={"results": [{"id": "g-4301", "title": "Roadmap"}], "next_cursor": "gc2"}
                ),
            ),
            (
                Sent("GET", "pages/4301/grids", {"page_size": "50", "cursor": "gc2"}),
                Reply(json={"results": [{"id": "g-4302", "title": "Budget"}]}),
            ),
        ],
    ),
    Case(
        "wiki.pages.grids",
        args=(4310,),
        kwargs={"limit": 12, "order_by": "created_at"},
        cli=["wiki", "pages", "grids", "4310", "--limit", "12", "--order-by", "created_at"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/4310/grids", {"page_size": "50", "order_by": "created_at"}),
                Reply(json={"results": [{"id": "g-4310", "title": "Hiring"}]}),
            )
        ],
    ),
    Case(
        "wiki.pages.create",
        args=({"slug": "eng/new", "title": "New page", "content": "# New"},),
        cli=[
            "wiki",
            "pages",
            "create",
            "--slug",
            "eng/new",
            "--title",
            "New page",
            "--content",
            "# New",
        ],
        mcp=("wiki_pages_create", {"slug": "eng/new", "title": "New page", "content": "# New"}),
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages",
                    json={"slug": "eng/new", "title": "New page", "content": "# New"},
                ),
                Reply(json=_page(4401, "eng/new")),
            )
        ],
    ),
    Case(
        "wiki.pages.update",
        args=(4402, {"content": "# Rewritten", "title": "Renamed"}),
        cli=[
            "wiki",
            "pages",
            "update",
            "4402",
            "--content",
            "# Rewritten",
            "--title",
            "Renamed",
        ],
        mcp=("wiki_pages_update", {"page_id": 4402, "content": "# Rewritten", "title": "Renamed"}),
        exchanges=[
            (
                Sent("POST", "pages/4402", json={"content": "# Rewritten", "title": "Renamed"}),
                Reply(json=_page(4402, "eng/renamed")),
            )
        ],
        effect="idempotent_write",
    ),
    Case(
        "wiki.pages.update",
        args=(4403, {"content": "# Body only"}),
        cli=["wiki", "pages", "update", "4403", "--content", "# Body only"],
        mcp=("wiki_pages_update", {"page_id": 4403, "content": "# Body only"}),
        exchanges=[
            (
                Sent("POST", "pages/4403", json={"content": "# Body only"}),
                Reply(json=_page(4403, "eng/body")),
            )
        ],
        effect="idempotent_write",
    ),
    Case(
        "wiki.pages.delete",
        args=(4501,),
        cli=["wiki", "pages", "delete", "4501"],
        mcp=("wiki_pages_delete", {"page_id": 4501}),
        exchanges=[
            (
                Sent("DELETE", "pages/4501"),
                Reply(json={"recovery_token": "recovery-token-2"}),
            )
        ],
    ),
    Case(
        "wiki.pages.append_content",
        args=(4601, {"content": "## Top note", "body": {"location": "top"}}),
        cli=["wiki", "pages", "append", "4601", "--content", "## Top note", "--location", "top"],
        mcp=(
            "wiki_pages_append_content",
            {"page_id": 4601, "body": {"content": "## Top note", "body": {"location": "top"}}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/4601/append-content",
                    json={"content": "## Top note", "body": {"location": "top"}},
                ),
                Reply(json=_page(4601, "eng/notes")),
            )
        ],
    ),
    Case(
        "wiki.pages.append_content",
        args=(4602, {"content": "## Footer", "body": {"location": "bottom"}}),
        cli=["wiki", "pages", "append", "4602", "--content", "## Footer"],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/4602/append-content",
                    json={"content": "## Footer", "body": {"location": "bottom"}},
                ),
                Reply(json=_page(4602, "eng/footer")),
            )
        ],
    ),
    Case(
        "wiki.pages.append_content",
        args=(
            4603,
            {
                "content": "## Under the anchor",
                "anchor": {"name": "Risks", "fallback": True, "regex": True},
            },
        ),
        cli=None,
        mcp=(
            "wiki_pages_append_content",
            {
                "page_id": 4603,
                "body": {
                    "content": "## Under the anchor",
                    "anchor": {"name": "Risks", "fallback": True, "regex": True},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/4603/append-content",
                    json={
                        "content": "## Under the anchor",
                        "anchor": {"name": "Risks", "fallback": True, "regex": True},
                    },
                ),
                Reply(json=_page(4603, "eng/risks")),
            )
        ],
    ),
    Case(
        "wiki.pages.append_content",
        args=(4604, {"content": "## In section", "section": {"id": 3, "location": "bottom"}}),
        cli=None,
        mcp=(
            "wiki_pages_append_content",
            {
                "page_id": 4604,
                "body": {"content": "## In section", "section": {"id": 3, "location": "bottom"}},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/4604/append-content",
                    json={"content": "## In section", "section": {"id": 3, "location": "bottom"}},
                ),
                Reply(json=_page(4604, "eng/section")),
            )
        ],
    ),
    Case(
        "wiki.pages.clone",
        args=(4701, {"target": "eng/copy", "title": "Copy", "subscribe_me": True}),
        cli=[
            "wiki",
            "pages",
            "clone",
            "4701",
            "--target",
            "eng/copy",
            "--title",
            "Copy",
            "--subscribe-me",
            "--no-wait",
        ],
        mcp=(
            "wiki_pages_clone",
            {
                "page_id": 4701,
                "body": {"target": "eng/copy", "title": "Copy", "subscribe_me": True},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/4701/clone",
                    json={"target": "eng/copy", "title": "Copy", "subscribe_me": True},
                ),
                Reply(json={"operation": {"type": "clone", "id": "task-4701"}, "status_url": "u"}),
            )
        ],
    ),
    Case(
        "wiki.pages.clone",
        args=(4702, {"target": "eng/mirror", "subscribe_me": False}),
        cli=["wiki", "pages", "clone", "4702", "--target", "eng/mirror", "--no-wait"],
        mcp=("wiki_pages_clone", {"page_id": 4702, "body": {"target": "eng/mirror"}}),
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/4702/clone",
                    json={"target": "eng/mirror", "subscribe_me": False},
                ),
                Reply(json={"operation": {"type": "clone", "id": "task-4702"}}),
            )
        ],
    ),
]

"""Contract cases for Wiki ``/pages`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent


def _page(page_id: int, slug: str, **extra: object) -> dict[str, object]:
    return {"id": page_id, "slug": slug, "title": f"Page {page_id}", **extra}


def _refs(*pairs: tuple[int, str], cursor: str | None = None) -> dict[str, object]:
    return {"results": [{"id": i, "slug": s} for i, s in pairs], "next_cursor": cursor}


_PERSON = {
    "id": 8104,
    "identity": {"uid": "9104", "cloud_uid": "cloud-9104"},
    "username": "vera",
    "display_name": "Vera",
    "is_dismissed": False,
    "affiliation": "",
}
_ACCESS_FIELDS = {
    "access_policy": {
        "access_type": "custom",
        "inherited_access_type": "all_staff",
        "all_staff_role": "editor",
        "has_external": False,
        "invite": {"status": "none"},
    },
    "access_lists": {
        "direct": [
            {
                "id": "5104",
                "created_at": "2026-10-02T17:10:49.322Z",
                "user": _PERSON,
                "group": None,
                "role": "author",
                "inheritance": "inherited",
            }
        ],
        "by_link": [],
        "inherited": [
            {
                "id": "5105",
                "group": {
                    "id": "7104",
                    "identity": {"src": "staff", "id": "7104"},
                    "name": "Staff",
                    "type": "department",
                    "members_count": 40,
                },
                "role": "reader",
                "inheritance": "inherited",
            }
        ],
    },
    "owner": {"user": _PERSON, "group": None},
}


def _revision(revision_id: int, created_at: str, status: str | None) -> dict[str, object]:
    return {
        "id": revision_id,
        "author": _PERSON,
        "created_at": created_at,
        "page_type": "wysiwyg",
        "revision_draft": None,
        "publication": {"status": status} if status else None,
    }


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
        mcp=("wiki_pages_get_by_id", {"page_id": 4101, "fields": "content,breadcrumbs"}),
        exchanges=[
            (
                Sent("GET", "pages/4101", {"fields": "content,breadcrumbs"}),
                Reply(json=_page(4101, "eng/arch", content="# Arch")),
            )
        ],
    ),
    Case(
        "wiki.pages.get_by_id",
        args=(4104,),
        kwargs={"fields": "access_policy,access_lists,owner"},
        cli=["wiki", "pages", "get-by-id", "4104", "--fields", "access_policy,access_lists,owner"],
        mcp=(
            "wiki_pages_get_by_id",
            {"page_id": 4104, "fields": "access_policy,access_lists,owner"},
        ),
        exchanges=[
            (
                Sent("GET", "pages/4104", {"fields": "access_policy,access_lists,owner"}),
                Reply(json=_page(4104, "eng/secure", **_ACCESS_FIELDS)),
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
        mcp=("wiki_pages_get_by_id", {"page_id": 4103}),
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
        mcp=("wiki_pages_descendants_by_id", {"page_id": 4210, "limit": 35}),
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
        cli=["wiki", "pages", "grids-list", "4301", "--limit", "30"],
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
        cli=["wiki", "pages", "grids-list", "4310", "--limit", "12", "--order-by", "created_at"],
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
            "wiki_pages_append",
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
            "wiki_pages_append",
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
            "wiki_pages_append",
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
    # POST /pages/move (undocumented): a dry run is never polled, so the default --wait is safe.
    Case(
        "wiki.pages.move",
        args=(
            {
                "operations": [
                    {
                        "source": "eng/old-plan",
                        "target": "archive/plan",
                        "next_to_slug": "archive/first",
                        "position": "after",
                    }
                ],
                "copy_inherited_access": True,
            },
        ),
        kwargs={"dry_run": True},
        cli=[
            "wiki",
            "pages",
            "move",
            "eng/old-plan",
            "archive/plan",
            "--next-to",
            "archive/first",
            "--position",
            "after",
            "--copy-inherited-access",
            "--validate-only",
        ],
        mcp=(
            "wiki_pages_move",
            {
                "body": {
                    "operations": [
                        {
                            "source": "eng/old-plan",
                            "target": "archive/plan",
                            "next_to_slug": "archive/first",
                            "position": "after",
                        }
                    ],
                    "copy_inherited_access": True,
                },
                "dry_run": True,
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/move",
                    {"dry_run": "true"},
                    json={
                        "operations": [
                            {
                                "source": "eng/old-plan",
                                "target": "archive/plan",
                                "next_to_slug": "archive/first",
                                "position": "after",
                            }
                        ],
                        "copy_inherited_access": True,
                    },
                ),
                Reply(
                    json={
                        "operation": {"type": "move", "id": "mv-6101"},
                        "status_url": "/v1/operations/move/mv-6101",
                        "dry_run": True,
                    }
                ),
            )
        ],
    ),
    # The API refuses a move that does not say whether to copy inherited access, so the default
    # is an explicit false on every surface.
    Case(
        "wiki.pages.move",
        args=(
            {
                "operations": [{"source": "eng/b", "target": "eng/c"}],
                "copy_inherited_access": False,
            },
        ),
        cli=["wiki", "pages", "move", "eng/b", "eng/c", "--no-wait"],
        mcp=(
            "wiki_pages_move",
            {"body": {"operations": [{"source": "eng/b", "target": "eng/c"}]}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/move",
                    json={
                        "operations": [{"source": "eng/b", "target": "eng/c"}],
                        "copy_inherited_access": False,
                    },
                ),
                Reply(
                    json={
                        "operation": {"type": "move", "id": "mv-6102"},
                        "status_url": "/v1/operations/move/mv-6102",
                        "dry_run": False,
                    }
                ),
            )
        ],
    ),
    # GET /pages/{id}/revisions (undocumented): ids filter, cursor paging, a limit.
    Case(
        "wiki.pages.revisions",
        args=(6201,),
        kwargs={"ids": "7001,7002,7003", "limit": 40},
        cli=[
            "wiki",
            "pages",
            "revisions-list",
            "6201",
            "--ids",
            "7001,7002,7003",
            "--limit",
            "40",
        ],
        mcp=(
            "wiki_pages_revisions_list",
            {"page_id": 6201, "ids": "7001,7002,7003", "limit": 40},
        ),
        exchanges=[
            (
                Sent("GET", "pages/6201/revisions", {"page_size": "50", "ids": "7001,7002,7003"}),
                Reply(
                    json={
                        "results": [_revision(7003, "2026-10-02T10:03:00Z", "published")],
                        "next_cursor": "rev-2",
                    }
                ),
            ),
            (
                Sent(
                    "GET",
                    "pages/6201/revisions",
                    {"page_size": "50", "ids": "7001,7002,7003", "cursor": "rev-2"},
                ),
                Reply(json={"results": [_revision(7002, "2026-10-02T10:02:00Z", None)]}),
            ),
        ],
    ),
    # --all lifts the configured cap (shrunk to 1 here, so a CLI ignoring --all keeps one).
    Case(
        "wiki.pages.revisions",
        args=(6202,),
        kwargs={"limit": None},
        cli=["wiki", "pages", "revisions-list", "6202", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/6202/revisions", {"page_size": "50"}),
                Reply(
                    json={
                        "results": [
                            _revision(7011, "2026-10-02T11:01:00Z", "published"),
                            _revision(7012, "2026-10-02T11:02:00Z", "pending_publication"),
                        ]
                    }
                ),
            )
        ],
        env={"YCLI__HTTP__MAX_ITEMS": "1"},
    ),
    # GET /pages/{id}/backlinks (undocumented): both flags, cursor paging, a limit.
    Case(
        "wiki.pages.backlinks",
        args=(6301,),
        kwargs={"for_cluster": True, "show_all": True, "limit": 30},
        cli=[
            "wiki",
            "pages",
            "backlinks-list",
            "6301",
            "--for-cluster",
            "--show-all",
            "--limit",
            "30",
        ],
        mcp=(
            "wiki_pages_backlinks_list",
            {"page_id": 6301, "for_cluster": True, "show_all": True, "limit": 30},
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    "pages/6301/backlinks",
                    {"page_size": "100", "for_cluster": "true", "show_all": "true"},
                ),
                Reply(json=_refs((6311, "eng/linker-a"), cursor="bl-2")),
            ),
            (
                Sent(
                    "GET",
                    "pages/6301/backlinks",
                    {
                        "page_size": "100",
                        "for_cluster": "true",
                        "show_all": "true",
                        "cursor": "bl-2",
                    },
                ),
                Reply(json=_refs((6312, "eng/linker-b"))),
            ),
        ],
    ),
    Case(
        "wiki.pages.backlinks",
        args=(6302,),
        kwargs={"limit": None},
        cli=["wiki", "pages", "backlinks-list", "6302", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "pages/6302/backlinks", {"page_size": "100"}),
                Reply(json=_refs((6321, "ops/linker-c"), (6322, "ops/linker-d"))),
            )
        ],
        env={"YCLI__HTTP__MAX_ITEMS": "1"},
    ),
]

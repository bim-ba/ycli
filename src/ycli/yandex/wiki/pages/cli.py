"""`wiki pages` commands — argument-based; dumps full pydantic models as JSON."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.progress import wait_for
from ycli.cli.typedefs import AllOption, LimitOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.models import ItemList, SortDirection
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.models import AsyncOperation, Location, OrderPosition
from ycli.yandex.wiki.operations.models import CloneOperationStatus, MoveOperationStatus
from ycli.yandex.wiki.pages.models import (
    GridOrder,
    GridRef,
    PageAppendContent,
    PageAppendContentBody,
    PageClone,
    PageCreate,
    PageDeleteResult,
    PageDetails,
    PageMove,
    PageMoveStep,
    PageRef,
    PageRevision,
    PageUpdate,
)

app = typer.Typer(name="pages", help="Wiki pages.", no_args_is_help=True)

SlugArg = Annotated[str, typer.Argument(metavar="SLUG", help="Wiki page slug.")]
PageIdArg = Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")]
RevisionIdOption = Annotated[
    int | None,
    typer.Option("--revision-id", help="Show this past revision (ids from `revisions-list`)."),
]
RaiseOnRedirectOption = Annotated[
    bool,
    typer.Option("--raise-on-redirect", help="Fail if the page is a redirect, do not follow it."),
]
ReplyFieldsOption = Annotated[
    str | None, typer.Option("--fields", help="Comma-separated blocks to include in the reply.")
]
SilentOption = Annotated[
    bool, typer.Option("--silent", help="Do not notify the page's subscribers.")
]
IncludeSelfOption = Annotated[
    bool, typer.Option("--include-self", help="Also list the ancestor page itself.")
]
ShowAllOption = Annotated[bool, typer.Option("--show-all", help="The API's show_all flag.")]


@app.command()
def get(
    slug: SlugArg,
    fields: Annotated[
        str, typer.Option(help="Comma-separated fields, e.g. content,attributes.")
    ] = "content",
    revision_id: RevisionIdOption = None,
    raise_on_redirect: RaiseOnRedirectOption = False,
    *,
    wiki: WikiClient,
) -> str:
    """Print the page body (default fields=content) for SLUG."""
    page = wiki.pages.get(
        slug=slug, fields=fields, revision_id=revision_id, raise_on_redirect=raise_on_redirect
    )
    return page.content or ""


@app.command()
def descendants(
    slug: SlugArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    include_self: IncludeSelfOption = False,
    show_all: ShowAllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[PageRef]:
    """Print descendant slugs under SLUG (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.descendants(
        slug=slug, limit=cap, include_self=include_self, show_all=show_all
    )


@app.command("get-by-id")
def get_by_id(
    page_id: PageIdArg,
    fields: Annotated[
        str, typer.Option(help="Comma-separated fields, e.g. content,attributes.")
    ] = "content",
    revision_id: RevisionIdOption = None,
    raise_on_redirect: RaiseOnRedirectOption = False,
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Fetch a page by numeric id (GET /pages/{id}); dumps the full model."""
    return wiki.pages.get_by_id(
        page_id=page_id,
        fields=fields,
        revision_id=revision_id,
        raise_on_redirect=raise_on_redirect,
    )


@app.command("descendants-by-id")
def descendants_by_id(
    page_id: PageIdArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    include_self: IncludeSelfOption = False,
    show_all: ShowAllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[PageRef]:
    """Print descendant slugs under a numeric PAGE_ID (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.descendants_by_id(
        page_id=page_id, limit=cap, include_self=include_self, show_all=show_all
    )


@app.command()
def grids_list(
    page_id: PageIdArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    order_by: Annotated[
        str | None, values_option(GridOrder, "--order-by", help="Sort field.")
    ] = None,
    order_direction: Annotated[
        str | None,
        values_option(SortDirection, "--order-direction", help="Sort direction for --order-by."),
    ] = None,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[GridRef]:
    """List dynamic tables (grids) attached to a numeric PAGE_ID (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.grids_list(
        page_id=page_id,
        limit=cap,
        order_by=order_by,
        order_direction=order_direction,
    )


@app.command()
def create(
    slug: Annotated[str, typer.Option(help="Target slug, e.g. data/x.")],
    title: Annotated[str, typer.Option(help="Page title.")],
    content: Annotated[str, typer.Option(help='Markdown body — pass "$(cat file.md)".')],
    fields: ReplyFieldsOption = None,
    silent: SilentOption = False,
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Create a wiki page (POST /pages)."""
    return wiki.pages.create(
        body=PageCreate(slug=slug, title=title, content=content),
        fields=fields,
        is_silent=silent,
    )


@app.command()
def update(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    content: Annotated[str, typer.Option(help='Markdown body — pass "$(cat file.md)".')],
    title: Annotated[str | None, typer.Option(help="New title (optional).")] = None,
    fields: ReplyFieldsOption = None,
    silent: SilentOption = False,
    allow_merge: Annotated[
        bool,
        typer.Option("--allow-merge", help="Merge with a concurrent edit instead of failing."),
    ] = False,
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Update a wiki page by id (POST /pages/{id})."""
    return wiki.pages.update(
        page_id=page_id,
        body=PageUpdate(content=content, title=title),
        fields=fields,
        is_silent=silent,
        allow_merge=allow_merge,
    )


@app.command()
def delete(
    page_id: PageIdArg,
    recursive: Annotated[
        bool, typer.Option("--recursive", help="Also delete every page under it.")
    ] = False,
    *,
    wiki: WikiClient,
) -> PageDeleteResult:
    """Delete a wiki page (DELETE /pages/{id}); emits the recovery_token to undo it."""
    return wiki.pages.delete(page_id=page_id, recursive=recursive)


@app.command()
def append(
    page_id: PageIdArg,
    content: Annotated[str, typer.Option(help='YFM fragment to append — pass "$(cat file.md)".')],
    location: Annotated[str, values_option(Location, help="Where in the body.")] = "bottom",
    fields: ReplyFieldsOption = None,
    silent: SilentOption = False,
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Append content to a wiki page (POST /pages/{id}/append-content).

    The API requires exactly one placement selector (``body`` / ``section`` / ``anchor``) and
    rejects a bare ``{content}`` with 400, so the CLI always sends the whole-page ``body``
    selector — ``--location bottom`` unless overridden with ``--location top``.
    """
    payload = PageAppendContent(
        content=content,
        body=PageAppendContentBody(location=location),
    )
    return wiki.pages.append(
        page_id=page_id,
        body=payload,
        fields=fields,
        is_silent=silent,
    )


@app.command()
def clone(
    page_id: PageIdArg,
    target: Annotated[str, typer.Option("--target", help="Destination slug for the copy.")],
    title: Annotated[str | None, typer.Option(help="Title of the copy, if renaming.")] = None,
    subscribe_me: Annotated[
        bool, typer.Option("--subscribe-me", help="Subscribe yourself to the copy.")
    ] = False,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
    *,
    wiki: WikiClient,
) -> AsyncOperation | CloneOperationStatus:
    """Copy a page to a new address (POST /pages/{id}/clone; async). --wait polls to completion."""
    body = PageClone(target=target, title=title, subscribe_me=subscribe_me)
    operation = wiki.pages.clone(page_id=page_id, body=body)
    if wait and operation.operation is not None and operation.operation.id is not None:
        task_id = operation.operation.id
        status = wait_for(
            lambda: wiki.operations.clone_get(task_id),
            lambda state: state.is_terminal,
            message="Waiting for page clone…",
        )
        return status
    return operation


@app.command()
def move(
    source: Annotated[str, typer.Argument(metavar="SOURCE", help="Slug of the page to move.")],
    target: Annotated[str, typer.Argument(metavar="TARGET", help="New slug for the page.")],
    next_to: Annotated[
        str | None, typer.Option("--next-to", help="Sibling slug to place the page next to.")
    ] = None,
    position: Annotated[
        str | None, values_option(OrderPosition, "--position", help="Which side of --next-to.")
    ] = None,
    copy_inherited_access: Annotated[
        bool,
        typer.Option(
            "--copy-inherited-access/--no-copy-inherited-access",
            help="Copy accesses inherited from the old parent (the API needs an explicit choice).",
        ),
    ] = False,
    validate_only: Annotated[
        bool,
        typer.Option(
            "--validate-only", help="Validate the move without applying it (nothing to wait for)."
        ),
    ] = False,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
    *,
    wiki: WikiClient,
) -> AsyncOperation | MoveOperationStatus:
    """Move or rename a page (POST /pages/move; async, undocumented by Yandex). --wait polls."""
    step = PageMoveStep(
        source=source,
        target=target,
        next_to_slug=next_to,
        position=position,
    )
    body = PageMove(operations=[step], copy_inherited_access=copy_inherited_access)
    operation = wiki.pages.move(body=body, dry_run=validate_only)
    # A validation applies nothing, and the task id it returns answers 404 when polled.
    polled = wait and not validate_only
    if polled and operation.operation is not None and operation.operation.id is not None:
        task_id = operation.operation.id
        status = wait_for(
            lambda: wiki.operations.move_get(task_id),
            lambda state: state.is_terminal,
            message="Waiting for page move…",
        )
        return status
    return operation


@app.command()
def revisions_list(
    page_id: PageIdArg,
    ids: Annotated[
        str | None, typer.Option("--ids", help="Only these revision ids (comma separated).")
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[PageRevision]:
    """List a page's saved revisions (GET /pages/{id}/revisions; undocumented by Yandex)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.revisions_list(page_id=page_id, ids=ids, limit=cap)


@app.command()
def backlinks_list(
    page_id: PageIdArg,
    for_cluster: Annotated[
        bool, typer.Option("--for-cluster", help="Links to the page's whole subtree.")
    ] = False,
    show_all: Annotated[
        bool, typer.Option("--show-all", help="The API's show_all flag (no effect seen live).")
    ] = False,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[PageRef]:
    """List the pages that link to PAGE_ID (GET /pages/{id}/backlinks; undocumented by Yandex)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.backlinks_list(
        page_id=page_id, for_cluster=for_cluster, show_all=show_all, limit=cap
    )

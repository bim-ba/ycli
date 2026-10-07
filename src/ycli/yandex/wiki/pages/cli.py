"""`wiki pages` commands — argument-based; dumps full pydantic models as JSON."""

from datetime import datetime
from typing import Annotated

import typer

from ycli.cli.progress import wait_for
from ycli.cli.typedefs import AllOption, LimitOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.models import ItemList, SortDirection
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.models import AsyncOperation, Location, OrderPosition, UserIdentity
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
    SearchDateRange,
    SearchDocumentType,
    SearchFilters,
    SearchOrder,
    SearchPage,
    SearchRequest,
)
from ycli.yandex.wiki.typedefs import PageIDArg

app = typer.Typer(name="pages", help="Wiki pages.", no_args_is_help=True)

SlugArg = Annotated[str, typer.Argument(metavar="SLUG", help="Wiki page slug.")]
RevisionIDOption = Annotated[
    int | None,
    typer.Option("--revision-id", help="Show this past revision (ids from `revisions-list`)."),
]
RaiseOnRedirectOption = Annotated[
    bool | None,
    typer.Option(
        "--raise-on-redirect/--no-raise-on-redirect",
        help="Fail if the page is a redirect, do not follow it.",
    ),
]
ReplyFieldsOption = Annotated[
    str | None, typer.Option("--fields", help="Comma-separated blocks to include in the reply.")
]
SilentOption = Annotated[
    bool | None,
    typer.Option("--is-silent/--no-is-silent", help="Do not notify the page's subscribers."),
]
IncludeSelfOption = Annotated[
    bool | None,
    typer.Option("--include-self/--no-include-self", help="Also list the ancestor page itself."),
]
ShowAllOption = Annotated[
    bool | None, typer.Option("--show-all/--no-show-all", help="The API's show_all flag.")
]
ActualityOption = Annotated[
    str | None, typer.Option(help="Only the pages in this state: actual or obsolete.")
]


@app.command()
def get(
    slug: SlugArg,
    revision_id: RevisionIDOption = None,
    raise_on_redirect: RaiseOnRedirectOption = None,
    *,
    wiki: WikiClient,
) -> str:
    """Print the text of the page SLUG; `get-meta` prints what is known about it."""
    # violation(as-given): the API returns a page without its text unless asked; `get` shows it
    page = wiki.pages.get(
        slug=slug, fields="content", revision_id=revision_id, raise_on_redirect=raise_on_redirect
    )
    return page.content or ""


@app.command("get-meta")
def get_meta(slug: SlugArg, *, wiki: WikiClient) -> PageDetails:
    """Print the page SLUG without its text: id, title, attributes and owner."""
    # violation(as-given): the API returns neither block unless asked; `get-meta` is those two
    return wiki.pages.get(slug=slug, fields="attributes,owner")


@app.command()
def descendants_list(
    slug: SlugArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    include_self: IncludeSelfOption = None,
    show_all: ShowAllOption = None,
    actuality: ActualityOption = None,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[PageRef]:
    """Print descendant slugs under SLUG (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.descendants_list(
        slug=slug, limit=cap, actuality=actuality, include_self=include_self, show_all=show_all
    )


@app.command("get-by-id")
def get_by_id(
    page_id: PageIDArg,
    fields: Annotated[
        str | None, typer.Option(help="Comma-separated fields, e.g. content,attributes.")
    ] = None,
    revision_id: RevisionIDOption = None,
    raise_on_redirect: RaiseOnRedirectOption = None,
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


@app.command("descendants-list-by-id")
def descendants_list_by_id(
    page_id: PageIDArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    include_self: IncludeSelfOption = None,
    show_all: ShowAllOption = None,
    actuality: ActualityOption = None,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[PageRef]:
    """Print descendant slugs under a numeric PAGE_ID (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.descendants_list_by_id(
        page_id=page_id,
        limit=cap,
        actuality=actuality,
        include_self=include_self,
        show_all=show_all,
    )


@app.command()
def grids_list(
    page_id: PageIDArg,
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
    is_silent: SilentOption = None,
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Create a wiki page (POST /pages)."""
    return wiki.pages.create(
        body=PageCreate(slug=slug, title=title, content=content),
        fields=fields,
        is_silent=is_silent,
    )


@app.command()
def update(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    content: Annotated[
        str | None,
        typer.Option(help='New Markdown body, replacing the whole one — pass "$(cat file.md)".'),
    ] = None,
    title: Annotated[str | None, typer.Option(help="New title.")] = None,
    fields: ReplyFieldsOption = None,
    is_silent: SilentOption = None,
    allow_merge: Annotated[
        bool | None,
        typer.Option(
            "--allow-merge/--no-allow-merge",
            help="Merge with a concurrent edit instead of failing.",
        ),
    ] = None,
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Update a wiki page by id (POST /pages/{id}): only what is given changes."""
    return wiki.pages.update(
        page_id=page_id,
        body=PageUpdate(content=content, title=title),
        fields=fields,
        is_silent=is_silent,
        allow_merge=allow_merge,
    )


@app.command()
def delete(
    page_id: PageIDArg,
    recursive: Annotated[
        bool | None,
        typer.Option("--recursive/--no-recursive", help="Also delete every page under it."),
    ] = None,
    *,
    wiki: WikiClient,
) -> PageDeleteResult:
    """Delete a wiki page (DELETE /pages/{id}); emits the recovery_token to undo it."""
    return wiki.pages.delete(page_id=page_id, recursive=recursive)


@app.command()
def append(
    page_id: PageIDArg,
    content: Annotated[str, typer.Option(help='YFM fragment to append — pass "$(cat file.md)".')],
    location: Annotated[
        str | None,
        values_option(Location, help="Where in the body; without a placement the API answers 400."),
    ] = None,
    fields: ReplyFieldsOption = None,
    is_silent: SilentOption = None,
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Append content to a wiki page (POST /pages/{id}/append-content).

    The API requires exactly one placement selector (``body`` / ``section`` / ``anchor``) and
    rejects a bare ``{content}`` with 400: ``--location`` gives the whole-page ``body`` selector.
    """
    payload = PageAppendContent(
        content=content,
        body=PageAppendContentBody(location=location) if location is not None else None,
    )
    return wiki.pages.append(
        page_id=page_id,
        body=payload,
        fields=fields,
        is_silent=is_silent,
    )


@app.command()
def clone(
    page_id: PageIDArg,
    target: Annotated[str, typer.Option("--target", help="Destination slug for the copy.")],
    title: Annotated[str | None, typer.Option(help="Title of the copy, if renaming.")] = None,
    subscribe_me: Annotated[
        bool | None,
        typer.Option("--subscribe-me/--no-subscribe-me", help="Subscribe yourself to the copy."),
    ] = None,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
    *,
    config: AppConfig,
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
            max_wait_seconds=config.http.max_wait_seconds,
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
        bool | None,
        typer.Option(
            "--copy-inherited-access/--no-copy-inherited-access",
            help="Copy accesses inherited from the old parent; "
            "the API can refuse a move without a choice.",
        ),
    ] = None,
    validate_only: Annotated[
        bool | None,
        typer.Option(
            "--validate-only/--no-validate-only",
            help="Validate the move without applying it (nothing to wait for).",
        ),
    ] = None,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
    *,
    config: AppConfig,
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
    operation = wiki.pages.move(body=body, validate_only=validate_only)
    # A validation applies nothing, and the task id it returns answers 404 when polled.
    polled = wait and not validate_only
    if polled and operation.operation is not None and operation.operation.id is not None:
        task_id = operation.operation.id
        status = wait_for(
            lambda: wiki.operations.move_get(task_id),
            lambda state: state.is_terminal,
            message="Waiting for page move…",
            max_wait_seconds=config.http.max_wait_seconds,
        )
        return status
    return operation


@app.command()
def revisions_list(
    page_id: PageIDArg,
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
    page_id: PageIDArg,
    for_cluster: Annotated[
        bool | None,
        typer.Option("--for-cluster/--no-for-cluster", help="Links to the page's whole subtree."),
    ] = None,
    show_all: Annotated[
        bool | None,
        typer.Option(
            "--show-all/--no-show-all", help="The API's show_all flag (no effect seen live)."
        ),
    ] = None,
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


def _window(start: datetime | None, end: datetime | None) -> SearchDateRange | None:
    """The window from ``--*-from`` / ``--*-to``; ``None`` when neither is given."""
    if start is None and end is None:
        return None
    return SearchDateRange.model_validate({"from": start, "to": end})


@app.command("search")
def search(
    text: Annotated[str, typer.Argument(metavar="QUERY", help="Text to search for.")],
    type_: Annotated[
        str | None, values_option(SearchDocumentType, "--type", help="Only pages or only files.")
    ] = None,
    cluster: Annotated[
        str | None, typer.Option(help="Only documents under this page slug, e.g. team/handbook.")
    ] = None,
    author_uid: Annotated[
        list[str] | None,
        typer.Option("--author-uid", help="Only documents by this passport uid (repeatable)."),
    ] = None,
    author_cloud_uid: Annotated[
        list[str] | None,
        typer.Option("--author-cloud-uid", help="Only documents by this cloud uid (repeatable)."),
    ] = None,
    created_from: Annotated[
        datetime | None, typer.Option("--created-from", help="Created from (with --created-to).")
    ] = None,
    created_to: Annotated[
        datetime | None, typer.Option("--created-to", help="Created until (with --created-from).")
    ] = None,
    modified_from: Annotated[
        datetime | None, typer.Option("--modified-from", help="Modified from (with --modified-to).")
    ] = None,
    modified_to: Annotated[
        datetime | None,
        typer.Option("--modified-to", help="Modified until (with --modified-from)."),
    ] = None,
    show_obsolete: Annotated[
        bool | None,
        typer.Option("--show-obsolete/--no-show-obsolete", help="Also return obsolete documents."),
    ] = None,
    order_by: Annotated[
        str | None,
        values_option(SearchOrder, "--order-by", help="What to sort the hits by."),
    ] = None,
    highlight: Annotated[
        bool | None, typer.Option("--highlight/--no-highlight", help="Wrap matches in <em> tags.")
    ] = None,
    limit: Annotated[int | None, typer.Option(help="Results per page.")] = None,
    cursor: Annotated[
        int | None, typer.Option(help="Result page to fetch, from 1 (see next_cursor).")
    ] = None,
    *,
    wiki: WikiClient,
) -> SearchPage:
    """Search pages and files by text (POST /search); prints one page, --cursor picks which.

    The API has refused a date window with one end (400), so give both.
    """
    authors = [UserIdentity(uid=uid) for uid in author_uid or []] + [
        UserIdentity(cloud_uid=cloud_uid) for cloud_uid in author_cloud_uid or []
    ]
    filters = SearchFilters(
        type=type_,
        authors=authors or None,
        cluster=cluster,
        created_at=_window(created_from, created_to),
        modified_at=_window(modified_from, modified_to),
        show_obsolete=show_obsolete,
    )
    request = SearchRequest(
        query=text,
        filters=filters if filters.model_dump(exclude_defaults=True) else None,
        cursor=cursor,
        limit=limit,
        order_by=order_by,
        highlight=highlight,
    )
    return wiki.pages.search(request)

"""`wiki search` commands — full-text search over pages and files."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

import typer

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.models import UserIdentity
from ycli.yandex.wiki.search.models import (
    SearchDateRange,
    SearchDocumentType,
    SearchFilters,
    SearchOrder,
    SearchPage,
    SearchRequest,
)

app = typer.Typer(name="search", help="Wiki full-text search.", no_args_is_help=True)


def _window(start: datetime | None, end: datetime | None) -> SearchDateRange | None:
    """The window from ``--*-from`` / ``--*-to``; one end alone fails (the API needs both)."""
    if start is None and end is None:
        return None
    given = {"from": start, "to": end}
    return SearchDateRange.model_validate({key: value for key, value in given.items() if value})


@app.command()
def query(
    text: Annotated[str, typer.Argument(metavar="QUERY", help="Text to search for.")],
    type_: Annotated[
        SearchDocumentType | None, typer.Option("--type", help="Only pages or only files.")
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
        bool, typer.Option("--show-obsolete", help="Also return obsolete documents.")
    ] = False,
    order_by: Annotated[
        SearchOrder, typer.Option("--order-by", help="relevancy, creation_date or modified_date.")
    ] = "relevancy",
    highlight: Annotated[
        bool, typer.Option("--highlight", help="Wrap matches in <em> tags.")
    ] = False,
    limit: Annotated[int, typer.Option(min=1, max=50, help="Results per page.")] = 10,
    cursor: Annotated[
        int, typer.Option(min=1, max=500, help="Result page to fetch, from 1 (see next_cursor).")
    ] = 1,
    *,
    wiki: WikiClient,
) -> SearchPage:
    """Search pages and files by text (POST /search); prints one page, --cursor picks which.

    A date window needs both ends (--created-from with --created-to, likewise --modified-*).
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
    return wiki.search.query(request.model_dump(mode="json", exclude_none=True))

"""`wiki pages` commands — argument-based; dumps full pydantic models as JSON."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.progress import wait_for
from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.operations.models import CloneOperationStatus
from ycli.yandex.wiki.pages.models import (
    GridRefList,
    PageAppendContent,
    PageAppendContentBody,
    PageClone,
    PageCloneOperation,
    PageDeleteResult,
    PageDetails,
    PageRefList,
)

app = typer.Typer(name="pages", help="Wiki pages.", no_args_is_help=True)

SlugArg = Annotated[str, typer.Argument(metavar="SLUG", help="Wiki page slug.")]
PageIdArg = Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")]


@app.command()
def get(
    slug: SlugArg,
    fields: Annotated[
        str, typer.Option(help="Comma-separated fields, e.g. content,attributes.")
    ] = "content",
    *,
    wiki: WikiClient,
) -> str:
    """Print the page body (default fields=content) for SLUG."""
    return wiki.pages.get(slug=slug, fields=fields).content or ""


@app.command()
def descendants(
    slug: SlugArg,
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> PageRefList:
    """Print descendant slugs under SLUG (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.descendants(slug=slug, limit=cap)


@app.command("get-by-id")
def get_by_id(
    page_id: PageIdArg,
    fields: Annotated[
        str, typer.Option(help="Comma-separated fields, e.g. content,attributes.")
    ] = "content",
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Fetch a page by numeric id (GET /pages/{id}); dumps the full model."""
    return wiki.pages.get_by_id(page_id=page_id, fields=fields)


@app.command("descendants-by-id")
def descendants_by_id(
    page_id: PageIdArg,
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> PageRefList:
    """Print descendant slugs under a numeric PAGE_ID (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.descendants_by_id(page_id=page_id, limit=cap)


@app.command()
def grids(
    page_id: PageIdArg,
    limit: LimitOption = 0,
    all_: AllOption = False,
    order_by: Annotated[
        str, typer.Option("--order-by", help="Sort field: title or created_at.")
    ] = "",
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> GridRefList:
    """List dynamic tables (grids) attached to a numeric PAGE_ID (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.pages.grids(page_id=page_id, limit=cap, order_by=order_by or None)


@app.command()
def create(
    slug: Annotated[str, typer.Option(help="Target slug, e.g. data/x.")],
    title: Annotated[str, typer.Option(help="Page title.")],
    content: Annotated[str, typer.Option(help='Markdown body — pass "$(cat file.md)".')],
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Create a wiki page (POST /pages)."""
    return wiki.pages.create(body={"slug": slug, "title": title, "content": content})


@app.command()
def update(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    content: Annotated[str, typer.Option(help='Markdown body — pass "$(cat file.md)".')],
    title: Annotated[str, typer.Option(help="New title (optional).")] = "",
    *,
    wiki: WikiClient,
) -> PageDetails:
    """Update a wiki page by id (POST /pages/{id})."""
    body: dict[str, str] = {"content": content}
    if title:
        body["title"] = title
    return wiki.pages.update(page_id=page_id, body=body)


@app.command()
def delete(page_id: PageIdArg, *, wiki: WikiClient) -> PageDeleteResult:
    """Delete a wiki page (DELETE /pages/{id}); emits the recovery_token to undo it."""
    return wiki.pages.delete(page_id=page_id)


@app.command()
def append(
    page_id: PageIdArg,
    content: Annotated[str, typer.Option(help='YFM fragment to append — pass "$(cat file.md)".')],
    location: Annotated[
        str, typer.Option(help="Where in the body: top or bottom (default: bottom).")
    ] = "bottom",
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
        body=PageAppendContentBody(location=location),  # ty: ignore[invalid-argument-type]  # pydantic validates the top|bottom literal
    )
    return wiki.pages.append_content(page_id=page_id, body=payload.model_dump(exclude_none=True))


@app.command()
def clone(
    page_id: PageIdArg,
    target: Annotated[str, typer.Option("--target", help="Destination slug for the copy.")],
    title: Annotated[str, typer.Option(help="Title of the copy, if renaming.")] = "",
    subscribe_me: Annotated[
        bool, typer.Option("--subscribe-me", help="Subscribe yourself to the copy.")
    ] = False,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
    *,
    wiki: WikiClient,
) -> PageCloneOperation | CloneOperationStatus:
    """Copy a page to a new address (POST /pages/{id}/clone; async). --wait polls to completion."""
    body = PageClone(target=target, title=title or None, subscribe_me=subscribe_me).model_dump(
        exclude_none=True
    )
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

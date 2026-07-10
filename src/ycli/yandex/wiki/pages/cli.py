"""`wiki pages` commands — argument-based; dumps full pydantic models as JSON."""

from __future__ import annotations

import time
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.polling import poll
from ycli.yandex.wiki.pages.models import PageAppendContent, PageAppendContentBody, PageClone

app = typer.Typer(name="pages", help="Wiki pages.", no_args_is_help=True)

SlugArg = Annotated[str, typer.Argument(metavar="SLUG", help="Wiki page slug.")]
PageIdArg = Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")]


@app.command()
def get(
    ctx: typer.Context,
    slug: SlugArg,
    fields: Annotated[
        str, typer.Option(help="Comma-separated fields, e.g. content,attributes.")
    ] = "content",
) -> None:
    """Print the page body (default fields=content) for SLUG."""
    app_ctx = AppContext.from_typer_context(ctx)
    print(app_ctx.wiki.pages.get(slug=slug, fields=fields).content or "")


@app.command()
def descendants(
    ctx: typer.Context,
    slug: SlugArg,
    limit: Annotated[int, typer.Option(help="Max refs (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every descendant (no cap).")] = False,
) -> None:
    """Print descendant slugs under SLUG (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(
        app_ctx.wiki.pages.descendants(slug=slug, limit=cap), app_ctx.strategy, app_ctx.console
    )


@app.command("get-by-id")
def get_by_id(
    ctx: typer.Context,
    page_id: PageIdArg,
    fields: Annotated[
        str, typer.Option(help="Comma-separated fields, e.g. content,attributes.")
    ] = "content",
) -> None:
    """Fetch a page by numeric id (GET /pages/{id}); dumps the full model."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.pages.get_by_id(page_id=page_id, fields=fields),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command("descendants-by-id")
def descendants_by_id(
    ctx: typer.Context,
    page_id: PageIdArg,
    limit: Annotated[int, typer.Option(help="Max refs (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every descendant (no cap).")] = False,
) -> None:
    """Print descendant slugs under a numeric PAGE_ID (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(
        app_ctx.wiki.pages.descendants_by_id(page_id=page_id, limit=cap),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def grids(
    ctx: typer.Context,
    page_id: PageIdArg,
    limit: Annotated[int, typer.Option(help="Max grids (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every grid (no cap).")] = False,
    order_by: Annotated[
        str, typer.Option("--order-by", help="Sort field: title or created_at.")
    ] = "",
) -> None:
    """List dynamic tables (grids) attached to a numeric PAGE_ID (auto-paginated)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(
        app_ctx.wiki.pages.grids(page_id=page_id, limit=cap, order_by=order_by or None),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def create(
    ctx: typer.Context,
    slug: Annotated[str, typer.Option(help="Target slug, e.g. data/x.")],
    title: Annotated[str, typer.Option(help="Page title.")],
    content: Annotated[str, typer.Option(help='Markdown body — pass "$(cat file.md)".')],
) -> None:
    """Create a wiki page (POST /pages)."""
    app_ctx = AppContext.from_typer_context(ctx)
    page = app_ctx.wiki.pages.create(body={"slug": slug, "title": title, "content": content})
    Serializer.serialize(page, app_ctx.strategy, app_ctx.console)


@app.command()
def update(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    content: Annotated[str, typer.Option(help='Markdown body — pass "$(cat file.md)".')],
    title: Annotated[str, typer.Option(help="New title (optional).")] = "",
) -> None:
    """Update a wiki page by id (POST /pages/{id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    body: dict[str, str] = {"content": content}
    if title:
        body["title"] = title
    Serializer.serialize(
        app_ctx.wiki.pages.update(page_id=page_id, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def delete(ctx: typer.Context, page_id: PageIdArg) -> None:
    """Delete a wiki page (DELETE /pages/{id}); emits the recovery_token to undo it."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.pages.delete(page_id=page_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def append(
    ctx: typer.Context,
    page_id: PageIdArg,
    content: Annotated[str, typer.Option(help='YFM fragment to append — pass "$(cat file.md)".')],
    location: Annotated[
        str, typer.Option(help="Where in the body: top or bottom (default: end).")
    ] = "",
) -> None:
    """Append content to a wiki page (POST /pages/{id}/append-content)."""
    app_ctx = AppContext.from_typer_context(ctx)
    payload = PageAppendContent(
        content=content,
        body=PageAppendContentBody(location=location) if location else None,  # ty: ignore[invalid-argument-type]
    )
    Serializer.serialize(
        app_ctx.wiki.pages.append_content(
            page_id=page_id, body=payload.model_dump(exclude_none=True)
        ),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def clone(
    ctx: typer.Context,
    page_id: PageIdArg,
    target: Annotated[str, typer.Option("--target", help="Destination slug for the copy.")],
    title: Annotated[str, typer.Option(help="Title of the copy, if renaming.")] = "",
    subscribe_me: Annotated[
        bool, typer.Option("--subscribe-me", help="Subscribe yourself to the copy.")
    ] = False,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
) -> None:
    """Copy a page to a new address (POST /pages/{id}/clone; async). --wait polls to completion."""
    app_ctx = AppContext.from_typer_context(ctx)
    body = PageClone(target=target, title=title or None, subscribe_me=subscribe_me).model_dump(
        exclude_none=True
    )
    operation = app_ctx.wiki.pages.clone(page_id=page_id, body=body)
    if wait and operation.operation is not None and operation.operation.id is not None:
        task_id = operation.operation.id
        status = poll(
            lambda: app_ctx.wiki.operations.clone_get(task_id),
            lambda state: state.is_terminal,
            sleep=lambda seconds: time.sleep(seconds),
        )
        Serializer.serialize(status, app_ctx.strategy, app_ctx.console)
    else:
        Serializer.serialize(operation, app_ctx.strategy, app_ctx.console)

"""`wiki pages` commands — argument-based; dumps full pydantic models as JSON."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.context import AppContext
from ycli.output import Serializer
from ycli.settings import AppConfig

app = typer.Typer(name="pages", help="Wiki pages.", no_args_is_help=True)

SlugArg = Annotated[str, typer.Argument(metavar="SLUG", help="Wiki page slug.")]


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
    cap = None if all_ else (limit or AppConfig().max_items)
    Serializer.serialize(
        app_ctx.wiki.pages.descendants(slug=slug, limit=cap), app_ctx.strategy, app_ctx.console
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

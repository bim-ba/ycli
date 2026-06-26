"""`wiki pages` commands — argument-based; dumps full pydantic models as JSON."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.wiki._clideps import wiki_client

app = typer.Typer(name="pages", help="Wiki pages.", no_args_is_help=True)

SlugArg = Annotated[str, typer.Argument(metavar="SLUG", help="Wiki page slug.")]


@app.command()
def get(
    ctx: typer.Context,
    slug: SlugArg,
    fields: Annotated[str, typer.Option(help="Comma-separated fields, e.g. content,attributes.")] = "content",
) -> None:
    """Print the page body (default fields=content) for SLUG."""
    client = wiki_client(ctx)
    print(client.pages.get(slug=slug, fields=fields).content or "")


@app.command()
def descendants(
    ctx: typer.Context,
    slug: SlugArg,
    limit: Annotated[int, typer.Option(help="page_size (max 100/call).")] = 100,
    cursor: Annotated[str, typer.Option(help="Pagination cursor (one page per call).")] = "",
) -> None:
    """Print one page of descendant slugs under SLUG (caller paginates via --cursor)."""
    client = wiki_client(ctx)
    resp = client.pages.descendants(slug=slug, page_size=limit, cursor=cursor or None)
    print(resp.model_dump_json(by_alias=True))


@app.command()
def create(
    ctx: typer.Context,
    slug: Annotated[str, typer.Option(help="Target slug, e.g. data/x.")],
    title: Annotated[str, typer.Option(help="Page title.")],
    content: Annotated[str, typer.Option(help='Markdown body — pass "$(cat file.md)".')],
) -> None:
    """Create a wiki page (POST /pages)."""
    client = wiki_client(ctx)
    page = client.pages.create(body={"slug": slug, "title": title, "content": content})
    print(page.model_dump_json(by_alias=True))


@app.command()
def update(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    content: Annotated[str, typer.Option(help='Markdown body — pass "$(cat file.md)".')],
    title: Annotated[str, typer.Option(help="New title (optional).")] = "",
) -> None:
    """Update a wiki page by id (POST /pages/{id})."""
    client = wiki_client(ctx)
    body: dict[str, str] = {"content": content}
    if title:
        body["title"] = title
    print(client.pages.update(page_id=page_id, body=body).model_dump_json(by_alias=True))

"""`tracker filters` commands."""

from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.filters.models import FilterCreate, FilterUpdate

app = typer.Typer(name="filters", help="Tracker saved filters.", no_args_is_help=True)


def _parse_filter(raw: str) -> dict[str, Any] | None:
    """Parse a ``--filter`` JSON object string into a dict, or return None when empty."""
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"--filter must be valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise typer.BadParameter("--filter must be a JSON object.")
    return parsed


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(
    ctx: typer.Context,
    filter_id: Annotated[
        str, typer.Argument(metavar="FILTER_ID", help="Identifier of the saved filter.")
    ],
) -> None:
    """Get parameters of one saved filter by FILTER_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.filters.get(filter_id=filter_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help="Display name of the new filter.")],
    query: Annotated[
        str, typer.Option(help="Filtering conditions in Tracker query language.")
    ] = "",
    filter_: Annotated[
        str, typer.Option("--filter", help="Filtering conditions as a JSON object.")
    ] = "",
) -> None:
    """Create a saved filter (POST /filters/)."""
    body = FilterCreate(name=name, query=query or None, filter=_parse_filter(filter_))
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.filters.create(body), app_ctx.strategy, app_ctx.console)


@app.command()
def edit(
    ctx: typer.Context,
    filter_id: Annotated[
        str, typer.Argument(metavar="FILTER_ID", help="Identifier of the saved filter.")
    ],
    name: Annotated[str, typer.Option(help="New display name of the filter.")] = "",
    query: Annotated[str, typer.Option(help="New filtering conditions in query language.")] = "",
    filter_: Annotated[
        str, typer.Option("--filter", help="Replacement filtering conditions as a JSON object.")
    ] = "",
) -> None:
    """Edit filter FILTER_ID (PATCH /filters/{id}) — no version lock; filter is replaced whole."""
    body = FilterUpdate(name=name or None, query=query or None, filter=_parse_filter(filter_))
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.filters.edit(filter_id, body), app_ctx.strategy, app_ctx.console
    )

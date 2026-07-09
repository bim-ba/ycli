"""`tracker queues` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="queues", help="Tracker queues.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option(help="Max queues (auto-paginates over pages).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every queue (no cap).")] = False,
) -> None:
    """List all queues (auto-paginated over pages; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(app_ctx.tracker.queues.list(limit=cap), app_ctx.strategy, app_ctx.console)


@app.command()
def get(
    ctx: typer.Context,
    queue_id: Annotated[str, typer.Argument(help="Queue key (case-sensitive) or numeric id.")],
    expand: Annotated[
        str, typer.Option(help="Extra blocks to include, e.g. all or types,team,versions.")
    ] = "",
) -> None:
    """Print one queue's settings for QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.queues.get(queue_id, expand=expand or None),
        app_ctx.strategy,
        app_ctx.console,
    )

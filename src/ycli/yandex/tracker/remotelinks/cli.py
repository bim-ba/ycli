"""`tracker remotelinks` commands — list/create/delete links to external-app objects."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.remotelinks.models import RemoteLinkCreate
from ycli.yandex.tracker.typedefs import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(
    name="remotelinks", help="Tracker issue external-app links.", no_args_is_help=True
)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List external links on issue KEY (GET /issues/{key}/remotelinks)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.remotelinks.list(key), app_ctx.strategy, app_ctx.console)


@app.command()
def create(
    ctx: typer.Context,
    key: KeyArg,
    object_key: Annotated[
        str, typer.Option("--key", help="Key of the object in the external app.")
    ],
    origin: Annotated[str, typer.Option(help="Identifier of the external application.")],
    relationship: Annotated[str, typer.Option(help="Link type (RELATES recommended).")] = "RELATES",
    backlink: Annotated[
        bool,
        typer.Option("--backlink/--no-backlink", help="Also create the mirror link in the app."),
    ] = False,
) -> None:
    """Add an external link to issue KEY (POST /issues/{key}/remotelinks)."""
    body = RemoteLinkCreate(relationship=relationship, key=object_key, origin=origin).model_dump(
        exclude_none=True
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.remotelinks.create(
            key, body=body, backlink="true" if backlink else "false"
        ),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(
    ctx: typer.Context,
    key: KeyArg,
    link_id: Annotated[str, typer.Argument(metavar="LINK_ID", help="Remote-link id to delete.")],
) -> None:
    """Delete external link LINK_ID from issue KEY (DELETE /issues/{key}/remotelinks/{id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.remotelinks.delete(key, link_id)
    print(f"Deleted remote link {link_id} on {key}")

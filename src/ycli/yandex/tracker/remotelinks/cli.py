"""`tracker remotelinks` commands — list/create/delete links to external-app objects."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.remotelinks.models import RemoteLink, RemoteLinkCreate, RemoteLinkList
from ycli.yandex.tracker.typedefs import (
    KeyArg,
)

app = typer.Typer(
    name="remotelinks", help="Tracker issue external-app links.", no_args_is_help=True
)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(key: KeyArg, *, tracker: TrackerClient) -> RemoteLinkList:
    """List external links on issue KEY (GET /issues/{key}/remotelinks)."""
    return tracker.remotelinks.list(key)


@app.command()
def create(
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
    *,
    tracker: TrackerClient,
) -> RemoteLink:
    """Add an external link to issue KEY (POST /issues/{key}/remotelinks)."""
    body = RemoteLinkCreate(relationship=relationship, key=object_key, origin=origin).model_dump(
        exclude_none=True
    )
    return tracker.remotelinks.create(key, body=body, backlink="true" if backlink else "false")


@app.command()
def delete(
    key: KeyArg,
    link_id: Annotated[str, typer.Argument(metavar="LINK_ID", help="Remote-link id to delete.")],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete external link LINK_ID from issue KEY (DELETE /issues/{key}/remotelinks/{id})."""
    tracker.remotelinks.delete(key, link_id)
    return Ack.deleted("remote link", link_id, on=key)

"""`tracker remotelinks` commands — list/create/delete links to external-app objects."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.remotelinks.models import RemoteLink, RemoteLinkCreate
from ycli.yandex.tracker.typedefs import IssueKeyArg

app = typer.Typer(
    name="remotelinks", help="Tracker issue external-app links.", no_args_is_help=True
)


@app.command("list")
def list_(issue_key: IssueKeyArg, *, tracker: TrackerClient) -> ItemList[RemoteLink]:
    """List external links on issue ISSUE_KEY (GET /issues/{issue_key}/remotelinks)."""
    return tracker.remotelinks.list(issue_key)


@app.command()
def create(
    issue_key: IssueKeyArg,
    object_key: Annotated[
        str, typer.Option("--key", help="Key of the object in the external app.")
    ],
    origin: Annotated[str, typer.Option(help="Identifier of the external application.")],
    relationship: Annotated[str, typer.Option(help="Link type (RELATES recommended).")],
    backlink: Annotated[
        bool | None,
        typer.Option("--backlink/--no-backlink", help="Also create the mirror link in the app."),
    ] = None,
    *,
    tracker: TrackerClient,
) -> RemoteLink:
    """Add an external link to issue ISSUE_KEY (POST /issues/{issue_key}/remotelinks)."""
    body = RemoteLinkCreate(relationship=relationship, key=object_key, origin=origin)
    return tracker.remotelinks.create(issue_key, body=body, backlink=backlink)


@app.command()
def delete(
    issue_key: IssueKeyArg,
    link_id: Annotated[str, typer.Argument(metavar="LINK_ID", help="Remote-link id to delete.")],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete external link LINK_ID from issue ISSUE_KEY (DELETE …/remotelinks/{id})."""
    tracker.remotelinks.delete(issue_key, link_id)
    return Ack.deleted("remote link", link_id, on=issue_key)

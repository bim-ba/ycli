"""`tracker issuetypes` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issuetypes.models import (
    IssueType,
    IssueTypeCreate,
    IssueTypeList,
    IssueTypeUpdate,
    LocalizedName,
)

app = typer.Typer(name="issuetypes", help="Tracker issue types.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(*, tracker: TrackerClient) -> IssueTypeList:
    """List all issue types."""
    return tracker.issuetypes.list()


@app.command()
def create(
    key: Annotated[str, typer.Option(help="Key of the new issue type.")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="Issue type name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Issue type name in English.")] = "",
    *,
    tracker: TrackerClient,
) -> IssueType:
    """Create an issue type (POST /issuetypes/)."""
    body = IssueTypeCreate(
        key=key,
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
    )
    return tracker.issuetypes.create(body)


@app.command()
def edit(
    issue_type_id: Annotated[
        str, typer.Argument(metavar="ISSUE_TYPE_ID", help="Issue type id or key.")
    ],
    name_ru: Annotated[str, typer.Option("--name-ru", help="New issue type name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="New issue type name in English.")] = "",
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> IssueType:
    """Edit issue type ISSUE_TYPE_ID (PATCH /issuetypes/{id}?version=)."""
    body = IssueTypeUpdate(name=LocalizedName(ru=name_ru or None, en=name_en or None))
    return tracker.issuetypes.edit(issue_type_id, body, version=version)

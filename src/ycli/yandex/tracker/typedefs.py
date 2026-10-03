"""Shared tracker CLI argument type aliases."""

from __future__ import annotations

from typing import Annotated

import typer

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key, e.g. DATAENGINEERING-1.")]

# The parameters most write operations share: what the reply carries and who is notified.
ExpandOpt = Annotated[str, typer.Option("--expand", help="Extra blocks to include in the reply.")]
ReplyFieldsOpt = Annotated[
    str, typer.Option("--fields", help="Comma-separated fields to include in the reply.")
]
NotifyOpt = Annotated[
    bool | None,
    typer.Option(
        "--notify/--no-notify",
        help="Notify the users in the fields of the object (the API notifies by default).",
    ),
]
NotifyAuthorOpt = Annotated[
    bool | None,
    typer.Option(
        "--notify-author/--no-notify-author",
        help="Notify the author of the change (the API does not by default).",
    ),
]
AddToFollowersOpt = Annotated[
    bool | None,
    typer.Option(
        "--add-to-followers/--no-add-to-followers",
        help="Add the comment's author to the followers (the API adds by default).",
    ),
]

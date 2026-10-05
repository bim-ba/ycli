"""Shared tracker CLI argument type aliases."""

from __future__ import annotations

from typing import Annotated

import typer

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key, e.g. DATAENGINEERING-1.")]

# The parameters most write operations share: what the reply carries and who is notified.
ExpandOpt = Annotated[
    str | None, typer.Option("--expand", help="Extra blocks to include in the reply.")
]
ReplyFieldsOpt = Annotated[
    str | None, typer.Option("--fields", help="Comma-separated fields to include in the reply.")
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
QueueIDArg = Annotated[
    str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
]
BoardIDArg = Annotated[int, typer.Argument(metavar="BOARD_ID", help="Numeric board identifier.")]
ItemIDArg = Annotated[str, typer.Argument(metavar="ITEM_ID", help="Checklist item id.")]
OptionsTypeOpt = Annotated[
    str, typer.Option("--options-type", help="Drop-down provider type for --option values.")
]
OptionOpt = Annotated[
    list[str] | None,
    typer.Option("--option", help="Allowed drop-down value (repeatable)."),
]
ImportCreatedAtOpt = Annotated[
    str, typer.Option("--created-at", help="Original creation time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
]
ImportCreatedByOpt = Annotated[
    str, typer.Option("--created-by", help="Login or id of the original author.")
]

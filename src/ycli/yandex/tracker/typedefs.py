"""Shared tracker CLI argument type aliases."""

from typing import Annotated

import typer

from ycli.yandex.tracker.models import DeadlineInput, OptionsProviderInput

IssueKeyArg = Annotated[
    str, typer.Argument(metavar="ISSUE_KEY", help="Issue key, e.g. DATAENGINEERING-1.")
]

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
        "--is-add-to-followers/--no-is-add-to-followers",
        help="Add the comment's author to the followers (the API adds by default).",
    ),
]
QueueIDArg = Annotated[
    str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
]
BoardIDArg = Annotated[int, typer.Argument(metavar="BOARD_ID", help="Numeric board identifier.")]
ItemIDArg = Annotated[str, typer.Argument(metavar="ITEM_ID", help="Checklist item id.")]
DeadlineTypeOpt = Annotated[
    str | None, typer.Option(help="Deadline kind: date or quarter; the API requires it.")
]
OptionsTypeOpt = Annotated[
    str | None, typer.Option("--options-type", help="Drop-down provider type for --option values.")
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


def options_provider(
    values: list[str] | None, provider_type: str | None
) -> OptionsProviderInput | None:
    """The drop-down of a field from ``--option`` and ``--options-type``, or ``None``.

    Args:
        values: The ``--option`` values, when given.
        provider_type: The ``--options-type``, when given.

    Returns:
        The provider, or ``None`` when neither option was given.

    Raises:
        typer.BadParameter: Only one of the two options was given.
    """
    if values is None and provider_type is None:
        return None
    if values is None or provider_type is None:
        # violation(arch-9): a drop-down is its type and its values; one alone builds no provider
        raise typer.BadParameter("--option and --options-type go together")
    return OptionsProviderInput(type=provider_type, values=values)


def deadline_option(date: str | None, deadline_type: str | None) -> DeadlineInput | None:
    """The deadline of a checklist item from ``--deadline`` and ``--deadline-type``, or ``None``.

    Args:
        date: The ``--deadline`` value, when given.
        deadline_type: The ``--deadline-type`` value, when given.

    Returns:
        The deadline, or ``None`` when neither option was given.

    Raises:
        typer.BadParameter: Only one of the two options was given.
    """
    if date is None and deadline_type is None:
        return None
    if date is None or deadline_type is None:
        # violation(arch-9): a deadline is its date and its kind; one alone builds no deadline
        raise typer.BadParameter("--deadline and --deadline-type go together")
    return DeadlineInput.model_validate({"date": date, "deadlineType": deadline_type})

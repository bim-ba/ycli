"""`tracker checklists` commands (checklist item lifecycle on an issue)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.checklists.models import (
    ChecklistDeadlineInput,
    ChecklistItemCreate,
    ChecklistItemUpdate,
)
from ycli.yandex.tracker.typedefs import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="checklists", help="Tracker issue checklists.", no_args_is_help=True)

ItemIdArg = Annotated[str, typer.Argument(metavar="ITEM_ID", help="Checklist item id.")]
TextOpt = Annotated[str, typer.Option(help="Item text.")]
CheckedOpt = Annotated[bool | None, typer.Option("--checked/--no-checked", help="Done flag.")]
AssigneeOpt = Annotated[str, typer.Option(help="Assignee login or id.")]
DeadlineOpt = Annotated[str, typer.Option(help="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(ctx: typer.Context, key: KeyArg) -> None:
    """List the checklist items on issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.checklists.get(key), app_ctx.strategy, app_ctx.console)


@app.command()
def add(
    ctx: typer.Context,
    key: KeyArg,
    text: TextOpt,
    checked: CheckedOpt = None,
    assignee: AssigneeOpt = "",
    deadline: DeadlineOpt = "",
) -> None:
    """Add a checklist item to issue KEY (creates the checklist if absent)."""
    body = ChecklistItemCreate(
        text=text,
        checked=checked,
        assignee=assignee or None,
        deadline=ChecklistDeadlineInput(date=deadline) if deadline else None,
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.checklists.create(key, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def edit(
    ctx: typer.Context,
    key: KeyArg,
    item_id: ItemIdArg,
    text: TextOpt = "",
    checked: CheckedOpt = None,
    assignee: AssigneeOpt = "",
    deadline: DeadlineOpt = "",
) -> None:
    """Edit checklist item ITEM_ID on issue KEY — only supplied fields are sent."""
    body = ChecklistItemUpdate(
        text=text or None,
        checked=checked,
        assignee=assignee or None,
        deadline=ChecklistDeadlineInput(date=deadline) if deadline else None,
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.checklists.edit(key, item_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(ctx: typer.Context, key: KeyArg, item_id: ItemIdArg) -> None:
    """Delete checklist item ITEM_ID from issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.checklists.delete(key, item_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def clear(ctx: typer.Context, key: KeyArg) -> None:
    """Delete the entire checklist from issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.checklists.clear(key), app_ctx.strategy, app_ctx.console)

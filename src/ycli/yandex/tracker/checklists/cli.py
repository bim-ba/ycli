"""`tracker checklists` commands (checklist item lifecycle on an issue)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.tracker.checklists.models import (
    Checklist,
    ChecklistDeadlineInput,
    ChecklistItemCreate,
    ChecklistItemList,
    ChecklistItemUpdate,
)
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.typedefs import (
    KeyArg,
)

app = typer.Typer(name="checklists", help="Tracker issue checklists.", no_args_is_help=True)

ItemIdArg = Annotated[str, typer.Argument(metavar="ITEM_ID", help="Checklist item id.")]
TextOpt = Annotated[str, typer.Option(help="Item text.")]
CheckedOpt = Annotated[bool | None, typer.Option("--checked/--no-checked", help="Done flag.")]
AssigneeOpt = Annotated[str, typer.Option(help="Assignee login or id.")]
DeadlineOpt = Annotated[str, typer.Option(help="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")]


@app.command()
def get(key: KeyArg, *, tracker: TrackerClient) -> ChecklistItemList:
    """List the checklist items on issue KEY."""
    return tracker.checklists.get(key)


@app.command()
def add(
    key: KeyArg,
    text: TextOpt,
    checked: CheckedOpt = None,
    assignee: AssigneeOpt = "",
    deadline: DeadlineOpt = "",
    *,
    tracker: TrackerClient,
) -> Checklist:
    """Add a checklist item to issue KEY (creates the checklist if absent)."""
    body = ChecklistItemCreate(
        text=text,
        checked=checked,
        assignee=assignee or None,
        deadline=ChecklistDeadlineInput(date=deadline) if deadline else None,
    ).model_dump(by_alias=True, exclude_none=True)
    return tracker.checklists.create(key, body=body)


@app.command()
def edit(
    key: KeyArg,
    item_id: ItemIdArg,
    text: TextOpt = "",
    checked: CheckedOpt = None,
    assignee: AssigneeOpt = "",
    deadline: DeadlineOpt = "",
    *,
    tracker: TrackerClient,
) -> Checklist:
    """Edit checklist item ITEM_ID on issue KEY — only supplied fields are sent."""
    body = ChecklistItemUpdate(
        text=text or None,
        checked=checked,
        assignee=assignee or None,
        deadline=ChecklistDeadlineInput(date=deadline) if deadline else None,
    ).model_dump(by_alias=True, exclude_none=True)
    return tracker.checklists.edit(key, item_id, body=body)


@app.command()
def delete(key: KeyArg, item_id: ItemIdArg, *, tracker: TrackerClient) -> Checklist:
    """Delete checklist item ITEM_ID from issue KEY."""
    return tracker.checklists.delete(key, item_id)


@app.command()
def clear(key: KeyArg, *, tracker: TrackerClient) -> Checklist:
    """Delete the entire checklist from issue KEY."""
    return tracker.checklists.clear(key)

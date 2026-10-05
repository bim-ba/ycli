"""`tracker checklists` commands (checklist item lifecycle on an issue)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.checklists.models import (
    Checklist,
    ChecklistItem,
    ChecklistItemCreate,
    ChecklistItemUpdate,
)
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.models import DeadlineInput
from ycli.yandex.tracker.typedefs import (
    ItemIDArg,
    KeyArg,
)

app = typer.Typer(name="checklists", help="Tracker issue checklists.", no_args_is_help=True)

TextOpt = Annotated[str | None, typer.Option(help="Item text.")]
CheckedOpt = Annotated[bool | None, typer.Option("--checked/--no-checked", help="Done flag.")]
AssigneeOpt = Annotated[str | None, typer.Option(help="Assignee login or id.")]
DeadlineOpt = Annotated[
    str | None, typer.Option(help="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
]


@app.command("list")
def list_(key: KeyArg, *, tracker: TrackerClient) -> ItemList[ChecklistItem]:
    """List the checklist items on issue KEY."""
    return tracker.checklists.list(key)


@app.command()
def create(
    key: KeyArg,
    text: Annotated[str, typer.Option(help="Item text.")],
    checked: CheckedOpt = None,
    assignee: AssigneeOpt = None,
    deadline: DeadlineOpt = None,
    *,
    tracker: TrackerClient,
) -> Checklist:
    """Add a checklist item to issue KEY (creates the checklist if absent)."""
    body = ChecklistItemCreate(
        text=text,
        checked=checked,
        assignee=assignee,
        deadline=DeadlineInput(date=deadline) if deadline is not None else None,
    )
    return tracker.checklists.create(key, body=body)


@app.command()
def update(
    key: KeyArg,
    item_id: ItemIDArg,
    text: TextOpt = None,
    checked: CheckedOpt = None,
    assignee: AssigneeOpt = None,
    deadline: DeadlineOpt = None,
    *,
    tracker: TrackerClient,
) -> Checklist:
    """Edit checklist item ITEM_ID on issue KEY — only supplied fields are sent."""
    body = ChecklistItemUpdate(
        text=text,
        checked=checked,
        assignee=assignee,
        deadline=DeadlineInput(date=deadline) if deadline is not None else None,
    )
    return tracker.checklists.update(key, item_id, body=body)


@app.command()
def delete(key: KeyArg, item_id: ItemIDArg, *, tracker: TrackerClient) -> Checklist:
    """Delete checklist item ITEM_ID from issue KEY."""
    return tracker.checklists.delete(key, item_id)


@app.command()
def clear(key: KeyArg, *, tracker: TrackerClient) -> Checklist:
    """Delete the entire checklist from issue KEY."""
    return tracker.checklists.clear(key)

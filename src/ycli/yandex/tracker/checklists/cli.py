"""`tracker checklists` commands (checklist item lifecycle on an issue)."""

from typing import Annotated

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.checklists.models import (
    ChecklistItem,
    ChecklistItemCreate,
    ChecklistItemUpdate,
)
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.models import Issue
from ycli.yandex.tracker.typedefs import (
    DeadlineTypeOpt,
    IssueKeyArg,
    ItemIDArg,
    deadline_option,
)

app = typer.Typer(name="checklists", help="Tracker issue checklists.", no_args_is_help=True)

TextOpt = Annotated[str | None, typer.Option(help="Item text.")]
CheckedOpt = Annotated[bool | None, typer.Option("--checked/--no-checked", help="Done flag.")]
AssigneeOpt = Annotated[str | None, typer.Option(help="Assignee login or id.")]
DeadlineOpt = Annotated[
    str | None, typer.Option(help="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
]


@app.command("list")
def list_(issue_key: IssueKeyArg, *, tracker: TrackerClient) -> ItemList[ChecklistItem]:
    """List the checklist items on issue ISSUE_KEY."""
    return tracker.checklists.list(issue_key)


@app.command()
def create(
    issue_key: IssueKeyArg,
    text: Annotated[str, typer.Option(help="Item text.")],
    checked: CheckedOpt = None,
    assignee: AssigneeOpt = None,
    deadline: DeadlineOpt = None,
    deadline_type: DeadlineTypeOpt = None,
    *,
    tracker: TrackerClient,
) -> Issue:
    """Add a checklist item to issue ISSUE_KEY (creates the checklist if absent)."""
    body = ChecklistItemCreate(
        text=text,
        checked=checked,
        assignee=assignee,
        deadline=deadline_option(deadline, deadline_type),
    )
    return tracker.checklists.create(issue_key, body=body)


@app.command()
def update(
    issue_key: IssueKeyArg,
    item_id: ItemIDArg,
    text: TextOpt = None,
    checked: CheckedOpt = None,
    assignee: AssigneeOpt = None,
    deadline: DeadlineOpt = None,
    deadline_type: DeadlineTypeOpt = None,
    *,
    tracker: TrackerClient,
) -> Issue:
    """Edit checklist item ITEM_ID on issue ISSUE_KEY — only supplied fields are sent."""
    body = ChecklistItemUpdate(
        text=text,
        checked=checked,
        assignee=assignee,
        deadline=deadline_option(deadline, deadline_type),
    )
    return tracker.checklists.update(issue_key, item_id, body=body)


@app.command()
def delete(issue_key: IssueKeyArg, item_id: ItemIDArg, *, tracker: TrackerClient) -> Issue:
    """Delete checklist item ITEM_ID from issue ISSUE_KEY."""
    return tracker.checklists.delete(issue_key, item_id)


@app.command()
def clear(issue_key: IssueKeyArg, *, tracker: TrackerClient) -> Issue:
    """Delete the entire checklist from issue ISSUE_KEY."""
    return tracker.checklists.clear(issue_key)

"""`tracker workflows` commands.

Nested objects (steps, actions, resolutions) come in as JSON in the shape of the API docs, e.g.
``--step '{"status": "open", "actions": [...]}'``; the typed request models validate them.
"""

from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.workflows.models import (
    QueueWorkflows,
    Workflow,
    WorkflowActionUpdate,
    WorkflowCreate,
    WorkflowUpdate,
)

app = typer.Typer(name="workflows", help="Tracker workflows.", no_args_is_help=True)

WorkflowIdArg = Annotated[
    str, typer.Argument(metavar="WORKFLOW_ID", help="Workflow id, e.g. quickStartV2PresetWorkflow.")
]
VersionOpt = Annotated[
    int,
    typer.Option(help="Current version of the workflow (optimistic lock); see `workflows get`."),
]
InitialActionOpt = Annotated[
    str, typer.Option("--initial-action", help="Initial action as a JSON object.")
]
StepOpt = Annotated[
    list[str] | None,
    typer.Option("--step", help="Step as a JSON object: status plus actions (repeatable)."),
]
ResolutionOpt = Annotated[
    list[str] | None,
    typer.Option(
        "--issue-type-resolution",
        help='Resolutions of an issue type, e.g. \'{"issueType":"task","resolutions":["fixed"]}\' '
        "(repeatable).",
    ),
]


def _json(raw: str, option: str) -> Any:
    """Parse a JSON option; a malformed value is a usage error, not a traceback."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"{option} must be valid JSON: {exc}") from exc


def _json_list(raw: list[str] | None, option: str) -> list[Any] | None:
    return [_json(item, option) for item in raw] if raw else None


@app.command("list")
def list_(*, tracker: TrackerClient) -> ItemList[Workflow]:
    """List the organization's workflows (deleted ones excluded)."""
    return tracker.workflows.list()


@app.command()
def get(workflow_id: WorkflowIdArg, *, tracker: TrackerClient) -> Workflow:
    """Print workflow WORKFLOW_ID with its steps and actions."""
    return tracker.workflows.get(workflow_id)


@app.command("for-queue")
def for_queue(
    queue_id: Annotated[
        str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
    ],
    *,
    tracker: TrackerClient,
) -> QueueWorkflows:
    """Show which workflow each issue type of QUEUE_ID uses."""
    return tracker.workflows.for_queue(queue_id)


@app.command()
def create(
    name: Annotated[str, typer.Option(help="Name of the workflow.")],
    initial_action: InitialActionOpt,
    step: StepOpt = None,
    workflow_id: Annotated[
        str, typer.Option("--id", help="Identifier of the workflow (generated if omitted).")
    ] = "",
    queue: Annotated[str, typer.Option(help="Queue key to bind to (shared if omitted).")] = "",
    visual: Annotated[
        bool, typer.Option("--visual", help="Send type VISUAL (the only type today).")
    ] = False,
    issue_type_resolution: ResolutionOpt = None,
    *,
    tracker: TrackerClient,
) -> Workflow:
    """Create a workflow (POST /workflows).

    --initial-action and each --step are JSON objects as in the API docs, e.g.
    --initial-action '{"id":"open","name":{"ru":"Открыть","en":"Open"},"target":"open"}'
    --step '{"status":"open","actions":[{"id":"close","name":{"ru":"Закрыть"},"target":"closed"}]}'.
    Every action name needs its Russian text: Tracker refuses one without it.
    """
    body = WorkflowCreate.model_validate(
        {
            "id": workflow_id or None,
            "name": name,
            "queue": queue or None,
            "type": "VISUAL" if visual else None,
            "initialAction": _json(initial_action, "--initial-action"),
            "steps": _json_list(step, "--step") or [],
            "issueTypeResolutions": _json_list(issue_type_resolution, "--issue-type-resolution"),
        }
    )
    return tracker.workflows.create(body)


@app.command()
def update(
    workflow_id: WorkflowIdArg,
    version: VersionOpt,
    name: Annotated[str, typer.Option(help="New name of the workflow.")] = "",
    initial_action: Annotated[
        str, typer.Option("--initial-action", help="New initial action as a JSON object.")
    ] = "",
    step: StepOpt = None,
    visual: Annotated[
        bool, typer.Option("--visual", help="Send type VISUAL (the only type today).")
    ] = False,
    issue_type_resolution: ResolutionOpt = None,
    *,
    tracker: TrackerClient,
) -> Workflow:
    """Edit workflow WORKFLOW_ID (PATCH /workflows/{id}?version=); only given options change.

    Giving any --step replaces the whole step list.
    """
    body = WorkflowUpdate.model_validate(
        {
            "name": name or None,
            "type": "VISUAL" if visual else None,
            "initialAction": _json(initial_action, "--initial-action") if initial_action else None,
            "steps": _json_list(step, "--step"),
            "issueTypeResolutions": _json_list(issue_type_resolution, "--issue-type-resolution"),
        }
    )
    return tracker.workflows.edit(workflow_id, body, version=version)


@app.command("update-action")
def update_action(
    workflow_id: WorkflowIdArg,
    status: Annotated[
        str, typer.Argument(metavar="STATUS", help="Key of the step the action leaves.")
    ],
    action_id: Annotated[str, typer.Argument(metavar="ACTION_ID", help="Id of the action.")],
    version: VersionOpt,
    action: Annotated[
        str,
        typer.Option(
            "--action",
            help="Action fields as a JSON object; Tracker requires name and target, e.g. "
            '\'{"name":{"ru":"Закрыть"},"target":"closed"}\'.',
        ),
    ],
    *,
    tracker: TrackerClient,
) -> Workflow:
    """Edit one action of a workflow step (PATCH …/steps/{status}/actions/{action})."""
    body = WorkflowActionUpdate.model_validate(_json(action, "--action"))
    return tracker.workflows.edit_action(workflow_id, status, action_id, body, version=version)


@app.command()
def delete(workflow_id: WorkflowIdArg, *, tracker: TrackerClient) -> Ack:
    """Delete workflow WORKFLOW_ID (DELETE /workflows/{id})."""
    tracker.workflows.delete(workflow_id)
    return Ack.deleted("workflow", workflow_id)

"""Tracker ``/workflows`` FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    tracker_client,
)
from ycli.yandex.tracker.workflows.models import (
    QueueWorkflows,
    Workflow,
    WorkflowActionUpdate,
    WorkflowCreate,
    WorkflowUpdate,
)

mcp = FastMCP("tracker-workflows")

WorkflowId = Annotated[str, Field(description="Workflow id, from ``workflows_list``.")]
Version = Annotated[
    int,
    Field(description="Current version of the workflow (optimistic lock), from ``workflows_get``."),
]


@mcp.tool(name="workflows_list", annotations={**RO, "title": "List Tracker workflows"})
def list_(client: TrackerClient = Depends(tracker_client)) -> ItemList[Workflow]:
    """Every workflow of the organization (deleted ones excluded) with its steps and actions.

    A workflow is the status graph an issue type follows. Use ``workflows_get`` for one by id
    and ``workflows_for_queue`` to see which workflow each issue type of a queue uses.
    """
    return client.workflows.list()


@mcp.tool(name="workflows_get", annotations={**RO, "title": "Get Tracker workflow"})
def get(workflow_id: WorkflowId, client: TrackerClient = Depends(tracker_client)) -> Workflow:
    """One workflow with its steps, initial action, queue binding and ``version``.

    A step is a status with the transitions leaving it; ``version`` is needed to edit the workflow.
    """
    return client.workflows.get(workflow_id)


@mcp.tool(
    name="workflows_for_queue",
    annotations={**RO, "title": "List workflows of a Tracker queue"},
)
def for_queue(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> QueueWorkflows:
    """The workflows a queue uses: a map from workflow id to the issue types that follow it."""
    return client.workflows.for_queue(queue_id)


@mcp.tool(
    name="workflows_create",
    annotations={**WRITE, "title": "Create Tracker workflow"},
)
def create(body: WorkflowCreate, client: TrackerClient = Depends(tracker_client)) -> Workflow:
    """Create a workflow; returns it with its generated id and version.

    Required: ``name``, ``initialAction`` (name and target status) and ``steps`` (each a status
    with its ``actions``). Statuses are given as keys such as ``open`` and must exist; names are
    ``{"ru": …, "en": …}`` objects.
    """
    return client.workflows.create(body)


@mcp.tool(
    name="workflows_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker workflow"},
)
def update(
    workflow_id: WorkflowId,
    body: WorkflowUpdate,
    version: Version,
    client: TrackerClient = Depends(tracker_client),
) -> Workflow:
    """Edit a workflow.

    Only the fields set in ``body`` change, and a given ``steps`` list replaces the whole step
    list. Returns the workflow with its incremented version.
    """
    return client.workflows.update(workflow_id, body, version=version)


@mcp.tool(
    name="workflows_update_action",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker workflow action"},
)
def update_action(
    workflow_id: WorkflowId,
    status: Annotated[str, Field(description="Key of the step (status) the action leaves.")],
    action_id: Annotated[str, Field(description="Id of the action within that step.")],
    body: WorkflowActionUpdate,
    version: Version,
    client: TrackerClient = Depends(tracker_client),
) -> Workflow:
    """Edit one action (transition) of a workflow step; only the fields set in ``body`` change.

    Returns the whole workflow with its incremented version.
    """
    return client.workflows.update_action(workflow_id, status, action_id, body, version=version)


@mcp.tool(
    name="workflows_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker workflow"},
)
def delete(workflow_id: WorkflowId, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Delete a workflow (irreversible). Returns an acknowledgement."""
    client.workflows.delete(workflow_id)
    return Ack.deleted("workflow", workflow_id)

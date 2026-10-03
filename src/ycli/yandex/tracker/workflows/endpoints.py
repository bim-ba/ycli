"""Tracker ``/workflows`` operations, each declared once (sans-IO).

Examples:
    >>> edit_action("W21", "inProgress", "close", {"target": "closed"}, version=2).path
    'workflows/W21/steps/inProgress/actions/close'
    >>> delete_workflow("W21").effect
    'destructive'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.workflows.models import (
    QueueWorkflows,
    Workflow,
    WorkflowActionUpdate,
    WorkflowCreate,
    WorkflowUpdate,
)


def list_workflows() -> Endpoint[ItemList[Workflow]]:
    return Endpoint("GET", "workflows", ItemList[Workflow])


def get_workflow(workflow_id: str) -> Endpoint[Workflow]:
    return Endpoint("GET", f"workflows/{segment(workflow_id)}", Workflow)


def list_queue_workflows(queue_id: str) -> Endpoint[QueueWorkflows]:
    return Endpoint("GET", f"queues/{segment(queue_id)}/workflows", QueueWorkflows)


def create_workflow(body: WorkflowCreate) -> Endpoint[Workflow]:
    return Endpoint("POST", "workflows", Workflow, json=body)


def edit_workflow(workflow_id: str, body: WorkflowUpdate, *, version: int) -> Endpoint[Workflow]:
    """``PATCH /workflows/{id}?version=`` — the optimistic lock is required by the API."""
    return Endpoint(
        "PATCH",
        f"workflows/{segment(workflow_id)}",
        Workflow,
        json=body,
        params={"version": version},
    )


def edit_action(
    workflow_id: str, status: str, action_id: str, body: WorkflowActionUpdate, *, version: int
) -> Endpoint[Workflow]:
    """``PATCH /workflows/{id}/steps/{status}/actions/{action}?version=`` — one action only."""
    path = f"workflows/{segment(workflow_id)}/steps/{segment(status)}/actions/{segment(action_id)}"
    return Endpoint("PATCH", path, Workflow, json=body, params={"version": version})


def delete_workflow(workflow_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", f"workflows/{segment(workflow_id)}")

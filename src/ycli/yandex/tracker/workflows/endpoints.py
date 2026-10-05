"""Tracker ``/workflows`` operations, each declared once (sans-IO).

Examples:
    >>> actions_update("W21", "inProgress", "close", {"target": "closed"}, version=2).path
    'workflows/W21/steps/inProgress/actions/close'
    >>> delete("W21").effect
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


def list_() -> Endpoint[ItemList[Workflow]]:
    return Endpoint("GET", "workflows", ItemList[Workflow])


def get(workflow_id: str) -> Endpoint[Workflow]:
    return Endpoint("GET", f"workflows/{segment(workflow_id)}", Workflow)


def list_for_queue(queue_id: str) -> Endpoint[QueueWorkflows]:
    return Endpoint("GET", f"queues/{segment(queue_id)}/workflows", QueueWorkflows)


def create(body: WorkflowCreate) -> Endpoint[Workflow]:
    return Endpoint("POST", "workflows", Workflow, json=body)


def update(workflow_id: str, body: WorkflowUpdate, *, version: int) -> Endpoint[Workflow]:
    """``PATCH /workflows/{id}?version=`` — the optimistic lock is required by the API."""
    return Endpoint(
        "PATCH",
        f"workflows/{segment(workflow_id)}",
        Workflow,
        json=body,
        params={"version": version},
    )


def actions_update(
    workflow_id: str, status: str, action_id: str, body: WorkflowActionUpdate, *, version: int
) -> Endpoint[Workflow]:
    """``PATCH /workflows/{id}/steps/{status}/actions/{action}?version=`` — one action only."""
    path = f"workflows/{segment(workflow_id)}/steps/{segment(status)}/actions/{segment(action_id)}"
    return Endpoint("PATCH", path, Workflow, json=body, params={"version": version})


def delete(workflow_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", f"workflows/{segment(workflow_id)}")

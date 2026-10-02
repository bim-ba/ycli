"""Tracker ``/workflows`` client on the httpx2 core — sends :mod:`.endpoints`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.workflows import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.workflows.models import (
        QueueWorkflows,
        Workflow,
        WorkflowActionUpdate,
        WorkflowCreate,
        WorkflowList,
        WorkflowUpdate,
    )


class WorkflowsClient(Resource):
    """List, get, create, edit and delete workflows; read the workflows of a queue."""

    def list(self) -> WorkflowList:
        """``GET /workflows`` → every workflow of the organization except deleted ones.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.workflows.list().root[0].name  # doctest: +SKIP
            'Design'
        """
        return self._session.send(endpoints.list_workflows())

    def get(self, workflow_id: str) -> Workflow:
        """``GET /workflows/{workflow_id}`` → one workflow with its steps and actions.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.workflows.get("W21").version  # doctest: +SKIP
            1
        """
        return self._session.send(endpoints.get_workflow(workflow_id))

    def for_queue(self, queue_id: str) -> QueueWorkflows:
        """``GET /queues/{queue_id}/workflows`` → workflow id → the issue types that use it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.workflows.for_queue("TEST").root["dev"][0].key  # doctest: +SKIP
            'task'
        """
        return self._session.send(endpoints.list_queue_workflows(queue_id))

    def create(self, body: WorkflowCreate) -> Workflow:
        """``POST /workflows`` → create a workflow from a typed ``WorkflowCreate`` body.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.workflows.create(
            ...     WorkflowCreate(
            ...         name="Design",
            ...         initial_action=WorkflowActionInput(
            ...             name=LocalizedText(en="Open"), target="open"
            ...         ),
            ...         steps=[WorkflowStepInput(status="open")],
            ...     )
            ... ).id  # doctest: +SKIP
            'W21'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_workflow(dumped))

    def edit(self, workflow_id: str, body: WorkflowUpdate, *, version: int) -> Workflow:
        """``PATCH /workflows/{workflow_id}?version=`` → change the set fields of a workflow.

        ``version`` is the workflow's current version (the API answers 412/428 without a
        matching one); the reply carries the incremented version.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.workflows.edit(
            ...     "W21", WorkflowUpdate(name="QA"), version=3
            ... ).version  # doctest: +SKIP
            4
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_workflow(workflow_id, dumped, version=version))

    def edit_action(
        self,
        workflow_id: str,
        status: str,
        action_id: str,
        body: WorkflowActionUpdate,
        *,
        version: int,
    ) -> Workflow:
        """``PATCH /workflows/{id}/steps/{status}/actions/{action_id}?version=`` → edit one action.

        ``status`` is the key of the step the action leaves. Returns the whole workflow.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.workflows.edit_action(
            ...     "W21", "inProgress", "close", WorkflowActionUpdate(target="closed"), version=2
            ... ).version  # doctest: +SKIP
            3
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        endpoint = endpoints.edit_action(workflow_id, status, action_id, dumped, version=version)
        return self._session.send(endpoint)

    def delete(self, workflow_id: str) -> None:
        """``DELETE /workflows/{workflow_id}`` → 204; raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.workflows.delete("W21")  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_workflow(workflow_id))

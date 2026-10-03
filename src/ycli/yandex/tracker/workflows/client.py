"""Tracker ``/workflows`` client on the httpx2 core — sends :mod:`.endpoints`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.workflows import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.workflows.models import (
        QueueWorkflows,
        Workflow,
        WorkflowActionUpdate,
        WorkflowCreate,
        WorkflowUpdate,
    )


class WorkflowsClient(Resource):
    """List, get, create, update and delete workflows; read the workflows of a queue."""

    def list(self) -> ItemList[Workflow]:
        """``GET /workflows`` → every workflow of the organization except deleted ones.

        Returns:
            The workflows.

        Examples:
            >>> tracker.workflows.list().root[0].name
            'Design'
        """
        return self._session.send(endpoints.list_workflows())

    def get(self, workflow_id: str) -> Workflow:
        """``GET /workflows/{workflow_id}`` → one workflow with its steps and actions.

        Args:
            workflow_id: The workflow's id.

        Returns:
            The workflow.

        Examples:
            >>> tracker.workflows.get("W21").version
            1
        """
        return self._session.send(endpoints.get_workflow(workflow_id))

    def for_queue(self, queue_id: str) -> QueueWorkflows:
        """``GET /queues/{queue_id}/workflows`` → workflow id → the issue types that use it.

        Args:
            queue_id: The queue's key or numeric id.

        Returns:
            The queue's workflows, each with the issue types that use it.

        Examples:
            >>> tracker.workflows.for_queue("WFQ").root["dev"][0].key
            'task'
        """
        return self._session.send(endpoints.list_queue_workflows(queue_id))

    def create(self, body: WorkflowCreate) -> Workflow:
        """``POST /workflows`` → create a workflow from a typed ``WorkflowCreate`` body.

        Args:
            body: The new workflow's name, initial action and steps.

        Returns:
            The created workflow.

        Examples:
            >>> from ycli.yandex.tracker.models import LocalizedName
            >>> from ycli.yandex.tracker.workflows.models import (
            ...     WorkflowActionInput,
            ...     WorkflowCreate,
            ...     WorkflowStepInput,
            ... )
            >>> new_workflow = WorkflowCreate(
            ...     id="design-flow",
            ...     name="Design",
            ...     initial_action=WorkflowActionInput(
            ...         name=LocalizedName(ru="Открыть", en="Open"), target="open"
            ...     ),
            ...     steps=[WorkflowStepInput(status="open")],
            ... )
            >>> tracker.workflows.create(new_workflow).id
            'design-flow'
        """
        return self._session.send(endpoints.create_workflow(body))

    def update(self, workflow_id: str, body: WorkflowUpdate, *, version: int) -> Workflow:
        """``PATCH /workflows/{workflow_id}?version=`` → change the set fields of a workflow.

        ``version`` is the workflow's current version (the API answers 412/428 without a
        matching one); the reply carries the incremented version.

        Args:
            workflow_id: The workflow's id.
            body: The fields to change.
            version: The workflow's current version, sent as ``?version=``.

        Returns:
            The updated workflow.

        Examples:
            >>> from ycli.yandex.tracker.workflows.models import WorkflowUpdate
            >>> tracker.workflows.update(
            ...     "W21", WorkflowUpdate(name="QA process"), version=3
            ... ).version
            4
        """
        return self._session.send(endpoints.update_workflow(workflow_id, body, version=version))

    def update_action(
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

        Args:
            workflow_id: The workflow's id.
            status: The key of the step the action leaves.
            action_id: The action's id.
            body: The fields to change.
            version: The workflow's current version, sent as ``?version=``.

        Returns:
            The whole updated workflow.

        Examples:
            >>> from ycli.yandex.tracker.models import LocalizedName
            >>> from ycli.yandex.tracker.workflows.models import WorkflowActionUpdate
            >>> action = WorkflowActionUpdate(
            ...     name=LocalizedName(ru="Завершить", en="Complete"), target="closed"
            ... )
            >>> tracker.workflows.update_action(
            ...     "W23", "inProgress", "close", action, version=2
            ... ).version
            3
        """
        endpoint = endpoints.update_action(workflow_id, status, action_id, body, version=version)
        return self._session.send(endpoint)

    def delete(self, workflow_id: str) -> None:
        """``DELETE /workflows/{workflow_id}`` → 204; raises on non-2xx.

        Args:
            workflow_id: The workflow's id.

        Examples:
            >>> tracker.workflows.delete("W24")
        """
        self._session.send(endpoints.delete_workflow(workflow_id))

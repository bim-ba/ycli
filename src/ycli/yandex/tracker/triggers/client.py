"""Tracker queue ``/triggers`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.triggers import endpoints

if TYPE_CHECKING:
    from ycli.yandex.core.listing import Listing
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.triggers.models import (
        Trigger,
        TriggerCreate,
        TriggerUpdate,
        WebhookLogEntry,
    )


class TriggersClient(Resource):
    """List, get, create and update a queue's triggers; read a trigger's webhook log."""

    def list(
        self, queue_id: str, *, limit: int | None = None, next: str | None = None
    ) -> Listing[Trigger]:
        """``GET /queues/{queue_id}/triggers`` → every trigger of the queue, ascending by id.

        Drains the relative cursor (``id=<last trigger id>``). Capped at ``limit`` (``None`` =
        every trigger); a small cap narrows the page to ``limit`` rows.

        Args:
            queue_id: The queue's key or numeric id.
            limit: The most triggers to return; ``None`` returns every trigger.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.

        Returns:
            The queue's triggers, ascending by id.

        Examples:
            >>> [trigger.name for trigger in tracker.triggers.list("LISTQ", limit=500)]
            ['First', 'Second']
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_(queue_id, page_size=page_size)
        return self._session.iterate(paged, limit=limit, next=next)

    def get(self, queue_id: str, trigger_id: int) -> Trigger:
        """``GET /queues/{queue_id}/triggers/{trigger_id}`` → a single trigger.

        Args:
            queue_id: The queue's key or numeric id.
            trigger_id: The trigger's id.

        Returns:
            The trigger.

        Examples:
            >>> tracker.triggers.get("DESIGN", 16).name
            'On comment'
        """
        return self._session.send(endpoints.get(queue_id, trigger_id))

    def create(self, queue_id: str, body: TriggerCreate) -> Trigger:
        """Create a trigger from a typed ``TriggerCreate`` body. Returns the created ``Trigger``.

        Args:
            queue_id: The queue's key or numeric id.
            body: The new trigger's name, actions and conditions.

        Returns:
            The created trigger.

        Examples:
            >>> from ycli.yandex.tracker.models import AutomationAction
            >>> from ycli.yandex.tracker.triggers.models import TriggerCreate
            >>> new_trigger = TriggerCreate(
            ...     name="Reopen on comment",
            ...     actions=[AutomationAction(type="Transition", status={"key": "open"})],
            ... )
            >>> tracker.triggers.create("ART", new_trigger).id
            17
        """
        return self._session.send(endpoints.create(queue_id, body))

    def update(
        self, queue_id: str, trigger_id: int, body: TriggerUpdate, *, version: int | None = None
    ) -> Trigger:
        """Edit a trigger from a typed ``TriggerUpdate`` body. Returns the updated ``Trigger``.

        Pass ``version`` (the trigger's current version) to guard against a concurrent edit;
        only the fields set on ``body`` are sent.

        Args:
            queue_id: The queue's key or numeric id.
            trigger_id: The trigger's id.
            body: The fields to change.
            version: The trigger's current version, sent as ``?version=``; ``None`` sends none.

        Returns:
            The updated trigger.

        Examples:
            >>> from ycli.yandex.tracker.triggers.models import TriggerUpdate
            >>> tracker.triggers.update(
            ...     "BIZ", 18, TriggerUpdate(name="Renamed trigger"), version=3
            ... ).name
            'Renamed trigger'
        """
        return self._session.send(endpoints.update(queue_id, trigger_id, body, version=version))

    def webhook_log_list(
        self,
        queue_id: str,
        trigger_id: int,
        issue_id: str | None = None,
        limit: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> ItemList[WebhookLogEntry]:
        """``GET /queues/{queue_id}/triggers/{trigger_id}/webhooks/log`` → HTTP-action run logs.

        Returns the trigger's Webhook-action execution records (default 10, ``limit`` up to 100).
        Optionally scope to one ``issue_id`` or a ``date_from``/``date_to`` window.

        Args:
            queue_id: The queue's key or numeric id.
            trigger_id: The trigger's id.
            issue_id: Only the runs for this issue.
            limit: The most records to return (default 10, up to 100).
            date_from: Only runs from this time on (ISO 8601).
            date_to: Only runs up to this time (ISO 8601).

        Returns:
            The trigger's Webhook-action execution records.

        Examples:
            >>> tracker.triggers.webhook_log_list(
            ...     "DEV",
            ...     6,
            ...     issue_id="DEV-5",
            ...     limit=100,
            ...     date_from="2026-01-01T00:00:00.000+0300",
            ...     date_to="2026-02-01T00:00:00.000+0300",
            ... ).root[0].duration
            235
        """
        return self._session.send(
            endpoints.webhook_log_list(
                queue_id,
                trigger_id,
                issue_id=issue_id,
                limit=limit,
                date_from=date_from,
                date_to=date_to,
            )
        )

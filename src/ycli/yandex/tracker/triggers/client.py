"""Tracker queue ``/triggers`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.triggers import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.triggers.models import (
        Trigger,
        TriggerCreate,
        TriggerUpdate,
        WebhookLogList,
    )


class TriggersClient(Resource):
    """Get, create and edit a queue's triggers; read a trigger's webhook log."""

    def get(self, queue_id: str, trigger_id: int) -> Trigger:
        """``GET /queues/{queue_id}/triggers/{trigger_id}`` → a single trigger.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.triggers.get(queue_id="DESIGN", trigger_id=16).name  # doctest: +SKIP
            'trigger_name'
        """
        return self._session.send(endpoints.get_trigger(queue_id, trigger_id))

    def create(self, queue_id: str, body: TriggerCreate) -> Trigger:
        """Create a trigger from a typed ``TriggerCreate`` body. Returns the created ``Trigger``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.triggers.create(
            ...     "DESIGN", TriggerCreate(name="T", actions=[TriggerAction(type="Transition")])
            ... ).id  # doctest: +SKIP
            16
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_trigger(queue_id, dumped))

    def edit(
        self, queue_id: str, trigger_id: int, body: TriggerUpdate, *, version: int | None = None
    ) -> Trigger:
        """Edit a trigger from a typed ``TriggerUpdate`` body. Returns the updated ``Trigger``.

        Pass ``version`` (the trigger's current version) to guard against a concurrent edit;
        only the fields set on ``body`` are sent.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.triggers.edit(
            ...     "DESIGN", 16, TriggerUpdate(active=False), version=1
            ... ).active  # doctest: +SKIP
            False
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(
            endpoints.edit_trigger(queue_id, trigger_id, dumped, version=version)
        )

    def webhook_log(
        self,
        queue_id: str,
        trigger_id: int,
        issue_id: str | None = None,
        limit: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> WebhookLogList:
        """``GET /queues/{queue_id}/triggers/{trigger_id}/webhooks/log`` → HTTP-action run logs.

        Returns the trigger's Webhook-action execution records (default 10, ``limit`` up to 100).
        Optionally scope to one ``issue_id`` or a ``date_from``/``date_to`` window.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.triggers.webhook_log("DEV", 6, limit=100).root[0].duration  # doctest: +SKIP
            235
        """
        return self._session.send(
            endpoints.list_webhook_log(
                queue_id,
                trigger_id,
                issue_id=issue_id,
                limit=limit,
                date_from=date_from,
                date_to=date_to,
            )
        )

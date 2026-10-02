"""Tracker queue ``/triggers`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.triggers import endpoints
from ycli.yandex.tracker.triggers.models import TriggerList

if TYPE_CHECKING:
    from ycli.yandex.tracker.triggers.models import (
        Trigger,
        TriggerCreate,
        TriggerUpdate,
        WebhookLogList,
    )


class TriggersClient(Resource):
    """List, get, create and edit a queue's triggers; read a trigger's webhook log."""

    def list(self, queue_id: str, *, limit: int | None = None) -> TriggerList:
        """``GET /queues/{queue_id}/triggers`` → every trigger of the queue, ascending by id.

        Drains the relative cursor (``id=<last trigger id>``). Capped at ``limit`` (``None`` =
        every trigger); a small cap narrows the page to ``limit`` rows.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.triggers.list("DESIGN").root[0].name  # doctest: +SKIP
            'trigger_name'
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_triggers(queue_id, page_size=page_size)
        return TriggerList(list(self._session.iterate(paged, limit=limit)))

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

"""Declarative Tracker queue triggers client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.triggers.models import (
    Trigger,
    TriggerCreate,
    TriggerUpdate,
    WebhookLogList,
)


class TriggersClient(TrackerResource):
    """Declarative HTTP for a queue's ``/triggers`` (get, create, edit, webhook log)."""

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/triggers/{trigger_id}")
    def get(self, queue_id: uplink.Path, trigger_id: uplink.Path) -> Trigger:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/triggers/{trigger_id}`` → a single trigger.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.triggers.get(queue_id="DESIGN", trigger_id=16).name  # doctest: +SKIP
            'trigger_name'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("queues/{queue_id}/triggers")
    def _create(self, queue_id: uplink.Path, body: uplink.Body) -> Trigger:  # ty: ignore[empty-body]
        """``POST /queues/{queue_id}/triggers`` from a ready JSON body (see ``create``)."""

    def create(self, queue_id: str, body: TriggerCreate) -> Trigger:
        """Create a trigger from a typed ``TriggerCreate`` body. Returns the created ``Trigger``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.triggers.create(
            ...     "DESIGN", TriggerCreate(name="T", actions=[TriggerAction(type="Transition")])
            ... ).id  # doctest: +SKIP
            16
        """
        return self._create(
            queue_id=queue_id, body=body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("queues/{queue_id}/triggers/{trigger_id}")
    def _edit(
        self,
        queue_id: uplink.Path,
        trigger_id: uplink.Path,
        body: uplink.Body,
        version: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> Trigger:  # ty: ignore[empty-body]
        """``PATCH /queues/{queue_id}/triggers/{trigger_id}?version=`` (see ``edit``)."""

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
        return self._edit(
            queue_id=queue_id,
            trigger_id=trigger_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
            version=version,
        )

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/triggers/{trigger_id}/webhooks/log")
    def webhook_log(
        self,
        queue_id: uplink.Path,
        trigger_id: uplink.Path,
        issue_id: uplink.Query("issueId") = None,  # ty: ignore[invalid-type-form]
        limit: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        date_from: uplink.Query("from") = None,  # ty: ignore[invalid-type-form]
        date_to: uplink.Query("to") = None,  # ty: ignore[invalid-type-form]
    ) -> WebhookLogList:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/triggers/{trigger_id}/webhooks/log`` → HTTP-action run logs.

        Returns the trigger's Webhook-action execution records (default 10, ``limit`` up to 100).
        Optionally scope to one ``issue_id`` or a ``date_from``/``date_to`` window.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.triggers.webhook_log("DEV", 6, limit=100).root[0].duration  # doctest: +SKIP
            235
        """

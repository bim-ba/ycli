"""Forms ``/notifications`` client on the httpx2 core (the runs of a form's integrations)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.notifications import endpoints
from ycli.yandex.forms.notifications.models import Notification, NotificationFilter
from ycli.yandex.models import ItemList, SortDirection

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.forms.models import IntegrationType, RunStatus
    from ycli.yandex.forms.notifications.models import (
        NotificationAction,
        NotificationDetails,
        NotificationStatus,
    )


class NotificationsClient(Resource):
    """List, inspect, restart and cancel the runs of a form's integrations."""

    def list(
        self,
        *,
        survey_id: str | None = None,
        hook_id: int | None = None,
        subscription_id: int | None = None,
        answer_id: int | None = None,
        status: Sequence[RunStatus] | None = None,
        created_since: str | None = None,
        created_until: str | None = None,
        finished_since: str | None = None,
        finished_until: str | None = None,
        visible: bool | None = None,
        integration_type: IntegrationType | None = None,
        ordering: SortDirection | None = None,
        limit: int | None = None,
    ) -> ItemList[Notification]:
        """``GET /notifications`` → runs matching every filter given, at most ``limit``.

        The API answers 404 Not Found to a listing without ``survey_id``, whatever else is given,
        though its reference marks no filter as required (seen on 2026-10-06): the other
        filters narrow the runs of that form.

        Args:
            survey_id: The form whose runs to list; without it the API answers 404.
            hook_id: Only runs of this integration group.
            subscription_id: Only runs of this integration.
            answer_id: Only runs triggered by this answer.
            status: Only runs in any of these states.
            created_since: ISO-8601 time: created at or after.
            created_until: ISO-8601 time: created at or before.
            finished_since: ISO-8601 time: finished at or after.
            finished_until: ISO-8601 time: finished at or before.
            visible: Only visible (``True``) or only hidden (``False``) runs.
            integration_type: Only runs of this integration type.
            ordering: ``asc`` (oldest first, the API's default) or ``desc``.
            limit: The most runs to return; ``None`` returns every run.

        Returns:
            The matching runs.

        Examples:
            >>> runs = forms.notifications.list(
            ...     survey_id="686d0a1b2c3d4e5f000000f0", status=["error", "pending"], limit=500
            ... )
            >>> [run.id for run in runs.root]
            [9001, 9002, 9003]
        """
        filters = NotificationFilter(
            survey_id=survey_id,
            hook_id=hook_id,
            subscription_id=subscription_id,
            answer_id=answer_id,
            status=None if status is None else list(status),
            created_since=created_since,
            created_until=created_until,
            finished_since=finished_since,
            finished_until=finished_until,
            visible=visible,
            integration_type=integration_type,
            ordering=ordering,
        )
        paged = endpoints.list_(filters)
        return ItemList[Notification](list(self._session.iterate(paged, limit=limit)))

    def get(self, notification_id: int) -> NotificationDetails:
        """``GET /notifications/{id}`` → the run with its context, response and error.

        Args:
            notification_id: The run's id.

        Returns:
            The run, with what the integration was given, answered and failed with.

        Examples:
            >>> forms.notifications.get(9100).error[0].name
            'detail'
        """
        return self._session.send(endpoints.get(notification_id))

    def status_get(self, notification_id: int) -> NotificationStatus:
        """``GET /notifications/{id}/status`` → just the run's state.

        Args:
            notification_id: The run's id.

        Returns:
            The run's state.

        Examples:
            >>> forms.notifications.status_get(9101).status
            'success'
        """
        return self._session.send(endpoints.status_get(notification_id))

    def restart(self, notification_id: int) -> NotificationAction:
        """``POST /notifications/{id}/restart`` — run the integration again for that answer.

        ``result.status`` is ``ok``, ``skip`` (a run that is still pending is left alone),
        ``fail`` (see ``detail``) or ``operation``: the run was queued again. A canceled run
        answered ``operation`` with the ``operation_id`` ``not-supported`` on the test
        organization, so there is nothing to poll: read the run's state with :meth:`status_get`.

        Args:
            notification_id: The run's id.

        Returns:
            How the restart went.

        Examples:
            >>> forms.notifications.restart(9102).result.status
            'operation'
        """
        return self._session.send(endpoints.restart(notification_id))

    def cancel(self, notification_id: int) -> NotificationAction:
        """``POST /notifications/{id}/cancel`` — stop a run that has not finished.

        A run that is already canceled or finished answers ``result.status`` ``skip``.

        Args:
            notification_id: The run's id.

        Returns:
            How the cancel went.

        Examples:
            >>> forms.notifications.cancel(9103).result.status
            'fail'
        """
        return self._session.send(endpoints.cancel(notification_id))

    def errors_list(self, survey_id: str) -> ItemList[int]:
        """``GET /surveys/{id}/show-errors`` → ids of the form's failed runs still shown.

        Read each with :meth:`get`.

        Args:
            survey_id: The form's id.

        Returns:
            The ids of the form's failed runs.

        Examples:
            >>> forms.notifications.errors_list("686d0a1b2c3d4e5f000000f2").root
            [9001, 9003]
        """
        return self._session.send(endpoints.errors_list(survey_id))

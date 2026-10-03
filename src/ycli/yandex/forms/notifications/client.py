"""Forms ``/notifications`` client on the httpx2 core (the runs of a form's integrations)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.notifications import endpoints
from ycli.yandex.forms.notifications.models import Notification, NotificationFilter
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    from ycli.yandex.forms.notifications.models import (
        NotificationAction,
        NotificationDetails,
        NotificationStatus,
    )


class NotificationsClient(Resource):
    """List, inspect, restart and cancel the runs of a form's integrations."""

    def list(
        self, filters: NotificationFilter | None = None, *, limit: int | None = None
    ) -> ItemList[Notification]:
        """``GET /notifications`` → runs matching every filter given, at most ``limit``.

        Args:
            filters: Which runs to return; ``None`` returns the runs of every form.
            limit: The most runs to return; ``None`` returns every run.

        Returns:
            The matching runs.

        Examples:
            >>> from ycli.yandex.forms.notifications.models import NotificationFilter
            >>> runs = forms.notifications.list(
            ...     NotificationFilter(
            ...         survey_id="686d0a1b2c3d4e5f000000f0", status=["error", "pending"]
            ...     ),
            ...     limit=500,
            ... )
            >>> [run.id for run in runs.root]
            [9001, 9002, 9003]
        """
        paged = endpoints.list_notifications(filters or NotificationFilter())
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
        return self._session.send(endpoints.get_notification(notification_id))

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
        return self._session.send(endpoints.get_notification_status(notification_id))

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
        return self._session.send(endpoints.restart_notification(notification_id))

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
        return self._session.send(endpoints.cancel_notification(notification_id))

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
        return self._session.send(endpoints.list_failed_notifications(survey_id))

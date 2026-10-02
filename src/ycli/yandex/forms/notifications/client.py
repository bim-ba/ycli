"""Forms ``/notifications`` client on the httpx2 core (the runs of a form's integrations)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.notifications import endpoints
from ycli.yandex.forms.notifications.models import NotificationList

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.forms.notifications.models import (
        NotificationAction,
        NotificationDetails,
        NotificationIdList,
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
        status: Sequence[str] | None = None,
        created_since: str | None = None,
        created_until: str | None = None,
        finished_since: str | None = None,
        finished_until: str | None = None,
        visible: bool | None = None,
        integration_type: str | None = None,
        ordering: str | None = None,
        limit: int | None = None,
    ) -> NotificationList:
        """``GET /notifications`` → runs matching every filter given, at most ``limit``.

        ``status`` holds any of pending, success, error, canceled; the ``*_since`` / ``*_until``
        bounds are ISO-8601 times (both ends inclusive); ``ordering`` is ``asc`` (the API
        default) or ``desc``.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.notifications.list(survey_id="686d0a1b", status=["error"]).root[
            ...     0
            ... ].id  # doctest: +SKIP
            744734758
        """
        paged = endpoints.list_notifications(
            survey_id=survey_id,
            hook_id=hook_id,
            subscription_id=subscription_id,
            answer_id=answer_id,
            status=status,
            created_since=created_since,
            created_until=created_until,
            finished_since=finished_since,
            finished_until=finished_until,
            visible=visible,
            integration_type=integration_type,
            ordering=ordering,
        )
        return NotificationList(list(self._session.iterate(paged, limit=limit)))

    def get(self, notification_id: int) -> NotificationDetails:
        """``GET /notifications/{id}`` → the run with its context, response and error.

        Example:
            >>> client.notifications.get(744734758).error  # doctest: +SKIP
        """
        return self._session.send(endpoints.get_notification(notification_id))

    def status_get(self, notification_id: int) -> NotificationStatus:
        """``GET /notifications/{id}/status`` → just the run's state.

        Example:
            >>> client.notifications.status_get(744734758).status  # doctest: +SKIP
            'pending'
        """
        return self._session.send(endpoints.get_notification_status(notification_id))

    def restart(self, notification_id: int) -> NotificationAction:
        """``POST /notifications/{id}/restart`` — run the integration again for that answer.

        ``result.status`` is ``ok``, ``skip`` (a run that is still pending is left alone),
        ``fail`` (see ``detail``) or ``operation``: the run was queued again. A canceled run
        answered ``operation`` with the ``operation_id`` ``not-supported`` on the test
        organization, so there is nothing to poll: read the run's state with :meth:`status_get`.

        Example:
            >>> client.notifications.restart(744734758).result.status  # doctest: +SKIP
            'ok'
        """
        return self._session.send(endpoints.restart_notification(notification_id))

    def cancel(self, notification_id: int) -> NotificationAction:
        """``POST /notifications/{id}/cancel`` — stop a run that has not finished.

        A run that is already canceled or finished answers ``result.status`` ``skip``.

        Example:
            >>> client.notifications.cancel(744734758).result.status  # doctest: +SKIP
            'ok'
        """
        return self._session.send(endpoints.cancel_notification(notification_id))

    def errors_list(self, survey_id: str) -> NotificationIdList:
        """``GET /surveys/{id}/show-errors`` → ids of the form's failed runs still shown.

        Read each with :meth:`get`.

        Example:
            >>> client.notifications.errors_list("686d0a1b").root  # doctest: +SKIP
            [744734758]
        """
        return self._session.send(endpoints.list_failed_notifications(survey_id))

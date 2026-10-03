"""Forms integrations (subscriptions) client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.subscriptions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.models import FileOut
    from ycli.yandex.forms.subscriptions.models import Subscription
    from ycli.yandex.models import ItemList


def _without_id(body: Subscription) -> Subscription:
    # ``id`` is the server's: a subscription read back and edited must not send it.
    return body.model_copy(update={"id": None})


class SubscriptionsClient(Resource):
    """List, get, create, modify and delete the integrations of a hook; upload attachments."""

    def list(self, survey_id: str, hook_id: int) -> ItemList[Subscription]:
        """``GET /surveys/{id}/hooks/{hook_id}/subscriptions`` → every integration of the hook.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.

        Returns:
            Every integration of the hook.

        Examples:
            >>> forms.subscriptions.list("686d0a1b2c3d4e5f000000b0", 21).root[0].type
            'http'
        """
        return self._session.send(endpoints.list_subscriptions(survey_id, hook_id))

    def get(self, survey_id: str, hook_id: int, subscription_id: int) -> Subscription:
        """``GET …/subscriptions/{subscription_id}`` → one integration, typed by ``type``.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            subscription_id: The integration's id.

        Returns:
            The integration.

        Examples:
            >>> forms.subscriptions.get("686d0a1b2c3d4e5f000000b0", 21, 4).type
            'tracker'
        """
        return self._session.send(endpoints.get_subscription(survey_id, hook_id, subscription_id))

    def create(self, survey_id: str, hook_id: int, body: Subscription) -> Subscription:
        """``POST …/subscriptions`` — add an integration to the hook → it, with its ``id``.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            body: The new integration.

        Returns:
            The created integration, with its ``id``.

        Examples:
            >>> from ycli.yandex.forms.subscriptions.models import HttpSubscription
            >>> forms.subscriptions.create(
            ...     "686d0a1b2c3d4e5f000000b0",
            ...     21,
            ...     HttpSubscription(url="https://example.com/hook", active=False),
            ... ).id
            5
        """
        return self._session.send(
            endpoints.create_subscription(survey_id, hook_id, _without_id(body))
        )

    def modify(
        self, survey_id: str, hook_id: int, subscription_id: int, body: Subscription
    ) -> Subscription:
        """``PATCH …/subscriptions/{subscription_id}`` — change the fields set in ``body``.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            subscription_id: The integration's id.
            body: The fields to change.

        Returns:
            The updated integration.

        Examples:
            >>> from ycli.yandex.forms.subscriptions.models import HttpSubscription
            >>> forms.subscriptions.modify(
            ...     "686d0a1b2c3d4e5f000000b0", 21, 6, HttpSubscription(active=False)
            ... ).active
            False
        """
        return self._session.send(
            endpoints.modify_subscription(survey_id, hook_id, subscription_id, _without_id(body))
        )

    def delete(self, survey_id: str, hook_id: int, subscription_id: int) -> None:
        """``DELETE …/subscriptions/{subscription_id}`` (200, no body).

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            subscription_id: The integration's id.

        Examples:
            >>> forms.subscriptions.delete("686d0a1b2c3d4e5f000000b0", 21, 8)
        """
        self._session.send(endpoints.delete_subscription(survey_id, hook_id, subscription_id))

    def attach(
        self, survey_id: str, hook_id: int, subscription_id: int, *, filename: str, data: bytes
    ) -> FileOut:
        """Upload a fixed attachment (multipart field ``file``) → its ``path``.

        Reference the returned ``path`` from ``attachments.static`` in a subscription body.
        Binary payload — SDK and CLI only.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            subscription_id: The integration's id.
            filename: The attachment's file name.
            data: The attachment's raw bytes.

        Returns:
            The stored attachment, with its ``path``.

        Examples:
            >>> forms.subscriptions.attach(
            ...     "686d0a1b2c3d4e5f000000b0", 21, 9, filename="terms.pdf", data=b"%PDF"
            ... ).path
            '/forms/terms.pdf'
        """
        return self._session.send(
            endpoints.attach_file(survey_id, hook_id, subscription_id, filename=filename, data=data)
        )

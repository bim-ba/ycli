"""Forms integrations (subscriptions) client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.subscriptions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.files.models import FileOut
    from ycli.yandex.forms.subscriptions.models import Subscription, SubscriptionList


def _dumped(body: Subscription) -> dict:
    # ``id`` is the server's: a subscription read back and edited must not send it.
    return body.model_dump(by_alias=True, exclude_none=True, exclude={"id"})


class SubscriptionsClient(Resource):
    """List, get, create, modify and delete the integrations of a hook; upload attachments."""

    def list(self, survey_id: str, hook_id: int) -> SubscriptionList:
        """``GET /surveys/{id}/hooks/{hook_id}/subscriptions`` → every integration of the hook.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.subscriptions.list("686d0a1b", 11).root[0].type  # doctest: +SKIP
            'http'
        """
        return self._session.send(endpoints.list_subscriptions(survey_id, hook_id))

    def get(self, survey_id: str, hook_id: int, subscription_id: int) -> Subscription:
        """``GET …/subscriptions/{subscription_id}`` → one integration, typed by ``type``.

        Example:
            >>> client.subscriptions.get("686d0a1b", 11, 4).url  # doctest: +SKIP
            'https://example.com/hook'
        """
        return self._session.send(endpoints.get_subscription(survey_id, hook_id, subscription_id))

    def create(self, survey_id: str, hook_id: int, body: Subscription) -> Subscription:
        """``POST …/subscriptions`` — add an integration to the hook → it, with its ``id``.

        Example:
            >>> from ycli.yandex.forms.subscriptions.models import HttpSubscription
            >>> client.subscriptions.create(
            ...     "686d0a1b", 11, HttpSubscription(url="https://example.com/hook", active=False)
            ... ).id  # doctest: +SKIP
            4
        """
        return self._session.send(endpoints.create_subscription(survey_id, hook_id, _dumped(body)))

    def modify(
        self, survey_id: str, hook_id: int, subscription_id: int, body: Subscription
    ) -> Subscription:
        """``PATCH …/subscriptions/{subscription_id}`` — change the fields set in ``body``.

        Example:
            >>> client.subscriptions.modify(
            ...     "686d0a1b", 11, 4, HttpSubscription(active=True)
            ... ).active  # doctest: +SKIP
            True
        """
        return self._session.send(
            endpoints.modify_subscription(survey_id, hook_id, subscription_id, _dumped(body))
        )

    def delete(self, survey_id: str, hook_id: int, subscription_id: int) -> None:
        """``DELETE …/subscriptions/{subscription_id}`` (200, no body).

        Example:
            >>> client.subscriptions.delete("686d0a1b", 11, 4)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_subscription(survey_id, hook_id, subscription_id))

    def attach(
        self, survey_id: str, hook_id: int, subscription_id: int, *, filename: str, data: bytes
    ) -> FileOut:
        """Upload a fixed attachment (multipart field ``file``) → its ``path``.

        Reference the returned ``path`` from ``attachments.static`` in a subscription body.
        Binary payload — SDK and CLI only.

        Example:
            >>> client.subscriptions.attach(
            ...     "686d0a1b", 11, 4, filename="terms.pdf", data=b"%PDF"
            ... ).path  # doctest: +SKIP
            '/forms/686d0a1b/terms.pdf'
        """
        return self._session.send(
            endpoints.attach_file(survey_id, hook_id, subscription_id, filename=filename, data=data)
        )

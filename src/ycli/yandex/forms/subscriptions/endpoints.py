"""Forms ``/surveys/{id}/hooks/{hook_id}/subscriptions`` operations, declared once (sans-IO).

Examples:
    >>> list_("686d", 11).path
    'surveys/686d/hooks/11/subscriptions'
    >>> attach("686d", 11, 4, filename="a.pdf", data=b"x").files
    {'file': ('a.pdf', b'x')}
"""

from __future__ import annotations

from http import HTTPMethod
from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.models import FileOut
from ycli.yandex.forms.subscriptions.models import Subscription, SubscriptionAdapter
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    import httpx2


def _subscription(response: httpx2.Response) -> Subscription:
    # A union is not a class an Endpoint can name as its response type: parse it here.
    return SubscriptionAdapter.validate_json(response.content)


def _subscriptions(survey_id: str, hook_id: int) -> str:
    return f"surveys/{segment(survey_id)}/hooks/{segment(hook_id)}/subscriptions"


def list_(survey_id: str, hook_id: int) -> Endpoint[ItemList[Subscription]]:
    return Endpoint(HTTPMethod.GET, _subscriptions(survey_id, hook_id), ItemList[Subscription])


def get(survey_id: str, hook_id: int, subscription_id: int) -> Endpoint[Subscription]:
    path = f"{_subscriptions(survey_id, hook_id)}/{segment(subscription_id)}"
    return Endpoint(HTTPMethod.GET, path, parser=_subscription)


def create(survey_id: str, hook_id: int, body: Subscription) -> Endpoint[Subscription]:
    path = _subscriptions(survey_id, hook_id)
    return Endpoint(HTTPMethod.POST, path, json=body, parser=_subscription)


def update(
    survey_id: str, hook_id: int, subscription_id: int, body: Subscription
) -> Endpoint[Subscription]:
    path = f"{_subscriptions(survey_id, hook_id)}/{segment(subscription_id)}"
    return Endpoint(HTTPMethod.PATCH, path, json=body, parser=_subscription)


def delete(survey_id: str, hook_id: int, subscription_id: int) -> Endpoint[None]:
    return Endpoint(
        HTTPMethod.DELETE, f"{_subscriptions(survey_id, hook_id)}/{segment(subscription_id)}"
    )


def attach(
    survey_id: str, hook_id: int, subscription_id: int, *, filename: str, data: bytes
) -> Endpoint[FileOut]:
    path = f"{_subscriptions(survey_id, hook_id)}/{segment(subscription_id)}/attachment"
    return Endpoint(HTTPMethod.POST, path, FileOut, files={"file": (filename, data)})

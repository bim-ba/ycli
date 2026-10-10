"""Pydantic models for Forms integration groups (hooks).

A hook groups integrations (``subscriptions``) that share trigger conditions: on a new answer,
a hook whose conditions match runs each of its active integrations.
"""

from typing import Annotated

from pydantic import Field

from ycli.yandex.forms.models import ConditionsResponse
from ycli.yandex.forms.subscriptions.models import Subscription
from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.sync.marks import Identity


class Hook(APIModel):
    """An integration group with its conditions and integrations.

    Examples:
        >>> Hook.model_validate(
        ...     {
        ...         "id": 11,
        ...         "name": "CRM",
        ...         "active": False,
        ...         "subscriptions": [{"type": "http", "id": 4}],
        ...     }
        ... ).subscriptions[0].id
        4
    """

    id: Annotated[int | None, Identity()] = Field(
        default=None, description="Integration group id (integer)."
    )
    name: str | None = Field(default=None, description="Integration group name.")
    active: bool | None = Field(default=None, description="Whether the group's integrations run.")
    conditions: ConditionsResponse | None = Field(
        default=None, description="Conditions that gate the group (absent when there are none)."
    )
    subscriptions: list[Subscription] = Field(
        default_factory=list, description="The group's integrations, each tagged by type."
    )


class HookCreate(RequestBody):
    """Typed body for ``POST /surveys/{id}/hooks``; unset fields are dropped before sending.

    Examples:
        >>> HookCreate(name="CRM", active=False).model_dump(exclude_none=True)
        {'name': 'CRM', 'active': False}
    """

    name: str | None = Field(default=None, description="Group name (max 100).")
    active: bool | None = Field(default=None, description="Whether the group's integrations run.")


class HookUpdate(HookCreate):
    """Typed body for ``PATCH /surveys/{id}/hooks/{hook_id}``: only the fields set change.

    Examples:
        >>> HookUpdate(active=True).model_dump(exclude_none=True)
        {'active': True}
    """

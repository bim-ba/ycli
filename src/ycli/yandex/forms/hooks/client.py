"""Forms ``/surveys/{id}/hooks`` client on the httpx2 core (integration groups)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.hooks import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.hooks.models import Hook, HookCreate, HookUpdate
    from ycli.yandex.models import ItemList


class HooksClient(Resource):
    """List, get, create, update and delete a form's integration groups."""

    def list(self, survey_id: str) -> ItemList[Hook]:
        """``GET /surveys/{id}/hooks`` → every integration group with its integrations.

        Args:
            survey_id: The form's id.

        Returns:
            Every integration group, with its integrations.

        Examples:
            >>> forms.hooks.list("686d0a1b2c3d4e5f000000a0").root[0].name
            'CRM'
        """
        return self._session.send(endpoints.list_(survey_id))

    def get(self, survey_id: str, hook_id: int) -> Hook:
        """``GET /surveys/{id}/hooks/{hook_id}`` → one :class:`Hook`.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.

        Returns:
            The integration group.

        Examples:
            >>> forms.hooks.get("686d0a1b2c3d4e5f000000a0", 12).active
            False
        """
        return self._session.send(endpoints.get(survey_id, hook_id))

    def create(self, survey_id: str, body: HookCreate) -> Hook:
        """``POST /surveys/{id}/hooks`` — create a group from a ``HookCreate``.

        Args:
            survey_id: The form's id.
            body: The ``HookCreate``: the group's name and whether it is active.

        Returns:
            The created integration group, with its ``id``.

        Examples:
            >>> from ycli.yandex.forms.hooks.models import HookCreate
            >>> forms.hooks.create(
            ...     "686d0a1b2c3d4e5f000000a0",
            ...     HookCreate.model_validate({"name": "CRM", "active": False}),
            ... ).id
            13
        """
        return self._session.send(endpoints.create(survey_id, body))

    def update(self, survey_id: str, hook_id: int, body: HookUpdate) -> Hook:
        """``PATCH /surveys/{id}/hooks/{hook_id}`` — only the keys in ``body`` change.

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.
            body: The keys to change.

        Returns:
            The updated integration group.

        Examples:
            >>> from ycli.yandex.forms.hooks.models import HookUpdate
            >>> forms.hooks.update(
            ...     "686d0a1b2c3d4e5f000000a0", 15, HookUpdate.model_validate({"name": "CRM"})
            ... ).name
            'CRM'
        """
        return self._session.send(endpoints.update(survey_id, hook_id, body))

    def delete(self, survey_id: str, hook_id: int) -> None:
        """``DELETE /surveys/{id}/hooks/{hook_id}`` — the group and its integrations (200).

        Args:
            survey_id: The form's id.
            hook_id: The integration group's (hook's) id.

        Examples:
            >>> forms.hooks.delete("686d0a1b2c3d4e5f000000a0", 16)
        """
        self._session.send(endpoints.delete(survey_id, hook_id))

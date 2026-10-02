"""Forms ``/surveys/{id}/hooks`` client on the httpx2 core (integration groups)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.hooks import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.hooks.models import Hook, HookList


class HooksClient(Resource):
    """List, get, create, modify and delete a form's integration groups."""

    def list(self, survey_id: str) -> HookList:
        """``GET /surveys/{id}/hooks`` → every integration group with its integrations.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.hooks.list("686d0a1b").root[0].name  # doctest: +SKIP
            'CRM'
        """
        return self._session.send(endpoints.list_hooks(survey_id))

    def get(self, survey_id: str, hook_id: int) -> Hook:
        """``GET /surveys/{id}/hooks/{hook_id}`` → one :class:`Hook`.

        Example:
            >>> client.hooks.get("686d0a1b", 11).active  # doctest: +SKIP
            False
        """
        return self._session.send(endpoints.get_hook(survey_id, hook_id))

    def create(self, survey_id: str, body: dict[str, Any]) -> Hook:
        """``POST /surveys/{id}/hooks`` — create a group from a dumped ``HookCreate``.

        Example:
            >>> client.hooks.create(
            ...     "686d0a1b", {"name": "CRM", "active": False}
            ... ).id  # doctest: +SKIP
            11
        """
        return self._session.send(endpoints.create_hook(survey_id, body))

    def modify(self, survey_id: str, hook_id: int, body: dict[str, Any]) -> Hook:
        """``PATCH /surveys/{id}/hooks/{hook_id}`` — only the keys in ``body`` change.

        Example:
            >>> client.hooks.modify("686d0a1b", 11, {"active": True}).active  # doctest: +SKIP
            True
        """
        return self._session.send(endpoints.modify_hook(survey_id, hook_id, body))

    def delete(self, survey_id: str, hook_id: int) -> None:
        """``DELETE /surveys/{id}/hooks/{hook_id}`` — the group and its integrations (200).

        Example:
            >>> client.hooks.delete("686d0a1b", 11)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_hook(survey_id, hook_id))

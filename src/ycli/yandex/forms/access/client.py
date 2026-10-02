"""Forms ``/surveys/{id}/access`` client on the httpx2 core (survey permissions)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.access import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.access.models import PermissionList


class AccessClient(Resource):
    """Read and change who may edit and who may fill a form."""

    def get(self, survey_id: str) -> PermissionList:
        """``GET /surveys/{id}/access`` → one permission per action (change, submit).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.access.get("686d0a1b").root[0].access  # doctest: +SKIP
            'restricted'
        """
        return self._session.send(endpoints.get_access(survey_id))

    def set(self, survey_id: str, body: dict[str, Any]) -> PermissionList:
        """``POST /surveys/{id}/access`` — set one action's level from a dumped ``AccessUpdate``.

        Example:
            >>> client.access.set(
            ...     "686d0a1b", {"action": "submit", "access": "common"}
            ... )  # doctest: +SKIP
        """
        return self._session.send(endpoints.set_access(survey_id, body))

    def grant(self, survey_id: str, body: dict[str, Any]) -> PermissionList:
        """``POST /surveys/{id}/access/grant`` — add a user or group (a dumped ``AccessGrant``).

        Example:
            >>> client.access.grant(
            ...     "686d0a1b", {"action": "change", "user": {"uid": "7"}}
            ... )  # doctest: +SKIP
        """
        return self._session.send(endpoints.grant_access(survey_id, body))

    def revoke(self, survey_id: str, body: dict[str, Any]) -> PermissionList:
        """``POST /surveys/{id}/access/revoke`` — remove a user or group (``AccessRevoke``).

        Example:
            >>> client.access.revoke(
            ...     "686d0a1b", {"action": "change", "user": {"uid": "7"}}
            ... )  # doctest: +SKIP
        """
        return self._session.send(endpoints.revoke_access(survey_id, body))

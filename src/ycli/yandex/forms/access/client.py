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

        Args:
            survey_id: The form's id.

        Returns:
            One permission per action.

        Examples:
            >>> forms.access.get("686d0a1b2c3d4e5f000000d0").root[0].access
            'restricted'
        """
        return self._session.send(endpoints.get_access(survey_id))

    def set(self, survey_id: str, body: dict[str, Any]) -> PermissionList:
        """``POST /surveys/{id}/access`` — set one action's level from a dumped ``AccessUpdate``.

        Args:
            survey_id: The form's id.
            body: The dumped ``AccessUpdate``: the action and its new access level.

        Returns:
            The permissions after the change.

        Examples:
            >>> forms.access.set(
            ...     "686d0a1b2c3d4e5f000000d0", {"action": "submit", "access": "common"}
            ... ).root[1].access
            'common'
        """
        return self._session.send(endpoints.set_access(survey_id, body))

    def grant(self, survey_id: str, body: dict[str, Any]) -> PermissionList:
        """``POST /surveys/{id}/access/grant`` — add a user or group (a dumped ``AccessGrant``).

        Args:
            survey_id: The form's id.
            body: The dumped ``AccessGrant``: the action and the user or group to add.

        Returns:
            The permissions after the change.

        Examples:
            >>> forms.access.grant(
            ...     "686d0a1b2c3d4e5f000000d0",
            ...     {"action": "change", "user": {"uid": "7001", "cloud_uid": "cloud-7001"}},
            ... ).root[0].action
            'change'
        """
        return self._session.send(endpoints.grant_access(survey_id, body))

    def revoke(self, survey_id: str, body: dict[str, Any]) -> PermissionList:
        """``POST /surveys/{id}/access/revoke`` — remove a user or group (``AccessRevoke``).

        Args:
            survey_id: The form's id.
            body: The dumped ``AccessRevoke``: the action and the user or group to remove.

        Returns:
            The permissions after the change.

        Examples:
            >>> forms.access.revoke(
            ...     "686d0a1b2c3d4e5f000000d0",
            ...     {"action": "submit", "group": {"src": "staff", "id": "42"}},
            ... ).root[1].action
            'submit'
        """
        return self._session.send(endpoints.revoke_access(survey_id, body))

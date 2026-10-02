"""Forms ``/surveys/{id}/keysets`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.keysets import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.keysets.models import Keyset, KeysetList


class KeysetsClient(Resource):
    """List, get, create, modify, delete and download a form's key sets."""

    def list(self, survey_id: str) -> KeysetList:
        """``GET /surveys/{id}/keysets`` → every key set (a bare, unpaged array).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.keysets.list("686d0a1b2c3d4e5f").root[0].name  # doctest: +SKIP
            'Q1 invites'
        """
        return self._session.send(endpoints.list_keysets(survey_id))

    def get(self, survey_id: str, keyset_id: int) -> Keyset:
        """``GET /surveys/{id}/keysets/{keyset_id}`` → a single :class:`Keyset`.

        Example:
            >>> client.keysets.get("686d0a1b2c3d4e5f", 3).id  # doctest: +SKIP
            3
        """
        return self._session.send(endpoints.get_keyset(survey_id, keyset_id))

    def create(self, survey_id: str, body: dict[str, Any]) -> Keyset:
        """``POST /surveys/{id}/keysets`` — create a key set from a dumped ``KeysetCreate``.

        The API requires ``is_enabled`` on create, alongside ``name`` and ``total``.

        Example:
            >>> client.keysets.create(
            ...     "686d0a1b2c3d4e5f", {"name": "Q1", "total": 100, "is_enabled": True}
            ... ).id  # doctest: +SKIP
            7
        """
        return self._session.send(endpoints.create_keyset(survey_id, body))

    def modify(self, survey_id: str, keyset_id: int, body: dict[str, Any]) -> Keyset:
        """``PATCH /surveys/{id}/keysets/{keyset_id}`` — replace a key set → the :class:`Keyset`.

        Despite the method, the API validates a full record: ``name``, ``total`` and
        ``is_enabled`` are all required (a ``KeysetUpdate`` with every field set).

        Example:
            >>> client.keysets.modify(
            ...     "686d0a1b2c3d4e5f", 3, {"name": "Q1", "total": 100, "is_enabled": False}
            ... ).is_enabled  # doctest: +SKIP
            False
        """
        return self._session.send(endpoints.modify_keyset(survey_id, keyset_id, body))

    def delete(self, survey_id: str, keyset_id: int) -> None:
        """``DELETE /surveys/{id}/keysets/{keyset_id}`` — delete a key set (no body comes back).

        Example:
            >>> client.keysets.delete("686d0a1b2c3d4e5f", 3)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_keyset(survey_id, keyset_id))

    def download(self, survey_id: str, keyset_id: int) -> bytes:
        """``GET /surveys/{id}/keysets/{keyset_id}/download`` → the key set's raw bytes.

        Binary payload — SDK and CLI only, never an MCP result.

        Example:
            >>> client.keysets.download("686d0a1b2c3d4e5f", 3)[:2]  # doctest: +SKIP
            b'PK'
        """
        return self._session.send(endpoints.download_keyset(survey_id, keyset_id))

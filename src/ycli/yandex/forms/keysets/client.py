"""Forms ``/surveys/{id}/keysets`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.keysets import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.keysets.models import Keyset, KeysetCreate, KeysetUpdate
    from ycli.yandex.models import ItemList


class KeysetsClient(Resource):
    """List, get, create, update, delete and download a form's key sets."""

    def list(self, survey_id: str) -> ItemList[Keyset]:
        """``GET /surveys/{id}/keysets`` → every key set (a bare, unpaged array).

        Args:
            survey_id: The form's id.

        Returns:
            Every key set of the form.

        Examples:
            >>> forms.keysets.list("686d0a1b2c3d4e5f00000020").root[0].name
            'Q1 invites'
        """
        return self._session.send(endpoints.list_(survey_id))

    def get(self, survey_id: str, keyset_id: int) -> Keyset:
        """``GET /surveys/{id}/keysets/{keyset_id}`` → a single :class:`Keyset`.

        Args:
            survey_id: The form's id.
            keyset_id: The key set's id.

        Returns:
            The key set.

        Examples:
            >>> forms.keysets.get("686d0a1b2c3d4e5f00000020", 3).id
            3
        """
        return self._session.send(endpoints.get(survey_id, keyset_id))

    def create(self, survey_id: str, body: KeysetCreate) -> Keyset:
        """``POST /surveys/{id}/keysets`` — create a key set from a ``KeysetCreate``.

        The API requires ``is_enabled`` on create, alongside ``name`` and ``total``.

        Args:
            survey_id: The form's id.
            body: The ``KeysetCreate``.

        Returns:
            The created key set, with its ``id``.

        Examples:
            >>> from ycli.yandex.forms.keysets.models import KeysetCreate
            >>> forms.keysets.create(
            ...     "686d0a1b2c3d4e5f00000020",
            ...     KeysetCreate.model_validate(
            ...         {"name": "Q1 invites", "total": 100, "is_enabled": True}
            ...     ),
            ... ).id
            3
        """
        return self._session.send(endpoints.create(survey_id, body))

    def update(self, survey_id: str, keyset_id: int, body: KeysetUpdate) -> Keyset:
        """``PATCH /surveys/{id}/keysets/{keyset_id}`` — replace a key set → the :class:`Keyset`.

        Despite the method, the API validates a full record: ``name``, ``total`` and
        ``is_enabled`` are all required (a ``KeysetUpdate`` with every field set).

        Args:
            survey_id: The form's id.
            keyset_id: The key set's id.
            body: The ``KeysetUpdate`` with every field set.

        Returns:
            The replaced key set.

        Examples:
            >>> from ycli.yandex.forms.keysets.models import KeysetUpdate
            >>> forms.keysets.update(
            ...     "686d0a1b2c3d4e5f00000020",
            ...     4,
            ...     KeysetUpdate.model_validate(
            ...         {"name": "Q1 invites", "total": 100, "is_enabled": True}
            ...     ),
            ... ).name
            'Q1 invites'
        """
        return self._session.send(endpoints.update(survey_id, keyset_id, body))

    def delete(self, survey_id: str, keyset_id: int) -> None:
        """``DELETE /surveys/{id}/keysets/{keyset_id}`` — delete a key set (no body comes back).

        Args:
            survey_id: The form's id.
            keyset_id: The key set's id.

        Examples:
            >>> forms.keysets.delete("686d0a1b2c3d4e5f00000020", 5)
        """
        self._session.send(endpoints.delete(survey_id, keyset_id))

    def download(self, survey_id: str, keyset_id: int) -> bytes:
        """``GET /surveys/{id}/keysets/{keyset_id}/download`` → the key set's raw bytes.

        Binary payload — SDK and CLI only, never an MCP result.

        Args:
            survey_id: The form's id.
            keyset_id: The key set's id.

        Returns:
            The key set's raw bytes.

        Examples:
            >>> forms.keysets.download("686d0a1b2c3d4e5f00000020", 6)[:5]
            b'key-1'
        """
        return self._session.send(endpoints.download(survey_id, keyset_id))

"""Declarative Forms /surveys/{id}/keysets client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.keysets.models import Keyset, KeysetList


class KeysetsClient(FormsResource):
    """Declarative HTTP for ``/surveys/{id}/keysets`` (list/get/create/modify/delete/download)."""

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/keysets")
    def list(self, survey_id: uplink.Path) -> KeysetList:  # ty: ignore[empty-body]
        """``GET /surveys/{id}/keysets`` → flat :class:`KeysetList` (a bare, unpaged array).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.keysets.list("686d0a1b2c3d4e5f").root[0].name  # doctest: +SKIP
            'Q1 invites'
        """

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/keysets/{keyset_id}")
    def get(self, survey_id: uplink.Path, keyset_id: uplink.Path) -> Keyset:  # ty: ignore[empty-body]
        """``GET /surveys/{id}/keysets/{keyset_id}`` → a single :class:`Keyset`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.keysets.get("686d0a1b2c3d4e5f", 7).used  # doctest: +SKIP
            3
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys/{survey_id}/keysets")
    def create(self, survey_id: uplink.Path, body: uplink.Body) -> Keyset:  # ty: ignore[empty-body]
        """``POST /surveys/{id}/keysets`` — create a key set. Returns the created :class:`Keyset`.

        Build ``body`` from a :class:`~ycli.yandex.forms.keysets.models.KeysetCreate`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.keysets.create(
            ...     "686d0a1b2c3d4e5f", {"name": "Q1", "total": 250}
            ... ).id  # doctest: +SKIP
            7
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("surveys/{survey_id}/keysets/{keyset_id}")
    def modify(self, survey_id: uplink.Path, keyset_id: uplink.Path, body: uplink.Body) -> Keyset:  # ty: ignore[empty-body]
        """``PATCH /surveys/{id}/keysets/{keyset_id}`` — replace a key set → the :class:`Keyset`.

        Despite being a PATCH, the API validates the body as a full record: ``name``, ``total`` and
        ``is_enabled`` are all required, and any missing field is rejected with ``400
        value_error.missing``. Build ``body`` from a
        :class:`~ycli.yandex.forms.keysets.models.KeysetUpdate` with every field set.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.keysets.modify(
            ...     "686d0a1b2c3d4e5f", 7, {"name": "Q1", "total": 250, "is_enabled": False}
            ... ).is_enabled  # doctest: +SKIP
            False
        """

    @uplink.delete("surveys/{survey_id}/keysets/{keyset_id}")
    def delete(self, survey_id: uplink.Path, keyset_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /surveys/{id}/keysets/{keyset_id}`` — delete a key set (200 OK, no body).

        Returns the raw response; a non-2xx status raises a typed ``YandexError`` first.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.keysets.delete("686d0a1b2c3d4e5f", 7).status_code  # doctest: +SKIP
            200
        """

    @uplink.get("surveys/{survey_id}/keysets/{keyset_id}/download")
    def _download(self, survey_id: uplink.Path, keyset_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """Raw binary response for a key set (internal; callers use ``download``).

        No ``@uplink.returns.json()`` — this is a byte stream, not JSON."""

    def download(self, survey_id: str, keyset_id: int) -> bytes:
        """``GET /surveys/{id}/keysets/{keyset_id}/download`` → the key set's raw bytes.

        Binary payload — SDK/CLI only (never MCP: base64 blobs are not an agent payload).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> Path("keys.csv").write_bytes(
            ...     client.keysets.download("686d0a1b2c3d4e5f", 7)
            ... )  # doctest: +SKIP
        """
        return self._download(survey_id, keyset_id).content

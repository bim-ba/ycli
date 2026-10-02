"""Wiki ``/pages/{id}/access`` client on the httpx2 core — who may do what on a page."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.access import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.access.models import PageAccess


class AccessClient(Resource):
    """``/pages/{id}/access``: grant, change, revoke and clear a page's personal accesses.

    Read them back with ``pages.get_by_id(page_id, fields="access_policy,access_lists")``.
    ``prevent_selflock=True`` makes the API refuse a change that would leave the caller without
    read access or the right to change accesses; the page owner's own grant cannot be changed
    or revoked either way.
    """

    def create(self, page_id: int, body: dict[str, Any]) -> PageAccess:
        """``POST /pages/{id}/access`` — grant a user or a group a role; returns the grant.

        ``body`` is a dumped :class:`PageAccessCreate` (``user`` or ``group``, ``role``, optional
        ``inheritance``). Granting a user who already holds a personal access is refused; use
        :meth:`update` instead.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> body = {"user": {"uid": "1000"}, "role": "reader"}
            >>> client.access.create(12345, body).id  # doctest: +SKIP
            '48723431'
        """
        return self._session.send(endpoints.create_access(page_id, body))

    def update(
        self, page_id: int, access_id: str, body: dict[str, Any], *, prevent_selflock: bool = False
    ) -> PageAccess:
        """``POST /pages/{id}/access/{access_id}`` — change a grant's role or reach.

        ``body`` is a dumped :class:`PageAccessUpdate` (``role`` and/or ``inheritance``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.access.update(
            ...     12345, "48723431", {"role": "editor"}, prevent_selflock=True
            ... ).role  # doctest: +SKIP
            'editor'
        """
        endpoint = endpoints.update_access(
            page_id, access_id, body, prevent_selflock=prevent_selflock
        )
        return self._session.send(endpoint)

    def delete(self, page_id: int, access_id: str, *, prevent_selflock: bool = False) -> None:
        """``DELETE /pages/{id}/access/{access_id}`` — revoke one personal access (``204``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.access.delete(12345, "48723431", prevent_selflock=True)  # doctest: +SKIP
        """
        self._session.send(
            endpoints.delete_access(page_id, access_id, prevent_selflock=prevent_selflock)
        )

    def clear(self, page_id: int, *, prevent_selflock: bool = False) -> None:
        """``DELETE /pages/{id}/access`` — revoke every personal access but the owner's (``204``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.access.clear(12345, prevent_selflock=True)  # doctest: +SKIP
        """
        self._session.send(endpoints.clear_access(page_id, prevent_selflock=prevent_selflock))

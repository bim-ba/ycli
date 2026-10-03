"""Wiki ``/pages/{id}/access`` client on the httpx2 core — who may do what on a page."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.access import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.access.models import PageAccess, PageAccessCreate, PageAccessUpdate


class AccessClient(Resource):
    """``/pages/{id}/access``: grant, change, revoke and clear a page's personal accesses.

    Read them back with ``pages.get_by_id(page_id, fields="access_policy,access_lists")``.
    ``prevent_selflock=True`` makes the API refuse a change that would leave the caller without
    read access or the right to change accesses; the page owner's own grant cannot be changed
    or revoked either way.
    """

    def create(self, page_id: int, body: PageAccessCreate) -> PageAccess:
        """``POST /pages/{id}/access`` — grant a user or a group a role; returns the grant.

        ``body`` is a :class:`PageAccessCreate` (``user`` or ``group``, ``role``, optional
        ``inheritance``). Granting a user who already holds a personal access is refused; use
        :meth:`update` instead.

        Args:
            page_id: The page's id.
            body: The grant: ``user`` or ``group``, ``role`` and optional ``inheritance``.

        Returns:
            The created grant.

        Examples:
            >>> from ycli.yandex.wiki.access.models import PageAccessCreate
            >>> body = PageAccessCreate.model_validate({"user": {"uid": "9001"}, "role": "editor"})
            >>> wiki.access.create(6001, body).id
            '5001'
        """
        return self._session.send(endpoints.create_access(page_id, body))

    def update(
        self,
        page_id: int,
        access_id: str,
        body: PageAccessUpdate,
        *,
        prevent_selflock: bool = False,
    ) -> PageAccess:
        """``POST /pages/{id}/access/{access_id}`` — change a grant's role or reach.

        ``body`` is a :class:`PageAccessUpdate` (``role`` and/or ``inheritance``).

        Args:
            page_id: The page's id.
            access_id: The grant's id.
            body: The fields to change: ``role`` and/or ``inheritance``.
            prevent_selflock: Refuse a change that would lock the caller out of the page.

        Returns:
            The updated grant.

        Examples:
            >>> from ycli.yandex.wiki.access.models import PageAccessUpdate
            >>> wiki.access.update(
            ...     6003,
            ...     "5003",
            ...     PageAccessUpdate.model_validate({"role": "extra_editor"}),
            ...     prevent_selflock=True,
            ... ).role
            'extra_editor'
        """
        endpoint = endpoints.update_access(
            page_id, access_id, body, prevent_selflock=prevent_selflock
        )
        return self._session.send(endpoint)

    def delete(self, page_id: int, access_id: str, *, prevent_selflock: bool = False) -> None:
        """``DELETE /pages/{id}/access/{access_id}`` — revoke one personal access (``204``).

        Args:
            page_id: The page's id.
            access_id: The grant's id.
            prevent_selflock: Refuse a change that would lock the caller out of the page.

        Examples:
            >>> wiki.access.delete(6005, "5005", prevent_selflock=True)
        """
        self._session.send(
            endpoints.delete_access(page_id, access_id, prevent_selflock=prevent_selflock)
        )

    def clear(self, page_id: int, *, prevent_selflock: bool = False) -> None:
        """``DELETE /pages/{id}/access`` — revoke every personal access but the owner's (``204``).

        Args:
            page_id: The page's id.
            prevent_selflock: Refuse a change that would lock the caller out of the page.

        Examples:
            >>> wiki.access.clear(6007, prevent_selflock=True)
        """
        self._session.send(endpoints.clear_access(page_id, prevent_selflock=prevent_selflock))

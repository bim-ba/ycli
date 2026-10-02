"""Tracker issue ``/links`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.links import endpoints
from ycli.yandex.tracker.links.models import LinkList

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.tracker.links.models import Link


class LinksClient(Resource):
    """List, search (paged), add and delete the links between issues."""

    def list(self, key: str) -> LinkList:
        """``GET /issues/{key}/links`` → link listing.

        Args:
            key: The issue's key.

        Returns:
            The issue's links.

        Examples:
            >>> tracker.links.list("DE-41").root[0].object_key
            'DE-40'
        """
        return self._session.send(endpoints.list_links(key))

    def search(
        self,
        key: str,
        *,
        link_types: Sequence[str] | None = None,
        fields: Sequence[str] | None = None,
        limit: int | None = None,
    ) -> LinkList:
        """``POST /issues/{key}/links/_list`` (a read) → links, paged by ``page``/``perPage``.

        ``link_types`` keeps only links of these relationships and ``fields`` picks the fields to
        return. Despite the docs calling them type ids, the API takes the relationship phrases
        of :meth:`add` (``relates``, ``depends on``, ``is subtask for``, ``has epic``, …) and
        answers 400 to a type id such as ``subtask``. Capped at ``limit`` (``None`` = every link).

        Args:
            key: The issue's key.
            link_types: Keep only links of these relationships.
            fields: The fields to return for each link.
            limit: The most links to return; ``None`` returns every link.

        Returns:
            The matching links.

        Examples:
            >>> found = tracker.links.search(
            ...     "DE-44", link_types=["relates", "subtask"], fields=["id", "type"]
            ... )
            >>> [link.id for link in found.root]
            [441, 442]
        """
        paged = endpoints.search_links(key, link_types=link_types, fields=fields)
        return LinkList(list(self._session.iterate(paged, limit=limit)))

    def add(self, key: str, body: dict[str, Any]) -> Link:
        """``POST /issues/{key}/links`` — link two issues. Returns the link.

        Args:
            key: The issue's key.
            body: The link's ``relationship`` and the other ``issue``.

        Returns:
            The created link.

        Examples:
            >>> tracker.links.add(
            ...     "DE-42", {"relationship": "is dependent by", "issue": "OPS-9"}
            ... ).object_key
            'OPS-9'
        """
        return self._session.send(endpoints.add_link(key, body))

    def delete(self, key: str, link_id: str) -> None:
        """Delete a link (``DELETE …/links/{link_id}`` → 204). Raises on non-2xx.

        Args:
            key: The issue's key.
            link_id: The link's id.

        Examples:
            >>> tracker.links.delete("DE-43", "431")
        """
        self._session.send(endpoints.delete_link(key, link_id))

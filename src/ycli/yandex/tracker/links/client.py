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

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.links.list(key="DATAENGINEERING-130").root[0].object_key  # doctest: +SKIP
            'DATAENGINEERING-129'
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

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.links.search("JUNE-2", link_types=["relates"]).root[
            ...     0
            ... ].object_key  # doctest: +SKIP
            'TREK-9844'
        """
        paged = endpoints.search_links(key, link_types=link_types, fields=fields)
        return LinkList(list(self._session.iterate(paged, limit=limit)))

    def add(self, key: str, body: dict[str, Any]) -> Link:
        """``POST /issues/{key}/links`` — link two issues. Returns the link.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.links.add(
            ...     "DATAENGINEERING-130",
            ...     {"relationship": "depends on", "issue": "DATAENGINEERING-129"},
            ... ).object_key  # doctest: +SKIP
            'DATAENGINEERING-129'
        """
        return self._session.send(endpoints.add_link(key, body))

    def delete(self, key: str, link_id: str) -> None:
        """Delete a link (``DELETE …/links/{link_id}`` → 204). Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.links.delete("DATAENGINEERING-130", 42)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_link(key, link_id))

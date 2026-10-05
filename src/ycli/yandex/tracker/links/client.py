"""Tracker issue ``/links`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.links import endpoints
from ycli.yandex.tracker.links.models import ImportLink, Link, LinkCreate

if TYPE_CHECKING:
    from collections.abc import Sequence


class LinksClient(Resource):
    """List, search (paged), add and delete the links between issues."""

    def list(self, issue_key: str) -> ItemList[Link]:
        """``GET /issues/{key}/links`` → link listing.

        Args:
            issue_key: The issue's key.

        Returns:
            The issue's links.

        Examples:
            >>> tracker.links.list("DE-41").root[0].object_key
            'DE-40'
        """
        return self._session.send(endpoints.list_(issue_key))

    def list_filtered(
        self,
        issue_key: str,
        *,
        link_types: Sequence[str] | None = None,
        fields: Sequence[str] | None = None,
        limit: int | None = None,
    ) -> ItemList[Link]:
        """``POST /issues/{key}/links/_list`` (a read) → links, paged by ``page``/``perPage``.

        ``link_types`` keeps only links of these relationships and ``fields`` picks the fields to
        return. Despite the docs calling them type ids, the API takes the relationship phrases
        of :meth:`create` (``relates``, ``depends on``, ``is subtask for``, ``has epic``, …) and
        answers 400 to a type id such as ``subtask``. Capped at ``limit`` (``None`` = every link).

        Args:
            issue_key: The issue's key.
            link_types: Keep only links of these relationships.
            fields: The fields to return for each link.
            limit: The most links to return; ``None`` returns every link.

        Returns:
            The matching links.

        Examples:
            >>> found = tracker.links.list_filtered(
            ...     "DE-44", link_types=["relates", "subtask"], fields=["id", "type"]
            ... )
            >>> [link.id for link in found.root]
            [441, 442]
        """
        paged = endpoints.list_filtered(issue_key, link_types=link_types, fields=fields)
        return ItemList[Link](list(self._session.iterate(paged, limit=limit)))

    def create(self, issue_key: str, body: LinkCreate) -> Link:
        """``POST /issues/{key}/links`` — link two issues. Returns the link.

        Args:
            issue_key: The issue's key.
            body: The link's ``relationship`` and the other ``issue``.

        Returns:
            The created link.

        Examples:
            >>> from ycli.yandex.tracker.links.models import LinkCreate
            >>> tracker.links.create(
            ...     "DE-42",
            ...     LinkCreate.model_validate(
            ...         {"relationship": "is dependent by", "issue": "OPS-9"}
            ...     ),
            ... ).object_key
            'OPS-9'
        """
        return self._session.send(endpoints.create(issue_key, body))

    def delete(self, issue_key: str, link_id: str) -> None:
        """Delete a link (``DELETE …/links/{link_id}`` → 204). Raises on non-2xx.

        Args:
            issue_key: The issue's key.
            link_id: The link's id.

        Examples:
            >>> tracker.links.delete("DE-43", "431")
        """
        self._session.send(endpoints.delete(issue_key, link_id))

    def import_(self, issue_key: str, body: ImportLink) -> Link:
        """``POST /issues/{issue_key}/links/_import`` — import an issue link. Returns the ``Link``.

        Args:
            issue_key: The issue's key.
            body: The link fields, including the source ``createdAt`` and ``createdBy``.

        Returns:
            The imported link.

        Examples:
            >>> from ycli.yandex.tracker.links.models import ImportLink
            >>> tracker.links.import_(
            ...     "TEST-3",
            ...     ImportLink.model_validate(
            ...         {
            ...             "relationship": "depends on",
            ...             "issue": "TEST-4",
            ...             "createdAt": "2020-03-04T05:06:07.000+0000",
            ...             "createdBy": "14",
            ...         }
            ...     ),
            ... ).object.key
            'TEST-4'
        """
        return self._session.send(endpoints.import_(issue_key, body))

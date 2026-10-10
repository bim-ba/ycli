"""DataLens entries client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.entries import endpoints

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.core.listing import Listing
    from ycli.yandex.datalens.entries.models import (
        EntriesPermissions,
        Entry,
        ListFilters,
        ListOrder,
        Relation,
        Renamed,
        Revision,
    )
    from ycli.yandex.datalens.models import EntryScope
    from ycli.yandex.models import ItemList


class EntriesClient(Resource):
    """Entries: the connections, datasets, charts and dashboards of the whole organization."""

    def list(
        self,
        *,
        limit: int | None = None,
        next: str | None = None,
        ids: Sequence[str] | None = None,
        scope: EntryScope | None = None,
        scopes: Sequence[EntryScope] | None = None,
        type: str | Sequence[str] | None = None,  # noqa: A002  # the API's own name for it
        created_by: Sequence[str] | None = None,
        order_by: ListOrder | None = None,
        exclude_locked: bool | None = None,
        include_links: bool | None = None,
        filters: ListFilters | None = None,
        include_permissions_info: bool | None = None,
        ignore_workbook_entries: bool | None = None,
        ignore_shared_entries: bool | None = None,
        include_data: bool | None = None,
    ) -> Listing[Entry]:
        """``getEntries`` → entries across the organization, draining ``nextPageToken``.

        The API requires one of ``scope``, ``scopes`` and ``ids``. Capped at ``limit``
        (``None`` = every entry found).

        Args:
            limit: The most entries to return; ``None`` returns every entry.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.
            ids: Keep only the entries with these ids.
            scope: Keep one kind of entry, e.g. ``dash`` or ``dataset``.
            scopes: Keep several kinds of entries.
            type: Keep one type of entry, or several (a chart's type, a connection's kind).
            created_by: Keep only what these users created.
            order_by: What to sort by and in which direction.
            exclude_locked: Leave out the entries the caller may not read.
            include_links: Also say what each entry is linked to.
            filters: Keep the entries whose name has a text.
            include_permissions_info: Also say what the caller may do with each entry.
            ignore_workbook_entries: Leave out the entries that lie in workbooks.
            ignore_shared_entries: Leave out the shared entries.
            include_data: Also give the content of each entry.

        Returns:
            The entries found; one the caller may not read comes with ``is_locked`` set.

        Examples:
            >>> found = datalens.entries.list(scope="dash", limit=45).collect().items
            >>> [(entry.entry_id, entry.key) for entry in found]
            [('ent00000000002', 'Sales/overview'), ('ent00000000003', 'Sales/margin')]
        """
        paged = endpoints.list_(
            ids=ids,
            scope=scope,
            scopes=scopes,
            type=type,
            created_by=created_by,
            order_by=order_by,
            exclude_locked=exclude_locked,
            include_links=include_links,
            filters=filters,
            include_permissions_info=include_permissions_info,
            ignore_workbook_entries=ignore_workbook_entries,
            ignore_shared_entries=ignore_shared_entries,
            include_data=include_data,
        )
        return self._session.iterate(paged, limit=limit, next=next)

    def relations_list(
        self,
        entry_ids: Sequence[str],
        *,
        limit: int | None = None,
        next: str | None = None,
        link_direction: str | None = None,
        include_permissions_info: bool | None = None,
        scope: EntryScope | None = None,
    ) -> Listing[Relation]:
        """``getEntriesRelations`` → what entries use, or what uses them, draining the pages.

        Capped at ``limit`` (``None`` = every relation).

        Args:
            entry_ids: The ids of the entries.
            limit: The most relations to return; ``None`` returns every relation.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.
            link_direction: ``from`` lists what the entries use, ``to`` what uses them.
            include_permissions_info: Also say what the caller may do with each related entry.
            scope: Keep one kind of related entry.

        Returns:
            The related entries.

        Examples:
            >>> related = datalens.entries.relations_list(["ent00000000002"], link_direction="from")
            >>> [relation.entry_id for relation in related]
            ['ent00000000001']
        """
        paged = endpoints.relations_list(
            entry_ids,
            link_direction=link_direction,
            include_permissions_info=include_permissions_info,
            scope=scope,
        )
        return self._session.iterate(paged, limit=limit, next=next)

    def permissions_get(self, entry_ids: Sequence[str]) -> EntriesPermissions:
        """``getEntriesPermissions`` → what the caller may do with each entry.

        The reply is a map by id: an entry the caller can see gives its ``permissions``, one
        that does not exist gives ``error: "NOT_FOUND"``. An id of a wrong form refuses the
        whole request (400).

        Args:
            entry_ids: The ids of the entries.

        Returns:
            Id → what was found.

        Examples:
            >>> found = datalens.entries.permissions_get(["ent00000000001", "ent00000000009"])
            >>> found.root["ent00000000001"].permissions.read
            True
            >>> found.root["ent00000000009"].error
            'NOT_FOUND'
        """
        return self._session.send(endpoints.permissions_get(entry_ids))

    def revisions_list(
        self,
        entry_id: str,
        *,
        limit: int | None = None,
        next: str | None = None,
        rev_ids: Sequence[str] | None = None,
    ) -> Listing[Revision]:
        """``getRevisions`` → the revisions of an entry, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every revision).

        Args:
            entry_id: The entry's id.
            limit: The most revisions to return; ``None`` returns every revision.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.
            rev_ids: Keep only these revisions.

        Returns:
            The revisions, the newest first.

        Examples:
            >>> revisions = (
            ...     datalens.entries.revisions_list("ent00000000001", limit=45).collect().items
            ... )
            >>> [revision.rev_id for revision in revisions]
            ['rev2', 'rev1']
        """
        paged = endpoints.revisions_list(entry_id, rev_ids=rev_ids)
        return self._session.iterate(paged, limit=limit, next=next)

    def rename(self, entry_id: str, *, name: str) -> ItemList[Renamed]:
        """``renameEntry`` — give an entry another name.

        Args:
            entry_id: The entry's id.
            name: The new name.

        Returns:
            The renamed entry, in a list as the API answers it.

        Examples:
            >>> datalens.entries.rename("ent00000000001", name="orders 2026").root[0].key
            'Sales/orders 2026'
        """
        return self._session.send(endpoints.rename(entry_id, name=name))

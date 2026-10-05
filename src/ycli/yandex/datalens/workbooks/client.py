"""DataLens workbooks client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.models import SubjectWithBindings
from ycli.yandex.datalens.workbooks import endpoints
from ycli.yandex.datalens.workbooks.models import WorkbookEntry, WorkbookListed
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.datalens.models import AccessBindingDelta, Operation, OrderField
    from ycli.yandex.datalens.workbooks.models import (
        EntriesFilters,
        EntriesOrder,
        EntryScope,
        Workbook,
        WorkbookCreated,
        WorkbookDetails,
        WorkbooksDeleted,
        WorkbooksMoved,
    )
    from ycli.yandex.models import SortDirection


class WorkbooksClient(Resource):
    """Workbooks: where connections, datasets, charts and dashboards live."""

    def get(
        self, workbook_id: str, *, include_permissions_info: bool | None = None
    ) -> WorkbookDetails:
        """``getWorkbook`` → one workbook.

        Args:
            workbook_id: The workbook's id.
            include_permissions_info: Also say what the caller may do with it.

        Returns:
            The workbook.

        Examples:
            >>> datalens.workbooks.get("wb000000000001").title
            'Q1'
        """
        return self._session.send(
            endpoints.get(workbook_id, include_permissions_info=include_permissions_info)
        )

    def list(
        self,
        *,
        limit: int | None = None,
        collection_id: str | None = None,
        filter_string: str | None = None,
        order_field: OrderField | None = None,
        order_direction: SortDirection | None = None,
        only_my: bool | None = None,
        include_permissions_info: bool | None = None,
    ) -> ItemList[WorkbookListed]:
        """``getWorkbooksList`` → the workbooks of a collection, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every workbook).

        Args:
            limit: The most workbooks to return; ``None`` returns every workbook.
            collection_id: The collection to list; the root when left out.
            filter_string: Keep the workbooks whose title has this text.
            order_field: What to sort by: ``title``, ``createdAt`` or ``updatedAt``.
            order_direction: The sort direction: ``asc`` or ``desc``.
            only_my: Keep only what the caller created.
            include_permissions_info: Also say what the caller may do with each one.

        Returns:
            The workbooks.

        Examples:
            >>> found = datalens.workbooks.list(collection_id="col00000000001", limit=45)
            >>> [workbook.title for workbook in found.root]
            ['Q1', 'Q2']
        """
        paged = endpoints.list_(
            collection_id=collection_id,
            filter_string=filter_string,
            order_field=order_field,
            order_direction=order_direction,
            only_my=only_my,
            include_permissions_info=include_permissions_info,
        )
        return ItemList[WorkbookListed](list(self._session.iterate(paged, limit=limit)))

    def list_by_ids(self, workbook_ids: Sequence[str]) -> ItemList[Workbook]:
        """``getWorkbooksByIds`` → the workbooks with these ids.

        Args:
            workbook_ids: The ids of the workbooks.

        Returns:
            The workbooks found; an id the caller cannot see is left out.

        Examples:
            >>> ids = ["wb000000000001", "wb000000000002"]
            >>> [found.title for found in datalens.workbooks.list_by_ids(ids).root]
            ['Q1', 'Q2']
        """
        return self._session.send(endpoints.list_by_ids(workbook_ids))

    def access_bindings_list(
        self,
        workbook_id: str,
        *,
        limit: int | None = None,
        get_inherited_bindings: bool | None = None,
    ) -> ItemList[SubjectWithBindings]:
        """``listWorkbookAccessBindings`` → who has which role, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every subject).

        Args:
            workbook_id: The workbook's id.
            limit: The most subjects to return; ``None`` returns every subject.
            get_inherited_bindings: Also list the roles inherited from the collections above.

        Returns:
            The subjects with their roles.

        Examples:
            >>> subjects = datalens.workbooks.access_bindings_list("wb000000000001").root
            >>> subjects[0].access_bindings[0].role_id
            'datalens.workbooks.editor'
        """
        paged = endpoints.access_bindings_list(
            workbook_id, get_inherited_bindings=get_inherited_bindings
        )
        return ItemList[SubjectWithBindings](list(self._session.iterate(paged, limit=limit)))

    def entries_list(
        self,
        workbook_id: str,
        *,
        limit: int | None = None,
        include_permissions_info: bool | None = None,
        only_my: bool | None = None,
        created_by: str | None = None,
        scope: EntryScope | Sequence[EntryScope] | None = None,
        order_by: EntriesOrder | None = None,
        filters: EntriesFilters | None = None,
    ) -> ItemList[WorkbookEntry]:
        """``getWorkbookEntries`` → what a workbook holds, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every entry).

        Args:
            workbook_id: The workbook's id.
            limit: The most entries to return; ``None`` returns every entry.
            include_permissions_info: Also say what the caller may do with each entry.
            only_my: Keep only what the caller created.
            created_by: Keep only what this user created.
            scope: Keep only these kinds: one (``dash``) or several.
            order_by: What to sort by and in which direction.
            filters: Keep the entries whose name has a text.

        Returns:
            The connections, datasets, charts and dashboards of the workbook.

        Examples:
            >>> entries = datalens.workbooks.entries_list("wb000000000001", limit=45).root
            >>> [(entry.scope.root, entry.key) for entry in entries]
            [('dataset', 'Sales/orders'), ('dash', 'Sales/overview')]
        """
        paged = endpoints.entries_list(
            workbook_id,
            include_permissions_info=include_permissions_info,
            only_my=only_my,
            created_by=created_by,
            scope=scope,
            order_by=order_by,
            filters=filters,
        )
        return ItemList[WorkbookEntry](list(self._session.iterate(paged, limit=limit)))

    def create(
        self, *, title: str, collection_id: str | None = None, description: str | None = None
    ) -> WorkbookCreated:
        """``createWorkbook`` — create a workbook.

        Args:
            title: The workbook's title.
            collection_id: The collection to create it in; the root when left out.
            description: The workbook's description.

        Returns:
            The created workbook, with its ``workbook_id``.

        Examples:
            >>> datalens.workbooks.create(title="Q1", collection_id="col00000000001").workbook_id
            'wb000000000001'
        """
        return self._session.send(
            endpoints.create(title=title, collection_id=collection_id, description=description)
        )

    def update(
        self, workbook_id: str, *, title: str | None = None, description: str | None = None
    ) -> Workbook:
        """``updateWorkbook`` — change a workbook's title or description.

        Args:
            workbook_id: The workbook's id.
            title: The new title.
            description: The new description.

        Returns:
            The workbook as it is now.

        Examples:
            >>> datalens.workbooks.update("wb000000000001", title="Q1 2026").title
            'Q1 2026'
        """
        return self._session.send(
            endpoints.update(workbook_id, title=title, description=description)
        )

    def move(
        self, workbook_id: str, *, collection_id: str | None = None, title: str | None = None
    ) -> Workbook:
        """``moveWorkbook`` — move a workbook into a collection, or into the root.

        Args:
            workbook_id: The workbook's id.
            collection_id: The collection to move it into; the root when left out.
            title: A new title to give it on the way.

        Returns:
            The workbook as it is now.

        Examples:
            >>> moved = datalens.workbooks.move("wb000000000001", collection_id="col00000000002")
            >>> moved.collection_id
            'col00000000002'
        """
        return self._session.send(
            endpoints.move(workbook_id, collection_id=collection_id, title=title)
        )

    def move_bulk(
        self, workbook_ids: Sequence[str], *, collection_id: str | None = None
    ) -> WorkbooksMoved:
        """``moveWorkbooks`` — move several workbooks into a collection, or into the root.

        Args:
            workbook_ids: The ids of the workbooks.
            collection_id: The collection to move them into; the root when left out.

        Returns:
            The moved workbooks.

        Examples:
            >>> ids = ["wb000000000001", "wb000000000002"]
            >>> moved = datalens.workbooks.move_bulk(ids, collection_id="col00000000002")
            >>> len(moved.workbooks)
            2
        """
        return self._session.send(endpoints.move_bulk(workbook_ids, collection_id=collection_id))

    def delete(self, workbook_id: str) -> Workbook:
        """``deleteWorkbook`` — delete a workbook with everything it holds.

        Args:
            workbook_id: The workbook's id.

        Returns:
            The deleted workbook.

        Examples:
            >>> datalens.workbooks.delete("wb000000000001").title
            'Q1'
        """
        return self._session.send(endpoints.delete(workbook_id))

    def delete_bulk(self, workbook_ids: Sequence[str]) -> WorkbooksDeleted:
        """``deleteWorkbooks`` — delete several workbooks with everything they hold.

        Args:
            workbook_ids: The ids of the workbooks.

        Returns:
            The deleted workbooks.

        Examples:
            >>> ids = ["wb000000000001", "wb000000000002"]
            >>> len(datalens.workbooks.delete_bulk(ids).workbooks)
            2
        """
        return self._session.send(endpoints.delete_bulk(workbook_ids))

    def access_bindings_update(
        self, workbook_id: str, *, deltas: Sequence[AccessBindingDelta]
    ) -> Operation:
        """``updateWorkbookAccessBindings`` — give or take away roles on a workbook.

        Each delta adds (``ADD``) or removes (``REMOVE``) one role of one subject; the roles not
        named stay as they are.

        Args:
            workbook_id: The workbook's id.
            deltas: The roles to add and to remove.

        Returns:
            The operation that applies the change.

        Examples:
            >>> from ycli.yandex.datalens.models import AccessBindingDelta
            >>> delta = AccessBindingDelta.model_validate(
            ...     {
            ...         "action": "ADD",
            ...         "accessBinding": {
            ...             "roleId": "datalens.workbooks.viewer",
            ...             "subject": {"id": "user-2", "type": "userAccount"},
            ...         },
            ...     }
            ... )
            >>> datalens.workbooks.access_bindings_update("wb000000000001", deltas=[delta]).done
            True
        """
        return self._session.send(endpoints.access_bindings_update(workbook_id, deltas=deltas))

"""DataLens collections client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.collections import endpoints
from ycli.yandex.datalens.collections.models import ContentItem
from ycli.yandex.datalens.models import SubjectWithBindings
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.datalens.collections.models import (
        Collection,
        CollectionBreadcrumb,
        CollectionCreated,
        CollectionDetails,
        CollectionsDeleted,
        CollectionsMoved,
        RootPermissions,
    )
    from ycli.yandex.datalens.models import AccessBindingDelta, Operation


class CollectionsClient(Resource):
    """Collections: the folders of DataLens that hold workbooks and other collections."""

    def get(
        self, collection_id: str, *, include_permissions_info: bool | None = None
    ) -> CollectionDetails:
        """``getCollection`` → one collection.

        Args:
            collection_id: The collection's id.
            include_permissions_info: Also say what the caller may do with it.

        Returns:
            The collection.

        Examples:
            >>> datalens.collections.get("col00000000001").title
            'Sales'
        """
        return self._session.send(
            endpoints.get(collection_id, include_permissions_info=include_permissions_info)
        )

    def list_by_ids(self, collection_ids: Sequence[str]) -> ItemList[Collection]:
        """``getCollectionsByIds`` → the collections with these ids.

        Args:
            collection_ids: The ids of the collections.

        Returns:
            The collections found; an id the caller cannot see is left out.

        Examples:
            >>> ids = ["col00000000001", "col00000000002"]
            >>> [found.title for found in datalens.collections.list_by_ids(ids).root]
            ['Sales', 'Finance']
        """
        return self._session.send(endpoints.list_by_ids(collection_ids))

    def content_list(
        self,
        collection_id: str | None,
        *,
        limit: int | None = None,
        filter_string: str | None = None,
        order_field: str | None = None,
        order_direction: str | None = None,
        only_my: bool | None = None,
        mode: str | None = None,
        include_permissions_info: bool | None = None,
    ) -> ItemList[ContentItem]:
        """``getCollectionContent`` → what a collection holds, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every item).

        Args:
            collection_id: The collection's id; ``None`` lists the root.
            limit: The most items to return; ``None`` returns every item.
            filter_string: Keep the items whose title has this text.
            order_field: What to sort by: ``title``, ``createdAt`` or ``updatedAt``.
            order_direction: The sort direction: ``asc`` or ``desc``.
            only_my: Keep only what the caller created.
            mode: Which kinds to list: ``all``, ``onlyCollections``, ``onlyWorkbooks`` or
                ``onlyEntries``.
            include_permissions_info: Also say what the caller may do with each item.

        Returns:
            The collections, workbooks and entries of the collection.

        Examples:
            >>> items = datalens.collections.content_list("col00000000001", limit=45).root
            >>> [item.title for item in items]
            ['Reports', 'Q1']
        """
        paged = endpoints.content_list(
            collection_id,
            filter_string=filter_string,
            order_field=order_field,
            order_direction=order_direction,
            only_my=only_my,
            mode=mode,
            include_permissions_info=include_permissions_info,
        )
        return ItemList[ContentItem](list(self._session.iterate(paged, limit=limit)))

    def breadcrumbs_list(
        self, collection_id: str, *, include_permissions_info: bool | None = None
    ) -> ItemList[CollectionBreadcrumb]:
        """``getCollectionBreadcrumbs`` → the collections from the root down to this one.

        Args:
            collection_id: The collection's id.
            include_permissions_info: Also say what the caller may do with each one.

        Returns:
            The path of collections, the root's child first.

        Examples:
            >>> path = datalens.collections.breadcrumbs_list("col00000000002").root
            >>> [crumb.title for crumb in path]
            ['Sales', 'Finance']
        """
        return self._session.send(
            endpoints.breadcrumbs_list(
                collection_id, include_permissions_info=include_permissions_info
            )
        )

    def permissions_get_root(self) -> RootPermissions:
        """``getRootCollectionPermissions`` → what the caller may create in the root.

        Returns:
            Whether the caller may create a collection and a workbook in the root.

        Examples:
            >>> datalens.collections.permissions_get_root().create_workbook_in_root
            True
        """
        return self._session.send(endpoints.permissions_get_root())

    def access_bindings_list(
        self,
        collection_id: str,
        *,
        limit: int | None = None,
        get_inherited_bindings: bool | None = None,
    ) -> ItemList[SubjectWithBindings]:
        """``listCollectionAccessBindings`` → who has which role, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every subject).

        Args:
            collection_id: The collection's id.
            limit: The most subjects to return; ``None`` returns every subject.
            get_inherited_bindings: Also list the roles inherited from the collections above.

        Returns:
            The subjects with their roles.

        Examples:
            >>> subjects = datalens.collections.access_bindings_list("col00000000001").root
            >>> subjects[0].access_bindings[0].role_id
            'datalens.collections.editor'
        """
        paged = endpoints.access_bindings_list(
            collection_id, get_inherited_bindings=get_inherited_bindings
        )
        return ItemList[SubjectWithBindings](list(self._session.iterate(paged, limit=limit)))

    def create(
        self, *, title: str, parent_id: str | None = None, description: str | None = None
    ) -> CollectionCreated:
        """``createCollection`` — create a collection.

        Args:
            title: The collection's title.
            parent_id: The collection to create it in; the root when left out.
            description: The collection's description.

        Returns:
            The created collection, with its ``collection_id``.

        Examples:
            >>> datalens.collections.create(title="Sales").collection_id
            'col00000000001'
        """
        return self._session.send(
            endpoints.create(title=title, parent_id=parent_id, description=description)
        )

    def update(
        self, collection_id: str, *, title: str | None = None, description: str | None = None
    ) -> Collection:
        """``updateCollection`` — change a collection's title or description.

        Args:
            collection_id: The collection's id.
            title: The new title.
            description: The new description.

        Returns:
            The collection as it is now.

        Examples:
            >>> datalens.collections.update("col00000000001", title="Sales 2026").title
            'Sales 2026'
        """
        return self._session.send(
            endpoints.update(collection_id, title=title, description=description)
        )

    def move(
        self, collection_id: str, *, parent_id: str | None = None, title: str | None = None
    ) -> Collection:
        """``moveCollection`` — move a collection into another one, or into the root.

        Args:
            collection_id: The collection's id.
            parent_id: The collection to move it into; the root when left out.
            title: A new title to give it on the way.

        Returns:
            The collection as it is now.

        Examples:
            >>> moved = datalens.collections.move("col00000000002", parent_id="col00000000001")
            >>> moved.parent_id
            'col00000000001'
        """
        return self._session.send(endpoints.move(collection_id, parent_id=parent_id, title=title))

    def move_bulk(
        self, collection_ids: Sequence[str], *, parent_id: str | None = None
    ) -> CollectionsMoved:
        """``moveCollections`` — move several collections into another one, or into the root.

        Args:
            collection_ids: The ids of the collections.
            parent_id: The collection to move them into; the root when left out.

        Returns:
            The moved collections.

        Examples:
            >>> ids = ["col00000000002", "col00000000003"]
            >>> moved = datalens.collections.move_bulk(ids, parent_id="col00000000001")
            >>> len(moved.collections)
            2
        """
        return self._session.send(endpoints.move_bulk(collection_ids, parent_id=parent_id))

    def delete(self, collection_id: str) -> CollectionsDeleted:
        """``deleteCollection`` — delete a collection with everything it holds.

        Args:
            collection_id: The collection's id.

        Returns:
            The deleted collections: the one named and those nested in it.

        Examples:
            >>> deleted = datalens.collections.delete("col00000000001")
            >>> [found.title for found in deleted.collections]
            ['Sales', 'Finance']
        """
        return self._session.send(endpoints.delete(collection_id))

    def delete_bulk(self, collection_ids: Sequence[str]) -> CollectionsDeleted:
        """``deleteCollections`` — delete several collections with everything they hold.

        Args:
            collection_ids: The ids of the collections.

        Returns:
            The deleted collections: those named and those nested in them.

        Examples:
            >>> ids = ["col00000000001", "col00000000002"]
            >>> len(datalens.collections.delete_bulk(ids).collections)
            2
        """
        return self._session.send(endpoints.delete_bulk(collection_ids))

    def access_bindings_update(
        self, collection_id: str, *, deltas: Sequence[AccessBindingDelta]
    ) -> Operation:
        """``updateCollectionAccessBindings`` — give or take away roles on a collection.

        Each delta adds (``ADD``) or removes (``REMOVE``) one role of one subject; the roles not
        named stay as they are.

        Args:
            collection_id: The collection's id.
            deltas: The roles to add and to remove.

        Returns:
            The operation that applies the change.

        Examples:
            >>> from ycli.yandex.datalens.models import AccessBindingDelta
            >>> delta = AccessBindingDelta.model_validate(
            ...     {
            ...         "action": "ADD",
            ...         "accessBinding": {
            ...             "roleId": "datalens.collections.viewer",
            ...             "subject": {"id": "user-2", "type": "userAccount"},
            ...         },
            ...     }
            ... )
            >>> datalens.collections.access_bindings_update("col00000000001", deltas=[delta]).done
            True
        """
        return self._session.send(endpoints.access_bindings_update(collection_id, deltas=deltas))

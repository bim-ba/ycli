"""DataLens shared entries client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.sharedentries import endpoints

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.core.listing import Listing
    from ycli.yandex.datalens.models import AccessBindingDelta, Operation, SubjectWithBindings


class SharedEntriesClient(Resource):
    """Shared entries: a connection or a dataset that lies in a collection, not in a workbook."""

    def access_bindings_list(
        self,
        entry_id: str,
        *,
        limit: int | None = None,
        next: str | None = None,
        get_inherited_bindings: bool | None = None,
    ) -> Listing[SubjectWithBindings]:
        """``listSharedEntryAccessBindings`` → who has which role, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every subject). An entry that lies in a workbook, or an
        id nothing knows, answers an empty list, not an error.

        Args:
            entry_id: The shared entry's id.
            limit: The most subjects to return; ``None`` returns every subject.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.
            get_inherited_bindings: Also list the roles inherited from the collections above.

        Returns:
            The subjects with their roles.

        Examples:
            >>> subjects = (
            ...     datalens.sharedentries.access_bindings_list("ent0000000001").collect().items
            ... )
            >>> subjects[0].access_bindings[0].role_id
            'datalens.sharedEntries.admin'
        """
        paged = endpoints.access_bindings_list(
            entry_id, get_inherited_bindings=get_inherited_bindings
        )
        return self._session.iterate(paged, limit=limit, next=next)

    def access_bindings_update(
        self, entry_id: str, *, deltas: Sequence[AccessBindingDelta]
    ) -> Operation:
        """``updateSharedEntryAccessBindings`` — give or take away roles on a shared entry.

        Each delta adds (``ADD``) or removes (``REMOVE``) one role of one subject; the roles not
        named stay as they are. The roles are ``datalens.sharedEntries.*``.

        Args:
            entry_id: The shared entry's id.
            deltas: The roles to add and to remove.

        Returns:
            The operation that applies the change.

        Examples:
            >>> from ycli.yandex.datalens.models import AccessBindingDelta
            >>> delta = AccessBindingDelta.model_validate(
            ...     {
            ...         "action": "ADD",
            ...         "accessBinding": {
            ...             "roleId": "datalens.sharedEntries.viewer",
            ...             "subject": {"id": "user-2", "type": "userAccount"},
            ...         },
            ...     }
            ... )
            >>> datalens.sharedentries.access_bindings_update("ent0000000001", deltas=[delta]).done
            True
        """
        return self._session.send(endpoints.access_bindings_update(entry_id, deltas=deltas))

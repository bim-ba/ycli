"""Tracker issue-types client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.issuetypes.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.issuetypes import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.issuetypes.models import (
        IssueType,
        IssueTypeCreate,
        IssueTypeList,
        IssueTypeUpdate,
    )


class IssueTypesClient(Resource):
    """List, create and edit issue types."""

    def list(self) -> IssueTypeList:
        """``GET /issuetypes`` → issue-type listing.

        Returns:
            The issue types.

        Examples:
            >>> tracker.issuetypes.list().root[0].key
            'bug'
        """
        return self._session.send(endpoints.list_issue_types())

    def create(self, body: IssueTypeCreate) -> IssueType:
        """Create an issue type from a typed ``IssueTypeCreate`` body. Returns the ``IssueType``.

        Args:
            body: The new issue type's key and localized name.

        Returns:
            The created issue type.

        Examples:
            >>> from ycli.yandex.tracker.issuetypes.models import IssueTypeCreate, LocalizedName
            >>> tracker.issuetypes.create(
            ...     IssueTypeCreate(key="client", name=LocalizedName(ru="Клиент", en="Client"))
            ... ).key
            'client'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_issue_type(dumped))

    def edit(
        self, issue_type_id: str, body: IssueTypeUpdate, *, version: int | None = None
    ) -> IssueType:
        """Edit issue type ``issue_type_id`` from a typed ``IssueTypeUpdate`` body.

        ``version`` is the current issue-type version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version with 409).

        Args:
            issue_type_id: The issue type's id.
            body: The fields to change.
            version: The current issue-type version, sent as ``?version=``; ``None`` sends none.

        Returns:
            The updated issue type.

        Examples:
            >>> from ycli.yandex.tracker.issuetypes.models import IssueTypeUpdate, LocalizedName
            >>> tracker.issuetypes.edit(
            ...     "23",
            ...     IssueTypeUpdate(name=LocalizedName(ru="Покупатель", en="Buyer")),
            ...     version=2,
            ... ).key
            'client'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_issue_type(issue_type_id, dumped, version=version))

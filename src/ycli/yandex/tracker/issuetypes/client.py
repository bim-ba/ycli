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

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issuetypes.list().root[0].key  # doctest: +SKIP
            'bug'
        """
        return self._session.send(endpoints.list_issue_types())

    def create(self, body: IssueTypeCreate) -> IssueType:
        """Create an issue type from a typed ``IssueTypeCreate`` body. Returns the ``IssueType``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issuetypes.create(
            ...     IssueTypeCreate(key="client", name=LocalizedName(ru="Клиент"))
            ... ).key  # doctest: +SKIP
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

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issuetypes.edit(
            ...     "23", IssueTypeUpdate(name=LocalizedName(ru="Покупатель")), version=1
            ... ).key  # doctest: +SKIP
            'client'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_issue_type(issue_type_id, dumped, version=version))

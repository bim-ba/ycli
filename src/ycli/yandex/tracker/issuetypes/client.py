"""Declarative Tracker issue-types client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.issuetypes.models import (
    IssueType,
    IssueTypeCreate,
    IssueTypeList,
    IssueTypeUpdate,
)


class IssueTypesClient(TrackerResource):
    """Declarative HTTP for ``/issuetypes`` (list + create + edit)."""

    @uplink.returns.json()
    @uplink.get("issuetypes")
    def list(self) -> IssueTypeList:  # ty: ignore[empty-body]
        """``GET /issuetypes`` → issue-type listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issuetypes.list().root[0].key  # doctest: +SKIP
            'bug'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issuetypes/")
    def _create(self, body: uplink.Body) -> IssueType:  # ty: ignore[empty-body]
        """``POST /issuetypes/`` — create from a ready JSON body (see ``create``)."""

    def create(self, body: IssueTypeCreate) -> IssueType:
        """Create an issue type from a typed ``IssueTypeCreate`` body. Returns the ``IssueType``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issuetypes.create(
            ...     IssueTypeCreate(key="client", name=LocalizedName(ru="Клиент"))
            ... ).key  # doctest: +SKIP
            'client'
        """
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("issuetypes/{issue_type_id}")
    def _edit(
        self,
        issue_type_id: uplink.Path,
        body: uplink.Body,
        version: uplink.Query("version") = None,  # ty: ignore[invalid-type-form]
    ) -> IssueType:  # ty: ignore[empty-body]
        """``PATCH /issuetypes/{issue_type_id}?version=`` — edit (see ``edit``)."""

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
        return self._edit(
            issue_type_id=issue_type_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
            version=version,
        )

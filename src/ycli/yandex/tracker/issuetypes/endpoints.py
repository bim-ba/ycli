"""Tracker ``/issuetypes`` operations, declared once (sans-IO).

Examples:
    >>> update("23", {"description": "x"}, version=1).params
    {'version': 1}
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.issuetypes.models import IssueType, IssueTypeCreate, IssueTypeUpdate


def list_() -> Endpoint[ItemList[IssueType]]:
    return Endpoint(HTTPMethod.GET, "issuetypes", ItemList[IssueType])


def create(body: IssueTypeCreate) -> Endpoint[IssueType]:
    return Endpoint(HTTPMethod.POST, "issuetypes/", IssueType, json=body)


def update(
    issue_type_id: str, body: IssueTypeUpdate, *, version: int | None = None
) -> Endpoint[IssueType]:
    """``PATCH /issuetypes/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        HTTPMethod.PATCH,
        f"issuetypes/{segment(issue_type_id)}",
        IssueType,
        json=body,
        params={"version": version},
    )

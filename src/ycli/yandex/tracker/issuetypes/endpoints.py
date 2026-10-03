"""Tracker ``/issuetypes`` operations, declared once (sans-IO).

Examples:
    >>> update_issue_type("23", {"description": "x"}, version=1).params
    {'version': 1}
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.issuetypes.models import IssueType, IssueTypeCreate, IssueTypeUpdate


def list_issue_types() -> Endpoint[ItemList[IssueType]]:
    return Endpoint("GET", "issuetypes", ItemList[IssueType])


def create_issue_type(body: IssueTypeCreate) -> Endpoint[IssueType]:
    return Endpoint("POST", "issuetypes/", IssueType, json=body)


def update_issue_type(
    issue_type_id: str, body: IssueTypeUpdate, *, version: int | None = None
) -> Endpoint[IssueType]:
    """``PATCH /issuetypes/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        "PATCH",
        f"issuetypes/{segment(issue_type_id)}",
        IssueType,
        json=body,
        params={"version": version},
    )

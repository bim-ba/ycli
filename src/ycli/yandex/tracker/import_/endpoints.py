"""Tracker ``/_import`` operations (admin-only back-fill), each declared once (sans-IO).

Example:
    >>> import_worklog("TEST-1", {"duration": "PT1H"}).path
    'issues/TEST-1/worklogs/_import'
    >>> import_file("JUNE-2", filename="a.png", created_at="t", created_by="11", data=b"").params
    {'filename': 'a.png', 'createdAt': 't', 'createdBy': '11'}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.attachments.models import Attachment
from ycli.yandex.tracker.comments.models import Comment
from ycli.yandex.tracker.issues.models import Issue
from ycli.yandex.tracker.links.models import Link
from ycli.yandex.tracker.worklog.models import WorklogList


def import_task(body: dict[str, Any]) -> Endpoint[Issue]:
    return Endpoint("POST", "issues/_import", Issue, json=body)


def import_comment(issue_key: str, body: dict[str, Any]) -> Endpoint[Comment]:
    return Endpoint("POST", f"issues/{segment(issue_key)}/comments/_import", Comment, json=body)


def import_link(issue_key: str, body: dict[str, Any]) -> Endpoint[Link]:
    return Endpoint("POST", f"issues/{segment(issue_key)}/links/_import", Link, json=body)


def import_worklog(issue_key: str, body: dict[str, Any]) -> Endpoint[WorklogList]:
    """The live endpoint answers with a JSON array of the created record(s)."""
    path = f"issues/{segment(issue_key)}/worklogs/_import"
    return Endpoint("POST", path, WorklogList, json=body)


def import_file(
    issue_key: str, *, filename: str, created_at: str, created_by: str, data: bytes
) -> Endpoint[Attachment]:
    """Multipart upload; the API docs name no part, so it keeps the name ycli always sent."""
    return Endpoint(
        "POST",
        f"issues/{segment(issue_key)}/attachments/_import",
        Attachment,
        params={"filename": filename, "createdAt": created_at, "createdBy": created_by},
        files={"file_data": ("file_data", data)},
    )

"""Tracker ``/_import`` operations (admin-only back-fill), each declared once (sans-IO).

Examples:
    >>> worklog("TEST-1", {"duration": "PT1H"}).path
    'issues/TEST-1/worklogs/_import'
    >>> file("JUNE-2", filename="a.png", created_at="t", created_by="11", data=b"").params
    {'filename': 'a.png', 'createdAt': 't', 'createdBy': '11'}
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.attachments.models import Attachment
from ycli.yandex.tracker.comments.models import Comment
from ycli.yandex.tracker.issues.models import Issue
from ycli.yandex.tracker.links.models import Link
from ycli.yandex.tracker.worklog.models import Worklog

if TYPE_CHECKING:
    from ycli.yandex.tracker.import_.models import (
        ImportComment,
        ImportLink,
        ImportTask,
        ImportWorklog,
    )


def task(body: ImportTask) -> Endpoint[Issue]:
    return Endpoint("POST", "issues/_import", Issue, json=body)


def comment(issue_key: str, body: ImportComment) -> Endpoint[Comment]:
    return Endpoint("POST", f"issues/{segment(issue_key)}/comments/_import", Comment, json=body)


def link(issue_key: str, body: ImportLink) -> Endpoint[Link]:
    return Endpoint("POST", f"issues/{segment(issue_key)}/links/_import", Link, json=body)


def worklog(issue_key: str, body: ImportWorklog) -> Endpoint[ItemList[Worklog]]:
    """The live endpoint answers with a JSON array of the created record(s)."""
    path = f"issues/{segment(issue_key)}/worklogs/_import"
    return Endpoint("POST", path, ItemList[Worklog], json=body)


def file(
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


def comment_file(
    issue_key: str, comment_id: str, *, filename: str, created_at: str, created_by: str, data: bytes
) -> Endpoint[Attachment]:
    """Multipart upload onto a comment; the part name is the one :func:`file` sends."""
    return Endpoint(
        "POST",
        f"issues/{segment(issue_key)}/comments/{segment(comment_id)}/attachments/_import",
        Attachment,
        params={"filename": filename, "createdAt": created_at, "createdBy": created_by},
        files={"file_data": ("file_data", data)},
    )

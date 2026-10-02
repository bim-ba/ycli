"""Tracker issue ``/attachments`` operations, each declared once (sans-IO).

Example:
    >>> download_thumbnail("JUNE-2", "4159").path
    'issues/JUNE-2/thumbnails/4159'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.attachments.models import AttachmentList


def list_attachments(issue_key: str) -> Endpoint[AttachmentList]:
    return Endpoint("GET", f"issues/{segment(issue_key)}/attachments", AttachmentList)


def download_attachment(issue_key: str, file_id: str, filename: str) -> Endpoint[bytes]:
    path = f"issues/{segment(issue_key)}/attachments/{segment(file_id)}/{segment(filename)}"
    return Endpoint("GET", path, bytes)


def download_thumbnail(issue_key: str, file_id: str) -> Endpoint[bytes]:
    return Endpoint("GET", f"issues/{segment(issue_key)}/thumbnails/{segment(file_id)}", bytes)

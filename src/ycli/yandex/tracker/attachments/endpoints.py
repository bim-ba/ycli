"""Tracker issue ``/attachments`` operations, each declared once (sans-IO).

Examples:
    >>> download_thumbnail("JUNE-2", "4159").path
    'issues/JUNE-2/thumbnails/4159'
    >>> upload_temp_attachment(filename="a.txt", data=b"", rename_to="b.txt").params
    {'filename': 'b.txt'}
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.attachments.models import Attachment


def list_attachments(issue_key: str) -> Endpoint[ItemList[Attachment]]:
    return Endpoint("GET", f"issues/{segment(issue_key)}/attachments", ItemList[Attachment])


def download_attachment(issue_key: str, file_id: str, filename: str) -> Endpoint[bytes]:
    path = f"issues/{segment(issue_key)}/attachments/{segment(file_id)}/{segment(filename)}"
    return Endpoint("GET", path, bytes)


def download_thumbnail(issue_key: str, file_id: str) -> Endpoint[bytes]:
    return Endpoint("GET", f"issues/{segment(issue_key)}/thumbnails/{segment(file_id)}", bytes)


def get_attachment(issue_key: str, file_id: str) -> Endpoint[Attachment]:
    """``GET …/attachments/{file_id}`` → the metadata; the bytes come from the ``/{name}`` path."""
    path = f"issues/{segment(issue_key)}/attachments/{segment(file_id)}"
    return Endpoint("GET", path, Attachment)


def delete_attachment(issue_key: str, file_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", f"issues/{segment(issue_key)}/attachments/{segment(file_id)}")


def upload_attachment(
    issue_key: str, *, filename: str, data: bytes, rename_to: str | None
) -> Endpoint[Attachment]:
    """Multipart field ``file``; the query ``filename`` renames the stored file when set."""
    return Endpoint(
        "POST",
        f"issues/{segment(issue_key)}/attachments",
        Attachment,
        params={"filename": rename_to},
        files={"file": (filename, data)},
    )


def upload_temp_attachment(
    *, filename: str, data: bytes, rename_to: str | None
) -> Endpoint[Attachment]:
    """``POST /attachments``: the returned id attaches to one issue or comment, once."""
    return Endpoint(
        "POST",
        "attachments",
        Attachment,
        params={"filename": rename_to},
        files={"file": (filename, data)},
    )

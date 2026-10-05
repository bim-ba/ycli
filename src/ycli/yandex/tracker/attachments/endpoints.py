"""Tracker issue ``/attachments`` operations, each declared once (sans-IO).

Examples:
    >>> thumbnails_download("JUNE-2", "4159").path
    'issues/JUNE-2/thumbnails/4159'
    >>> upload_temp(filename="a.txt", data=b"", rename_to="b.txt").params
    {'filename': 'b.txt'}
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.attachments.models import Attachment


def list_(issue_key: str) -> Endpoint[ItemList[Attachment]]:
    return Endpoint(
        HTTPMethod.GET, f"issues/{segment(issue_key)}/attachments", ItemList[Attachment]
    )


def download(issue_key: str, file_id: str, filename: str) -> Endpoint[bytes]:
    path = f"issues/{segment(issue_key)}/attachments/{segment(file_id)}/{segment(filename)}"
    return Endpoint(HTTPMethod.GET, path, bytes)


def thumbnails_download(issue_key: str, file_id: str) -> Endpoint[bytes]:
    return Endpoint(
        HTTPMethod.GET, f"issues/{segment(issue_key)}/thumbnails/{segment(file_id)}", bytes
    )


def get(issue_key: str, file_id: str) -> Endpoint[Attachment]:
    """``GET …/attachments/{file_id}`` → the metadata; the bytes come from the ``/{name}`` path."""
    path = f"issues/{segment(issue_key)}/attachments/{segment(file_id)}"
    return Endpoint(HTTPMethod.GET, path, Attachment)


def delete(issue_key: str, file_id: str) -> Endpoint[None]:
    return Endpoint(
        HTTPMethod.DELETE, f"issues/{segment(issue_key)}/attachments/{segment(file_id)}"
    )


def upload(
    issue_key: str, *, filename: str, data: bytes, rename_to: str | None
) -> Endpoint[Attachment]:
    """Multipart field ``file``; the query ``filename`` renames the stored file when set."""
    return Endpoint(
        HTTPMethod.POST,
        f"issues/{segment(issue_key)}/attachments",
        Attachment,
        params={"filename": rename_to},
        files={"file": (filename, data)},
    )


def upload_temp(*, filename: str, data: bytes, rename_to: str | None) -> Endpoint[Attachment]:
    """``POST /attachments``: the returned id attaches to one issue or comment, once."""
    return Endpoint(
        HTTPMethod.POST,
        "attachments",
        Attachment,
        params={"filename": rename_to},
        files={"file": (filename, data)},
    )


def import_(
    issue_key: str, *, filename: str, created_at: str, created_by: str, data: bytes
) -> Endpoint[Attachment]:
    """Multipart upload; the API docs name no part, so it keeps the name ycli always sent."""
    return Endpoint(
        HTTPMethod.POST,
        f"issues/{segment(issue_key)}/attachments/_import",
        Attachment,
        params={"filename": filename, "createdAt": created_at, "createdBy": created_by},
        files={"file_data": ("file_data", data)},
    )


def import_for_comment(
    issue_key: str, comment_id: str, *, filename: str, created_at: str, created_by: str, data: bytes
) -> Endpoint[Attachment]:
    """Multipart upload onto a comment; the part name is the one :func:`import_` sends."""
    return Endpoint(
        HTTPMethod.POST,
        f"issues/{segment(issue_key)}/comments/{segment(comment_id)}/attachments/_import",
        Attachment,
        params={"filename": filename, "createdAt": created_at, "createdBy": created_by},
        files={"file_data": ("file_data", data)},
    )
